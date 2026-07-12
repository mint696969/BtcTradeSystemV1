# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_adapter.py
# desc: Pure MR-F5.4 tests for explicit feature/signal adaptation into a shadow-only future MarketRegime packet.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, MarketRegimeCode, SourceCoverage
from btcts.prediction.market_regime.features import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.future_shadow_adapter import build_market_regime_future_shadow_packet
from btcts.prediction.market_regime.horizon_policy import build_default_horizon_policy


def _bundle(*, source_snapshot_ok: bool = True, include_session: bool = False) -> MarketRegimeFeatureBundle:
    coverage = tuple(
        SourceCoverage(group, True, FreshnessState.LIVE, used_sources=(f"source:{group.value}",))
        for group in (FeatureGroup.PRICE_STRUCTURE, FeatureGroup.VOLATILITY, FeatureGroup.LIQUIDITY, FeatureGroup.SOURCE_QUALITY)
    )
    signals = tuple(
        FeatureSignal(group, f"signal_{group.value}", 1.0, True, source_refs=(f"ref:{group.value}",))
        for group in (FeatureGroup.PRICE_STRUCTURE, FeatureGroup.VOLATILITY, FeatureGroup.LIQUIDITY, FeatureGroup.SOURCE_QUALITY)
    )
    if include_session:
        signals += (FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "session_context", "asia", True, source_refs=("ref:session",)),)
    return MarketRegimeFeatureBundle(
        generated_at="2026-07-12T00:00:00Z",
        signals=signals,
        coverage=coverage,
        source_snapshot_ok=source_snapshot_ok,
    )


def _report() -> dict:
    rows = []
    for horizon in build_default_horizon_policy().horizons:
        if horizon.horizon_sec == 0:
            continue
        rows.append({
            "horizon_sec": horizon.horizon_sec,
            "horizon_key": horizon.horizon_key,
            "regime_scores": {"BREAKOUT": 0.8, "RANGE": 0.2, "UP_TREND": 0.1},
        })
    return {"market_regime_only": True, "horizons": rows}


def test_adapter_builds_exact_seven_horizon_shadow_packet() -> None:
    packet = build_market_regime_future_shadow_packet(
        feature_bundle=_bundle(include_session=True),
        signal_score_report=_report(),
        origin_current_state=MarketRegimeCode.LOW_VOL_COMPRESSION,
        source_timestamp_epoch_sec=100.0,
        origin_timestamp_epoch_sec=100.0,
    )
    assert tuple(item.target_horizon_sec for item in packet.forecasts) == (300, 900, 1800, 3600, 21600, 43200, 86400)
    payload = packet.to_dict()
    assert payload["shadow_only"] is True
    assert payload["canonical_replacement"] is False
    assert payload["safety"]["writes_dhot"] is False
    assert all(not item.abstain_reason for item in packet.forecasts)


def test_feature_snapshot_identity_is_deterministic() -> None:
    kwargs = dict(
        feature_bundle=_bundle(include_session=True),
        signal_score_report=_report(),
        origin_current_state=MarketRegimeCode.RANGE,
        source_timestamp_epoch_sec=100.0,
        origin_timestamp_epoch_sec=100.0,
    )
    first = build_market_regime_future_shadow_packet(**kwargs)
    second = build_market_regime_future_shadow_packet(**kwargs)
    assert first.feature_snapshot_ref == second.feature_snapshot_ref


def test_unsupported_horizon_or_mismatched_horizon_key_fails_closed() -> None:
    extra = _report()
    extra["horizons"].append({"horizon_sec": 600, "horizon_key": "600s", "regime_scores": {"RANGE": 1.0, "BREAKOUT": 0.1}})
    with pytest.raises(ValueError, match="future_shadow_unsupported_horizon:600"):
        build_market_regime_future_shadow_packet(
            feature_bundle=_bundle(include_session=True), signal_score_report=extra, origin_current_state=MarketRegimeCode.RANGE,
            source_timestamp_epoch_sec=100.0, origin_timestamp_epoch_sec=100.0,
        )
    mismatch = _report()
    mismatch["horizons"][0]["horizon_key"] = "wrong"
    with pytest.raises(ValueError, match="future_shadow_horizon_key_mismatch:300"):
        build_market_regime_future_shadow_packet(
            feature_bundle=_bundle(include_session=True), signal_score_report=mismatch, origin_current_state=MarketRegimeCode.RANGE,
            source_timestamp_epoch_sec=100.0, origin_timestamp_epoch_sec=100.0,
        )


def test_missing_canonical_horizon_score_fails_closed() -> None:
    report = _report()
    report["horizons"] = [row for row in report["horizons"] if row["horizon_sec"] != 86400]
    with pytest.raises(ValueError, match="future_shadow_horizon_score_missing:86400"):
        build_market_regime_future_shadow_packet(
            feature_bundle=_bundle(include_session=True),
            signal_score_report=report,
            origin_current_state=MarketRegimeCode.RANGE,
            source_timestamp_epoch_sec=100.0,
            origin_timestamp_epoch_sec=100.0,
        )


def test_bad_source_snapshot_or_non_market_report_fails_closed() -> None:
    with pytest.raises(ValueError, match="future_shadow_source_snapshot_not_ok"):
        build_market_regime_future_shadow_packet(
            feature_bundle=_bundle(source_snapshot_ok=False), signal_score_report=_report(), origin_current_state=MarketRegimeCode.RANGE,
            source_timestamp_epoch_sec=100.0, origin_timestamp_epoch_sec=100.0,
        )
    report = _report(); report["market_regime_only"] = False
    with pytest.raises(ValueError, match="future_shadow_signal_report_not_market_regime_only"):
        build_market_regime_future_shadow_packet(
            feature_bundle=_bundle(), signal_score_report=report, origin_current_state=MarketRegimeCode.RANGE,
            source_timestamp_epoch_sec=100.0, origin_timestamp_epoch_sec=100.0,
        )


def test_negative_regime_score_fails_closed() -> None:
    report = _report()
    report["horizons"][1]["regime_scores"]["BREAKOUT"] = -0.1
    with pytest.raises(ValueError, match="future_baseline_regime_score_invalid"):
        build_market_regime_future_shadow_packet(
            feature_bundle=_bundle(include_session=True),
            signal_score_report=report,
            origin_current_state=MarketRegimeCode.RANGE,
            source_timestamp_epoch_sec=100.0,
            origin_timestamp_epoch_sec=100.0,
        )


def test_missing_long_horizon_session_context_abstains_not_synthesizes() -> None:
    packet = build_market_regime_future_shadow_packet(
        feature_bundle=_bundle(include_session=False),
        signal_score_report=_report(),
        origin_current_state=MarketRegimeCode.RANGE,
        source_timestamp_epoch_sec=100.0,
        origin_timestamp_epoch_sec=100.0,
    )
    long_rows = [item for item in packet.forecasts if item.target_horizon_sec >= 21600]
    assert all(item.abstain_reason == "required_feature_family_missing" for item in long_rows)
    assert all("missing_required_feature:session_context" in item.invalidation_conditions for item in long_rows)
