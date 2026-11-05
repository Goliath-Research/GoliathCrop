"""Typed input/output models for crop domain actions."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FieldImportBoundariesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    farm_id: int
    geojson: str = Field(description="GeoJSON FeatureCollection of field polygons")
    replace_existing: bool = False


class FieldImportBoundariesOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    imported_count: int
    field_ids: list[int]


class OperationRecordInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    planting_id: int
    kind: str
    performed_on: datetime
    rate: Optional[float] = None
    rate_unit: Optional[str] = None
    equipment: Optional[str] = None
    operator: Optional[str] = None
    notes: Optional[str] = None


class OperationRecordOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation_id: int


class WeatherRefreshInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    farm_id: Optional[int] = None
    field_id: Optional[int] = None
    days_back: int = Field(default=7, ge=1, le=30)


class WeatherRefreshOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fields_refreshed: int
    rows_upserted: int


class TrialRecordObservationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plot_id: int
    metric: str
    value: float
    measured_on: Optional[date] = None


class TrialRecordObservationOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    measurement_id: int


class SensorReadingPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ts: datetime
    metric: str
    value: float
    quality: Optional[str] = None


class SensorIngestBatchInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    device_id: int
    readings: list[SensorReadingPoint] = Field(min_length=1)


class SensorIngestBatchOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    inserted_count: int
    task_id: Optional[int] = None


class SceneFetchAndIndexInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_id: int
    days_back: int = Field(default=30, ge=1, le=120)
    max_cloud_fraction: float = Field(default=0.3, ge=0.0, le=1.0)
    collections: list[str] = Field(
        default_factory=lambda: ["sentinel-2-l2a", "landsat-c2-l2"]
    )


class SceneFetchAndIndexOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenes_registered: int
    scene_ids: list[int]


class ImageryProcessInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene_id: int


class ImageryProcessOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene_id: int
    cog_uri: str
    ndvi_mean: float


class SensorQcInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    device_id: int
    reading_count: int = 0


class SensorQcOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    device_id: int
    alerts_opened: int


class AlertEvaluateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alert_id: int
    farm_id: Optional[int] = None
    kind: Optional[str] = None


class AlertEvaluateOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alert_id: int
    status: str = "noted"


class DroneUploadInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_id: int
    storage_uri: str
    acquired_at: Optional[datetime] = None
    footprint_wkt: Optional[str] = None


class DroneUploadOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene_id: int
    task_id: Optional[int] = None
