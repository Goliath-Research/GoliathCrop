# GoliathCrop semantic layer

GoliathCrop is a **descendant application** on [GoliathApp](https://github.com/Goliath-Research/GoliathApp). Raw tables in `crop_core`, `crop_ops`, and `crop_trial` are internal; the portal, Exograph, and agents reach them only through registered semantic requests and typed `ActionSpec` actions.

Platform background: [GoliathApp semantic layer](https://goliath-research.github.io/GoliathApp/semantic-layer/) and [semantic extensions](https://goliath-research.github.io/GoliathApp/semantic-extensions/).

## Namespace

| Item | Value |
| --- | --- |
| Namespace code | `crop` |
| Python specs | `src/goliath_crop/semantic/catalog.py` |
| Export | `goliath-crop-semantic-export` → `schemas/semantic/catalog.json`, `database/schema/portal_semantic_row_types.sql` |
| DB seed | `goliath-crop-seed-semantic` (calls `portal.sp_semantic_register_*`) |

Apply order: GoliathApp `apply_schema.sh`, then `./scripts/apply_domain_schema.sh`, then semantic seed.

## Phase 1 entities

Entities and `storage_relation` views match [docs/plan.md](plan.md): `crop.farm`, `crop.field`, `crop.plot`, `crop.season`, `crop.planting`, `crop.variety`, `crop.operation`, `crop.input_lot`, `crop.trial`.

Sensor, weather, sample, scene, scouting, and yield entities are planned for later phases.

## Phase 1 named requests

| Request | Function target |
| --- | --- |
| `crop.field.list_by_farm` | `crop_core.fn_semantic_field_list_by_farm` |
| `crop.planting.list_by_season` | `crop_core.fn_semantic_planting_list_by_season` |
| `crop.operation.list` | `crop_ops.fn_semantic_operation_list` |
| `crop.trial.results` | `crop_trial.fn_trial_results` |

Targets use `target_kind=function` because GoliathApp semantic runner v1 executes organization- and farm-scoped reads inside SQL (see `crop_core.fn_user_can_access_farm`).

## Actions

Domain actions publish through the setuptools entry point:

```toml
[project.entry-points."goliath.action_catalogs"]
crop = "goliath_crop.actions.catalog:ACTIONS"
```

Phase 1 ships typed specs (and stub in-process handlers) for:

- `crop.field.import_boundaries`
- `crop.operation.record`

Sync into `wf.workflow_action` with GoliathApp `seed_action_catalog.py --use-db` after installing this package.

## NavTree

`database/schema/05_nav_crop.sql` registers the **Crop** menu and Phase 1 leaves (Farms & fields, Seasons & plantings, Operations, Trials). Foundation GoliathApp nodes are never updated. Python helper: `goliath-crop-seed-nav`.

## Row-level security

Base tables enable RLS scoped by organization membership (`portal.fn_semantic_user_organization_ids`) and optional `crop_core.farm_members`. Session-scoped writes set `goliath.crop.user_id` when using direct table access; semantic reads enforce scope in SECURITY DEFINER functions.
