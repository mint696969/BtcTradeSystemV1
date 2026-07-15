# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_feature_builder_source_quality_freshness.py
# desc: Regression tests for source-quality freshness when live L4 candles coexist with stale forecast artifacts.

from __future__ import annotations

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState
from btcts.prediction.market_regime.features.feature_builder import _coverage_for_group
from btcts.prediction.market_regime.features.feature_bundle import FeatureSignal


def _signal(name: str, value: object, *, warnings: tuple[str, ...] = ()) -> FeatureSignal:
    return FeatureSignal(
        feature_group=FeatureGroup.SOURCE_QUALITY,
        name=name,
        value=value,
        available=True,
        source_refs=("fixture",),
        warnings=warnings,
    )


def test_source_quality_is_live_when_current_l4_candle_is_current_even_if_forecast_is_stale() -> None:
    coverage = _coverage_for_group(
        FeatureGroup.SOURCE_QUALITY,
        (
            _signal(
                "forecast_records_current_enough",
                False,
                warnings=("forecast_records_stale", "forecast_records_age_sec:99999"),
            ),
            _signal("current_l4_candle_window_current_enough", True),
            _signal("current_l4_candle_window_generated_at", "2026-07-15T08:24:00Z"),
        ),
    )
    assert coverage.available is True
    assert coverage.freshness_state is FreshnessState.LIVE
    assert "forecast_records_stale" in coverage.warnings


def test_source_quality_remains_stale_when_forecast_is_stale_and_l4_candle_is_not_current() -> None:
    coverage = _coverage_for_group(
        FeatureGroup.SOURCE_QUALITY,
        (
            _signal(
                "forecast_records_current_enough",
                False,
                warnings=("forecast_records_stale",),
            ),
            _signal(
                "current_l4_candle_window_current_enough",
                False,
                warnings=("current_l4_candle_window_stale",),
            ),
        ),
    )
    assert coverage.freshness_state is FreshnessState.STALE


def test_cross_venue_does_not_inherit_source_quality_l4_override() -> None:
    signal = FeatureSignal(
        feature_group=FeatureGroup.CROSS_VENUE,
        name="cross_venue_agreement",
        value=None,
        available=False,
        source_refs=("fixture",),
        warnings=("forecast_records_stale",),
    )
    coverage = _coverage_for_group(FeatureGroup.CROSS_VENUE, (signal,))
    assert coverage.freshness_state is FreshnessState.STALE
