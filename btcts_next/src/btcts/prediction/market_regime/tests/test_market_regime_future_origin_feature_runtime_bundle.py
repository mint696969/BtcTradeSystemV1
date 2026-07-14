# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_feature_runtime_bundle.py
# desc: MR-F6.15 tests for explicit-candidate read-only runtime feature completion from canonical L4 candles.

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, SourceCoverage
from btcts.prediction.market_regime.features import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.future_origin_feature_runtime_bundle import (
    build_market_regime_origin_feature_runtime_bundle,
)

CANDIDATE_ID = "market_regime.origin_feature.shadow.ma_5_20.interquartile.v1"


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _rows() -> tuple[dict[str, object], ...]:
    start = datetime(2026, 7, 13, 23, 0, tzinfo=timezone.utc)
    return tuple({
        "time_utc": _iso(start + timedelta(minutes=index)),
        "close": 100.0 + index,
    } for index in range(60))


def _bundle() -> MarketRegimeFeatureBundle:
    signals = (
        FeatureSignal(FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_generated_at", "2026-07-13T23:59:00Z", True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_net_change_bps", 125.0, True),
        FeatureSignal(FeatureGroup.VOLATILITY, "current_l4_candle_realized_volatility_bps", 20.0, True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_regime_hint", "RANGE", True),
    )
    coverage = tuple(
        SourceCoverage(group, True, FreshnessState.LIVE)
        for group in (FeatureGroup.SOURCE_QUALITY, FeatureGroup.PRICE_STRUCTURE, FeatureGroup.VOLATILITY)
    )
    return MarketRegimeFeatureBundle(
        generated_at="2026-07-14T00:00:00Z",
        signals=signals,
        coverage=coverage,
        source_snapshot_ok=True,
    )


def test_explicit_shadow_candidate_completes_runtime_feature_inputs() -> None:
    result = build_market_regime_origin_feature_runtime_bundle(
        feature_bundle=_bundle(),
        previous_current_state={"regime_code": "DOWN_TREND"},
        canonical_current_l4_candle_rows=_rows(),
        shadow_candidate_id=CANDIDATE_ID,
    )
    assert result["runtime_source_ready"] is True
    assert result["feature_bundle_generated_at"] == "2026-07-14T00:00:00Z"
    assert result["feature_snapshot_ref"].startswith("market_regime_feature_snapshot:")
    assert result["shadow_candidate_id"] == CANDIDATE_ID
    assert result["parameter_set_id"] == CANDIDATE_ID
    inputs = result["feature_inputs"]
    assert inputs.fast_ma == pytest.approx(sum(range(155, 160)) / 5)
    assert inputs.slow_ma == pytest.approx(sum(range(140, 160)) / 20)
    assert inputs.low_volatility_threshold == pytest.approx(4.47257112 / 10000.0)
    assert inputs.high_volatility_threshold == pytest.approx(7.35462997 / 10000.0)


def test_candidate_is_explicit_and_unknown_candidate_fails_closed() -> None:
    with pytest.raises(ValueError, match="explicit_candidate_id_required"):
        build_market_regime_origin_feature_runtime_bundle(
            feature_bundle=_bundle(), previous_current_state={"regime_code": "RANGE"},
            canonical_current_l4_candle_rows=_rows(), shadow_candidate_id="",
        )
    with pytest.raises(KeyError, match="candidate_not_found"):
        build_market_regime_origin_feature_runtime_bundle(
            feature_bundle=_bundle(), previous_current_state={"regime_code": "RANGE"},
            canonical_current_l4_candle_rows=_rows(), shadow_candidate_id="unknown",
        )


def test_candle_time_contract_rejects_gap_future_and_wrong_count() -> None:
    gap = list(_rows())
    gap[-1] = {"time_utc": "2026-07-14T00:00:00Z", "close": 159.0}
    with pytest.raises(ValueError, match="candle_gap_detected"):
        build_market_regime_origin_feature_runtime_bundle(
            feature_bundle=_bundle(), previous_current_state={"regime_code": "RANGE"},
            canonical_current_l4_candle_rows=tuple(gap), shadow_candidate_id=CANDIDATE_ID,
        )

    future_bundle = _bundle()
    future_rows = tuple(dict(row) for row in _rows())
    with pytest.raises(ValueError, match="candle_lookahead_detected"):
        build_market_regime_origin_feature_runtime_bundle(
            feature_bundle=MarketRegimeFeatureBundle(
                generated_at=future_bundle.generated_at,
                signals=tuple(
                    FeatureSignal(signal.feature_group, signal.name, "2026-07-13T23:58:00Z", signal.available)
                    if signal.name == "current_l4_candle_window_generated_at" else signal
                    for signal in future_bundle.signals
                ),
                coverage=future_bundle.coverage,
                source_snapshot_ok=True,
            ),
            previous_current_state={"regime_code": "RANGE"},
            canonical_current_l4_candle_rows=future_rows,
            shadow_candidate_id=CANDIDATE_ID,
        )

    with pytest.raises(ValueError, match="candle_row_count_not_sixty"):
        build_market_regime_origin_feature_runtime_bundle(
            feature_bundle=_bundle(), previous_current_state={"regime_code": "RANGE"},
            canonical_current_l4_candle_rows=_rows()[:-1], shadow_candidate_id=CANDIDATE_ID,
        )


def test_stale_coverage_or_bad_snapshot_blocks_runtime_readiness() -> None:
    bundle = _bundle()
    stale_bundle = MarketRegimeFeatureBundle(
        generated_at=bundle.generated_at,
        signals=bundle.signals,
        coverage=tuple(
            SourceCoverage(
                item.feature_group,
                item.available,
                FreshnessState.STALE if item.feature_group is FeatureGroup.VOLATILITY else item.freshness_state,
            )
            for item in bundle.coverage
        ),
        source_snapshot_ok=True,
    )
    result = build_market_regime_origin_feature_runtime_bundle(
        feature_bundle=stale_bundle,
        previous_current_state={"regime_code": "RANGE"},
        canonical_current_l4_candle_rows=_rows(),
        shadow_candidate_id=CANDIDATE_ID,
    )
    assert result["runtime_source_ready"] is False
    assert result["source_quality_ready"] is False
    assert (
        "origin_feature_runtime_bundle_coverage_not_live:volatility:STALE"
        in result["blockers"]
    )
    assert result["feature_inputs"] is None

    bad_snapshot_bundle = MarketRegimeFeatureBundle(
        generated_at=bundle.generated_at,
        signals=bundle.signals,
        coverage=bundle.coverage,
        source_snapshot_ok=False,
    )
    result = build_market_regime_origin_feature_runtime_bundle(
        feature_bundle=bad_snapshot_bundle,
        previous_current_state={"regime_code": "RANGE"},
        canonical_current_l4_candle_rows=_rows(),
        shadow_candidate_id=CANDIDATE_ID,
    )
    assert result["runtime_source_ready"] is False
    assert "origin_feature_runtime_bundle_source_snapshot_not_ok" in result["blockers"]
    assert result["feature_inputs"] is None


def test_missing_base_runtime_field_remains_blocked_without_substitution() -> None:
    result = build_market_regime_origin_feature_runtime_bundle(
        feature_bundle=_bundle(),
        previous_current_state=None,
        canonical_current_l4_candle_rows=_rows(),
        shadow_candidate_id=CANDIDATE_ID,
    )
    assert result["runtime_source_ready"] is False
    assert "origin_feature_runtime_bundle_missing:previous_state" in result["blockers"]
    assert result["feature_inputs"] is None
    assert result["semantic_substitution_used"] is False


def test_bundle_is_read_only_and_never_selects_applies_or_writes() -> None:
    result = build_market_regime_origin_feature_runtime_bundle(
        feature_bundle=_bundle(),
        previous_current_state={"regime_code": "DOWN_TREND"},
        canonical_current_l4_candle_rows=_rows(),
        shadow_candidate_id=CANDIDATE_ID,
    )
    assert result["explicit_candidate_required"] is True
    assert result["candidate_selection_performed"] is False
    assert result["writer_invoked"] is False
    assert result["writes_dhot"] is False
    assert result["scheduler_enabled"] is False
    assert result["live_parameter_apply_allowed"] is False
    assert result["auto_promotion_allowed"] is False
    assert result["canonical_replacement_allowed"] is False
