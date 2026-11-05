"""FAO-56 soil water balance helpers (CPU worker; simplified single-layer bucket)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WaterBalanceResult:
    depletion_mm: float
    etc_mm: float
    effective_precip_mm: float
    recommended_irrigation_mm: float


def compute_daily_balance(
    *,
    previous_depletion_mm: float,
    et0_mm: float,
    precip_mm: float,
    irrigation_mm: float,
    kc: float = 1.0,
    taw_mm: float = 150.0,
    depletion_fraction: float = 0.5,
    precip_effective_factor: float = 0.8,
    soil_moisture_pct: float | None = None,
) -> WaterBalanceResult:
    """Update root-zone depletion (Dr) and recommend irrigation when Dr exceeds RAW."""
    etc_mm = max(0.0, kc * et0_mm)
    room_to_fill = max(0.0, taw_mm - previous_depletion_mm)
    effective_precip_mm = min(max(0.0, precip_mm) * precip_effective_factor, room_to_fill)
    depletion_mm = previous_depletion_mm + etc_mm - effective_precip_mm - max(0.0, irrigation_mm)
    depletion_mm = max(0.0, min(taw_mm, depletion_mm))

    if soil_moisture_pct is not None:
        # Map volumetric moisture to depletion when a sensor is present (field capacity ~100%).
        sensor_depletion = taw_mm * (1.0 - max(0.0, min(100.0, soil_moisture_pct)) / 100.0)
        depletion_mm = max(0.0, min(taw_mm, (depletion_mm + sensor_depletion) / 2.0))

    raw_mm = depletion_fraction * taw_mm
    recommended_irrigation_mm = max(0.0, depletion_mm - raw_mm) if depletion_mm > raw_mm else 0.0
    return WaterBalanceResult(
        depletion_mm=depletion_mm,
        etc_mm=etc_mm,
        effective_precip_mm=effective_precip_mm,
        recommended_irrigation_mm=recommended_irrigation_mm,
    )
