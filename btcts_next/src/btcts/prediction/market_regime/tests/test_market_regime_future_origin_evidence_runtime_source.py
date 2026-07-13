# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_evidence_runtime_source.py
# desc: MR-F6.8 tests for exact runtime-source provenance and fail-closed missing canonical inputs.

from __future__ import annotations

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, MarketRegimeCode, SourceCoverage
from btcts.prediction.market_regime.features import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.future_origin_evidence_runtime_source import build_market_regime_origin_runtime_source


def _bundle() -> MarketRegimeFeatureBundle:
    signals = (
        FeatureSignal(FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_generated_at", "2026-07-14T00:00:00Z", True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_net_change_bps", 125.0, True),
        FeatureSignal(FeatureGroup.VOLATILITY, "current_l4_candle_realized_volatility_bps", 20.0, True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_regime_hint", "RANGE", True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "ma_slope", 0.3, True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_thresholds", {"low_vol_range_bps_max": 25.0}, True),
    )
    coverage = tuple(
        SourceCoverage(group, True, FreshnessState.LIVE)
        for group in (FeatureGroup.SOURCE_QUALITY, FeatureGroup.PRICE_STRUCTURE, FeatureGroup.VOLATILITY)
    )
    return MarketRegimeFeatureBundle(
        generated_at="2026-07-14T00:00:01Z",
        signals=signals,
        coverage=coverage,
        source_snapshot_ok=True,
    )


def test_extracts_only_values_with_exact_runtime_semantics() -> None:
    result = build_market_regime_origin_runtime_source(
        feature_bundle=_bundle(),
        previous_current_state={"regime_code": "DOWN_TREND"},
    )
    values = result["extracted_values"]
    assert values["previous_state"] is MarketRegimeCode.DOWN_TREND
    assert values["recent_return"] == 0.0125
    assert values["realized_volatility"] == 0.002
    assert values["current_forecast_label_selection"] is MarketRegimeCode.RANGE


def test_ma_slope_is_not_substituted_for_fast_or_slow_ma() -> None:
    result = build_market_regime_origin_runtime_source(
        feature_bundle=_bundle(),
        previous_current_state={"regime_code": "RANGE"},
    )
    assert result["extracted_values"]["fast_ma"] is None
    assert result["extracted_values"]["slow_ma"] is None
    assert "origin_runtime_source_missing:fast_ma" in result["blockers"]
    assert "origin_runtime_source_missing:slow_ma" in result["blockers"]
    assert result["semantic_substitution_used"] is False


def test_current_l4_thresholds_are_not_substituted_for_volatility_thresholds() -> None:
    result = build_market_regime_origin_runtime_source(
        feature_bundle=_bundle(),
        previous_current_state={"regime_code": "RANGE"},
    )
    assert result["extracted_values"]["low_volatility_threshold"] is None
    assert result["extracted_values"]["high_volatility_threshold"] is None
    assert "origin_runtime_source_missing:low_volatility_threshold" in result["blockers"]
    assert "origin_runtime_source_missing:high_volatility_threshold" in result["blockers"]


def test_runtime_source_remains_not_ready_until_canonical_fields_exist() -> None:
    result = build_market_regime_origin_runtime_source(
        feature_bundle=_bundle(),
        previous_current_state={"regime_code": "DOWN_TREND"},
    )
    assert result["runtime_source_ready"] is False
    assert result["feature_inputs"] is None
    assert result["writer_invoked"] is False
    assert result["writes_dhot"] is False


def test_missing_previous_state_is_reported() -> None:
    result = build_market_regime_origin_runtime_source(
        feature_bundle=_bundle(),
        previous_current_state=None,
    )
    assert "origin_runtime_source_missing:previous_state" in result["blockers"]
