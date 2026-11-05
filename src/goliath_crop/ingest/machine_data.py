"""Stub parsers for ISOBUS, ADAPT, and yield-monitor machine exports (Phase 5)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

MachineFormat = Literal["adapt", "isobus", "yield_monitor"]


@dataclass(frozen=True)
class MachineImportResult:
    format: MachineFormat
    rows_parsed: int
    rows_applied: int
    incomplete_edges: tuple[str, ...]
    notes: str


def import_machine_file(*, format: MachineFormat, payload: str) -> MachineImportResult:
    """Parse a small, documented subset; full ISO 11783 / ADAPT coverage is future work."""
    if format == "adapt":
        return _parse_adapt_stub(payload)
    if format == "isobus":
        return _parse_isobus_stub(payload)
    return _parse_yield_monitor_stub(payload)


def _parse_adapt_stub(payload: str) -> MachineImportResult:
    edges = (
        "ADAPT full object model not implemented",
        "Only JSON wrapper with products[].yield_t_ha is accepted in this stub",
    )
    try:
        doc = json.loads(payload)
    except json.JSONDecodeError:
        return MachineImportResult("adapt", 0, 0, edges, "Payload is not JSON; use ADAPT JSON export stub.")
    products = doc.get("products") if isinstance(doc, dict) else None
    count = len(products) if isinstance(products, list) else 0
    return MachineImportResult(
        "adapt",
        count,
        0,
        edges,
        "Parsed ADAPT stub rows are not written until planting linkage lands.",
    )


def _parse_isobus_stub(payload: str) -> MachineImportResult:
    edges = (
        "ISOBUS Task Controller XML/binary not parsed",
        "Provide yield_monitor CSV via format=yield_monitor instead",
    )
    _ = payload
    return MachineImportResult("isobus", 0, 0, edges, "ISOBUS import is a documented placeholder.")


def _parse_yield_monitor_stub(payload: str) -> MachineImportResult:
    edges = ("GeoJSON polygon ↔ planting match not implemented",)
    lines = [ln for ln in payload.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    parsed = max(0, len(lines) - 1) if lines else 0
    return MachineImportResult(
        "yield_monitor",
        parsed,
        0,
        edges,
        "Yield monitor CSV rows counted but not persisted in the stub importer.",
    )
