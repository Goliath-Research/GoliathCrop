# GoliathCrop database schema

Apply **after** the GoliathApp platform schema is present on the database.

## Prerequisites

- PostgreSQL 14+ with **PostGIS** (`CREATE EXTENSION postgis`)
- GoliathApp portal semantic registry and RBAC (`workflow_engine/sql_pg/apply_schema.sh`)

## Apply

```bash
export PGHOST=localhost PGPORT=5432 PGDATABASE=goliath_crop PGUSER=postgres PGPASSWORD='...'
./scripts/apply_domain_schema.sh
```

Scripts under `database/schema/` are idempotent (`CREATE IF NOT EXISTS`, `CREATE OR REPLACE`).

## Layout

| Schema | Purpose |
| --- | --- |
| `crop_core` | Farms, fields (PostGIS), plots, seasons, crops, varieties, plantings |
| `crop_ops` | Operations, inputs, equipment, inventory |
| `crop_trial` | Trials, treatments, replicates, plot measurements |
| `crop_obs` | Devices, sensor readings (TimescaleDB hypertable when available), daily weather |
| `crop_img` | Raster COG assets, imagery scenes, field NDVI stats |
| `crop_alerts` | Threshold rules and alert events (frost, stress, pest) |
| `crop_scout` | Scouting observations, pest catalog, photos |
| `crop_irr` | FAO-56 field water balance and irrigation recommendations |
| `crop_wf` | Domain processing task backlog + Postgres NOTIFY wakes |

Semantic **views** (`v_*`) back `storage_relation` on entities. Named reads use **functions** scoped to the session user (organization membership and optional farm membership). Phase 2 adds write procs `crop_ops.sp_record_operation` and `crop_trial.sp_record_plot_observation` for portal actions. Phase 3 adds sensor ingest (`crop_obs.sp_ingest_sensor_batch`), imagery registration, and alert procs with dual-activation wakes via `crop_wf.sp_enqueue_processing_task`. Phase 4 adds scouting writes (`crop_scout.sp_record_observation`), irrigation balance storage (`crop_irr.sp_store_balance`), and irrigation wakes on weather ET0 upserts and soil-moisture ingest (`crop_irr.sp_wake_schedule_for_field`).

**TimescaleDB:** enable the extension when your host supports it (Neon Apache-2: hypertables, `time_bucket`, `drop_chunks` only). If the extension is missing, readings stay on a regular Postgres table and bucketing falls back to `date_trunc`.
