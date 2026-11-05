"""Sensor batch ingest worker helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from goliath_crop.db import connect


@dataclass(frozen=True)
class SensorIngestResult:
    inserted_count: int


def ingest_sensor_batch(*, device_id: int, readings: list[dict[str, Any]]) -> SensorIngestResult:
    payload = json.dumps(readings)
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT crop_obs.sp_ingest_sensor_batch(%s, %s::jsonb)",
                (device_id, payload),
            )
            row = cur.fetchone()
            if row is None:
                raise RuntimeError("sp_ingest_sensor_batch returned no row")
            inserted = int(row[0])
        conn.commit()
    return SensorIngestResult(inserted_count=inserted)


def run_sensor_qc(*, device_id: int) -> int:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT crop_alerts.sp_evaluate_sensor_thresholds(%s)",
                (device_id,),
            )
            row = cur.fetchone()
            opened = int(row[0]) if row and row[0] is not None else 0
        conn.commit()
    return opened
