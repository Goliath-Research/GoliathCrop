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
    omics_run_ref: Optional[str] = None
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


class FarmListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    organization_id: Optional[int] = None


class SeasonListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    farm_id: int


class InputLotListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    farm_id: int


class TrialListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    season_id: int


class WeatherRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_id: int
    date: date
    tmin: Optional[float] = None
    tmax: Optional[float] = None
    precip: Optional[float] = None
    gdd: Optional[float] = None
    et0: Optional[float] = None
    source: Optional[str] = None


class WeatherDailyParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_id: int
    from_: Optional[date] = Field(default=None, alias="from")
    to: Optional[date] = None


class SensorRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    device_id: int
    farm_id: int
    kind: str
    field_id: Optional[int] = None
    label: Optional[str] = None
    last_reading_at: Optional[datetime] = None


class ReadingRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    device_id: int
    ts: datetime
    metric: str
    value: float
    bucket: Optional[datetime] = None


class SceneRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene_id: int
    field_id: int
    acquired_at: datetime
    source: str
    ndvi_mean: Optional[float] = None
    cog_uri: Optional[str] = None


class SensorListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    farm_id: int


class ReadingWindowParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sensor_id: int
    from_: Optional[datetime] = Field(default=None, alias="from")
    to: Optional[datetime] = None
    bucket: Optional[str] = None


class SceneListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_id: int
    from_: Optional[datetime] = Field(default=None, alias="from")
    to: Optional[datetime] = None


class ScoutingRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observation_id: int
    field_id: int
    observed_at: datetime
    pest: str
    pest_name: Optional[str] = None
    severity: int
    notes: Optional[str] = None
    geo_json: Optional[str] = None
    photo_uri: Optional[str] = None


class ScoutingListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_id: int
    from_: Optional[datetime] = Field(default=None, alias="from")
    to: Optional[datetime] = None


class IrrigationRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_id: int
    schedule_date: date
    depletion_mm: float
    soil_moisture_pct: Optional[float] = None
    recommended_irrigation_mm: float
    etc_mm: Optional[float] = None
    precip_mm: Optional[float] = None
    applied_irrigation_mm: Optional[float] = None
    computed_at: Optional[datetime] = None


class IrrigationScheduleParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_id: int
    from_: Optional[date] = Field(default=None, alias="from")
    to: Optional[date] = None


class YieldRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    planting_id: int
    season_id: int
    field_id: int
    measured_t_ha: Optional[float] = None
    predicted_t_ha: Optional[float] = None
    model_version: Optional[str] = None
    predicted_at: Optional[datetime] = None


class YieldBySeasonParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    season_id: int


class SampleRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sample_id: int
    field_id: int
    plot_id: Optional[int] = None
    kind: str
    collected_on: date
    depth_cm: Optional[float] = None
    geo_json: Optional[str] = None
    omics_run_ref: Optional[str] = None
    n_ppm: Optional[float] = None
    p_ppm: Optional[float] = None
    k_ppm: Optional[float] = None
    ph: Optional[float] = None
    om_pct: Optional[float] = None


class SampleListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_id: int
    kind: Optional[str] = None
    from_: Optional[date] = Field(default=None, alias="from")
    to: Optional[date] = None


class GroundstationLinkRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    link_id: int
    field_id: int
    external_flight_ref: str
    telemetry_uri: Optional[str] = None
    imagery_uri: Optional[str] = None
    source_product: str
    registered_at: datetime
    notes: Optional[str] = None


class GroundstationListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_id: int
