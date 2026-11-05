"""Semantic catalog and export tests."""

from __future__ import annotations

from goliath_crop.semantic.catalog import SEMANTIC_CATALOG, SEMANTIC_REQUESTS
from goliath_crop.semantic.export import export_catalog_document


def test_entity_codes_unique() -> None:
    codes = [e.code for e in SEMANTIC_CATALOG]
    assert len(codes) == len(set(codes))


def test_requests_reference_known_entities() -> None:
    entity_codes = {e.code for e in SEMANTIC_CATALOG}
    for req in SEMANTIC_REQUESTS:
        assert req.entity_code in entity_codes
        assert req.namespace == "crop"
        assert req.request_code.startswith("crop.")


def test_export_document_matches_committed_catalog() -> None:
    live = export_catalog_document()
    committed_keys = set(live.keys()) - {"row_types_sql"}
    assert committed_keys == {"entities", "requests"}
    assert len(live["entities"]) == len(SEMANTIC_CATALOG)
    assert len(live["requests"]) == len(SEMANTIC_REQUESTS)
