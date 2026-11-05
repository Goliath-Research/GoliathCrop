"""STAC helper unit tests (offline)."""

from goliath_crop.imagery.stac import default_scene_window


def test_default_scene_window() -> None:
    start, end = default_scene_window(days_back=7)
    assert start <= end
    assert (end - start).days == 7
