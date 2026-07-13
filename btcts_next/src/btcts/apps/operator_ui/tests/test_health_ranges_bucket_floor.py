# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_ranges_bucket_floor.py
# desc: Verifies arbitrary-width Health bucket floor calculations.

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from btcts.apps.operator_ui.health_ranges import bucket_floor


def _utc(hour: int, minute: int, second: int = 0) -> datetime:
    return datetime(2026, 7, 14, hour, minute, second, tzinfo=timezone.utc)


def test_bucket_floor_supports_one_minute_buckets() -> None:
    assert bucket_floor(_utc(1, 23, 59), 1) == _utc(1, 23)


def test_bucket_floor_supports_thirty_minute_buckets() -> None:
    assert bucket_floor(_utc(0, 29, 59), 30) == _utc(0, 0)
    assert bucket_floor(_utc(0, 30), 30) == _utc(0, 30)
    assert bucket_floor(_utc(23, 59, 59), 30) == _utc(23, 30)


def test_bucket_floor_supports_three_hour_buckets() -> None:
    assert bucket_floor(_utc(0, 1), 180) == _utc(0, 0)
    assert bucket_floor(_utc(1, 59), 180) == _utc(0, 0)
    assert bucket_floor(_utc(2, 30), 180) == _utc(0, 0)
    assert bucket_floor(_utc(3, 0), 180) == _utc(3, 0)
    assert bucket_floor(_utc(23, 59), 180) == _utc(21, 0)


def test_bucket_floor_rejects_non_positive_width() -> None:
    with pytest.raises(ValueError, match="bucket_minutes must be at least 1"):
        bucket_floor(_utc(0, 0), 0)
