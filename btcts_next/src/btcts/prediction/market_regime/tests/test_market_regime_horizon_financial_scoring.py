# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_horizon_financial_scoring.py
# desc: MR-F9.18A3 guards for horizon-specific explainable financial feature scoring.

from __future__ import annotations

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, SourceCoverage
from btcts.prediction.market_regime.features.feature_bundle import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.signal_scoring import score_market_regime_signals


def _bundle() -> MarketRegimeFeatureBundle:
    signals = (
        FeatureSignal(FeatureGroup.SOURCE_QUALITY, "source_quality_score", 1.0, True, source_refs=("quality",)),
        FeatureSignal(FeatureGroup.SOURCE_QUALITY, "session_context", "asia", True, source_refs=("generated_at",)),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_regime_hint", "UP_TREND", True, source_refs=("candles",)),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_net_change_bps", 18.0, True, source_refs=("candles",)),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_close_position", 0.82, True, source_refs=("candles",)),
        FeatureSignal(FeatureGroup.VOLATILITY, "current_l4_candle_realized_volatility_bps", 12.0, True, source_refs=("candles",)),
        FeatureSignal(FeatureGroup.VOLATILITY, "current_l4_candle_average_range_bps", 16.0, True, source_refs=("candles",)),
    )
    coverage = (
        SourceCoverage(FeatureGroup.SOURCE_QUALITY, True, FreshnessState.LIVE),
        SourceCoverage(FeatureGroup.PRICE_STRUCTURE, True, FreshnessState.LIVE),
        SourceCoverage(FeatureGroup.VOLATILITY, True, FreshnessState.LIVE),
    )
    return MarketRegimeFeatureBundle(
        generated_at="2026-07-16T08:30:00Z",
        signals=signals,
        coverage=coverage,
        source_snapshot_ok=True,
    )


def test_numeric_financial_features_create_explainable_votes() -> None:
    report = score_market_regime_signals(_bundle(), top_n=20)
    row = {item["horizon_key"]: item for item in report["horizons"]}["300s"]
    vote_ids = {item["signal_id"] for item in row["signal_votes_all"]}
    assert {
        "current_l4_candle_net_change_bps",
        "current_l4_candle_close_position",
        "current_l4_candle_realized_volatility_bps",
        "current_l4_candle_average_range_bps",
    } <= vote_ids
    assert row["regime_scores"]["UP_TREND"] > 0.0
    assert row["regime_scores"]["HIGH_VOL_CHOP"] > 0.0


def test_directional_evidence_decays_by_horizon_without_becoming_probability() -> None:
    report = score_market_regime_signals(_bundle(), top_n=20)
    rows = {item["horizon_key"]: item for item in report["horizons"]}
    assert rows["300s"]["regime_scores"]["UP_TREND"] > rows["3600s"]["regime_scores"]["UP_TREND"]
    assert rows["3600s"]["regime_scores"]["UP_TREND"] > rows["86400s"]["regime_scores"]["UP_TREND"]
    assert report["read_only"] is True
    assert report["producer_enabled"] is False


def test_source_refs_and_reasons_remain_auditable() -> None:
    report = score_market_regime_signals(_bundle(), top_n=20)
    row = {item["horizon_key"]: item for item in report["horizons"]}["900s"]
    vote = next(item for item in row["signal_votes_all"] if item["signal_id"] == "current_l4_candle_net_change_bps")
    assert vote["source_refs"] == ["candles"]
    assert "horizon decay" in vote["reason"]
    assert 0.0 < vote["weighted_strength"] <= 1.0
