# GoliathCrop portal domain views (Phase 2 MVP)

Mobile-first HTML views extend the GoliathApp portal shell via `portal."NodeInfos"."FrameKey"` values registered in `database/schema/05_nav_crop.sql`.

## Integration

1. Serve this directory as static assets beside the GoliathApp portal bundle (same origin as the semantic/action gateway).
2. The shell loads `frames.json` and embeds the mapped view in an iframe or inline fetch.
3. Views call the platform gateway using a session token injected by the shell as `window.GOLIATH_SESSION` (see `static/crop-api.js`).

## Views

| FrameKey | View | Semantic reads / actions |
| --- | --- | --- |
| `crop.field.list_by_farm` | `views/farm-map.html` | `crop.farm.list`, `crop.field.list_by_farm` |
| `crop.field.detail` | `views/field-detail.html` | `crop.season.list_by_farm`, `crop.planting.list_by_season`, `crop.operation.list`, `crop.weather.daily` |
| `crop.operation.list` | `views/operations.html` | `crop.operation.list`; action `crop.operation.record` |
| `crop.input_lot.list_by_farm` | `views/inventory.html` | `crop.input_lot.list_by_farm` |
| `crop.weather.daily` | `views/weather.html` | `crop.weather.daily` |
| `crop.trial.list_by_season` | `views/trials.html` | `crop.trial.list_by_season`, `crop.trial.results`; action `crop.trial.record_observation` |

Layouts use a single column, 16px base tap targets, and `env(safe-area-inset-*)` padding for phones.

## Local preview

Open `views/shell.html` in a browser with dev tools mobile emulation. Without a gateway, views show fixture data from `static/demo-fixtures.json`.
