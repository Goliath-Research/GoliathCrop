"""Stub in-process handlers for Phase 1 domain actions."""

from __future__ import annotations

from typing import Any

from goliath_crop.actions.models import (
    FieldImportBoundariesInput,
    FieldImportBoundariesOutput,
    OperationRecordInput,
    OperationRecordOutput,
)


def handle_field_import_boundaries(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Placeholder until ingest worker and SQL write path land in Phase 2."""
    model = FieldImportBoundariesInput.model_validate(payload)
    _ = context
    out = FieldImportBoundariesOutput(imported_count=0, field_ids=[])
    if model.replace_existing:
        return out.model_dump(mode="json")
    return out.model_dump(mode="json")


def handle_operation_record(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Placeholder until portal write API lands in Phase 2."""
    model = OperationRecordInput.model_validate(payload)
    _ = context
    return OperationRecordOutput(operation_id=0).model_dump(mode="json")
