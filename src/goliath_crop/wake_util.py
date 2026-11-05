"""Capability wake channel naming aligned with GoliathApp dual activation."""

from __future__ import annotations

import re

_SEGMENT_SAFE = re.compile(r"[^a-zA-Z0-9._-]+")


def capability_pg_notify_channel(capability: str) -> str:
    """Map ``crop.ingest`` → ``gw1_capability_crop_ingest`` (Postgres NOTIFY identifier)."""
    cleaned = _SEGMENT_SAFE.sub("_", capability.strip())
    if not cleaned:
        raise ValueError("capability must not be empty")
    suffix = f"capability.{cleaned}".replace(".", "_")
    return f"gw1_{suffix}"
