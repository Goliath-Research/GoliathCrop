# GoliathCrop semantic layer

GoliathCrop is a **descendant application** on [GoliathApp](https://github.com/Goliath-Research/GoliathApp). Raw tables in `crop_core`, `crop_ops`, `crop_trial`, and `crop_obs` are internal; the portal, Exograph, and agents reach them only through registered semantic requests and typed `ActionSpec` actions.

Platform background: [GoliathApp semantic layer](https://goliath-research.github.io/GoliathApp/semantic-layer/) and [semantic extensions](https://goliath-research.github.io/GoliathApp/semantic-extensions/).

## Namespace

| Item | Value |
| --- | --- |
| Namespace code | `crop` |
| Python specs | `src/goliath_crop/semantic/catalog.py` |
| Export | `goliath-crop-semantic-export` → `schemas/semantic/catalog.json`, `database/schema/portal_semantic_row_types.sql` |
| DB seed | `goliath-crop-seed-semantic` (calls `portal.sp_semantic_register_*`) |

Apply order: GoliathApp `apply_schema.sh`, then `./scripts/apply_domain_schema.sh`, then semantic seed.

## Entities (Phase 1 + Phase 2 weather)

Entities and `storage_relation` views match [docs/plan.md](plan.md). Phase 2 adds `crop.weather` backed by `crop_obs.v_weather_daily`.

Sensor readings, samples, imagery, scouting, and yield entities remain planned for later phases.

## Named requests (Phase 2 MVP)

| Request | Function target |
| --- | --- |
| `crop.farm.list` | `crop_core.fn_semantic_farm_list` |
| `crop.field.list_by_farm` | `crop_core.fn_semantic_field_list_by_farm` |
| `crop.season.list_by_farm` | `crop_core.fn_semantic_season_list_by_farm` |
| `crop.planting.list_by_season` | `crop_core.fn_semantic_planting_list_by_season` |
| `crop.operation.list` | `crop_ops.fn_semantic_operation_list` |
| `crop.input_lot.list_by_farm` | `crop_ops.fn_semantic_input_lot_list_by_farm` |
| `crop.weather.daily` | `crop_obs.fn_semantic_weather_daily` |
| `crop.trial.list_by_season` | `crop_trial.fn_semantic_trial_list_by_season` |
| `crop.trial.results` | `crop_trial.fn_trial_results` |

Targets use `target_kind=function` because GoliathApp semantic runner v1 executes organization- and farm-scoped reads inside SQL (see `crop_core.fn_user_can_access_farm`).

## Actions

Domain actions publish through the setuptools entry point:

```toml
[project.entry-points."goliath.action_catalogs"]
crop = "goliath_crop.actions.catalog:ACTIONS"
```

Phase 2 ships:

| Action | Exposure | Notes |
| --- | --- | --- |
| `crop.field.import_boundaries` | RBAC | Stub ingest until Phase 3 worker |
| `crop.operation.record` | RBAC | Writes via `crop_ops.sp_record_operation` when libpq env is set |
| `crop.weather.refresh` | HIDDEN | Open-Meteo worker; upserts `crop_obs.weather_daily` |
| `crop.trial.record_observation` | RBAC | Plot measurements for research trials |

Sync into `wf.workflow_action` with GoliathApp `seed_action_catalog.py --use-db` after installing this package.

## NavTree

`database/schema/05_nav_crop.sql` registers the **Crop** menu and Phase 2 leaves (Farms & fields, Seasons & plantings, Operations, Inventory, Sensors & weather, Trials). Foundation GoliathApp nodes are never updated. Python helper: `goliath-crop-seed-nav`.

Portal FrameKey → view mapping: [`portal/frames.json`](../portal/frames.json).

## Row-level security

Base tables enable RLS scoped by organization membership (`portal.fn_semantic_user_organization_ids`) and optional `crop_core.farm_members`. Session-scoped writes set `goliath.crop.user_id` when using direct table access; semantic reads enforce scope in SECURITY DEFINER functions.
