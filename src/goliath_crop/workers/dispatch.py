"""Dispatch crop DomainProgram actions to in-process handlers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Final

from goliath_crop.actions.handlers import handle_weather_refresh

HandlerFn = Callable[[dict[str, Any], dict[str, Any] | None], dict[str, Any]]

ACTION_CAPABILITY: Final[dict[str, str]] = {
    "crop.weather.refresh": "crop.weather",
}

_ACTION_HANDLERS: Final[dict[str, HandlerFn]] = {
    "crop.weather.refresh": lambda payload, ctx=None: handle_weather_refresh(payload, context=ctx),
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
