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
