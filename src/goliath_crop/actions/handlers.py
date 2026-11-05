"""In-process handlers for GoliathCrop domain actions."""

from __future__ import annotations

from datetime import date
from typing import Any

from goliath_crop.actions.models import (
    FieldImportBoundariesInput,
    FieldImportBoundariesOutput,
    OperationRecordInput,
    OperationRecordOutput,
    TrialRecordObservationInput,
    TrialRecordObservationOutput,
    WeatherRefreshInput,
    WeatherRefreshOutput,
)
from goliath_crop.db import connect, libpq_configured, user_id_from_context
from goliath_crop.workers.weather_sync import refresh_weather


def handle_field_import_boundaries(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Placeholder until shapefile ingest worker lands in Phase 3."""
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
    model = OperationRecordInput.model_validate(payload)
    user_id = user_id_from_context(context)
    if user_id is None or not libpq_configured():
        raise RuntimeError("operation record requires authenticated user and database configuration")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT crop_ops.sp_record_operation(
                  %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    user_id,
                    model.planting_id,
                    model.kind,
                    model.performed_on,
                    model.rate,
                    model.rate_unit,
                    model.equipment,
                    model.operator,
                    model.notes,
                ),
            )
            row = cur.fetchone()
            if row is None:
                raise RuntimeError("sp_record_operation returned no row")
            operation_id = int(row[0])
        conn.commit()
    return OperationRecordOutput(operation_id=operation_id).model_dump(mode="json")


def handle_weather_refresh(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = WeatherRefreshInput.model_validate(payload)
    _ = context
    if not libpq_configured():
        return WeatherRefreshOutput(fields_refreshed=0, rows_upserted=0).model_dump(mode="json")
    result = refresh_weather(
        farm_id=model.farm_id,
        field_id=model.field_id,
        days_back=model.days_back,
    )
    return WeatherRefreshOutput(
        fields_refreshed=result.fields_refreshed,
        rows_upserted=result.rows_upserted,
    ).model_dump(mode="json")


def handle_trial_record_observation(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = TrialRecordObservationInput.model_validate(payload)
    user_id = user_id_from_context(context)
    measured_on: date | None = model.measured_on
    if user_id is None or not libpq_configured():
        raise RuntimeError("trial observation requires authenticated user and database configuration")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT crop_trial.sp_record_plot_observation(%s, %s, %s, %s, %s)
                """,
                (user_id, model.plot_id, model.metric, model.value, measured_on),
            )
            row = cur.fetchone()
            if row is None:
                raise RuntimeError("sp_record_plot_observation returned no row")
            measurement_id = int(row[0])
        conn.commit()
    return TrialRecordObservationOutput(measurement_id=measurement_id).model_dump(mode="json")
