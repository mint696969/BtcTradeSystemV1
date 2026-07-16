# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_origin_feature_candidate_scoring.py
# desc: MR-F9.18A8 guards that origin-feature candidates influence scoring through calculated facts, not candidate IDs or arbitrary multipliers.

from __future__ import annotations

from btcts.prediction.market_regime.contracts import EvidenceQuality, FeatureGroup, FreshnessState, SourceCoverage
from btcts.prediction.market_regime.features.feature_bundle import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.signal_scoring import score_market_regime_signals


def _bundle() -> MarketRegimeFeatureBundle:
    return MarketRegimeFeatureBundle(
        generated_at="2026-07-16T10:00:00Z",
        signals=(
            FeatureSignal(FeatureGroup.SOURCE_QUALITY, "source_quality_score", 1.0, True, source_refs=("quality",)),
            FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_regime_hint", "RANGE", True, source_refs=("candles",)),
        ),
        coverage=(
            SourceCoverage(FeatureGroup.SOURCE_QUALITY, True, FreshnessState.LIVE),
            SourceCoverage(FeatureGroup.PRICE_STRUCTURE, True, FreshnessState.LIVE),
            SourceCoverage(FeatureGroup.VOLATILITY, True, FreshnessState.LIVE),
        ),
        source_snapshot_ok=True,
    )


def _context(candidate_id: str, fast: float, slow: float, fast_window: int, slow_window: int):
    return {
        "shadow_candidate_id": candidate_id,
        "calculated_features": {
            "fast_ma": fast,
            "slow_ma": slow,
            "fast_ma_window_rows": fast_window,
            "slow_ma_window_rows": slow_window,
            "realized_volatility_bps": 6.0,
            "low_volatility_threshold_bps": 4.0,
            "high_volatility_threshold_bps": 9.0,
        },
    }


def test_candidate_calculated_features_change_score_distribution() -> None:
    fast = score_market_regime_signals(_bundle(), origin_feature_context=_context("fast", 101.0, 100.0, 3, 10))
    slow = score_market_regime_signals(_bundle(), origin_feature_context=_context("slow", 100.2, 100.0, 15, 60))
    fast_rows = {x["horizon_key"]: x for x in fast["horizons"]}
    slow_rows = {x["horizon_key"]: x for x in slow["horizons"]}
    assert fast_rows["300s"]["regime_scores"] != slow_rows["300s"]["regime_scores"]
    assert fast_rows["86400s"]["regime_scores"] != slow_rows["86400s"]["regime_scores"]


def test_candidate_id_alone_does_not_change_scores() -> None:
    a = score_market_regime_signals(_bundle(), origin_feature_context=_context("candidate-a", 101.0, 100.0, 3, 10))
    b = score_market_regime_signals(_bundle(), origin_feature_context=_context("candidate-b", 101.0, 100.0, 3, 10))
    assert [x["regime_scores"] for x in a["horizons"]] == [x["regime_scores"] for x in b["horizons"]]


def test_origin_feature_votes_are_explainable_and_read_only() -> None:
    report = score_market_regime_signals(_bundle(), origin_feature_context=_context("candidate-a", 101.0, 100.0, 3, 10))
    row = {x["horizon_key"]: x for x in report["horizons"]}["300s"]
    vote = next(x for x in row["signal_votes_all"] if x["signal_id"] == "origin_feature_ma_spread_bps")
    assert "window-aware horizon decay" in vote["reason"]
    assert vote["source_refs"] == ["candidate-a"]
    assert report["origin_feature_context_used"] is True
    assert report["read_only"] is True
    assert report["producer_enabled"] is False
