"""Open-Meteo client unit tests."""

from __future__ import annotations

import json
from datetime import date
from unittest import mock

from goliath_crop.weather.open_meteo import fetch_open_meteo_daily, observation_with_gdd


def test_fetch_open_meteo_daily_parses_archive_payload() -> None:
    payload = {
        "daily": {
            "time": ["2026-05-01", "2026-05-02"],
            "temperature_2m_min": [5.0, 6.5],
            "temperature_2m_max": [18.0, 20.0],
            "precipitation_sum": [0.0, 4.2],
            "et0_fao_evapotranspiration": [2.5, 3.0],
        }
    }
    body = json.dumps(payload).encode("utf-8")

    class FakeResponse:
        def read(self) -> bytes:
            return body

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *args: object) -> None:
            return None

    with mock.patch("urllib.request.urlopen", return_value=FakeResponse()):
        rows = fetch_open_meteo_daily(41.0, -93.0, start=date(2026, 5, 1), end=date(2026, 5, 2))

    assert len(rows) == 2
    assert rows[0].tmin_c == 5.0
    assert rows[1].precip_mm == 4.2


def test_observation_with_gdd() -> None:
    from goliath_crop.weather.open_meteo import DailyWeatherObservation

    obs = DailyWeatherObservation(date(2026, 5, 1), 8.0, 22.0, 0.0, 3.1)
    gdd, et0 = observation_with_gdd(obs)
    assert gdd == 5.0
    assert et0 == 3.1
