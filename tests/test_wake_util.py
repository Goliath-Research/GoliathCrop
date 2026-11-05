"""Wake channel naming tests."""

from goliath_crop.wake_util import capability_pg_notify_channel


def test_crop_ingest_notify_channel() -> None:
    assert capability_pg_notify_channel("crop.ingest") == "gw1_capability_crop_ingest"


def test_crop_imagery_notify_channel() -> None:
    assert capability_pg_notify_channel("crop.imagery") == "gw1_capability_crop_imagery"
