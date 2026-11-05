# GoliathCrop ecosystem integrations (Phase 5)

GoliathCrop stays a semantic + ActionSpec extension of GoliathApp. Cross-product links are stored in domain tables and exposed through named semantic requests; there is no shared database with sibling repos.

## GoliathOmics

| Crop side | Mechanism |
| --- | --- |
| `crop_lab.samples.omics_run_ref` | Opaque run reference (URI or GoliathOmics semantic code) on a soil/tissue sample |
| `crop_core.plots.omics_run_ref` | Same reference on a trial plot |
| Action `crop.integration.link_omics` | RBAC `crop.sample.write`; sets `omics_run_ref` on `sample_id` and/or `plot_id` |
| Read `crop.sample.list_by_field` | Portal/agents list samples with lab analytes and omics link |

**Expected Omics counterpart (not in this repo):** GoliathOmics stores `external_sample_ref` or plot codes that match `crop.sample` / `crop.plot` keys. Agents reconcile by organization scope and shared identifiers agreed at export time.

## GoliathGroundStation

| Crop side | Mechanism |
| --- | --- |
| `crop_link.groundstation_flights` | Registers `external_flight_ref`, optional `telemetry_uri` and `imagery_uri` per field |
| Action `crop.integration.register_groundstation` | RBAC `crop.imagery.write`; upserts a flight row |
| Read `crop.groundstation.list_by_field` | Lists registered flights for a field |
| Wake path | When `imagery_uri` is set, enqueues `crop.drone.upload` → NDVI processing (same as manual drone ortho) |

Ground Station telemetry remains in the Ground Station product; Crop only holds pointers suitable for imagery ingest and audit.

## ISOBUS / ADAPT machine data

Action `crop.machine.import_file` accepts `format` of `adapt`, `isobus`, or `yield_monitor`. Implementation lives in `goliath_crop.ingest.machine_data`:

- **ADAPT:** JSON stub with `products[]` only; full ADAPT object model not implemented.
- **ISOBUS:** placeholder; no Task Controller binary/XML parser yet.
- **yield_monitor:** CSV line count only; planting linkage and `crop_yield.sp_upsert_measured` wiring are future work.

Responses include `incomplete_edges` so UIs and agents can surface partial coverage.

## Yield model compute (RunPod)

MVP inference runs in-process on CPU (`baseline-cpu-v1` in `goliath_crop.yield_model`).

Optional GPU workers (not called in CI):

| Variable | Purpose |
| --- | --- |
| `RUNPOD_API_KEY` | RunPod API token on the worker host (never commit) |
| `RUNPOD_YIELD_ENDPOINT_ID` | Serverless endpoint or pod template for `crop-yield-model` |

When both are set, `resolve_model_backend()` returns `runpod`, but this repository raises until a deployed DomainProgram image performs the remote call. Weekly season backlog uses `crop_yield.sp_enqueue_season_backlog` → capability `crop.model`.

## Paid providers and auth

Phase 5 leaves John Deere Operations Center, paid weather/imagery, and non–GoliathApp auth as documented future options. MVP remains on free providers and inherited GoliathApp sessions.
