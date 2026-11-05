"""Yield prediction DomainProgram (CPU baseline; RunPod-ready backend hook)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from goliath_crop.db import connect
from goliath_crop.yield_model import PlantingFeatures, predict_for_planting


@dataclass(frozen=True)
class SeasonYieldResult:
    season_id: int
    planting_count: int
    predictions_written: int
    model_backend: str


def _features_for_planting(cur, planting_id: int) -> PlantingFeatures:
    cur.execute(
        """
        SELECT
          pl.id,
          COALESCE(SUM(w.gdd), 0) AS gdd_total,
          (
            SELECT AVG(fis.mean_value)
            FROM crop_img.field_index_stats fis
            WHERE fis.field_id = pl.field_id
              AND fis.index_name = 'ndvi'
          ) AS ndvi_mean,
          v.maturity_days,
          fld.area_ha
        FROM crop_core.plantings pl
        INNER JOIN crop_core.fields fld ON fld.id = pl.field_id
        INNER JOIN crop_core.varieties v ON v.id = pl.variety_id
        LEFT JOIN crop_obs.weather_daily w
          ON w.field_id = pl.field_id
         AND w.obs_date >= pl.sown_on
        WHERE pl.id = %s
        GROUP BY pl.id, v.maturity_days, fld.area_ha, pl.field_id, pl.sown_on
        """,
        (planting_id,),
    )
    row = cur.fetchone()
    if row is None:
        raise ValueError(f"unknown planting_id {planting_id}")
    return PlantingFeatures(
        planting_id=int(row[0]),
        gdd_total=float(row[1] or 0.0),
        ndvi_mean=float(row[2]) if row[2] is not None else None,
        maturity_days=int(row[3]) if row[3] is not None else None,
        area_ha=float(row[4]) if row[4] is not None else None,
    )


def run_yield_predict_for_season(*, season_id: int, user_id: int | None = None) -> SeasonYieldResult:
    run_id = uuid.uuid4()
    predictions_written = 0
    planting_count = 0
    backend = "cpu"
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id FROM crop_core.plantings WHERE season_id = %s ORDER BY id
                """,
                (season_id,),
            )
            planting_ids = [int(r[0]) for r in cur.fetchall()]
            planting_count = len(planting_ids)
            for planting_id in planting_ids:
                features = _features_for_planting(cur, planting_id)
                prediction = predict_for_planting(features)
                backend = prediction.model_backend
                cur.execute(
                    """
                    SELECT crop_yield.sp_store_prediction(%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        user_id,
                        planting_id,
                        prediction.predicted_t_ha,
                        prediction.model_version,
                        prediction.model_backend,
                        str(run_id),
                    ),
                )
                predictions_written += 1
        conn.commit()
    return SeasonYieldResult(
        season_id=season_id,
        planting_count=planting_count,
        predictions_written=predictions_written,
        model_backend=backend,
    )


def enqueue_season_backlog(season_id: int | None = None) -> int:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT crop_yield.sp_enqueue_season_backlog(%s)",
                (season_id,),
            )
            row = cur.fetchone()
        conn.commit()
    return int(row[0]) if row else 0
