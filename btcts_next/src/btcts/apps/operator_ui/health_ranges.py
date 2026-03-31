# path: ./btcts_next/src/btcts/apps/operator_ui/health_ranges.py
# desc: Health タブ向けのレンジ定義と bucket helper。

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


HEALTH_RANGE_PRESETS: dict[str, dict[str, Any]] = {
    "1h": {
        "label": "1時間",
        "window_minutes": 60,
        "bucket_minutes": 1,
    },
    "24h": {
        "label": "24時間",
        "window_minutes": 24 * 60,
        "bucket_minutes": 30,
    },
    "1w": {
        "label": "1週間",
        "window_minutes": 7 * 24 * 60,
        "bucket_minutes": 180,
    },
}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def range_config(range_key: str) -> dict[str, Any]:
    return HEALTH_RANGE_PRESETS.get(range_key, HEALTH_RANGE_PRESETS["1h"])


def bucket_floor(dt: datetime, bucket_minutes: int) -> datetime:
    minute_bucket = (dt.minute // bucket_minutes) * bucket_minutes
    return dt.replace(minute=minute_bucket, second=0, microsecond=0)


def time_buckets(window_minutes: int, bucket_minutes: int) -> list[datetime]:
    now = bucket_floor(now_utc(), bucket_minutes)
    bucket_count = max(1, window_minutes // bucket_minutes)
    start = now - timedelta(minutes=bucket_minutes * (bucket_count - 1))
    return [start + timedelta(minutes=bucket_minutes * i) for i in range(bucket_count)]


def display_buckets(buckets: list[datetime], *, include_in_progress: bool) -> list[datetime]:
    if include_in_progress:
        return buckets
    if len(buckets) <= 1:
        return buckets
    return buckets[:-1]


def bucket_end(bucket: datetime, bucket_minutes: int) -> datetime:
    return bucket + timedelta(minutes=bucket_minutes)