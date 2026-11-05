"""Worker-side domain handlers (claim path via goliath-gateway)."""

from __future__ import annotations

from dataclasses import dataclass

from goliath_crop.db import connect
from goliath_crop.weather.open_meteo import (
    default_backfill_window,
    fetch_open_meteo_daily,
    observation_with_gdd,
)


@dataclass(frozen=True)
class WeatherSyncResult:
    fields_refreshed: int
    rows_upserted: int


def refresh_weather(
    *,
    farm_id: int | None,
    field_id: int | None,
    days_back: int = 7,
) -> WeatherSyncResult:
    start, end = default_backfill_window(days_back=days_back)
    fields_refreshed = 0
    rows_upserted = 0
    with connect() as conn:
        with conn.cursor() as cur:
            if field_id is not None:
                field_rows = [(field_id,)]
            elif farm_id is not None:
                cur.execute(
                    """
                    SELECT f.id
                    FROM crop_core.fields f
                    WHERE f.farm_id = %s AND f.geom IS NOT NULL
                    ORDER BY f.id
                    """,
                    (farm_id,),
                )
                field_rows = cur.fetchall()
            else:
                cur.execute(
                    """
                    SELECT f.id
                    FROM crop_core.fields f
                    WHERE f.geom IS NOT NULL
                    ORDER BY f.id
                    LIMIT 500
                    """
                )
                field_rows = cur.fetchall()

        for (fid,) in field_rows:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT latitude, longitude
                    FROM crop_obs.fn_field_centroid_wgs84(%s)
                    """,
                    (fid,),
                )
                centroid = cur.fetchone()
                if centroid is None or centroid[0] is None:
                    continue
                latitude, longitude = float(centroid[0]), float(centroid[1])
                cur.execute(
                    """
                    SELECT COALESCE(f.timezone, 'UTC')
                    FROM crop_core.fields fld
                    INNER JOIN crop_core.farms f ON f.id = fld.farm_id
                    WHERE fld.id = %s
                    """,
                    (fid,),
                )
                tz_row = cur.fetchone()
                timezone = tz_row[0] if tz_row else "UTC"
            observations = fetch_open_meteo_daily(
                latitude,
                longitude,
                start=start,
                end=end,
                timezone=str(timezone),
            )
            if not observations:
                continue
            with conn.cursor() as cur:
                fields_refreshed += 1
                for obs in observations:
                    gdd, et0 = observation_with_gdd(obs)
                    cur.execute(
                        """
                        SELECT crop_obs.sp_upsert_weather_daily(
                          %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        """,
                        (
                            fid,
                            obs.obs_date,
                            obs.tmin_c,
                            obs.tmax_c,
                            obs.precip_mm,
                            gdd,
                            et0,
                            "open-meteo",
                        ),
                    )
                    rows_upserted += 1
            conn.commit()
    return WeatherSyncResult(fields_refreshed=fields_refreshed, rows_upserted=rows_upserted)
