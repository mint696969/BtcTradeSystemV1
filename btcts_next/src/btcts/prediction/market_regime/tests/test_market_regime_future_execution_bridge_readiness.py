# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_execution_bridge_readiness.py
# desc: MR-F9.10 guards for read-only legacy-trace bridge readiness without inferred execution facts.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.future_execution_bridge_readiness import (
    audit_market_regime_trace_for_future_execution_bridge,
)
from btcts.prediction.market_regime.future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC

ACTIVE = "market_regime.future.transparent_baseline.params.v1"
SHADOW = "market_regime.future.transparent_baseline.params.conservative.v1"


def _safety():
    return {
        "scheduler_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_intent_submitted": False,
        "trade_ledger_append_allowed": False,
        "would_send_to_broker": False,
    }


def _legacy_trace():
    horizons = [
        {
            "horizon_sec": int(horizon),
            "horizon_key": f"h{horizon}",
            "parameter_set_id": ACTIVE,
            "confidence_percent": 72,
            "freshness_state": "fresh",
        }
        for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC
    ]
    return {
        "artifact_kind": "trace_row",
        "prediction_family_id": "market_regime",
        "run_id": "market_regime_20260716T020823Z_once",
        "generated_at": "2026-07-16T02:08:23Z",
        "source_refs": {"l1": "source:l1"},
        "prediction_summary": {"horizons": horizons},
        "safety": _safety(),
    }


def _ready_trace():
    trace = _legacy_trace()
    rows = []
    for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC:
        for candidate in (ACTIVE, SHADOW):
            rows.append({
                "horizon_sec": int(horizon),
                "parameter_set_id": candidate,
                "inference_mode": "FULL_INFERENCE",
                "raw_model_score_or_probability": 0.6,
                "raw_output_semantics": "SCORE",
                "source_freshness_state": "FRESH",
                "source_age_sec": 1.0,
                "abstention_decision": False,
                "abstain_reason": "",
                "fallback_used": False,
                "fallback_reason": "",
                "fallback_source_ref": "",
                "feature_snapshot_ref": "snapshot:1",
                "target_definition_version": "target:1",
                "forecast_status": "PREDICTED",
                "model_id": "model:1",
                "logic_version": "logic:1",
            })
    trace["prediction_summary"] = {"horizons": rows}
    return trace


def test_current_active_only_legacy_trace_is_blocked_without_inference() -> None:
    result = audit_market_regime_trace_for_future_execution_bridge(
        trace_row=_legacy_trace(),
        expected_active_parameter_set_id=ACTIVE,
        expected_shadow_parameter_set_id=SHADOW,
    )
    assert result["bridge_ready"] is False
    assert "active_only_runtime_trace" in result["blockers"]
    assert "paired_candidate_execution_missing" in result["blockers"]
    assert "expected_shadow_candidate_missing" in result["blockers"]
    assert "explicit_field_missing:raw_output_semantics" in result["blockers"]
    assert "legacy_confidence_is_not_raw_probability" in result["warnings"]
    assert result["facts_inferred_from_legacy_display"] is False
    assert result["legacy_confidence_promoted_to_probability"] is False


def test_explicit_paired_trace_is_ready() -> None:
    result = audit_market_regime_trace_for_future_execution_bridge(
        trace_row=_ready_trace(),
        expected_active_parameter_set_id=ACTIVE,
        expected_shadow_parameter_set_id=SHADOW,
    )
    assert result["bridge_ready"] is True
    assert result["blockers"] == ()
    assert result["expected_slot_count"] == len(FUTURE_MARKET_REGIME_HORIZONS_SEC) * 2
    assert result["observed_slot_count"] == len(FUTURE_MARKET_REGIME_HORIZONS_SEC) * 2
    assert result["missing_slots"] == ()
    assert result["unexpected_slots"] == ()
    assert result["would_build_evidence"] is True
    assert result["would_write"] is False


def test_missing_horizon_and_unsafe_trace_fail_readiness() -> None:
    trace = _ready_trace()
    trace["prediction_summary"]["horizons"] = [
        row for row in trace["prediction_summary"]["horizons"]
        if int(row["horizon_sec"]) != int(FUTURE_MARKET_REGIME_HORIZONS_SEC[-1])
    ]
    trace["safety"]["scheduler_enabled"] = True
    result = audit_market_regime_trace_for_future_execution_bridge(
        trace_row=trace,
        expected_active_parameter_set_id=ACTIVE,
        expected_shadow_parameter_set_id=SHADOW,
    )
    assert "canonical_future_horizon_set_missing" in result["blockers"]
    assert "unsafe_trace_flag:scheduler_enabled" in result["blockers"]


def test_partial_shadow_coverage_and_unexpected_candidate_are_blocked() -> None:
    partial = _ready_trace()
    partial["prediction_summary"]["horizons"] = [
        row
        for row in partial["prediction_summary"]["horizons"]
        if row["parameter_set_id"] != SHADOW
        or int(row["horizon_sec"]) == int(FUTURE_MARKET_REGIME_HORIZONS_SEC[0])
    ]
    partial_result = audit_market_regime_trace_for_future_execution_bridge(
        trace_row=partial,
        expected_active_parameter_set_id=ACTIVE,
        expected_shadow_parameter_set_id=SHADOW,
    )
    assert partial_result["bridge_ready"] is False
    assert "expected_future_candidate_slots_missing" in partial_result["blockers"]
    assert len(partial_result["missing_slots"]) == len(FUTURE_MARKET_REGIME_HORIZONS_SEC) - 1

    unexpected = _ready_trace()
    rows = list(unexpected["prediction_summary"]["horizons"])
    rows.append(dict(rows[0], parameter_set_id="candidate:unexpected"))
    unexpected["prediction_summary"]["horizons"] = rows
    unexpected_result = audit_market_regime_trace_for_future_execution_bridge(
        trace_row=unexpected,
        expected_active_parameter_set_id=ACTIVE,
        expected_shadow_parameter_set_id=SHADOW,
    )
    assert unexpected_result["bridge_ready"] is False
    assert "unexpected_future_candidate_slots_present" in unexpected_result["blockers"]


def test_duplicate_horizon_candidate_slot_is_blocked() -> None:
    trace = _ready_trace()
    rows = list(trace["prediction_summary"]["horizons"])
    rows.append(dict(rows[0]))
    trace["prediction_summary"]["horizons"] = rows
    result = audit_market_regime_trace_for_future_execution_bridge(
        trace_row=trace,
        expected_active_parameter_set_id=ACTIVE,
        expected_shadow_parameter_set_id=SHADOW,
    )
    assert result["bridge_ready"] is False
    assert "duplicate_future_candidate_slot" in result["blockers"]


def test_duplicate_candidate_identity_and_invalid_kind_fail_closed() -> None:
    with pytest.raises(ValueError, match="candidate_identity_duplicate"):
        audit_market_regime_trace_for_future_execution_bridge(
            trace_row=_legacy_trace(),
            expected_active_parameter_set_id=ACTIVE,
            expected_shadow_parameter_set_id=ACTIVE,
        )
    trace = _legacy_trace()
    trace["artifact_kind"] = "other"
    with pytest.raises(ValueError, match="trace_kind_invalid"):
        audit_market_regime_trace_for_future_execution_bridge(
            trace_row=trace,
            expected_active_parameter_set_id=ACTIVE,
            expected_shadow_parameter_set_id=SHADOW,
        )
