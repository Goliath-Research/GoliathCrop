"""Open-Meteo archive API client (free, no API key)."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable


@dataclass(frozen=True)
class DailyWeatherObservation:
    obs_date: date
    tmin_c: float | None
    tmax_c: float | None
    precip_mm: float | None
    et0_mm: float | None


def _gdd(tmin: float | None, tmax: float | None, base_c: float = 10.0) -> float | None:
    if tmin is None or tmax is None:
        return None
    avg = (tmin + tmax) / 2.0
    delta = avg - base_c
    return round(max(0.0, delta), 2)


def fetch_open_meteo_daily(
    latitude: float,
    longitude: float,
    *,
    start: date,
    end: date,
    timezone: str = "UTC",
) -> list[DailyWeatherObservation]:
    if end < start:
        return []
    params = {
        "latitude": f"{latitude:.6f}",
        "longitude": f"{longitude:.6f}",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": ",".join(
            (
                "temperature_2m_min",
                "temperature_2m_max",
                "precipitation_sum",
                "et0_fao_evapotranspiration",
            )
        ),
        "timezone": timezone,
    }
    url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    daily = payload.get("daily") or {}
    dates_raw: Iterable[str] = daily.get("time") or []
    tmin_list = daily.get("temperature_2m_min") or []
    tmax_list = daily.get("temperature_2m_max") or []
    precip_list = daily.get("precipitation_sum") or []
    et0_list = daily.get("et0_fao_evapotranspiration") or []
    observations: list[DailyWeatherObservation] = []
    for idx, day_str in enumerate(dates_raw):
        obs_date = date.fromisoformat(day_str)
        tmin = _cell(tmin_list, idx)
        tmax = _cell(tmax_list, idx)
        precip = _cell(precip_list, idx)
        et0 = _cell(et0_list, idx)
        observations.append(
            DailyWeatherObservation(
                obs_date=obs_date,
                tmin_c=tmin,
                tmax_c=tmax,
                precip_mm=precip,
                et0_mm=et0,
            )
        )
    return observations


def default_backfill_window(*, days_back: int = 7) -> tuple[date, date]:
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=max(0, days_back - 1))
    return start, end


def _cell(values: list[object], index: int) -> float | None:
    if index >= len(values):
        return None
    value = values[index]
    if value is None:
        return None
    if not isinstance(value, (int, float, str)):
        return None
    return float(value)


def observation_with_gdd(obs: DailyWeatherObservation, *, gdd_base_c: float = 10.0) -> tuple[float | None, float | None]:
    gdd = _gdd(obs.tmin_c, obs.tmax_c, gdd_base_c)
    return gdd, obs.et0_mm
