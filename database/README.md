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

## Layout (Phase 1)

| Schema | Purpose |
| --- | --- |
| `crop_core` | Farms, fields (PostGIS), plots, seasons, crops, varieties, plantings |
| `crop_ops` | Operations, inputs, equipment, inventory |
| `crop_trial` | Trials, treatments, replicates, plot measurements |

Semantic **views** (`v_*`) back `storage_relation` on entities. Named reads use **functions** scoped to the session user (organization membership and optional farm membership).

TimescaleDB hypertables (`crop_obs`) are Phase 3; not required for Phase 1 apply.
