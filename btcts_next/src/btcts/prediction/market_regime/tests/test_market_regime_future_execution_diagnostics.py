# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_execution_diagnostics.py
# desc: MR-F9.7 guards for multi-origin execution diagnostics without probability or promotion claims.

from __future__ import annotations

from copy import deepcopy

import pytest

from btcts.prediction.market_regime.future_execution_diagnostics import build_future_execution_diagnostics


def _plan(origin: str, suite_id: str, raw_shift: float = 0.0, stale: bool = False):
    rows = []
    for horizon in (300, 900):
        for candidate, mode, fallback in (
            ("active", "FULL_INFERENCE", False),
            ("shadow", "FALLBACK", True),
        ):
            trace_id = f"trace:{origin}:{horizon}:{candidate}"
            rows.append({
                "trace_id": trace_id,
                "prediction_origin": origin,
                "generated_at": origin,
                "target_horizon_sec": horizon,
                "parameter_set_id": candidate,
                "inference_mode": mode,
                "raw_model_score_or_probability": 0.5 + raw_shift if candidate == "active" else 0.4,
                "raw_output_semantics": "SCORE",
                "source_freshness_state": "STALE" if stale else "FRESH",
                "source_age_sec": 2.0,
                "abstention_decision": False,
                "fallback_used": fallback,
            })
    rows = tuple(sorted(rows, key=lambda row: row["trace_id"]))
    return {
        "artifact_kind": "future_shadow_origin_execution_evidence_set",
        "generated_at": origin,
        "suite_id": suite_id,
        "evidence_count": len(rows),
        "trace_ids": tuple(row["trace_id"] for row in rows),
        "rows": rows,
    }


def test_multi_origin_rates_and_fixed_output_diagnostic() -> None:
    result = build_future_execution_diagnostics(
        execution_evidence_plans=(
            _plan("2026-07-16T00:00:00Z", "suite:1"),
            _plan("2026-07-16T00:05:00Z", "suite:2"),
        ),
        evaluated_at="2026-07-16T01:00:00Z",
    )
    assert result["origin_count"] == 2
    assert result["trace_count"] == 8
    active_300 = next(
        item for item in result["summaries"]
        if item["target_horizon_sec"] == 300 and item["parameter_set_id"] == "active"
    )
    shadow_300 = next(
        item for item in result["summaries"]
        if item["target_horizon_sec"] == 300 and item["parameter_set_id"] == "shadow"
    )
    assert active_300["full_inference_rate"] == 1.0
    assert active_300["fixed_raw_output_across_origins"] is True
    assert shadow_300["fallback_rate"] == 1.0
    assert result["probability_metrics_computed"] is False


def test_raw_output_change_breaks_fixed_output_flag() -> None:
    result = build_future_execution_diagnostics(
        execution_evidence_plans=(
            _plan("2026-07-16T00:00:00Z", "suite:1"),
            _plan("2026-07-16T00:05:00Z", "suite:2", raw_shift=0.1),
        ),
        evaluated_at="2026-07-16T01:00:00Z",
    )
    active = next(item for item in result["summaries"] if item["parameter_set_id"] == "active")
    assert active["fixed_raw_output_across_origins"] is False
    assert active["raw_output_unique_count"] == 2


def test_stale_recurrence_is_counted() -> None:
    result = build_future_execution_diagnostics(
        execution_evidence_plans=(
            _plan("2026-07-16T00:00:00Z", "suite:1"),
            _plan("2026-07-16T00:05:00Z", "suite:2", stale=True),
        ),
        evaluated_at="2026-07-16T01:00:00Z",
    )
    assert all(item["stale_or_nonfresh_rate"] == 0.5 for item in result["summaries"])


def test_duplicate_slot_origin_mismatch_and_slot_set_mismatch_fail_closed() -> None:
    duplicate_slot = deepcopy(_plan("2026-07-16T00:00:00Z", "suite:1"))
    rows = list(duplicate_slot["rows"])
    copied = dict(rows[0])
    copied["trace_id"] = "trace:duplicate-slot"
    rows.append(copied)
    rows = tuple(sorted(rows, key=lambda row: row["trace_id"]))
    duplicate_slot["rows"] = rows
    duplicate_slot["trace_ids"] = tuple(row["trace_id"] for row in rows)
    duplicate_slot["evidence_count"] = len(rows)
    with pytest.raises(ValueError, match="duplicate_slot"):
        build_future_execution_diagnostics(
            execution_evidence_plans=(duplicate_slot,),
            evaluated_at="2026-07-16T01:00:00Z",
        )

    origin_mismatch = deepcopy(_plan("2026-07-16T00:00:00Z", "suite:1"))
    rows = list(origin_mismatch["rows"])
    rows[0] = dict(rows[0], prediction_origin="2026-07-16T00:05:00Z")
    origin_mismatch["rows"] = tuple(rows)
    with pytest.raises(ValueError, match="row_origin_mismatch"):
        build_future_execution_diagnostics(
            execution_evidence_plans=(origin_mismatch,),
            evaluated_at="2026-07-16T01:00:00Z",
        )

    complete = _plan("2026-07-16T00:00:00Z", "suite:1")
    incomplete = deepcopy(_plan("2026-07-16T00:05:00Z", "suite:2"))
    rows = tuple(row for row in incomplete["rows"] if row["parameter_set_id"] != "shadow")
    incomplete["rows"] = rows
    incomplete["trace_ids"] = tuple(row["trace_id"] for row in rows)
    incomplete["evidence_count"] = len(rows)
    with pytest.raises(ValueError, match="slot_set_mismatch"):
        build_future_execution_diagnostics(
            execution_evidence_plans=(complete, incomplete),
            evaluated_at="2026-07-16T01:00:00Z",
        )


def test_duplicate_trace_and_tampered_trace_set_fail_closed() -> None:
    first = _plan("2026-07-16T00:00:00Z", "suite:1")
    duplicate = deepcopy(first)
    duplicate["generated_at"] = "2026-07-16T00:05:00Z"
    duplicate["suite_id"] = "suite:2"
    with pytest.raises(ValueError, match="duplicate_trace_id"):
        build_future_execution_diagnostics(
            execution_evidence_plans=(first, duplicate),
            evaluated_at="2026-07-16T01:00:00Z",
        )
    tampered = deepcopy(first)
    tampered["trace_ids"] = tuple(reversed(tampered["trace_ids"]))
    with pytest.raises(ValueError, match="trace_set_mismatch"):
        build_future_execution_diagnostics(
            execution_evidence_plans=(tampered,),
            evaluated_at="2026-07-16T01:00:00Z",
        )
