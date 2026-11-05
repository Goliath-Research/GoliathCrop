"""COG storage paths for imagery workers (local dir or S3-compatible URI prefix)."""

from __future__ import annotations

import os
from pathlib import Path


def raster_root() -> str:
    return os.environ.get("CROP_RASTER_ROOT", "/tmp/goliath-crop-rasters").rstrip("/")


def cog_uri_for_scene(scene_id: int, *, suffix: str = "ndvi.tif") -> str:
    root = raster_root()
    if root.startswith("s3://"):
        return f"{root}/scenes/{scene_id}/{suffix}"
    path = Path(root) / "scenes" / str(scene_id) / suffix
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.as_uri()
