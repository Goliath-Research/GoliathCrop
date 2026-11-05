"""Dispatch crop DomainProgram actions to in-process handlers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Final

from goliath_crop.actions.handlers import (
    handle_alert_evaluate,
    handle_drone_upload,
    handle_imagery_process,
    handle_scene_fetch_and_index,
    handle_sensor_ingest_batch,
    handle_sensor_qc,
    handle_weather_refresh,
)

HandlerFn = Callable[[dict[str, Any], dict[str, Any] | None], dict[str, Any]]

ACTION_CAPABILITY: Final[dict[str, str]] = {
    "crop.weather.refresh": "crop.weather",
    "crop.sensor.ingest_batch": "crop.ingest",
    "crop.sensor.qc": "crop.ingest",
    "crop.scene.fetch_and_index": "crop.imagery",
    "crop.imagery.process": "crop.imagery",
    "crop.drone.upload": "crop.imagery",
    "crop.alert.evaluate": "crop.alerts",
}

_ACTION_HANDLERS: Final[dict[str, HandlerFn]] = {
    "crop.weather.refresh": lambda payload, ctx=None: handle_weather_refresh(payload, context=ctx),
    "crop.sensor.ingest_batch": lambda payload, ctx=None: handle_sensor_ingest_batch(
        payload, context=ctx
    ),
    "crop.sensor.qc": lambda payload, ctx=None: handle_sensor_qc(payload, context=ctx),
    "crop.scene.fetch_and_index": lambda payload, ctx=None: handle_scene_fetch_and_index(
        payload, context=ctx
    ),
    "crop.imagery.process": lambda payload, ctx=None: handle_imagery_process(payload, context=ctx),
    "crop.drone.upload": lambda payload, ctx=None: handle_drone_upload(payload, context=ctx),
    "crop.alert.evaluate": lambda payload, ctx=None: handle_alert_evaluate(payload, context=ctx),
}


def known_action_names() -> frozenset[str]:
    return frozenset(_ACTION_HANDLERS)


def capability_for_action(action_name: str) -> str:
    return ACTION_CAPABILITY[action_name]


def handle(
    action_name: str,
    input_json: dict[str, Any] | None = None,
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {} if input_json is None else dict(input_json)
    handler = _ACTION_HANDLERS[action_name]
    return handler(payload, context)
