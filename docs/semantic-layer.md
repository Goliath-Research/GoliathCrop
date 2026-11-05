# GoliathCrop semantic layer

GoliathCrop is a **descendant application** on [GoliathApp](https://github.com/Goliath-Research/GoliathApp). Raw tables in `crop_core`, `crop_ops`, `crop_trial`, `crop_obs`, `crop_scout`, and `crop_irr` are internal; the portal, Exograph, and agents reach them only through registered semantic requests and typed `ActionSpec` actions.

Platform background: [GoliathApp semantic layer](https://goliath-research.github.io/GoliathApp/semantic-layer/) and [semantic extensions](https://goliath-research.github.io/GoliathApp/semantic-extensions/).

## Namespace

| Item | Value |
| --- | --- |
| Namespace code | `crop` |
| Python specs | `src/goliath_crop/semantic/catalog.py` |
| Export | `goliath-crop-semantic-export` → `schemas/semantic/catalog.json`, `database/schema/portal_semantic_row_types.sql` |
| DB seed | `goliath-crop-seed-semantic` (calls `portal.sp_semantic_register_*`) |

Apply order: GoliathApp `apply_schema.sh`, then `./scripts/apply_domain_schema.sh`, then semantic seed.

## Entities

Entities and `storage_relation` views match [docs/plan.md](plan.md). Phase 3 adds sensors, readings, and imagery scenes. Phase 4 adds `crop.scouting` and `crop.irrigation`.

## Named requests (MVP + sensing + Phase 4)

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
| `crop.sensor.list_by_farm` | `crop_obs.fn_semantic_device_list` |
| `crop.reading.window` | `crop_obs.fn_readings_window` |
| `crop.scene.list_by_field` | `crop_img.fn_semantic_scene_list` |
| `crop.scouting.list_by_field` | `crop_scout.fn_semantic_list_by_field` |
| `crop.irrigation.schedule_by_field` | `crop_irr.fn_semantic_schedule_by_field` |

Targets use `target_kind=function` because GoliathApp semantic runner v1 executes organization- and farm-scoped reads inside SQL (see `crop_core.fn_user_can_access_farm`).

## Actions

Domain actions publish through the setuptools entry point:

```toml
[project.entry-points."goliath.action_catalogs"]
crop = "goliath_crop.actions.catalog:ACTIONS"
```

Phase 4 adds `crop.scouting.record` (RBAC) and hidden worker action `crop.irrigation.schedule`. Earlier phases ship field import, operations, weather refresh, trials, sensors, imagery, and alerts — see `src/goliath_crop/actions/catalog.py`.

Sync into `wf.workflow_action` with GoliathApp `seed_action_catalog.py --use-db` after installing this package.

## NavTree

`database/schema/05_nav_crop.sql` registers the **Crop** menu and leaves including Phase 4 **Scouting**, **Irrigation planner**, and **Field entry**. Foundation GoliathApp nodes are never updated. Python helper: `goliath-crop-seed-nav`.

Portal FrameKey → view mapping: [`portal/frames.json`](../portal/frames.json).

## Row-level security

Base tables enable RLS scoped by organization membership (`portal.fn_semantic_user_organization_ids`) and optional `crop_core.farm_members`. Session-scoped writes set `goliath.crop.user_id` when using direct table access; semantic reads enforce scope in SECURITY DEFINER functions.
