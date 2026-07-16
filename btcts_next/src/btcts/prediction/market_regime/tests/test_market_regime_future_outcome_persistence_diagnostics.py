# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_outcome_persistence_diagnostics.py
# desc: MR-F9.8 guards for multi-snapshot unresolved persistence and outcome-resolution diagnostics.

from __future__ import annotations

from copy import deepcopy

import pytest

from btcts.prediction.market_regime.future_outcome_persistence_diagnostics import (
    build_future_outcome_persistence_diagnostics,
)


def _row(trace: str, horizon: int, candidate: str, status: str, resolved_at: str, observed: str = "UNKNOWN"):
    return {
        "trace_id": trace,
        "origin_timestamp": "2026-07-16T00:00:00Z",
        "expiry_at": "2026-07-16T00:05:00Z" if horizon == 300 else "2026-07-16T00:15:00Z",
        "resolved_at": resolved_at,
        "target_horizon_sec": horizon,
        "parameter_set_id": candidate,
        "model_id": "model:1",
        "logic_version": "logic:1",
        "feature_snapshot_ref": "snapshot:1",
        "observed_future_state": observed,
        "outcome_status": status,
        "outcome_reason": (
            "observed_future_state_unknown"
            if status == "UNRESOLVED" and observed == "UNKNOWN"
            else "fixture_reason"
        ),
    }


def _snapshot(receipt: str, suite: str, polled_at: str, status_300: str, status_900: str):
    rows = (
        _row(f"{receipt}:300:active", 300, "active", status_300, polled_at, "RANGE" if status_300 != "UNRESOLVED" else "UNKNOWN"),
        _row(f"{receipt}:300:shadow", 300, "shadow", status_300, polled_at, "RANGE" if status_300 != "UNRESOLVED" else "UNKNOWN"),
        _row(f"{receipt}:900:active", 900, "active", status_900, polled_at, "RANGE" if status_900 != "UNRESOLVED" else "UNKNOWN"),
        _row(f"{receipt}:900:shadow", 900, "shadow", status_900, polled_at, "RANGE" if status_900 != "UNRESOLVED" else "UNKNOWN"),
    )
    rows = tuple(sorted(rows, key=lambda row: row["trace_id"]))
    return {
        "artifact_kind": "future_shadow_maturation_snapshot",
        "receipt_id": receipt,
        "suite_id": suite,
        "prediction_origin": "2026-07-16T00:00:00Z",
        "polled_at": polled_at,
        "trace_count": len(rows),
        "trace_ids": tuple(row["trace_id"] for row in rows),
        "outcome_rows": rows,
    }


def test_unresolved_persistence_and_resolution_delay_are_aggregated() -> None:
    result = build_future_outcome_persistence_diagnostics(
        maturation_snapshots=(
            _snapshot("receipt:1", "suite:1", "2026-07-16T00:04:00Z", "UNRESOLVED", "UNRESOLVED"),
            _snapshot("receipt:1", "suite:1", "2026-07-16T00:06:00Z", "CORRECT", "UNRESOLVED"),
            _snapshot("receipt:1", "suite:1", "2026-07-16T00:16:00Z", "CORRECT", "INCORRECT"),
        ),
        evaluated_at="2026-07-16T01:00:00Z",
    )
    assert result["snapshot_count"] == 3
    active_300 = next(
        item for item in result["summaries"]
        if item["target_horizon_sec"] == 300 and item["parameter_set_id"] == "active"
    )
    active_900 = next(
        item for item in result["summaries"]
        if item["target_horizon_sec"] == 900 and item["parameter_set_id"] == "active"
    )
    assert active_300["latest_terminal_coverage_rate"] == 1.0
    assert active_300["mean_unresolved_poll_count"] == 1.0
    assert active_300["mean_resolution_delay_sec"] == 60.0
    assert active_900["mean_unresolved_poll_count"] == 2.0
    assert active_900["mean_resolution_delay_sec"] == 60.0
    assert result["probability_metrics_computed"] is False


def test_multiple_receipts_are_aggregated_without_trace_reuse() -> None:
    result = build_future_outcome_persistence_diagnostics(
        maturation_snapshots=(
            _snapshot("receipt:1", "suite:1", "2026-07-16T00:16:00Z", "CORRECT", "INCORRECT"),
            _snapshot("receipt:2", "suite:2", "2026-07-16T00:16:00Z", "INVALIDATED", "ABSTAINED"),
        ),
        evaluated_at="2026-07-16T01:00:00Z",
    )
    assert result["receipt_count"] == 2
    active_300 = next(
        item for item in result["summaries"]
        if item["target_horizon_sec"] == 300 and item["parameter_set_id"] == "active"
    )
    assert active_300["trace_count"] == 2
    assert active_300["ever_invalidated_rate"] == 0.5


def test_terminal_regression_and_identity_change_fail_closed() -> None:
    first = _snapshot("receipt:1", "suite:1", "2026-07-16T00:06:00Z", "CORRECT", "UNRESOLVED")
    regressed = _snapshot("receipt:1", "suite:1", "2026-07-16T00:07:00Z", "UNRESOLVED", "UNRESOLVED")
    with pytest.raises(ValueError, match="terminal_regression"):
        build_future_outcome_persistence_diagnostics(
            maturation_snapshots=(first, regressed),
            evaluated_at="2026-07-16T01:00:00Z",
        )

    changed = _snapshot(
        "receipt:1",
        "suite:1",
        "2026-07-16T00:07:00Z",
        "CORRECT",
        "UNRESOLVED",
    )
    rows = list(changed["outcome_rows"])
    rows[0] = dict(rows[0], model_id="model:changed")
    changed["outcome_rows"] = tuple(rows)
    with pytest.raises(ValueError, match="trace_identity_changed"):
        build_future_outcome_persistence_diagnostics(
            maturation_snapshots=(first, changed),
            evaluated_at="2026-07-16T01:00:00Z",
        )


def test_unknown_observation_is_not_confused_with_missing_observation_and_terminal_change_fails() -> None:
    missing = _snapshot(
        "receipt:1",
        "suite:1",
        "2026-07-16T00:04:00Z",
        "UNRESOLVED",
        "UNRESOLVED",
    )
    missing_rows = tuple(
        dict(row, outcome_reason="observation_unavailable")
        for row in missing["outcome_rows"]
    )
    missing["outcome_rows"] = missing_rows
    result = build_future_outcome_persistence_diagnostics(
        maturation_snapshots=(missing,),
        evaluated_at="2026-07-16T01:00:00Z",
    )
    assert all(item["unknown_observed_rate"] == 0.0 for item in result["summaries"])

    first = _snapshot(
        "receipt:2",
        "suite:2",
        "2026-07-16T00:06:00Z",
        "CORRECT",
        "UNRESOLVED",
    )
    changed = _snapshot(
        "receipt:2",
        "suite:2",
        "2026-07-16T00:07:00Z",
        "INCORRECT",
        "UNRESOLVED",
    )
    with pytest.raises(ValueError, match="terminal_status_changed"):
        build_future_outcome_persistence_diagnostics(
            maturation_snapshots=(first, changed),
            evaluated_at="2026-07-16T01:00:00Z",
        )


def test_snapshot_causality_and_duplicate_trace_fail_closed() -> None:
    future_snapshot = _snapshot(
        "receipt:1",
        "suite:1",
        "2026-07-16T02:00:00Z",
        "CORRECT",
        "INCORRECT",
    )
    with pytest.raises(ValueError, match="snapshot_after_evaluated_at"):
        build_future_outcome_persistence_diagnostics(
            maturation_snapshots=(future_snapshot,),
            evaluated_at="2026-07-16T01:00:00Z",
        )

    row_time_mismatch = _snapshot(
        "receipt:2",
        "suite:2",
        "2026-07-16T00:16:00Z",
        "CORRECT",
        "INCORRECT",
    )
    rows = list(row_time_mismatch["outcome_rows"])
    rows[0] = dict(rows[0], resolved_at="2026-07-16T00:17:00Z")
    row_time_mismatch["outcome_rows"] = tuple(rows)
    with pytest.raises(ValueError, match="row_polled_at_mismatch"):
        build_future_outcome_persistence_diagnostics(
            maturation_snapshots=(row_time_mismatch,),
            evaluated_at="2026-07-16T01:00:00Z",
        )

    duplicate_trace = _snapshot(
        "receipt:3",
        "suite:3",
        "2026-07-16T00:16:00Z",
        "CORRECT",
        "INCORRECT",
    )
    rows = list(duplicate_trace["outcome_rows"])
    rows[1] = dict(rows[1], trace_id=rows[0]["trace_id"])
    rows = tuple(sorted(rows, key=lambda row: row["trace_id"]))
    duplicate_trace["outcome_rows"] = rows
    duplicate_trace["trace_ids"] = tuple(row["trace_id"] for row in rows)
    with pytest.raises(ValueError, match="duplicate_trace_id"):
        build_future_outcome_persistence_diagnostics(
            maturation_snapshots=(duplicate_trace,),
            evaluated_at="2026-07-16T01:00:00Z",
        )


def test_duplicate_snapshot_and_tampered_trace_set_fail_closed() -> None:
    snapshot = _snapshot("receipt:1", "suite:1", "2026-07-16T00:16:00Z", "CORRECT", "INCORRECT")
    with pytest.raises(ValueError, match="duplicate_snapshot"):
        build_future_outcome_persistence_diagnostics(
            maturation_snapshots=(snapshot, snapshot),
            evaluated_at="2026-07-16T01:00:00Z",
        )
    tampered = deepcopy(snapshot)
    tampered["trace_ids"] = tuple(reversed(tampered["trace_ids"]))
    with pytest.raises(ValueError, match="trace_set_mismatch"):
        build_future_outcome_persistence_diagnostics(
            maturation_snapshots=(tampered,),
            evaluated_at="2026-07-16T01:00:00Z",
        )
