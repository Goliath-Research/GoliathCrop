"""Element84 Earth Search STAC client (free, no API key)."""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone


EARTH_SEARCH_STAC_ROOT = "https://earth-search.aws.element84.com/v1"


@dataclass(frozen=True)
class StacSceneCandidate:
    item_id: str
    collection: str
    acquired_at: datetime
    cloud_fraction: float | None
    metadata: dict[str, object]


def _parse_datetime(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def search_field_scenes(
    *,
    bbox: tuple[float, float, float, float],
    collections: list[str],
    start: date,
    end: date,
    max_cloud_fraction: float,
    limit: int = 10,
) -> list[StacSceneCandidate]:
    if end < start:
        return []
    body = {
        "collections": collections,
        "bbox": list(bbox),
        "datetime": f"{start.isoformat()}/{end.isoformat()}",
        "limit": limit,
        "query": {"eo:cloud_cover": {"lt": max_cloud_fraction * 100.0}},
    }
    request = urllib.request.Request(
        f"{EARTH_SEARCH_STAC_ROOT}/search",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Accept": "application/geo+json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    features = payload.get("features") or []
    scenes: list[StacSceneCandidate] = []
    for feature in features:
        props = feature.get("properties") or {}
        item_id = str(feature.get("id") or "")
        if not item_id:
            continue
        datetime_raw = props.get("datetime") or props.get("start_datetime")
        if not datetime_raw:
            continue
        cloud = props.get("eo:cloud_cover")
        cloud_fraction = float(cloud) / 100.0 if cloud is not None else None
        if cloud_fraction is not None and cloud_fraction >= max_cloud_fraction:
            continue
        collection = str(feature.get("collection") or collections[0])
        scenes.append(
            StacSceneCandidate(
                item_id=item_id,
                collection=collection,
                acquired_at=_parse_datetime(str(datetime_raw)),
                cloud_fraction=cloud_fraction,
                metadata={"stac": feature},
            )
        )
    return scenes


def default_scene_window(*, days_back: int) -> tuple[date, date]:
    end = date.today()
    start = end - timedelta(days=days_back)
    return start, end
