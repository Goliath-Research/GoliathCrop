"""Baseline yield model tests."""

from __future__ import annotations

from goliath_crop.yield_model import PlantingFeatures, baseline_predict, resolve_model_backend


def test_baseline_predict_positive() -> None:
    pred = baseline_predict(
        PlantingFeatures(
            planting_id=1,
            gdd_total=600.0,
            ndvi_mean=0.62,
            maturity_days=110,
            area_ha=12.0,
        )
    )
    assert pred.planting_id == 1
    assert pred.predicted_t_ha > 0
    assert pred.model_backend == "cpu"


def test_resolve_backend_cpu_without_env(monkeypatch) -> None:
    monkeypatch.delenv("RUNPOD_API_KEY", raising=False)
    monkeypatch.delenv("RUNPOD_YIELD_ENDPOINT_ID", raising=False)
    assert resolve_model_backend() == "cpu"
