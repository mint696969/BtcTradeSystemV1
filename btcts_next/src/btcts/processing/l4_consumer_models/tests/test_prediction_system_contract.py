# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_system_contract.py
# desc: Verify Prediction System contract skeleton stays shared-first, additive, and horizon-separated.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (  # noqa: E402
    PredictionCalibrationHint,
    PredictionEvidenceBundle,
    PredictionEvidenceTrace,
    PredictionScenarioHorizonOutput,
    PredictionScenarioOutput,
    PredictionSystemInput,
)


def main() -> int:
    default_input = PredictionSystemInput()

    assert default_input.system_type == "prediction_system_input"
    assert default_input.system_version == "phase3.v1alpha1"
    assert default_input.source_kind == "market_summary_anchor"
    assert default_input.market_uid is None
    assert default_input.event_ts is None
    assert default_input.freshness == "UNKNOWN"
    assert default_input.is_stale is None
    assert default_input.requested_horizons == ("5m", "10m", "30m")
    assert default_input.evidence_bundle.market_summary is None
    assert default_input.evidence_bundle.health_digest is None
    assert default_input.evidence_bundle.liquidity_board_history == {}
    assert default_input.evidence_trace.active_families == ()
    assert default_input.evidence_trace.missing_families == ()

    evidence_bundle = PredictionEvidenceBundle(
        liquidity_board_history={
            "history_window_sec": 120,
            "wall_persistence_bias": "bid_support",
        },
        regime_turning_point={
            "transition_sign": "weakening_continuation",
            "turning_point_risk": "medium",
        },
    )
    evidence_trace = PredictionEvidenceTrace(
        active_families=("market_summary_anchor", "liquidity_board_history"),
        missing_families=("regime_turning_point",),
        caution_flags=("health_digest_absent",),
        evidence_refs=("market_summary:event_ts", "board_history:window_120s"),
        diagnostics={"trace_source": "skeleton_test"},
    )
    scenario_output = PredictionScenarioOutput(
        market_uid="bitflyer.spot.BTC_JPY",
        event_ts="2026-04-17T03:00:00Z",
        freshness="LIVE",
        is_stale=False,
        current_regime_state="continuation",
        current_hypothesis_health="stable",
        current_confidence=0.62,
        current_caution_level="low",
        outlooks=(
            PredictionScenarioHorizonOutput(
                horizon="5m",
                regime_bias="continuation",
                continuation_likelihood="high",
                reversal_likelihood="low",
                turning_point_risk="low",
                confidence=0.66,
                caution_level="low",
            ),
            PredictionScenarioHorizonOutput(
                horizon="10m",
                regime_bias="continuation",
                continuation_likelihood="medium",
                reversal_likelihood="medium",
                turning_point_risk="medium",
                confidence=0.55,
                caution_level="medium",
            ),
        ),
        invalidation_state="caution_increase",
        invalidation_signals=("continuity_weakening",),
        scenario_switch_hint="watch_reversal_path",
        scenario_trace={
            "trace_type": "prediction_scenario_trace",
            "trace_version": "phase3.v1alpha1",
            "regime_decision": "continuation_path",
            "hypothesis_health_path": "stable",
            "caution_path": "low",
            "invalidation_path": "caution_increase",
            "switch_reason": "watch_reversal_path",
        },
        evidence={
            "market_summary_anchor_present": True,
            "health_digest_present": False,
        },
        evidence_trace=evidence_trace,
        diagnostics={"skeleton_only": True},
    )

    assert evidence_bundle.liquidity_board_history["history_window_sec"] == 120
    assert evidence_bundle.regime_turning_point["turning_point_risk"] == "medium"

    assert scenario_output.prediction_type == "prediction_scenario_output"
    assert scenario_output.prediction_version == "phase3.v1alpha1"
    assert scenario_output.market_uid == "bitflyer.spot.BTC_JPY"
    assert scenario_output.current_regime_state == "continuation"
    assert scenario_output.current_hypothesis_health == "stable"
    assert scenario_output.current_confidence == 0.62
    assert scenario_output.current_caution_level == "low"
    assert len(scenario_output.outlooks) == 2
    assert scenario_output.outlooks[0].horizon == "5m"
    assert scenario_output.outlooks[0].regime_bias == "continuation"
    assert scenario_output.outlooks[1].turning_point_risk == "medium"
    assert scenario_output.invalidation_state == "caution_increase"
    assert scenario_output.invalidation_signals == ("continuity_weakening",)
    assert scenario_output.scenario_switch_hint == "watch_reversal_path"
    assert scenario_output.scenario_trace["trace_type"] == "prediction_scenario_trace"
    assert scenario_output.scenario_trace["trace_version"] == "phase3.v1alpha1"
    assert scenario_output.scenario_trace["regime_decision"] == "continuation_path"
    assert scenario_output.scenario_trace["hypothesis_health_path"] == "stable"
    assert scenario_output.scenario_trace["invalidation_path"] == "caution_increase"
    assert scenario_output.scenario_trace["switch_reason"] == "watch_reversal_path"
    assert scenario_output.evidence["market_summary_anchor_present"] is True
    assert scenario_output.evidence_trace.active_families == (
        "market_summary_anchor",
        "liquidity_board_history",
    )
    assert scenario_output.evidence_trace.missing_families == (
        "regime_turning_point",
    )
    assert scenario_output.evidence_trace.caution_flags == (
        "health_digest_absent",
    )

    calibration_hint = PredictionCalibrationHint(
        confidence_bias="slightly_overstated",
        caution_bias="understated_transition_risk",
        invalidation_sensitivity="slow",
        replay_priority="high",
        diagnostics={"origin": "replay_review"},
    )
    assert calibration_hint.hint_type == "prediction_calibration_hint"
    assert calibration_hint.hint_version == "phase3.v1alpha1"
    assert calibration_hint.confidence_bias == "slightly_overstated"
    assert calibration_hint.caution_bias == "understated_transition_risk"
    assert calibration_hint.invalidation_sensitivity == "slow"
    assert calibration_hint.replay_priority == "high"
    assert calibration_hint.diagnostics["origin"] == "replay_review"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())