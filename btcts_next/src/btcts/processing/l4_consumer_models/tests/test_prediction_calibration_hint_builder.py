# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_calibration_hint_builder.py
# desc: Verify PredictionCalibrationHint thin builder stays shared-first and scenario-output based.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (  # noqa: E402
    MarketSummaryBuildInput,
    PredictionCalibrationBuildInput,
    PredictionSystemBuildInput,
    PredictionScenarioBuildInput,
    build_market_summary,
    build_prediction_calibration_hint,
    build_prediction_scenario_output,
    build_prediction_system_input,
)


def main() -> int:
    market_summary = build_market_summary(
        MarketSummaryBuildInput(
            market_state_row={
                "exchange": "bitflyer",
                "symbol": "BTC_JPY",
                "market_uid": "bitflyer.spot.BTC_JPY",
                "collector_ts": "2026-04-17T04:10:00Z",
                "trust_state": "trusted",
                "continuity_state": "continuous",
                "interpretation_bucket": "allow_structural_use",
                "interpretation_reason": "ok",
                "semantic_observer_status": "healthy",
                "semantic_usage_summary": {
                    "source_kind": "market_state_semantic_usage_summary",
                    "contract_source": "l3_event_usage_policy",
                    "meaning_version": "l3_event_usage_policy.v1alpha1",
                    "observer_status": "healthy",
                    "active_event_count": 1,
                    "mapped_event_count": 1,
                    "unknown_event_count": 0,
                },
                "semantic_usage_contract_rows": [
                    {
                        "event_family": "wall",
                        "usage_grade": "strong",
                        "contract_source": "l3_event_usage_policy",
                        "meaning_version": "l3_event_usage_policy.v1alpha1",
                        "interpretation_bucket": "allow_structural_use",
                    }
                ],
                "orderbook_semantics_summary": {
                    "summary_slots_present": ["near_wall", "support", "persistence"],
                    "active_event_count": 1,
                    "active_event_names": ["support_candidate"],
                    "active_event_contracts": [],
                },
                "orderbook_persistence_observable": True,
            },
            diagnostics={
                "source_kind": "market_state_preferred",
                "preferred_row_age_sec": 3.0,
                "preferred_row_freshness": "LIVE",
            },
        )
    )

    prediction_input = build_prediction_system_input(
        PredictionSystemBuildInput(
            market_summary=market_summary,
            liquidity_board_history={
                "history_window_sec": 90,
                "wall_persistence_bias": "bid_support",
            },
            regime_turning_point={
                "transition_sign": "weakening_continuation",
                "turning_point_risk": "medium",
            },
        )
    )
    scenario_output = build_prediction_scenario_output(
        PredictionScenarioBuildInput(
            prediction_input=prediction_input,
        )
    )

    calibration_hint = build_prediction_calibration_hint(
        PredictionCalibrationBuildInput(
            prediction_input=prediction_input,
            scenario_output=scenario_output,
            diagnostics={"caller": "unit_test"},
        )
    )

    assert calibration_hint.hint_type == "prediction_calibration_hint"
    assert calibration_hint.hint_version == "phase3.v1alpha1"
    assert calibration_hint.confidence_bias == "balanced"
    assert calibration_hint.caution_bias == "balanced"
    assert calibration_hint.invalidation_sensitivity == "medium"
    assert calibration_hint.replay_priority == "high"
    assert calibration_hint.diagnostics["builder_type"] == "prediction_calibration_hint"
    assert calibration_hint.diagnostics["active_family_count"] == 3
    assert calibration_hint.diagnostics["missing_family_count"] == 0
    assert calibration_hint.diagnostics["caution_flag_count"] == 0
    assert calibration_hint.diagnostics["caller"] == "unit_test"

    unknown = build_prediction_calibration_hint(PredictionCalibrationBuildInput())
    assert unknown.hint_type == "prediction_calibration_hint"
    assert unknown.hint_version == "phase3.v1alpha1"
    assert unknown.confidence_bias == "unknown"
    assert unknown.caution_bias == "unknown"
    assert unknown.invalidation_sensitivity == "unknown"
    assert unknown.replay_priority == "normal"
    assert unknown.diagnostics["builder_type"] == "prediction_calibration_hint"
    assert unknown.diagnostics["active_family_count"] == 0
    assert unknown.diagnostics["missing_family_count"] == 0
    assert unknown.diagnostics["caution_flag_count"] == 0

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())