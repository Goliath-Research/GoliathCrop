"""ActionSpec catalog tests."""

from __future__ import annotations

from goliath_app.actions.spec import ActionExposure, ActionLevel

from goliath_crop.actions.catalog import ACTIONS


def test_phase1_domain_actions_typed() -> None:
    hidden = {
        "crop.weather.refresh",
        "crop.sensor.ingest_batch",
        "crop.sensor.qc",
        "crop.imagery.process",
        "crop.alert.evaluate",
    }
    for spec in ACTIONS:
        assert spec.level == ActionLevel.DOMAIN
        assert spec.input_model.model_json_schema()
        assert spec.output_model.model_json_schema()
        if spec.action_name in hidden:
            assert spec.resolved_exposure == ActionExposure.HIDDEN
            assert spec.required_permission is None
        else:
            assert spec.resolved_exposure == ActionExposure.RBAC
            assert spec.required_permission


def test_import_boundaries_action_metadata() -> None:
    spec = next(a for a in ACTIONS if a.action_name == "crop.field.import_boundaries")
    assert spec.capability == "crop.ingest"
    assert spec.in_process_handler is not None
