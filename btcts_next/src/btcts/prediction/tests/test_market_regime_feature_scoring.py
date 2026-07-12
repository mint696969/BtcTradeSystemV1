# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_feature_scoring.py
# desc: MR-F3 guards seven explainable candidate scores, six-group decomposition, parameterized weights, and explicit missing/blocker semantics.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime import FeatureGroup, FreshnessState, SourceCoverage  # noqa: E402
from btcts.prediction.market_regime.feature_scoring import (  # noqa: E402
    CANDIDATE_NAMES,
    score_market_regime_candidates,
    summarize_market_regime_candidate_scores,
)
from btcts.prediction.market_regime.features import FeatureSignal, MarketRegimeFeatureBundle  # noqa: E402
from btcts.prediction.market_regime.parameter_set import build_default_market_regime_parameter_set  # noqa: E402


def _bundle(*, current_enough: bool = True, include_orderflow: bool = True) -> MarketRegimeFeatureBundle:
    signals = [
        FeatureSignal(FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_current_enough", current_enough, True),
        FeatureSignal(FeatureGroup.SOURCE_QUALITY, "source_quality_score", 0.9, True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_net_change_bps", 30.0, True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_range_bps", 40.0, True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_close_position", 0.9, True),
        FeatureSignal(FeatureGroup.VOLATILITY, "current_l4_candle_realized_volatility_bps", 18.0, True),
        FeatureSignal(FeatureGroup.VOLATILITY, "current_l4_candle_average_range_bps", 16.0, True),
        FeatureSignal(FeatureGroup.LIQUIDITY, "spread_bps", 2.0, True),
        FeatureSignal(FeatureGroup.LIQUIDITY, "crossed_or_negative_spread", False, True),
        FeatureSignal(FeatureGroup.LIQUIDITY, "depth_imbalance", 0.4, True),
        FeatureSignal(FeatureGroup.LIQUIDITY, "liquidity_disappearance_score", 0.7, True),
        FeatureSignal(FeatureGroup.LIQUIDITY, "liquidity_replenishment_score", 0.3, True),
        FeatureSignal(FeatureGroup.CROSS_VENUE, "cross_venue_agreement", "aligned", True),
    ]
    if include_orderflow:
        signals.extend((
            FeatureSignal(FeatureGroup.ORDERFLOW, "orderflow_imbalance", 0.65, True),
            FeatureSignal(FeatureGroup.ORDERFLOW, "volume_acceleration", 0.7, True),
        ))
    return MarketRegimeFeatureBundle(
        generated_at="2026-07-12T01:00:00Z",
        signals=tuple(signals),
        coverage=tuple(
            SourceCoverage(group, True, FreshnessState.LIVE)
            for group in FeatureGroup
        ),
        source_snapshot_ok=True,
    )


def test_mr_f3_emits_all_candidates_with_six_group_decomposition() -> None:
    packet = score_market_regime_candidates(_bundle())
    assert packet["ok"] is True
    assert tuple(packet["candidate_scores"]) == CANDIDATE_NAMES
    for row in packet["candidate_scores"].values():
        assert row["score_status"] == "available"
        assert 0.0 <= row["score"] <= 1.0
        assert len(row["contributions"]) == 6
        assert {item["feature_group"] for item in row["contributions"]} == {group.value for group in FeatureGroup}
    assert packet["missing_feature_is_zero_evidence"] is False
    assert packet["would_send_to_broker"] is False


def test_mr_f3_missing_group_is_not_silently_zero() -> None:
    packet = score_market_regime_candidates(_bundle(include_orderflow=False))
    trend = packet["candidate_scores"]["trend_score"]
    orderflow = next(item for item in trend["contributions"] if item["feature_group"] == "orderflow")
    assert orderflow["status"] == "missing"
    assert orderflow["raw_support"] is None
    assert orderflow["weighted_support"] is None
    assert "orderflow" in trend["missing_feature_groups"]
    assert trend["score"] is not None


def test_mr_f3_stale_current_window_blocks_scores() -> None:
    packet = score_market_regime_candidates(_bundle(current_enough=False))
    assert packet["ok"] is False
    assert packet["blockers"] == ["current_l4_candle_window_not_current"]
    assert all(row["score"] is None and row["score_status"] == "blocked" for row in packet["candidate_scores"].values())


def test_mr_f3_weights_and_thresholds_are_parameter_set_fields() -> None:
    params = build_default_market_regime_parameter_set()
    assert set(params.weights) == {group.value for group in FeatureGroup}
    scoring = params.thresholds["explainable_candidate_scoring"]
    assert scoring["volatility_reference_bps"] > 0
    assert scoring["spread_stress_bps"] > 0
    assert 0 <= scoring["contradictory_support_max"] <= 1


def test_mr_f3_summary_ranks_candidates_and_keeps_cutover_disabled() -> None:
    packet = score_market_regime_candidates(_bundle())
    summary = summarize_market_regime_candidate_scores(packet)
    assert summary["top_candidate"] in CANDIDATE_NAMES
    assert summary["top_candidate_score"] is not None
    assert summary["runner_up_candidate"] in CANDIDATE_NAMES
    assert summary["score_margin"] is not None
    assert len(summary["top_candidate_contributions"]) == 6
    assert summary["label_selection_enabled"] is False
    assert summary["label_selection_deferred_reason"] == "mr_f3_observe_before_cutover"


def test_mr_f3_ranking_excludes_candidates_below_available_weight() -> None:
    bundle = _bundle(include_orderflow=False)
    signals = tuple(
        signal for signal in bundle.signals
        if signal.feature_group is not FeatureGroup.CROSS_VENUE
        and signal.name != "liquidity_replenishment_score"
    )
    dhot_like_missing = MarketRegimeFeatureBundle(
        generated_at=bundle.generated_at,
        signals=signals,
        coverage=bundle.coverage,
        source_snapshot_ok=True,
    )
    packet = score_market_regime_candidates(dhot_like_missing)
    summary = summarize_market_regime_candidate_scores(packet)
    compression = packet["candidate_scores"]["compression_score"]
    assert compression["available_weight"] == 0.53
    assert compression["missing_feature_groups"] == [
        "liquidity",
        "orderflow",
        "cross_venue",
    ]
    assert "compression_score" in summary["label_selection_ineligible_candidates"]
    assert "available_weight_below_minimum" in summary["label_selection_ineligible_candidates"]["compression_score"]
    assert "compression_score" not in summary["label_selection_eligible_candidates"]


def test_mr_f3_missing_required_group_blocks_label_selection_eligibility() -> None:
    bundle = _bundle()
    signals = tuple(
        signal for signal in bundle.signals
        if signal.feature_group is not FeatureGroup.LIQUIDITY
    )
    without_liquidity = MarketRegimeFeatureBundle(
        generated_at=bundle.generated_at,
        signals=signals,
        coverage=bundle.coverage,
        source_snapshot_ok=True,
    )
    packet = score_market_regime_candidates(without_liquidity)
    summary = summarize_market_regime_candidate_scores(packet)
    assert all(
        any(reason == "required_feature_group_missing:liquidity" for reason in reasons)
        for reasons in summary["label_selection_ineligible_candidates"].values()
    )
    assert summary["scoring_ready_for_label_selection"] is False
    assert "no_label_selection_eligible_candidate" in summary["label_selection_readiness_blockers"]


def test_mr_f3_observed_top_survives_when_no_candidate_is_label_eligible() -> None:
    bundle = _bundle()
    signals = tuple(
        signal for signal in bundle.signals
        if signal.feature_group is not FeatureGroup.LIQUIDITY
    )
    packet = score_market_regime_candidates(
        MarketRegimeFeatureBundle(
            generated_at=bundle.generated_at,
            signals=signals,
            coverage=bundle.coverage,
            source_snapshot_ok=True,
        )
    )
    summary = summarize_market_regime_candidate_scores(packet)
    assert summary["top_candidate"] in CANDIDATE_NAMES
    assert summary["top_candidate_score"] is not None
    assert summary["eligible_top_candidate"] == ""
    assert summary["eligible_top_candidate_score"] is None
    assert summary["eligible_score_margin"] is None
    assert summary["scoring_ready_for_label_selection"] is False
