"""Stub handler smoke tests."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from goliath_crop.actions.handlers import handle_field_import_boundaries, handle_operation_record


def test_field_import_stub() -> None:
    out = handle_field_import_boundaries(
        {"farm_id": 1, "geojson": "{\"type\":\"FeatureCollection\",\"features\":[]}"}
    )
    assert out["imported_count"] == 0
    assert out["field_ids"] == []


def test_operation_record_requires_db() -> None:
    with pytest.raises(RuntimeError, match="operation record requires"):
        handle_operation_record(
            {
                "planting_id": 2,
                "kind": "irrigation",
                "performed_on": datetime(2026, 5, 1, tzinfo=timezone.utc).isoformat(),
            }
        )
