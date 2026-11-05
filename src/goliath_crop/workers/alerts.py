"""Alert evaluation worker (wake + claim stub)."""

from __future__ import annotations

from dataclasses import dataclass

from goliath_crop.db import connect


@dataclass(frozen=True)
class AlertEvaluateResult:
    alert_id: int
    status: str


def evaluate_alert(*, alert_id: int) -> AlertEvaluateResult:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE crop_alerts.alert_events
                SET detail = detail || jsonb_build_object('evaluated', true)
                WHERE id = %s
                RETURNING id
                """,
                (alert_id,),
            )
            row = cur.fetchone()
            if row is None:
                raise RuntimeError(f"unknown alert_id {alert_id}")
        conn.commit()
    return AlertEvaluateResult(alert_id=alert_id, status="noted")
