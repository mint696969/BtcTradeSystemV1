# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_runtime_preflight_bridge.py
# desc: MR-F8.7 tests for pure runtime-input to paired shadow preflight bridging.

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, MarketRegimeCode, SourceCoverage
from btcts.prediction.market_regime.features import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.future_origin_feature_runtime_bundle import build_market_regime_origin_feature_runtime_bundle
from btcts.prediction.market_regime.future_shadow_adapter import build_market_regime_future_shadow_packet
from btcts.prediction.market_regime.future_shadow_runtime_preflight_bridge import build_future_shadow_runtime_preflight_report
from btcts.prediction.market_regime.horizon_policy import build_default_horizon_policy

CANDIDATE_ID = "market_regime.origin_feature.shadow.ma_5_20.interquartile.v1"


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _rows() -> tuple[dict[str, object], ...]:
    start = datetime(2026, 7, 13, 23, 0, tzinfo=timezone.utc)
    return tuple({"time_utc": _iso(start + timedelta(minutes=index)), "close": 100.0 + index} for index in range(60))


def _feature_bundle() -> MarketRegimeFeatureBundle:
    signals = (
        FeatureSignal(FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_generated_at", "2026-07-13T23:59:00Z", True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_net_change_bps", 125.0, True),
        FeatureSignal(FeatureGroup.VOLATILITY, "current_l4_candle_realized_volatility_bps", 20.0, True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_regime_hint", "RANGE", True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "session_context", "asia", True),
    )
    groups = (FeatureGroup.PRICE_STRUCTURE, FeatureGroup.VOLATILITY, FeatureGroup.LIQUIDITY, FeatureGroup.SOURCE_QUALITY)
    coverage = tuple(SourceCoverage(group, True, FreshnessState.LIVE) for group in groups)
    return MarketRegimeFeatureBundle(generated_at="2026-07-14T00:00:00Z", signals=signals, coverage=coverage, source_snapshot_ok=True)


def _report() -> dict[str, object]:
    return {"market_regime_only": True, "horizons": [
        {"horizon_sec": item.horizon_sec, "horizon_key": item.horizon_key, "regime_scores": {"RANGE": 0.8, "UP_TREND": 0.2}}
        for item in build_default_horizon_policy().horizons if item.horizon_sec
    ]}


def _packet():
    bundle = _feature_bundle()
    report = _report()
    epoch = datetime.fromisoformat(bundle.generated_at.replace("Z", "+00:00")).timestamp()
    return build_market_regime_future_shadow_packet(
        feature_bundle=bundle,
        signal_score_report=report,
        origin_current_state=MarketRegimeCode.RANGE,
        origin_timestamp_epoch_sec=epoch,
        source_timestamp_epoch_sec=epoch - 60.0,
    )


def _runtime_bundle():
    return build_market_regime_origin_feature_runtime_bundle(
        feature_bundle=_feature_bundle(),
        previous_current_state={"regime_code": "DOWN_TREND"},
        canonical_current_l4_candle_rows=_rows(),
        shadow_candidate_id=CANDIDATE_ID,
    )


def test_builds_seven_runtime_pairs_without_write_surface() -> None:
    result = build_future_shadow_runtime_preflight_report(
        packet=_packet(), signal_score_report=_report(), runtime_bundle=_runtime_bundle()
    )
    assert result["pair_count"] == 7
    assert all(item["candidate_count"] == 2 for item in result["pairs"])
    assert all(item["trace_plan"]["persistence_plan"]["would_write"] is False for item in result["pairs"])
    assert result["writer_invoked"] is False
    assert result["writes_dhot"] is False


def test_runtime_origin_mismatch_fails_closed() -> None:
    runtime = dict(_runtime_bundle())
    runtime["feature_bundle_generated_at"] = "2026-07-14T00:01:00Z"
    with pytest.raises(ValueError, match="origin_mismatch"):
        build_future_shadow_runtime_preflight_report(
            packet=_packet(), signal_score_report=_report(), runtime_bundle=runtime
        )


def test_unready_runtime_bundle_fails_closed() -> None:
    runtime = dict(_runtime_bundle())
    runtime["runtime_source_ready"] = False
    with pytest.raises(ValueError, match="runtime_source_not_ready"):
        build_future_shadow_runtime_preflight_report(
            packet=_packet(), signal_score_report=_report(), runtime_bundle=runtime
        )
