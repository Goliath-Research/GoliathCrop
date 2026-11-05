# GoliathCrop DomainPrograms (Phase 3–5)

| Program | Action | Capability | Activation |
| --- | --- | --- | --- |
| Weather sync | `crop.weather.refresh` | `crop.weather` | Claim (backlog) |
| Sensor ingest / QC | `crop.sensor.ingest_batch`, `crop.sensor.qc` | `crop.ingest` | Wake + claim (`crop_obs.sp_ingest_sensor_batch` → `crop_wf.sp_enqueue_processing_task`) |
| Satellite fetch | `crop.scene.fetch_and_index` | `crop.imagery` | Claim / user action |
| Imagery processing (NDVI) | `crop.imagery.process` | `crop.imagery` | Wake + claim (scene or drone upload registered) |
| Drone upload | `crop.drone.upload` | `crop.imagery` | Wake + claim |
| Alerts (frost, stress, pests) | `crop.alert.evaluate` | `crop.alerts` | Wake + claim (`crop_alerts.sp_open_alert`) |
| Irrigation scheduling | `crop.irrigation.schedule` | `crop.irrigation` | Wake + claim (ET0 upsert or soil moisture ingest; `crop_irr.sp_enqueue_daily_backlog` for daily claim backlog) |
| Yield prediction | `crop.yield.predict` | `crop.model` | Claim (`crop_yield.sp_enqueue_season_backlog` for weekly season backlog) |

Workers claim through **goliath-gateway**, then call `goliath_crop.workers.dispatch.handle`. Wake hints use Postgres `NOTIFY` on `gw1_capability_*` channels (see GoliathApp [dual activation](https://github.com/Goliath-Research/GoliathApp/blob/main/docs/dual-activation.md) and `crop_wf.sp_publish_capability_wake`).

```python
from goliath_crop.workers.dispatch import handle

handle("crop.sensor.qc", {"device_id": 1})
handle("crop.yield.predict", {"season_id": 3})
```

TimescaleDB: sensor readings use a hypertable when the extension is present (Neon Apache-2 tier). Without TimescaleDB, `crop_obs.sensor_readings` remains a plain Postgres table and `fn_readings_window` falls back to `date_trunc` bucketing.

Irrigation: FAO-56 single-layer bucket in `goliath_crop.irrigation.fao56` (CPU worker). Weather upserts and soil-moisture batches call `crop_irr.sp_wake_schedule_for_field`.

Imagery: STAC search uses the free Element84 Earth Search API. COG output paths come from `CROP_RASTER_ROOT` (local directory or `s3://` prefix; no secrets in repo).

Yield: baseline heuristic in `goliath_crop.yield_model` (CPU). Optional RunPod GPU path is selected when `RUNPOD_API_KEY` and `RUNPOD_YIELD_ENDPOINT_ID` are set on the worker host; this repo does not call RunPod in CI — see [docs/integrations.md](../docs/integrations.md).
