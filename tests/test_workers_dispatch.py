"""Worker dispatch tests."""

from __future__ import annotations

import pytest

from goliath_crop.workers.dispatch import capability_for_action, handle, known_action_names


def test_known_worker_actions() -> None:
    assert "crop.weather.refresh" in known_action_names()


def test_weather_refresh_without_db() -> None:
    out = handle("crop.weather.refresh", {"farm_id": 1, "days_back": 3})
    assert out["fields_refreshed"] == 0
    assert out["rows_upserted"] == 0


def test_capability_mapping() -> None:
    assert capability_for_action("crop.weather.refresh") == "crop.weather"


def test_dispatch_unknown_action_raises() -> None:
    with pytest.raises(KeyError):
        handle("crop.unknown.action", {})
