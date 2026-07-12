# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_current_state_persistence.py
# desc: MR-F2 guards current-state start, continuation, transition, UNKNOWN fail-closed, and persistence round-trip semantics.
from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.current_state_persistence import (  # noqa: E402
    build_persisted_current_state,
    read_persisted_current_state,
    write_persisted_current_state,
)


def test_persistence_starts_continues_and_transitions() -> None:
    started = build_persisted_current_state(
        previous={}, regime_code="RANGE", observed_at="2026-07-12T00:00:00Z",
        estimator_version="v1", source_cutoff_time="2026-07-12T00:00:00Z",
    )
    assert started["state_started_at"] == "2026-07-12T00:00:00Z"
    assert started["state_age_sec"] == 0
    assert started["persistence_status"] == "started"

    continued = build_persisted_current_state(
        previous=started, regime_code="RANGE", observed_at="2026-07-12T00:05:00Z",
        estimator_version="v1", source_cutoff_time="2026-07-12T00:05:00Z",
    )
    assert continued["state_started_at"] == "2026-07-12T00:00:00Z"
    assert continued["state_age_sec"] == 300
    assert continued["transition_detected"] is False

    changed = build_persisted_current_state(
        previous=continued, regime_code="UP_TREND", observed_at="2026-07-12T00:06:00Z",
        estimator_version="v1", source_cutoff_time="2026-07-12T00:06:00Z",
    )
    assert changed["state_started_at"] == "2026-07-12T00:06:00Z"
    assert changed["state_age_sec"] == 0
    assert changed["transition_detected"] is True


def test_persistence_unknown_fails_closed_and_round_trips(tmp_path: Path) -> None:
    unknown = build_persisted_current_state(
        previous={"regime_code": "RANGE", "state_started_at": "2026-07-12T00:00:00Z"},
        regime_code="UNKNOWN", observed_at="2026-07-12T00:05:00Z",
        estimator_version="v1", source_cutoff_time="2026-07-12T00:05:00Z",
    )
    assert unknown["state_started_at"] == ""
    assert unknown["state_age_sec"] is None
    assert unknown["persistence_status"] == "unavailable"
    result = write_persisted_current_state(tmp_path, unknown)
    assert result["ok"] is True
    assert read_persisted_current_state(tmp_path) == unknown
