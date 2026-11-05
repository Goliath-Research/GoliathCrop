"""Imagery NDVI processing worker (COG placeholder + index stats)."""

from __future__ import annotations

from dataclasses import dataclass

from goliath_crop.db import connect
from goliath_crop.imagery.storage import cog_uri_for_scene


@dataclass(frozen=True)
class ImageryProcessResult:
    scene_id: int
    cog_uri: str
    ndvi_mean: float


def _estimate_ndvi_from_metadata(metadata: dict[str, object] | None) -> float:
    if not metadata:
        return 0.45
    stac = metadata.get("stac")
    if isinstance(stac, dict):
        props = stac.get("properties")
        if isinstance(props, dict):
            for key in ("s2:vegetation_percentage", "eo:cloud_cover"):
                if key in props and isinstance(props[key], (int, float)):
                    if key == "eo:cloud_cover":
                        return max(0.1, 0.75 - float(props[key]) / 200.0)
    return 0.45


def process_scene(*, scene_id: int) -> ImageryProcessResult:
    cog_uri = cog_uri_for_scene(scene_id)
    ndvi_mean = 0.45
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT metadata
                FROM crop_img.imagery_scenes
                WHERE id = %s
                """,
                (scene_id,),
            )
            row = cur.fetchone()
            if row and row[0] is not None:
                ndvi_mean = _estimate_ndvi_from_metadata(row[0])
            cur.execute(
                """
                SELECT crop_img.sp_complete_scene_index(%s, %s, %s, %s, %s)
                """,
                (scene_id, cog_uri, ndvi_mean, ndvi_mean - 0.1, ndvi_mean + 0.1),
            )
        conn.commit()
    return ImageryProcessResult(scene_id=scene_id, cog_uri=cog_uri, ndvi_mean=ndvi_mean)


def register_drone_upload(
    *,
    field_id: int,
    storage_uri: str,
    acquired_at,
    footprint_wkt: str | None,
) -> int:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT crop_img.sp_register_drone_upload(%s, %s, %s, %s)
                """,
                (field_id, storage_uri, acquired_at, footprint_wkt),
            )
            row = cur.fetchone()
            if row is None:
                raise RuntimeError("sp_register_drone_upload returned no row")
            scene_id = int(row[0])
        conn.commit()
    return scene_id
