"""Crop semantic entity and request specifications (namespace ``crop``)."""

from __future__ import annotations

from goliath_app.semantic.spec import SemanticAttributeSpec, SemanticEntitySpec, SemanticRequestSpec

from goliath_crop.semantic.models import (
    FieldListParams,
    FieldRow,
    FarmRow,
    InputLotRow,
    OperationListParams,
    OperationRow,
    PlantingListParams,
    PlantingRow,
    PlotRow,
    SeasonRow,
    TrialResultRow,
    TrialResultsParams,
    TrialRow,
    VarietyRow,
)

FARM_ENTITY = SemanticEntitySpec(
    namespace="crop",
    code="farm",
    display_name="Farm",
    description="A farm belonging to a GoliathApp organization.",
    schema_version="1",
    row_model=FarmRow,
    storage_relation="crop_core.v_farm",
    attributes=(
        SemanticAttributeSpec("farm_id", "id", "integer", "key", ()),
        SemanticAttributeSpec(
            "organization_id",
            "organization_id",
            "integer",
            "filter",
            ("eq",),
        ),
        SemanticAttributeSpec("name", "name", "string", "label", ("ilike",)),
        SemanticAttributeSpec("location", "location", "string", "attribute", ()),
        SemanticAttributeSpec("timezone", "timezone", "string", "attribute", ()),
        SemanticAttributeSpec("units", "units", "string", "attribute", ()),
    ),
)

FIELD_ENTITY = SemanticEntitySpec(
    namespace="crop",
    code="field",
    display_name="Field",
    description="A managed field with boundary geometry.",
    schema_version="1",
    row_model=FieldRow,
    storage_relation="crop_core.v_field",
    attributes=(
        SemanticAttributeSpec("field_id", "id", "integer", "key", ()),
        SemanticAttributeSpec(
            "farm_id",
            "farm_id",
            "integer",
            "filter",
            ("eq",),
        ),
        SemanticAttributeSpec("name", "name", "string", "label", ("ilike",)),
        SemanticAttributeSpec(
            "area_ha",
            "area_ha",
            "number",
            "measure",
            ("gte", "lte"),
        ),
        SemanticAttributeSpec(
            "soil_type",
            "soil_type",
            "string",
            "attribute",
            ("eq", "in"),
        ),
        SemanticAttributeSpec("geometry", "geometry", "string", "attribute", ()),
    ),
)

PLOT_ENTITY = SemanticEntitySpec(
    namespace="crop",
    code="plot",
    display_name="Trial plot",
    description="A sub-field plot used in research trials.",
    schema_version="1",
    row_model=PlotRow,
    storage_relation="crop_core.v_plot",
    attributes=(
        SemanticAttributeSpec("plot_id", "id", "integer", "key", ()),
        SemanticAttributeSpec("field_id", "field_id", "integer", "filter", ("eq",)),
        SemanticAttributeSpec("trial_id", "trial_id", "integer", "filter", ("eq",)),
        SemanticAttributeSpec("code", "code", "string", "label", ("eq",)),
        SemanticAttributeSpec("geometry", "geometry", "string", "attribute", ()),
    ),
)

SEASON_ENTITY = SemanticEntitySpec(
    namespace="crop",
    code="season",
    display_name="Season",
    description="Growing season for a farm.",
    schema_version="1",
    row_model=SeasonRow,
    storage_relation="crop_core.v_season",
    attributes=(
        SemanticAttributeSpec("season_id", "id", "integer", "key", ()),
        SemanticAttributeSpec("farm_id", "farm_id", "integer", "filter", ("eq",)),
        SemanticAttributeSpec("year", "year", "integer", "attribute", ("eq",)),
        SemanticAttributeSpec("campaign", "campaign", "string", "attribute", ("eq",)),
        SemanticAttributeSpec("status", "status", "string", "attribute", ("eq",)),
    ),
)

PLANTING_ENTITY = SemanticEntitySpec(
    namespace="crop",
    code="planting",
    display_name="Planting",
    description="A variety sown on a field for a season.",
    schema_version="1",
    row_model=PlantingRow,
    storage_relation="crop_core.v_planting",
    attributes=(
        SemanticAttributeSpec("planting_id", "id", "integer", "key", ()),
        SemanticAttributeSpec("field_id", "field_id", "integer", "filter", ("eq",)),
        SemanticAttributeSpec("season_id", "season_id", "integer", "filter", ("eq",)),
        SemanticAttributeSpec("variety_id", "variety_id", "integer", "filter", ("eq",)),
        SemanticAttributeSpec("sown_on", "sown_on", "string", "attribute", ()),
        SemanticAttributeSpec("density", "density", "number", "measure", ()),
        SemanticAttributeSpec("seed_lot", "seed_lot", "string", "attribute", ()),
    ),
)

VARIETY_ENTITY = SemanticEntitySpec(
    namespace="crop",
    code="variety",
    display_name="Crop variety",
    description="Crop species and variety metadata.",
    schema_version="1",
    row_model=VarietyRow,
    storage_relation="crop_core.v_variety",
    attributes=(
        SemanticAttributeSpec("variety_id", "id", "integer", "key", ()),
        SemanticAttributeSpec("crop_id", "crop_id", "integer", "filter", ("eq",)),
        SemanticAttributeSpec("species", "species", "string", "attribute", ("eq",)),
        SemanticAttributeSpec("variety", "variety", "string", "label", ("ilike",)),
        SemanticAttributeSpec("maturity_days", "maturity_days", "integer", "attribute", ()),
        SemanticAttributeSpec("gdd_base_c", "gdd_base_c", "number", "attribute", ()),
    ),
)

OPERATION_ENTITY = SemanticEntitySpec(
    namespace="crop",
    code="operation",
    display_name="Field operation",
    description="Irrigation, fertilization, spraying, harvest, or other field work.",
    schema_version="1",
    row_model=OperationRow,
    storage_relation="crop_ops.v_operation",
    attributes=(
        SemanticAttributeSpec("operation_id", "id", "integer", "key", ()),
        SemanticAttributeSpec(
            "planting_id",
            "planting_id",
            "integer",
            "filter",
            ("eq",),
        ),
        SemanticAttributeSpec("kind", "kind", "string", "filter", ("eq",)),
        SemanticAttributeSpec("performed_on", "performed_on", "string", "attribute", ()),
        SemanticAttributeSpec("rate", "rate", "number", "measure", ()),
        SemanticAttributeSpec("equipment", "equipment", "string", "attribute", ()),
        SemanticAttributeSpec("operator", "operator", "string", "attribute", ()),
    ),
)

INPUT_LOT_ENTITY = SemanticEntitySpec(
    namespace="crop",
    code="input_lot",
    display_name="Input lot",
    description="Inventory lot for seeds, fertilizer, or crop protection products.",
    schema_version="1",
    row_model=InputLotRow,
    storage_relation="crop_ops.v_input_lot",
    attributes=(
        SemanticAttributeSpec("input_lot_id", "id", "integer", "key", ()),
        SemanticAttributeSpec("item_id", "item_id", "integer", "filter", ("eq",)),
        SemanticAttributeSpec("item_name", "item_name", "string", "label", ("ilike",)),
        SemanticAttributeSpec("lot", "lot", "string", "attribute", ("eq",)),
        SemanticAttributeSpec("on_hand", "on_hand", "number", "measure", ()),
        SemanticAttributeSpec("unit", "unit", "string", "attribute", ()),
    ),
)

TRIAL_ENTITY = SemanticEntitySpec(
    namespace="crop",
    code="trial",
    display_name="Trial",
    description="Research trial with treatments and replicates.",
    schema_version="1",
    row_model=TrialRow,
    storage_relation="crop_trial.v_trial",
    attributes=(
        SemanticAttributeSpec("trial_id", "id", "integer", "key", ()),
        SemanticAttributeSpec("season_id", "season_id", "integer", "filter", ("eq",)),
        SemanticAttributeSpec("name", "name", "string", "label", ("ilike",)),
        SemanticAttributeSpec("design", "design", "string", "attribute", ()),
        SemanticAttributeSpec(
            "treatment_count",
            "treatment_count",
            "integer",
            "measure",
            (),
        ),
        SemanticAttributeSpec(
            "replicate_count",
            "replicate_count",
            "integer",
            "measure",
            (),
        ),
    ),
)

SEMANTIC_CATALOG: list[SemanticEntitySpec] = [
    FARM_ENTITY,
    FIELD_ENTITY,
    PLOT_ENTITY,
    SEASON_ENTITY,
    PLANTING_ENTITY,
    VARIETY_ENTITY,
    OPERATION_ENTITY,
    INPUT_LOT_ENTITY,
    TRIAL_ENTITY,
]

SEMANTIC_REQUESTS: list[SemanticRequestSpec] = [
    SemanticRequestSpec(
        request_code="crop.field.list_by_farm",
        version="1",
        namespace="crop",
        entity_code="field",
        target_kind="function",
        target_name="crop_core.fn_semantic_field_list_by_farm",
        params_model=FieldListParams,
        result_row_model=FieldRow,
        required_permission="crop.field.read",
        max_rows=500,
    ),
    SemanticRequestSpec(
        request_code="crop.planting.list_by_season",
        version="1",
        namespace="crop",
        entity_code="planting",
        target_kind="function",
        target_name="crop_core.fn_semantic_planting_list_by_season",
        params_model=PlantingListParams,
        result_row_model=PlantingRow,
        required_permission="crop.planting.read",
        max_rows=500,
    ),
    SemanticRequestSpec(
        request_code="crop.operation.list",
        version="1",
        namespace="crop",
        entity_code="operation",
        target_kind="function",
        target_name="crop_ops.fn_semantic_operation_list",
        params_model=OperationListParams,
        result_row_model=OperationRow,
        required_permission="crop.operation.read",
        max_rows=500,
    ),
    SemanticRequestSpec(
        request_code="crop.trial.results",
        version="1",
        namespace="crop",
        entity_code="trial",
        target_kind="function",
        target_name="crop_trial.fn_trial_results",
        params_model=TrialResultsParams,
        result_row_model=TrialResultRow,
        required_permission="crop.trial.read",
        max_rows=2000,
    ),
]
