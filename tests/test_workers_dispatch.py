"""Worker dispatch tests."""

from __future__ import annotations

import pytest

from goliath_crop.workers.dispatch import capability_for_action, handle, known_action_names


def test_known_worker_actions() -> None:
    names = known_action_names()
    assert "crop.weather.refresh" in names
    assert "crop.sensor.qc" in names
    assert "crop.imagery.process" in names


def test_sensor_qc_without_db() -> None:
    out = handle("crop.sensor.qc", {"device_id": 1})
    assert out["alerts_opened"] == 0


def test_irrigation_schedule_without_db() -> None:
    out = handle("crop.irrigation.schedule", {"field_id": 10})
    assert out["field_id"] == 10
    assert out["recommended_irrigation_mm"] == 0.0


def test_capability_mapping() -> None:
    assert capability_for_action("crop.weather.refresh") == "crop.weather"
    assert capability_for_action("crop.sensor.ingest_batch") == "crop.ingest"
    assert capability_for_action("crop.alert.evaluate") == "crop.alerts"
    assert capability_for_action("crop.irrigation.schedule") == "crop.irrigation"


def test_dispatch_unknown_action_raises() -> None:
    with pytest.raises(KeyError):
        handle("crop.unknown.action", {})


def test_weather_refresh_without_db() -> None:
    out = handle("crop.weather.refresh", {"farm_id": 1, "days_back": 3})
    assert out["fields_refreshed"] == 0
    assert out["rows_upserted"] == 0
