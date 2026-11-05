"""Domain ActionSpec catalog for GoliathCrop (Phase 1)."""

from __future__ import annotations

from goliath_app.actions.spec import ActionExposure, ActionLevel, ActionSpec

from goliath_crop.actions.models import (
    FieldImportBoundariesInput,
    FieldImportBoundariesOutput,
    OperationRecordInput,
    OperationRecordOutput,
)

ACTIONS: list[ActionSpec] = [
    ActionSpec(
        action_name="crop.field.import_boundaries",
        namespace="crop",
        level=ActionLevel.DOMAIN,
        entity_code="field",
        display_name="Import field boundaries",
        description="Import or replace field polygons from GeoJSON or shapefile upload.",
        exposure=ActionExposure.RBAC,
        required_permission="crop.field.write",
        input_model=FieldImportBoundariesInput,
        output_model=FieldImportBoundariesOutput,
        schema_version="1",
        capability="crop.ingest",
        tool="crop-field-import",
        in_process_handler="goliath_crop.actions.handlers:handle_field_import_boundaries",
    ),
    ActionSpec(
        action_name="crop.operation.record",
        namespace="crop",
        level=ActionLevel.DOMAIN,
        entity_code="operation",
        display_name="Record field operation",
        description="Log irrigation, fertilization, spraying, harvest, or other field work.",
        exposure=ActionExposure.RBAC,
        required_permission="crop.operation.write",
        input_model=OperationRecordInput,
        output_model=OperationRecordOutput,
        schema_version="1",
        capability="crop.ops",
        tool="crop-operation-record",
        in_process_handler="goliath_crop.actions.handlers:handle_operation_record",
    ),
]
