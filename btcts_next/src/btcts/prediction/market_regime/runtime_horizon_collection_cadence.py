# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_collection_cadence.py
# desc: MR-F9.19L deterministic planned-start cadence calculations for bounded foreground collection.

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def _utc(value: datetime, *, field: str) -> datetime:
    if not isinstance(value, datetime):
        raise ValueError(f"runtime_horizon_collection_cadence_{field}_invalid")
    if value.tzinfo is None:
        raise ValueError(f"runtime_horizon_collection_cadence_{field}_timezone_required")
    return value.astimezone(timezone.utc)


def collection_start_wait_seconds(*, planned_start: datetime, observed_at: datetime) -> float:
    start = _utc(planned_start, field="planned_start")
    observed = _utc(observed_at, field="observed_at")
    return max(0.0, (start - observed).total_seconds())


def next_collection_cadence_at(
    *,
    planned_start: datetime,
    observed_at: datetime,
    cadence_sec: int,
) -> datetime:
    start = _utc(planned_start, field="planned_start")
    observed = _utc(observed_at, field="observed_at")
    if type(cadence_sec) is not int or cadence_sec <= 0:
        raise ValueError("runtime_horizon_collection_cadence_sec_invalid")
    if observed < start:
        return start
    elapsed = (observed - start).total_seconds()
    completed_slots = int(elapsed // cadence_sec)
    return start + timedelta(seconds=(completed_slots + 1) * cadence_sec)


def collection_cadence_sleep_seconds(
    *,
    planned_start: datetime,
    planned_end: datetime,
    observed_at: datetime,
    cadence_sec: int,
) -> float:
    start = _utc(planned_start, field="planned_start")
    end = _utc(planned_end, field="planned_end")
    observed = _utc(observed_at, field="observed_at")
    if end <= start:
        raise ValueError("runtime_horizon_collection_cadence_window_invalid")
    if observed >= end:
        return 0.0
    next_at = next_collection_cadence_at(
        planned_start=start,
        observed_at=observed,
        cadence_sec=cadence_sec,
    )
    bounded = min(next_at, end)
    return max(0.0, (bounded - observed).total_seconds())
