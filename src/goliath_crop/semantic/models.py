"""Pydantic row and parameter models for the crop semantic namespace."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FarmRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    farm_id: int
    organization_id: int
    name: str
    location: Optional[str] = None
    timezone: Optional[str] = None
    units: Optional[str] = None


class FieldRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_id: int
    farm_id: int
    name: str
    area_ha: Optional[float] = None
    soil_type: Optional[str] = None
    geometry: Optional[str] = None


class PlotRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plot_id: int
    field_id: int
    trial_id: Optional[int] = None
    code: str
    geometry: Optional[str] = None


class SeasonRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    season_id: int
    farm_id: int
    year: int
    campaign: Optional[str] = None
    status: Optional[str] = None


class PlantingRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    planting_id: int
    field_id: int
    season_id: int
    variety_id: int
    sown_on: Optional[date] = None
    density: Optional[float] = None
    seed_lot: Optional[str] = None


class VarietyRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    variety_id: int
    crop_id: int
    species: Optional[str] = None
    variety: str
    maturity_days: Optional[int] = None
    gdd_base_c: Optional[float] = None


class OperationRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation_id: int
    planting_id: int
    kind: str
    performed_on: datetime
    rate: Optional[float] = None
    rate_unit: Optional[str] = None
    equipment: Optional[str] = None
    operator: Optional[str] = None


class InputLotRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_lot_id: int
    item_id: int
    item_name: str
    lot: str
    on_hand: float
    unit: str


class TrialRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trial_id: int
    season_id: int
    name: str
    design: Optional[str] = None
    treatment_count: int = 0
    replicate_count: int = 0


class TrialResultRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plot_id: int
    plot_code: str
    treatment_code: Optional[str] = None
    replicate_number: Optional[int] = None
    metric: str
    value: Optional[float] = None
    measured_on: Optional[date] = None


class FieldListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    farm_id: int
    season_id: Optional[int] = None


class PlantingListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    season_id: int
    field_id: Optional[int] = None


class OperationListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    planting_id: Optional[int] = None
    kind: Optional[str] = None
    from_: Optional[datetime] = Field(default=None, alias="from")
    to: Optional[datetime] = None


class TrialResultsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trial_id: int
