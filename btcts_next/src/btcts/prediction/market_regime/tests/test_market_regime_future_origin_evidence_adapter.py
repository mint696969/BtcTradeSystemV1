# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_evidence_adapter.py
# desc: MR-F6.7 tests for pure seven-horizon origin-evidence bundle adaptation without writer execution.

from __future__ import annotations

from datetime import datetime

import pytest

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, MarketRegimeCode, SourceCoverage
from btcts.prediction.market_regime.features import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.future_origin_evidence_adapter import MarketRegimeOriginFeatureInputs, build_market_regime_origin_evidence_bundles
from btcts.prediction.market_regime.future_shadow_adapter import build_market_regime_future_shadow_packet
from btcts.prediction.market_regime.horizon_policy import build_default_horizon_policy


def _bundle() -> MarketRegimeFeatureBundle:
    groups = (FeatureGroup.PRICE_STRUCTURE, FeatureGroup.VOLATILITY, FeatureGroup.LIQUIDITY, FeatureGroup.SOURCE_QUALITY)
    return MarketRegimeFeatureBundle(
        generated_at="2026-07-14T00:00:00Z",
        signals=tuple(FeatureSignal(group, f"signal_{group.value}", 1.0, True, source_refs=(f"ref:{group.value}",)) for group in groups) + (FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "session_context", "asia", True, source_refs=("ref:session",)),),
        coverage=tuple(SourceCoverage(group, True, FreshnessState.LIVE, used_sources=(f"source:{group.value}",)) for group in groups),
        source_snapshot_ok=True,
    )


def _report() -> dict:
    return {"market_regime_only": True, "horizons": [
        {"horizon_sec": item.horizon_sec, "horizon_key": item.horizon_key, "regime_scores": {"RANGE": 0.8, "UP_TREND": 0.2}}
        for item in build_default_horizon_policy().horizons if item.horizon_sec
    ]}


def _epoch(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def _packet():
    return build_market_regime_future_shadow_packet(
        feature_bundle=_bundle(),
        signal_score_report=_report(),
        origin_current_state=MarketRegimeCode.RANGE,
        origin_timestamp_epoch_sec=_epoch("2026-07-14T00:00:00Z"),
        source_timestamp_epoch_sec=_epoch("2026-07-13T23:59:59Z"),
    )


def _inputs(**overrides: object) -> MarketRegimeOriginFeatureInputs:
    values = dict(source_timestamp="2026-07-13T23:59:59Z", previous_state=MarketRegimeCode.DOWN_TREND, recent_return=0.01, fast_ma=101.0, slow_ma=100.0, realized_volatility=0.02, low_volatility_threshold=0.01, high_volatility_threshold=0.03, current_forecast_label_selection=MarketRegimeCode.RANGE)
    values.update(overrides)
    return MarketRegimeOriginFeatureInputs(**values)


def test_builds_exact_seven_origin_bundles_without_write() -> None:
    bundles = build_market_regime_origin_evidence_bundles(packet=_packet(), signal_score_report=_report(), feature_inputs=_inputs())
    assert len(bundles) == 7
    assert tuple(item["target_horizon_sec"] for item in bundles) == (300, 900, 1800, 3600, 21600, 43200, 86400)
    assert len({item["trace_id"] for item in bundles}) == 7
    assert all(item["write_performed"] is False for item in bundles)
    assert all(item["historical_backfill_allowed"] is False for item in bundles)


def test_bundle_uses_explicit_origin_features_and_full_score_distribution() -> None:
    bundle = build_market_regime_origin_evidence_bundles(packet=_packet(), signal_score_report=_report(), feature_inputs=_inputs())[0]
    assert bundle["feature_snapshot"]["recent_return"] == 0.01
    assert bundle["feature_snapshot"]["fast_ma"] == 101.0
    assert bundle["candidate_probability_by_state"] == {"RANGE": 0.8, "UP_TREND": 0.2}


def test_lookahead_and_timestamp_contract_fail_closed() -> None:
    with pytest.raises(ValueError, match="timezone_missing"):
        _inputs(source_timestamp="2026-07-13T23:59:59")
    with pytest.raises(ValueError, match="lookahead_detected"):
        build_market_regime_origin_evidence_bundles(
            packet=_packet(),
            signal_score_report=_report(),
            feature_inputs=_inputs(source_timestamp="2026-07-14T00:00:01Z"),
        )


def test_missing_or_invalid_score_rows_fail_closed() -> None:
    report = _report(); report["horizons"] = report["horizons"][:-1]
    with pytest.raises(ValueError, match="missing_horizons"):
        build_market_regime_origin_evidence_bundles(packet=_packet(), signal_score_report=report, feature_inputs=_inputs())

    report = _report(); report["horizons"][0]["regime_scores"] = {
        "RANGE": 0.0,
        "UP_TREND": -1.0,
        "UNKNOWN": 99.0,
    }
    with pytest.raises(ValueError, match="positive_score_missing"):
        build_market_regime_origin_evidence_bundles(packet=_packet(), signal_score_report=report, feature_inputs=_inputs())

    report = _report(); report["horizons"][0]["regime_scores"]["RANGE"] = float("nan")
    with pytest.raises(ValueError, match="score_non_finite"):
        build_market_regime_origin_evidence_bundles(packet=_packet(), signal_score_report=report, feature_inputs=_inputs())


def test_signed_raw_scores_are_clamped_and_normalized_at_evidence_boundary() -> None:
    report = _report()
    report["horizons"][0]["regime_scores"] = {
        "RANGE": 2.0,
        "UP_TREND": 1.0,
        "DOWN_TREND": -5.0,
        "UNKNOWN": 100.0,
    }

    bundle = build_market_regime_origin_evidence_bundles(
        packet=_packet(),
        signal_score_report=report,
        feature_inputs=_inputs(),
    )[0]

    assert bundle["candidate_probability_by_state"] == pytest.approx({
        "RANGE": 2.0 / 3.0,
        "UP_TREND": 1.0 / 3.0,
    })
    assert "DOWN_TREND" not in bundle["candidate_probability_by_state"]
    assert "UNKNOWN" not in bundle["candidate_probability_by_state"]
    assert report["horizons"][0]["regime_scores"]["DOWN_TREND"] == -5.0


def test_adapter_has_no_writer_or_scheduler_surface() -> None:
    import btcts.prediction.market_regime.future_origin_evidence_adapter as module
    assert not hasattr(module, "write_origin_evidence_once")
    assert not hasattr(module, "main")
    assert not hasattr(module, "register")
