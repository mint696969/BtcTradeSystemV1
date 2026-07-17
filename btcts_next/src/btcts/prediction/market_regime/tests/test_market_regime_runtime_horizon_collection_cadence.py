# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_collection_cadence.py
# desc: MR-F9.19L planned-start anchored collection cadence tests.

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from btcts.prediction.market_regime.runtime_horizon_collection_cadence import (
    collection_cadence_sleep_seconds,
    collection_start_wait_seconds,
    next_collection_cadence_at,
)


def _dt(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)


def test_waits_until_planned_start() -> None:
    assert collection_start_wait_seconds(
        planned_start=_dt("2026-07-17T02:00:00Z"),
        observed_at=_dt("2026-07-17T01:59:45Z"),
    ) == 15.0
    assert collection_start_wait_seconds(
        planned_start=_dt("2026-07-17T02:00:00Z"),
        observed_at=_dt("2026-07-17T02:00:01Z"),
    ) == 0.0


def test_next_boundary_is_anchored_to_planned_start() -> None:
    assert next_collection_cadence_at(
        planned_start=_dt("2026-07-17T02:00:00Z"),
        observed_at=_dt("2026-07-17T02:00:07Z"),
        cadence_sec=60,
    ) == _dt("2026-07-17T02:01:00Z")
    assert next_collection_cadence_at(
        planned_start=_dt("2026-07-17T02:00:00Z"),
        observed_at=_dt("2026-07-17T02:01:12Z"),
        cadence_sec=60,
    ) == _dt("2026-07-17T02:02:00Z")


def test_tick_runtime_does_not_accumulate_drift() -> None:
    start = _dt("2026-07-17T02:00:00Z")
    end = _dt("2026-07-18T02:00:00Z")
    assert collection_cadence_sleep_seconds(
        planned_start=start,
        planned_end=end,
        observed_at=_dt("2026-07-17T02:00:07Z"),
        cadence_sec=60,
    ) == 53.0
    assert collection_cadence_sleep_seconds(
        planned_start=start,
        planned_end=end,
        observed_at=_dt("2026-07-17T02:01:12Z"),
        cadence_sec=60,
    ) == 48.0


def test_sleep_is_bounded_by_planned_end() -> None:
    assert collection_cadence_sleep_seconds(
        planned_start=_dt("2026-07-17T02:00:00Z"),
        planned_end=_dt("2026-07-17T02:02:30Z"),
        observed_at=_dt("2026-07-17T02:02:10Z"),
        cadence_sec=60,
    ) == 20.0
    assert collection_cadence_sleep_seconds(
        planned_start=_dt("2026-07-17T02:00:00Z"),
        planned_end=_dt("2026-07-17T02:02:30Z"),
        observed_at=_dt("2026-07-17T02:02:30Z"),
        cadence_sec=60,
    ) == 0.0


def test_invalid_inputs_fail_closed() -> None:
    naive = datetime(2026, 7, 17, 2, 0, 0)
    with pytest.raises(ValueError, match="timezone_required"):
        collection_start_wait_seconds(planned_start=naive, observed_at=_dt("2026-07-17T02:00:00Z"))
    with pytest.raises(ValueError, match="sec_invalid"):
        next_collection_cadence_at(
            planned_start=_dt("2026-07-17T02:00:00Z"),
            observed_at=_dt("2026-07-17T02:00:00Z"),
            cadence_sec=0,
        )
    with pytest.raises(ValueError, match="window_invalid"):
        collection_cadence_sleep_seconds(
            planned_start=_dt("2026-07-17T02:00:00Z"),
            planned_end=_dt("2026-07-17T02:00:00Z"),
            observed_at=_dt("2026-07-17T02:00:00Z"),
            cadence_sec=60,
        )
