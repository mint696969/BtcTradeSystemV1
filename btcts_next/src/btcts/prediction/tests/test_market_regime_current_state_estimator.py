# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_current_state_estimator.py
# desc: MR-F2 guards true current-state estimation from current L4 candle evidence without forecast-label reuse.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime import FeatureGroup, FreshnessState, SourceCoverage  # noqa: E402
from btcts.prediction.market_regime.current_state_estimator import (  # noqa: E402
    CURRENT_STATE_ESTIMATOR_VERSION,
    estimate_current_market_regime,
)
from btcts.prediction.market_regime.features import FeatureSignal, MarketRegimeFeatureBundle  # noqa: E402


def _bundle(*, current_enough: bool, hint: str, cutoff: str) -> MarketRegimeFeatureBundle:
    signals = (
        FeatureSignal(
            feature_group=FeatureGroup.SOURCE_QUALITY,
            name="current_l4_candle_window_current_enough",
            value=current_enough,
            available=True,
            source_refs=("warroom_candles",),
        ),
        FeatureSignal(
            feature_group=FeatureGroup.SOURCE_QUALITY,
            name="current_l4_candle_window_generated_at",
            value=cutoff,
            available=bool(cutoff),
            source_refs=("warroom_candles",),
        ),
        FeatureSignal(
            feature_group=FeatureGroup.PRICE_STRUCTURE,
            name="current_l4_candle_regime_hint",
            value=hint,
            available=hint != "UNKNOWN",
            source_refs=("warroom_candles",),
        ),
        FeatureSignal(
            feature_group=FeatureGroup.PRICE_STRUCTURE,
            name="current_l4_candle_regime_reason",
            value="test_current_reason",
            available=True,
            source_refs=("warroom_candles",),
        ),
        FeatureSignal(
            feature_group=FeatureGroup.PRICE_STRUCTURE,
            name="current_l4_candle_threshold_set_id",
            value="thresholds-v1",
            available=True,
            source_refs=("active_parameter_set",),
        ),
        FeatureSignal(
            feature_group=FeatureGroup.PRICE_STRUCTURE,
            name="current_l4_candle_window_first_ts",
            value="2026-07-11T23:55:00Z",
            available=True,
            source_refs=("warroom_candles",),
        ),
        FeatureSignal(
            feature_group=FeatureGroup.PRICE_STRUCTURE,
            name="current_l4_candle_net_change_bps",
            value=18.0,
            available=True,
            source_refs=("warroom_candles",),
        ),
        FeatureSignal(
            feature_group=FeatureGroup.PRICE_STRUCTURE,
            name="current_l4_candle_range_bps",
            value=24.0,
            available=True,
            source_refs=("warroom_candles",),
        ),
        FeatureSignal(
            feature_group=FeatureGroup.PRICE_STRUCTURE,
            name="current_l4_candle_close_position",
            value=0.9,
            available=True,
            source_refs=("warroom_candles",),
        ),
        FeatureSignal(
            feature_group=FeatureGroup.VOLATILITY,
            name="current_l4_candle_realized_volatility_bps",
            value=3.5,
            available=True,
            source_refs=("warroom_candles",),
        ),
        FeatureSignal(
            feature_group=FeatureGroup.PRICE_STRUCTURE,
            name="market_regime_labels_by_horizon_sec",
            value={"15": "trend_candidate"},
            available=True,
            source_refs=("forecast_records",),
        ),
    )
    return MarketRegimeFeatureBundle(
        generated_at="2026-07-12T00:00:01Z",
        signals=signals,
        coverage=(
            SourceCoverage(
                feature_group=FeatureGroup.PRICE_STRUCTURE,
                available=True,
                freshness_state=FreshnessState.LIVE,
            ),
        ),
        source_snapshot_ok=True,
    )


def test_current_estimator_uses_current_l4_and_never_future_forecast_label() -> None:
    packet = estimate_current_market_regime(
        _bundle(
            current_enough=True,
            hint="RANGE",
            cutoff="2026-07-12T00:00:00Z",
        )
    )
    assert packet["ok"] is True
    assert packet["regime_label"] == "RANGE"
    assert packet["selection_reason"] == "current_state_estimator"
    assert packet["estimator_version"] == CURRENT_STATE_ESTIMATOR_VERSION
    assert packet["source_cutoff_time"] == "2026-07-12T00:00:00Z"
    assert packet["state_started_at"] == "2026-07-12T00:00:01Z"
    assert packet["state_age_sec"] == 0
    assert packet["state_start_estimation_status"] == "started"
    assert packet["state_transition_detected"] is False
    assert packet["previous_regime_code"] == "UNKNOWN"
    assert packet["state_window_started_at"] == "2026-07-11T23:55:00Z"
    assert packet["state_window_age_sec"] == 300
    assert packet["change_point_probability"] is None
    assert packet["change_point_probability_calibrated"] is False
    assert 0.0 <= packet["change_point_evidence_score"] <= 1.0
    assert packet["transition_candidate"] is True
    assert packet["transition_candidate_basis"] == "heuristic_change_point_evidence_score"
    assert packet["supporting_evidence"]["net_change_bps"] == 18.0
    assert packet["current_state_outcome_rule_version"] == "market_regime_current_state_outcome_rule.mr_f2.v1"
    assert packet["current_state_outcome_rule_defined"] is True
    assert packet["current_state_outcome_rule_gap"] == ""
    assert packet["future_forecast_label_used"] is False
    assert packet["label_source"] == "current_l4_candle_regime_hint"
    assert packet["candidate_scoring_version"] == "prediction.market_regime.feature_scoring.mr_f3.v1"
    assert set(packet["candidate_scores"]) == {
        "trend_score", "range_score", "breakout_score", "high_vol_chop_score",
        "compression_score", "reversal_score", "panic_score",
    }
    assert packet["top_candidate"]
    assert packet["top_candidate_score"] is not None
    assert "eligible_top_candidate" in packet
    assert "eligible_candidate_score_margin" in packet
    assert isinstance(packet["label_selection_eligible_candidates"], list)
    assert isinstance(packet["label_selection_ineligible_candidates"], dict)
    assert isinstance(packet["label_selection_readiness_blockers"], list)
    assert packet["scoring_label_selection_enabled"] is False
    assert packet["scoring_label_selection_deferred_reason"] == "mr_f3_observe_before_cutover"
    assert isinstance(packet["scoring_readiness_thresholds"]["required_feature_groups"], list)
    assert packet["would_send_to_broker"] is False


def test_current_estimator_fails_closed_when_current_evidence_is_not_live() -> None:
    packet = estimate_current_market_regime(
        _bundle(
            current_enough=False,
            hint="UP_TREND",
            cutoff="2026-07-11T23:00:00Z",
        )
    )
    assert packet["ok"] is False
    assert packet["regime_label"] == "UNKNOWN"
    assert packet["selection_reason"] == "current_state_estimator_unavailable"
    assert packet["state_started_at"] == ""
    assert packet["state_age_sec"] is None
    assert packet["state_window_started_at"] == ""
    assert packet["state_window_age_sec"] is None
    assert packet["change_point_probability"] is None
    assert packet["change_point_probability_calibrated"] is False
    assert packet["change_point_evidence_score"] == 0.0
    assert packet["transition_candidate"] is False
    assert packet["supporting_evidence"] == {}
    assert packet["future_forecast_label_used"] is False
