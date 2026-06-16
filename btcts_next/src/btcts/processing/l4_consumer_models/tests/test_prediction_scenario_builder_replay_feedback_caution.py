# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_scenario_builder_replay_feedback_caution.py
# desc: Verify replay feedback caution weighting stays adaptive, bidirectional and regime-gated.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (  # noqa: E402
    HealthDigest,
    MarketSummaryBuildInput,
    PredictionReplayFeedbackBuildInput,
    PredictionScenarioBuildInput,
    PredictionSystemBuildInput,
    build_market_summary,
    build_prediction_replay_feedback,
    build_prediction_scenario_output,
    build_prediction_system_input,
)


def _build_market_summary(*, interpretation_bucket: str) -> object:
    return build_market_summary(
        MarketSummaryBuildInput(
            market_state_row={
                "exchange": "bitflyer",
                "symbol": "BTC_JPY",
                "market_uid": "bitflyer.spot.BTC_JPY",
                "collector_ts": "2026-04-17T03:20:00Z",
                "trust_state": "trusted",
                "continuity_state": "continuous",
                "interpretation_bucket": interpretation_bucket,
                "interpretation_reason": "unit_test",
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
                "orderbook_semantics_summary": {
                    "summary_slots_present": ["near_wall"],
                    "active_event_count": 1,
                    "active_event_names": ["support_candidate"],
                    "active_event_contracts": [],
                },
                "orderbook_persistence_observable": True,
            },
            diagnostics={
                "source_kind": "market_state_preferred",
                "preferred_row_age_sec": 1.0,
                "preferred_row_freshness": "LIVE",
            },
        )
    )


def _build_health_digest_with_caution() -> HealthDigest:
    return HealthDigest(
        digest_type="health_digest",
        digest_version="v1alpha1",
        source_kind="unit_test",
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
        market_uid="bitflyer.spot.BTC_JPY",
        event_ts="2026-04-17T03:20:00Z",
        freshness="LIVE",
        is_stale=False,
        market_runtime={"interpretation_bucket": "allow_structural_use"},
        semantic_usage={"observer_status": "caution"},
    )


def main() -> int:
    fragile_input = build_prediction_system_input(
        PredictionSystemBuildInput(
            market_summary=_build_market_summary(
                interpretation_bucket="allow_structural_use"
            ),
            health_digest=_build_health_digest_with_caution(),
            regime_turning_point={
                "transition_sign": "weakening_continuation",
                "turning_point_risk": "medium",
            },
            replay_feedback=build_prediction_replay_feedback(
                PredictionReplayFeedbackBuildInput(
                    calibration_review={
                        "review_priority": "normal",
                        "primary_focus": "caution_overestimation_review",
                        "caution_review": "lower_caution_weight",
                    },
                    evaluation_report={
                        "entry_count": 2,
                        "average_caution_gap": -1.0,
                    },
                )
            ),
        )
    )
    fragile_output = build_prediction_scenario_output(
        PredictionScenarioBuildInput(prediction_input=fragile_input)
    )

    assert fragile_output.current_regime_state == "reversal_watch"
    assert fragile_output.current_caution_level == "medium"
    assert fragile_output.diagnostics["replay_feedback_caution_adjustment"] == 0
    assert fragile_output.diagnostics["replay_feedback_caution_adjustment_policy"] == (
        "gated_fragile_regime"
    )

    adaptive_input = build_prediction_system_input(
        PredictionSystemBuildInput(
            market_summary=_build_market_summary(interpretation_bucket="observe_only"),
            replay_feedback=build_prediction_replay_feedback(
                PredictionReplayFeedbackBuildInput(
                    calibration_review={
                        "review_priority": "normal",
                        "primary_focus": "caution_overestimation_review",
                        "caution_review": "lower_caution_weight",
                    },
                    evaluation_report={
                        "entry_count": 2,
                        "average_caution_gap": -1.0,
                    },
                )
            ),
        )
    )
    adaptive_output = build_prediction_scenario_output(
        PredictionScenarioBuildInput(prediction_input=adaptive_input)
    )

    assert adaptive_output.current_regime_state == "unstable"
    assert adaptive_output.current_caution_level == "low"
    assert round(adaptive_output.current_confidence, 2) == 0.25
    assert adaptive_output.diagnostics["replay_feedback_caution_adjustment"] == -1
    assert adaptive_output.diagnostics["replay_feedback_caution_adjustment_policy"] == (
        "lower_once"
    )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())