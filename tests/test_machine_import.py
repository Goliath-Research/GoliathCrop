"""Machine data import stub tests."""

from __future__ import annotations

from goliath_crop.actions.handlers import handle_machine_import
from goliath_crop.ingest.machine_data import import_machine_file


def test_adapt_json_stub_counts_products() -> None:
    result = import_machine_file(format="adapt", payload='{"products":[{"yield_t_ha":1.2}]}')
    assert result.rows_parsed == 1
    assert result.rows_applied == 0
    assert result.incomplete_edges


def test_isobus_stub_is_placeholder() -> None:
    result = import_machine_file(format="isobus", payload="binary-not-supported")
    assert result.rows_parsed == 0


def test_machine_import_handler() -> None:
    out = handle_machine_import(
        {"format": "yield_monitor", "payload": "lat,lon,yield\n1,2,3\n"},
    )
    assert out["format"] == "yield_monitor"
    assert out["rows_parsed"] >= 1
