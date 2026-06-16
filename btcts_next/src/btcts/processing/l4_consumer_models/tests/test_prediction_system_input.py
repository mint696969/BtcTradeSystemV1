# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_system_input.py
# desc: Verify PredictionSystemInput thin builder stays market_summary-anchored and additive.

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
    PredictionSystemBuildInput,
    build_market_summary,
    build_prediction_replay_feedback,
    build_prediction_system_input,
)


def main() -> int:
    market_summary = build_market_summary(
        MarketSummaryBuildInput(
            market_state_row={
                "exchange": "bitflyer",
                "symbol": "BTC_JPY",
                "market_uid": "bitflyer.spot.BTC_JPY",
                "collector_ts": "2026-04-17T03:10:00Z",
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
                    "summary_slots_present": ["near_wall", "support"],
                    "active_event_count": 1,
                    "active_event_names": ["support_candidate"],
                    "active_event_contracts": [],
                },
                "orderbook_persistence_observable": True,
            },
            diagnostics={
                "source_kind": "market_state_preferred",
                "preferred_row_age_sec": 4.0,
                "preferred_row_freshness": "LIVE",
            },
        )
    )

    health_digest = HealthDigest(
        digest_type="health_digest",
        digest_version="v1alpha1",
        source_kind="health_data_service",
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
        market_uid="bitflyer.spot.BTC_JPY.health",
        event_ts="2026-04-17T03:09:00Z",
        freshness="STALE",
        is_stale=True,
        market_runtime={"interpretation_bucket": "observe_only"},
        semantic_usage={"observer_status": "caution"},
        orderbook_runtime={"wiring_status": "partial"},
        diagnostics={},
    )

    built = build_prediction_system_input(
        PredictionSystemBuildInput(
            market_summary=market_summary,
            health_digest=health_digest,
            requested_horizons=("10m", "30m", "10m", "bad"),
            replay_feedback=build_prediction_replay_feedback(
                PredictionReplayFeedbackBuildInput(
                    calibration_review={
                        "review_priority": "high",
                        "primary_focus": "confidence_downside_review",
                    },
                    evaluation_report={
                        "entry_count": 3,
                        "average_confidence_gap": -0.18,
                        "average_caution_gap": 1.0,
                    },
                    diagnostics={"source": "unit_test"},
                )
            ),
            external_context={"operator_mode": "paper"},
            diagnostics={"caller": "unit_test"},
        )
    )

    assert built.system_type == "prediction_system_input"
    assert built.system_version == "phase3.v1alpha1"
    assert built.source_kind == "market_summary_anchor"
    assert built.market_uid == "bitflyer.spot.BTC_JPY"
    assert built.event_ts == "2026-04-17T03:10:00Z"
    assert built.freshness == "LIVE"
    assert built.is_stale is False
    assert built.requested_horizons == ("10m", "30m")

    assert built.evidence_bundle.market_summary == market_summary
    assert built.evidence_bundle.health_digest == health_digest
    assert built.evidence_bundle.liquidity_board_history["evidence_type"] == (
        "prediction_liquidity_board_history"
    )
    assert built.evidence_bundle.liquidity_board_history["source_kind"] == (
        "market_summary_anchor"
    )
    assert built.evidence_bundle.liquidity_board_history["market_uid"] == (
        "bitflyer.spot.BTC_JPY"
    )
    assert built.evidence_bundle.liquidity_board_history["event_ts"] == (
        "2026-04-17T03:10:00Z"
    )
    assert built.evidence_bundle.liquidity_board_history["history_window_sec"] == 120
    assert built.evidence_bundle.liquidity_board_history["liquidity_pressure_balance"] == (
        "bid_support"
    )
    assert built.evidence_bundle.liquidity_board_history["wall_persistence_bias"] == (
        "bid_support"
    )
    assert built.evidence_bundle.liquidity_board_history["persistence_confidence"] == "low"
    assert built.evidence_bundle.regime_turning_point["evidence_type"] == (
        "prediction_regime_turning_point"
    )
    assert built.evidence_bundle.regime_turning_point["source_kind"] == (
        "market_summary_anchor"
    )
    assert built.evidence_bundle.regime_turning_point["market_uid"] == (
        "bitflyer.spot.BTC_JPY"
    )
    assert built.evidence_bundle.regime_turning_point["event_ts"] == (
        "2026-04-17T03:10:00Z"
    )
    assert built.evidence_bundle.regime_turning_point["transition_sign"] == (
        "weakening_continuation"
    )
    assert built.evidence_bundle.regime_turning_point["turning_point_risk"] == "high"
    assert built.evidence_bundle.regime_turning_point["continuity_bias"] == "fragile"
    assert built.evidence_bundle.external_context["operator_mode"] == "paper"
    assert built.evidence_bundle.external_context["replay_feedback"]["feedback_type"] == (
        "prediction_replay_feedback"
    )
    assert built.evidence_bundle.external_context["replay_feedback"]["review_priority"] == (
        "high"
    )
    assert built.evidence_bundle.external_context["replay_feedback"]["primary_focus"] == (
        "confidence_downside_review"
    )
    assert built.evidence_bundle.external_context["replay_feedback"]["entry_count"] == 3
    assert built.evidence_bundle.external_context["replay_feedback"]["average_confidence_gap"] == (
        -0.18
    )
    assert built.evidence_bundle.external_context["replay_feedback"]["diagnostics"][
        "builder_type"
    ] == "prediction_replay_feedback"
    assert built.evidence_bundle.position_context == {}

    assert built.evidence_trace.active_families == (
        "market_summary_anchor",
        "liquidity_board_history",
        "regime_turning_point",
        "health_digest_caution",
    )
    assert built.evidence_trace.missing_families == ()
    assert built.evidence_trace.caution_flags == ("health_digest_stale",)
    assert built.evidence_trace.diagnostics["builder_type"] == "prediction_system_input"
    assert built.evidence_trace.diagnostics["caller"] == "unit_test"

    assert built.diagnostics["builder_type"] == "prediction_system_input"
    assert built.diagnostics["market_summary_present"] is True
    assert built.diagnostics["health_digest_present"] is True
    assert built.diagnostics["caller"] == "unit_test"

    blocked = build_prediction_system_input(PredictionSystemBuildInput())
    assert blocked.market_uid is None
    assert blocked.event_ts is None
    assert blocked.freshness == "UNKNOWN"
    assert blocked.is_stale is None
    assert blocked.requested_horizons == ("5m", "10m", "30m")
    assert blocked.evidence_trace.active_families == ()
    assert blocked.evidence_trace.missing_families == (
        "market_summary_anchor",
        "liquidity_board_history",
        "regime_turning_point",
    )
    assert blocked.evidence_trace.caution_flags == ("market_summary_absent",)

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())