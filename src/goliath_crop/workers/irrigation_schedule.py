"""Irrigation scheduling DomainProgram (FAO-56 water balance)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from goliath_crop.db import connect
from goliath_crop.irrigation.fao56 import compute_daily_balance


@dataclass(frozen=True)
class IrrigationScheduleResult:
    field_id: int
    balance_date: date
    recommended_irrigation_mm: float
    depletion_mm: float


def _latest_soil_moisture(cur, field_id: int) -> float | None:
    cur.execute(
        """
        SELECT r.value
        FROM crop_obs.sensor_readings r
        INNER JOIN crop_obs.devices d ON d.id = r.device_id
        WHERE d.field_id = %s
          AND r.metric IN ('soil_moisture_pct', 'soil_moisture', 'vwc')
        ORDER BY r.ts DESC
        LIMIT 1
        """,
        (field_id,),
    )
    row = cur.fetchone()
    if row is None or row[0] is None:
        return None
    value = float(row[0])
    if value <= 1.0:
        return value * 100.0
    return value


def _irrigation_applied_on_date(cur, field_id: int, balance_date: date) -> float:
    cur.execute(
        """
        SELECT COALESCE(SUM(o.rate), 0)
        FROM crop_ops.operations o
        INNER JOIN crop_core.plantings pl ON pl.id = o.planting_id
        WHERE pl.field_id = %s
          AND o.kind = 'irrigation'
          AND o.performed_on::date = %s
        """,
        (field_id, balance_date),
    )
    row = cur.fetchone()
    return float(row[0]) if row and row[0] is not None else 0.0


def run_irrigation_schedule(
    *,
    field_id: int,
    balance_date: date | None = None,
) -> IrrigationScheduleResult:
    target_date = balance_date or date.today()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT et0_mm, precip_mm
                FROM crop_obs.weather_daily
                WHERE field_id = %s AND obs_date = %s
                """,
                (field_id, target_date),
            )
            weather = cur.fetchone()
            et0_mm = float(weather[0]) if weather and weather[0] is not None else 0.0
            precip_mm = float(weather[1]) if weather and weather[1] is not None else 0.0

            cur.execute(
                """
                SELECT depletion_mm, taw_mm, kc
                FROM crop_irr.field_balance
                WHERE field_id = %s AND balance_date < %s
                ORDER BY balance_date DESC
                LIMIT 1
                """,
                (field_id, target_date),
            )
            prev = cur.fetchone()
            previous_depletion = float(prev[0]) if prev and prev[0] is not None else 0.0
            taw_mm = float(prev[1]) if prev and prev[1] is not None else 150.0
            kc = float(prev[2]) if prev and prev[2] is not None else 1.0

            soil_moisture = _latest_soil_moisture(cur, field_id)
            irrigation_mm = _irrigation_applied_on_date(cur, field_id, target_date)

            result = compute_daily_balance(
                previous_depletion_mm=previous_depletion,
                et0_mm=et0_mm,
                precip_mm=precip_mm,
                irrigation_mm=irrigation_mm,
                kc=kc,
                taw_mm=taw_mm,
                soil_moisture_pct=soil_moisture,
            )

            cur.execute(
                """
                SELECT crop_irr.sp_store_balance(
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    field_id,
                    target_date,
                    result.depletion_mm,
                    result.etc_mm,
                    precip_mm,
                    irrigation_mm,
                    soil_moisture,
                    result.recommended_irrigation_mm,
                    taw_mm,
                    kc,
                ),
            )
        conn.commit()
    return IrrigationScheduleResult(
        field_id=field_id,
        balance_date=target_date,
        recommended_irrigation_mm=result.recommended_irrigation_mm,
        depletion_mm=result.depletion_mm,
    )


def enqueue_daily_backlog() -> int:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT crop_irr.sp_enqueue_daily_backlog()")
            row = cur.fetchone()
            count = int(row[0]) if row and row[0] is not None else 0
        conn.commit()
    return count
