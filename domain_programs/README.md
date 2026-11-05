# GoliathCrop DomainPrograms (Phase 2 MVP)

| Program | Action | Capability | Trigger |
| --- | --- | --- | --- |
| Weather sync | `crop.weather.refresh` | `crop.weather` | Scheduled backlog per farm/field |

Workers claim through goliath-gateway, then call `goliath_crop.workers.dispatch.handle`. Weather uses the free Open-Meteo archive API (no paid keys). NOAA NWS can supplement US sites in a later patch; MVP stores Open-Meteo daily aggregates in `crop_obs.weather_daily`.

Python entry:

```python
from goliath_crop.workers.dispatch import handle

handle("crop.weather.refresh", {"farm_id": 1, "days_back": 7})
```
