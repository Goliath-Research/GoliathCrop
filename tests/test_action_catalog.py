"""ActionSpec catalog tests."""

from __future__ import annotations

from goliath_app.actions.spec import ActionExposure, ActionLevel

from goliath_crop.actions.catalog import ACTIONS


def test_phase1_domain_actions_typed() -> None:
    for spec in ACTIONS:
        assert spec.level == ActionLevel.DOMAIN
        assert spec.resolved_exposure == ActionExposure.RBAC
        assert spec.required_permission
        assert spec.input_model.model_json_schema()
        assert spec.output_model.model_json_schema()


def test_import_boundaries_action_metadata() -> None:
    spec = next(a for a in ACTIONS if a.action_name == "crop.field.import_boundaries")
    assert spec.capability == "crop.ingest"
    assert spec.in_process_handler is not None
