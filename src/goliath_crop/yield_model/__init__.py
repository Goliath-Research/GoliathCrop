"""CPU baseline yield model and optional RunPod GPU backend selection."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

ModelBackend = Literal["cpu", "runpod"]


@dataclass(frozen=True)
class PlantingFeatures:
    planting_id: int
    gdd_total: float
    ndvi_mean: float | None
    maturity_days: int | None
    area_ha: float | None


@dataclass(frozen=True)
class YieldPrediction:
    planting_id: int
    predicted_t_ha: float
    model_version: str
    model_backend: ModelBackend


def resolve_model_backend() -> ModelBackend:
    """Select GPU workers when RunPod env is configured on the host (never in repo secrets)."""
    api_key = os.environ.get("RUNPOD_API_KEY", "").strip()
    endpoint = os.environ.get("RUNPOD_YIELD_ENDPOINT_ID", "").strip()
    if api_key and endpoint:
        return "runpod"
    return "cpu"


def baseline_predict(features: PlantingFeatures) -> YieldPrediction:
    """Simple heuristic for CI and MVP: GDD progress × NDVI factor × nominal t/ha cap."""
    maturity = float(features.maturity_days or 120)
    gdd_progress = min(1.25, max(0.05, features.gdd_total / max(1.0, maturity * 12.0)))
    ndvi_factor = 0.85 if features.ndvi_mean is None else min(1.15, max(0.5, features.ndvi_mean / 0.55))
    area_scale = 1.0 if features.area_ha is None else min(1.1, max(0.9, features.area_ha / 10.0))
    predicted = round(8.5 * gdd_progress * ndvi_factor * area_scale, 2)
    return YieldPrediction(
        planting_id=features.planting_id,
        predicted_t_ha=predicted,
        model_version="baseline-cpu-v1",
        model_backend="cpu",
    )


def predict_for_planting(features: PlantingFeatures) -> YieldPrediction:
    backend = resolve_model_backend()
    if backend == "runpod":
        raise RuntimeError(
            "RunPod GPU yield inference is not invoked in this repository build. "
            "Configure RUNPOD_API_KEY and RUNPOD_YIELD_ENDPOINT_ID on the worker host "
            "and deploy the crop-yield-model DomainProgram image separately."
        )
    return baseline_predict(features)
