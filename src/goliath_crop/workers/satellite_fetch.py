"""Satellite STAC fetch worker."""

from __future__ import annotations

import json
from dataclasses import dataclass

from goliath_crop.db import connect
from goliath_crop.imagery.stac import default_scene_window, search_field_scenes


@dataclass(frozen=True)
class SceneFetchResult:
    scenes_registered: int
    scene_ids: list[int]


def fetch_scenes_for_field(
    *,
    user_id: int,
    field_id: int,
    days_back: int,
    max_cloud_fraction: float,
    collections: list[str],
) -> SceneFetchResult:
    start, end = default_scene_window(days_back=days_back)
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                  ST_XMin(ST_Envelope(fld.geom)),
                  ST_YMin(ST_Envelope(fld.geom)),
                  ST_XMax(ST_Envelope(fld.geom)),
                  ST_YMax(ST_Envelope(fld.geom))
                FROM crop_core.fields fld
                WHERE fld.id = %s AND fld.geom IS NOT NULL
                """,
                (field_id,),
            )
            bbox_row = cur.fetchone()
            if bbox_row is None or bbox_row[0] is None:
                return SceneFetchResult(scenes_registered=0, scene_ids=[])

        bbox = (
            float(bbox_row[0]),
            float(bbox_row[1]),
            float(bbox_row[2]),
            float(bbox_row[3]),
        )
        candidates = search_field_scenes(
            bbox=bbox,
            collections=collections,
            start=start,
            end=end,
            max_cloud_fraction=max_cloud_fraction,
            limit=5,
        )
        scene_ids: list[int] = []
        for candidate in candidates:
            source = "sentinel-2" if "sentinel" in candidate.collection else "landsat"
            metadata = json.dumps(candidate.metadata)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT crop_img.sp_register_stac_scene(
                      %s, %s, %s, %s, %s, %s, %s::jsonb
                    )
                    """,
                    (
                        user_id,
                        field_id,
                        candidate.item_id,
                        source,
                        candidate.acquired_at,
                        candidate.cloud_fraction,
                        metadata,
                    ),
                )
                row = cur.fetchone()
                if row is not None:
                    scene_ids.append(int(row[0]))
            conn.commit()
    return SceneFetchResult(scenes_registered=len(scene_ids), scene_ids=scene_ids)
