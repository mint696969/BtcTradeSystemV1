# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_future_forecastability_remediation.py
# desc: Tests for MR-F5 session-context feature and current-L4 hint scoring remediation.

from __future__ import annotations

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, SourceCoverage
from btcts.prediction.market_regime.features.feature_bundle import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.signal_scoring import score_market_regime_signals


def _bundle(*, generated_at: str, hint: str) -> MarketRegimeFeatureBundle:
    signals = (
        FeatureSignal(FeatureGroup.SOURCE_QUALITY, "source_quality_score", 1.0, True),
        FeatureSignal(FeatureGroup.SOURCE_QUALITY, "session_context", "asia", True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_regime_hint", hint, True),
    )
    coverage = (
        SourceCoverage(FeatureGroup.SOURCE_QUALITY, True, FreshnessState.LIVE),
        SourceCoverage(FeatureGroup.PRICE_STRUCTURE, True, FreshnessState.LIVE),
    )
    return MarketRegimeFeatureBundle(
        generated_at=generated_at,
        signals=signals,
        coverage=coverage,
        source_snapshot_ok=True,
    )


def test_session_context_signal_name_is_available_to_future_adapter_contract() -> None:
    bundle = _bundle(generated_at="2026-07-12T14:00:00Z", hint="BREAKOUT")
    names = {item.name for item in bundle.signals if item.available}
    assert "session_context" in names


def test_current_l4_hint_produces_second_non_unknown_regime_candidate() -> None:
    report = score_market_regime_signals(_bundle(generated_at="2026-07-12T14:00:00Z", hint="BREAKOUT"))
    by_horizon = {item["horizon_key"]: item for item in report["horizons"]}
    scores = by_horizon["300s"]["regime_scores"]
    positive = [name for name, value in scores.items() if name != "UNKNOWN" and value > 0.0]
    assert "RANGE" in positive
    assert "BREAKOUT" in positive
    assert len(positive) >= 2


def test_unknown_current_l4_hint_adds_no_directional_vote() -> None:
    report = score_market_regime_signals(_bundle(generated_at="2026-07-12T14:00:00Z", hint="UNKNOWN"))
    by_horizon = {item["horizon_key"]: item for item in report["horizons"]}
    vote_ids = {item["signal_id"] for item in by_horizon["300s"]["signal_votes_top_n"]}
    assert "current_l4_candle_regime_hint" not in vote_ids
