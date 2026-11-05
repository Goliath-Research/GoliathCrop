"""In-process handlers for GoliathCrop domain actions."""

from __future__ import annotations

from datetime import date
from typing import Any

from goliath_crop.actions.models import (
    AlertEvaluateInput,
    AlertEvaluateOutput,
    DroneUploadInput,
    DroneUploadOutput,
    FieldImportBoundariesInput,
    FieldImportBoundariesOutput,
    ImageryProcessInput,
    ImageryProcessOutput,
    OperationRecordInput,
    OperationRecordOutput,
    SceneFetchAndIndexInput,
    SceneFetchAndIndexOutput,
    SensorIngestBatchInput,
    SensorIngestBatchOutput,
    SensorQcInput,
    SensorQcOutput,
    TrialRecordObservationInput,
    TrialRecordObservationOutput,
    WeatherRefreshInput,
    WeatherRefreshOutput,
    ScoutingRecordInput,
    ScoutingRecordOutput,
    IrrigationScheduleInput,
    IrrigationScheduleOutput,
    YieldPredictInput,
    YieldPredictOutput,
    LinkOmicsInput,
    LinkOmicsOutput,
    RegisterGroundstationInput,
    RegisterGroundstationOutput,
    MachineImportInput,
    MachineImportOutput,
)
from goliath_crop.db import connect, libpq_configured, user_id_from_context
from goliath_crop.ingest.machine_data import import_machine_file
from goliath_crop.workers.alerts import evaluate_alert
from goliath_crop.workers.imagery_process import process_scene, register_drone_upload
from goliath_crop.workers.irrigation_schedule import run_irrigation_schedule
from goliath_crop.workers.satellite_fetch import fetch_scenes_for_field
from goliath_crop.workers.sensor_ingest import ingest_sensor_batch, run_sensor_qc
from goliath_crop.workers.weather_sync import refresh_weather
from goliath_crop.workers.yield_predict import run_yield_predict_for_season


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


def handle_sensor_ingest_batch(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = SensorIngestBatchInput.model_validate(payload)
    _ = context
    if not libpq_configured():
        return SensorIngestBatchOutput(inserted_count=0, task_id=None).model_dump(mode="json")
    readings = [r.model_dump(mode="json") for r in model.readings]
    result = ingest_sensor_batch(device_id=model.device_id, readings=readings)
    return SensorIngestBatchOutput(
        inserted_count=result.inserted_count,
        task_id=None,
    ).model_dump(mode="json")


def handle_sensor_qc(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = SensorQcInput.model_validate(payload)
    _ = context
    if not libpq_configured():
        return SensorQcOutput(device_id=model.device_id, alerts_opened=0).model_dump(mode="json")
    opened = run_sensor_qc(device_id=model.device_id)
    return SensorQcOutput(device_id=model.device_id, alerts_opened=opened).model_dump(mode="json")


def handle_scene_fetch_and_index(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = SceneFetchAndIndexInput.model_validate(payload)
    user_id = user_id_from_context(context)
    if user_id is None or not libpq_configured():
        raise RuntimeError("scene fetch requires authenticated user and database configuration")
    result = fetch_scenes_for_field(
        user_id=user_id,
        field_id=model.field_id,
        days_back=model.days_back,
        max_cloud_fraction=model.max_cloud_fraction,
        collections=list(model.collections),
    )
    return SceneFetchAndIndexOutput(
        scenes_registered=result.scenes_registered,
        scene_ids=result.scene_ids,
    ).model_dump(mode="json")


def handle_imagery_process(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = ImageryProcessInput.model_validate(payload)
    _ = context
    if not libpq_configured():
        return ImageryProcessOutput(
            scene_id=model.scene_id,
            cog_uri="",
            ndvi_mean=0.0,
        ).model_dump(mode="json")
    result = process_scene(scene_id=model.scene_id)
    return ImageryProcessOutput(
        scene_id=result.scene_id,
        cog_uri=result.cog_uri,
        ndvi_mean=result.ndvi_mean,
    ).model_dump(mode="json")


def handle_drone_upload(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = DroneUploadInput.model_validate(payload)
    user_id = user_id_from_context(context)
    if user_id is None or not libpq_configured():
        raise RuntimeError("drone upload requires authenticated user and database configuration")
    scene_id = register_drone_upload(
        user_id=user_id,
        field_id=model.field_id,
        storage_uri=model.storage_uri,
        acquired_at=model.acquired_at,
        footprint_wkt=model.footprint_wkt,
    )
    return DroneUploadOutput(scene_id=scene_id, task_id=None).model_dump(mode="json")


def handle_alert_evaluate(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = AlertEvaluateInput.model_validate(payload)
    _ = context
    if not libpq_configured():
        return AlertEvaluateOutput(alert_id=model.alert_id, status="skipped").model_dump(mode="json")
    result = evaluate_alert(alert_id=model.alert_id)
    return AlertEvaluateOutput(alert_id=result.alert_id, status=result.status).model_dump(mode="json")


def handle_scouting_record(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = ScoutingRecordInput.model_validate(payload)
    user_id = user_id_from_context(context)
    if user_id is None or not libpq_configured():
        raise RuntimeError("scouting record requires authenticated user and database configuration")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT crop_scout.sp_record_observation(
                  %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    user_id,
                    model.field_id,
                    model.observed_at,
                    model.pest_code,
                    model.severity,
                    model.notes,
                    model.geo_json,
                    model.photo_uri,
                ),
            )
            row = cur.fetchone()
            if row is None:
                raise RuntimeError("sp_record_observation returned no row")
            observation_id = int(row[0])
        conn.commit()
    return ScoutingRecordOutput(observation_id=observation_id).model_dump(mode="json")


def handle_irrigation_schedule(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = IrrigationScheduleInput.model_validate(payload)
    _ = context
    if not libpq_configured():
        today = date.today()
        return IrrigationScheduleOutput(
            field_id=model.field_id,
            balance_date=model.balance_date or today,
            recommended_irrigation_mm=0.0,
            depletion_mm=0.0,
        ).model_dump(mode="json")
    result = run_irrigation_schedule(
        field_id=model.field_id,
        balance_date=model.balance_date,
    )
    return IrrigationScheduleOutput(
        field_id=result.field_id,
        balance_date=result.balance_date,
        recommended_irrigation_mm=result.recommended_irrigation_mm,
        depletion_mm=result.depletion_mm,
    ).model_dump(mode="json")


def handle_yield_predict(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = YieldPredictInput.model_validate(payload)
    user_id = user_id_from_context(context)
    if not libpq_configured():
        return YieldPredictOutput(
            season_id=model.season_id,
            planting_count=0,
            predictions_written=0,
            model_backend="cpu",
        ).model_dump(mode="json")
    if user_id is not None:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT EXISTS (
                      SELECT 1
                      FROM crop_core.seasons s
                      INNER JOIN crop_core.farms f ON f.id = s.farm_id
                      WHERE s.id = %s
                        AND (
                          f.organization_id = ANY (
                            portal.fn_semantic_user_organization_ids(%s)
                          )
                          OR EXISTS (
                            SELECT 1
                            FROM crop_core.farm_members m
                            WHERE m.farm_id = f.id AND m.user_id = %s
                          )
                        )
                    )
                    """,
                    (model.season_id, user_id, user_id),
                )
                row = cur.fetchone()
                if row is None or not row[0]:
                    raise RuntimeError("season not accessible")
    result = run_yield_predict_for_season(season_id=model.season_id, user_id=user_id)
    return YieldPredictOutput(
        season_id=result.season_id,
        planting_count=result.planting_count,
        predictions_written=result.predictions_written,
        model_backend=result.model_backend,
    ).model_dump(mode="json")


def handle_link_omics(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = LinkOmicsInput.model_validate(payload)
    user_id = user_id_from_context(context)
    if model.sample_id is None and model.plot_id is None:
        raise ValueError("sample_id or plot_id is required")
    if user_id is None or not libpq_configured():
        return LinkOmicsOutput(linked=False).model_dump(mode="json")
    with connect() as conn:
        with conn.cursor() as cur:
            if model.sample_id is not None:
                cur.execute(
                    "SELECT crop_lab.sp_link_omics_run(%s, %s, %s)",
                    (user_id, model.sample_id, model.omics_run_ref),
                )
            if model.plot_id is not None:
                cur.execute(
                    "SELECT crop_core.sp_link_plot_omics_run(%s, %s, %s)",
                    (user_id, model.plot_id, model.omics_run_ref),
                )
        conn.commit()
    return LinkOmicsOutput(linked=True).model_dump(mode="json")


def handle_register_groundstation(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = RegisterGroundstationInput.model_validate(payload)
    user_id = user_id_from_context(context)
    if user_id is None or not libpq_configured():
        return RegisterGroundstationOutput(link_id=0).model_dump(mode="json")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT crop_link.sp_register_groundstation_flight(
                  %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    user_id,
                    model.field_id,
                    model.external_flight_ref,
                    model.telemetry_uri,
                    model.imagery_uri,
                    model.notes,
                ),
            )
            row = cur.fetchone()
        conn.commit()
    link_id = int(row[0]) if row else 0
    return RegisterGroundstationOutput(link_id=link_id).model_dump(mode="json")


def handle_machine_import(
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = MachineImportInput.model_validate(payload)
    _ = context
    fmt = model.format.strip().lower()
    if fmt not in ("adapt", "isobus", "yield_monitor"):
        raise ValueError("format must be adapt, isobus, or yield_monitor")
    result = import_machine_file(format=fmt, payload=model.payload)  # type: ignore[arg-type]
    return MachineImportOutput(
        format=result.format,
        rows_parsed=result.rows_parsed,
        rows_applied=result.rows_applied,
        incomplete_edges=list(result.incomplete_edges),
        notes=result.notes,
    ).model_dump(mode="json")
