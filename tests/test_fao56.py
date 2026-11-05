"""FAO-56 water balance unit tests."""

from __future__ import annotations

from goliath_crop.irrigation.fao56 import compute_daily_balance


def test_recommends_irrigation_when_depletion_exceeds_raw() -> None:
    result = compute_daily_balance(
        previous_depletion_mm=70.0,
        et0_mm=5.0,
        precip_mm=0.0,
        irrigation_mm=0.0,
        taw_mm=150.0,
        depletion_fraction=0.5,
    )
    assert result.depletion_mm == 75.0
    assert result.recommended_irrigation_mm == 0.0

    stressed = compute_daily_balance(
        previous_depletion_mm=80.0,
        et0_mm=4.0,
        precip_mm=0.0,
        irrigation_mm=0.0,
        taw_mm=150.0,
    )
    assert stressed.depletion_mm == 84.0
    assert stressed.recommended_irrigation_mm == 9.0


def test_precip_reduces_depletion() -> None:
    dry = compute_daily_balance(
        previous_depletion_mm=40.0,
        et0_mm=3.0,
        precip_mm=0.0,
        irrigation_mm=0.0,
    )
    wet = compute_daily_balance(
        previous_depletion_mm=40.0,
        et0_mm=3.0,
        precip_mm=10.0,
        irrigation_mm=0.0,
    )
    assert wet.depletion_mm < dry.depletion_mm
