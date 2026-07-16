# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_execution_observation_request.py
# desc: MR-F9.15 guards for immutable 14-trace observation request templates without inferred execution facts.

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, MarketRegimeCode, SourceCoverage
from btcts.prediction.market_regime.features import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.future_origin_feature_runtime_bundle import build_market_regime_origin_feature_runtime_bundle
from btcts.prediction.market_regime.future_shadow_adapter import build_market_regime_future_shadow_packet
from btcts.prediction.market_regime.future_shadow_execution_observation_request import build_future_shadow_execution_observation_request
from btcts.prediction.market_regime.future_shadow_runtime_preflight_bridge import build_future_shadow_runtime_preflight_report
from btcts.prediction.market_regime.horizon_policy import build_default_horizon_policy

CANDIDATE_ID = "market_regime.origin_feature.shadow.ma_5_20.interquartile.v1"


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _rows() -> tuple[dict[str, object], ...]:
    start = datetime(2026, 7, 13, 23, 0, tzinfo=timezone.utc)
    return tuple({"time_utc": _iso(start + timedelta(minutes=index)), "close": 100.0 + index} for index in range(60))


def _bundle() -> MarketRegimeFeatureBundle:
    signals = (
        FeatureSignal(FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_generated_at", "2026-07-13T23:59:00Z", True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_net_change_bps", 125.0, True),
        FeatureSignal(FeatureGroup.VOLATILITY, "current_l4_candle_realized_volatility_bps", 20.0, True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_regime_hint", "RANGE", True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "session_context", "asia", True),
    )
    groups = (FeatureGroup.PRICE_STRUCTURE, FeatureGroup.VOLATILITY, FeatureGroup.LIQUIDITY, FeatureGroup.SOURCE_QUALITY)
    return MarketRegimeFeatureBundle(
        generated_at="2026-07-14T00:00:00Z",
        signals=signals,
        coverage=tuple(SourceCoverage(group, True, FreshnessState.LIVE) for group in groups),
        source_snapshot_ok=True,
    )


def _report() -> dict[str, object]:
    return {"market_regime_only": True, "horizons": [
        {"horizon_sec": item.horizon_sec, "horizon_key": item.horizon_key, "regime_scores": {"RANGE": 0.8, "UP_TREND": 0.2}}
        for item in build_default_horizon_policy().horizons if item.horizon_sec
    ]}


def _preflight():
    bundle = _bundle()
    report = _report()
    epoch = datetime.fromisoformat(bundle.generated_at.replace("Z", "+00:00")).timestamp()
    packet = build_market_regime_future_shadow_packet(
        feature_bundle=bundle,
        signal_score_report=report,
        origin_current_state=MarketRegimeCode.RANGE,
        origin_timestamp_epoch_sec=epoch,
        source_timestamp_epoch_sec=epoch - 60.0,
    )
    runtime = build_market_regime_origin_feature_runtime_bundle(
        feature_bundle=bundle,
        previous_current_state={"regime_code": "DOWN_TREND"},
        canonical_current_l4_candle_rows=_rows(),
        shadow_candidate_id=CANDIDATE_ID,
    )
    return build_future_shadow_runtime_preflight_report(packet=packet, signal_score_report=report, runtime_bundle=runtime)


def test_builds_exact_fourteen_identity_locked_incomplete_rows() -> None:
    preflight = _preflight()
    result = build_future_shadow_execution_observation_request(preflight_report=preflight)
    assert result["trace_count"] == 14
    assert len(result["rows"]) == 14
    assert len({row["trace_id"] for row in result["rows"]}) == 14
    assert all(row["prediction_origin"] == preflight["prediction_origin"] for row in result["rows"])
    assert all(row["feature_snapshot_ref"] == preflight["feature_snapshot_ref"] for row in result["rows"])
    assert all(row["inference_mode"] is None for row in result["rows"])
    assert all(row["raw_output_semantics"] is None for row in result["rows"])
    assert all(row["source_freshness_state"] is None for row in result["rows"])
    assert all(row["observation_complete"] is False for row in result["rows"])
    assert result["request_complete"] is False


def test_request_identity_is_deterministic() -> None:
    first = build_future_shadow_execution_observation_request(preflight_report=_preflight())
    second = build_future_shadow_execution_observation_request(preflight_report=_preflight())
    assert first["request_id"] == second["request_id"]


def test_tampered_origin_snapshot_and_duplicate_trace_fail_closed() -> None:
    preflight = dict(_preflight())
    pairs = [dict(item) for item in preflight["pairs"]]
    forecasts = [dict(row) for row in pairs[0]["forecasts"]]
    forecasts[0]["origin_timestamp"] = "2026-07-14T00:01:00Z"
    pairs[0]["forecasts"] = tuple(forecasts)
    preflight["pairs"] = tuple(pairs)
    with pytest.raises(ValueError, match="origin_mismatch"):
        build_future_shadow_execution_observation_request(preflight_report=preflight)

    preflight = dict(_preflight())
    pairs = [dict(item) for item in preflight["pairs"]]
    forecasts = [dict(row) for row in pairs[0]["forecasts"]]
    forecasts[0]["feature_snapshot_ref"] = "snapshot:tampered"
    pairs[0]["forecasts"] = tuple(forecasts)
    preflight["pairs"] = tuple(pairs)
    with pytest.raises(ValueError, match="snapshot_mismatch"):
        build_future_shadow_execution_observation_request(preflight_report=preflight)

    preflight = dict(_preflight())
    pairs = [dict(item) for item in preflight["pairs"]]
    forecasts = [dict(row) for row in pairs[0]["forecasts"]]
    forecasts[1]["trace_id"] = forecasts[0]["trace_id"]
    pairs[0]["forecasts"] = tuple(forecasts)
    preflight["pairs"] = tuple(pairs)
    with pytest.raises(ValueError, match="trace_identity_duplicate"):
        build_future_shadow_execution_observation_request(preflight_report=preflight)


def test_unsafe_preflight_flag_fails_closed() -> None:
    preflight = dict(_preflight())
    preflight["writes_dhot"] = True
    with pytest.raises(ValueError, match="unsafe_preflight_flag:writes_dhot"):
        build_future_shadow_execution_observation_request(preflight_report=preflight)


def test_output_is_immutable_and_never_infers_or_writes() -> None:
    result = build_future_shadow_execution_observation_request(preflight_report=_preflight())
    with pytest.raises(TypeError):
        result["trace_count"] = 0
    with pytest.raises(TypeError):
        result["rows"][0]["inference_mode"] = "FULL_INFERENCE"
    assert result["facts_inferred_from_preflight"] is False
    assert result["facts_inferred_from_classifier_diagnostics"] is False
    assert result["legacy_confidence_promoted_to_probability"] is False
    assert result["would_write"] is False
    safety = result["safety"]
    assert safety["writes_dhot"] is False
    assert safety["writes_repository"] is False
    assert safety["scheduler_enabled"] is False
    assert safety["producer_loop_enabled"] is False
    assert safety["parameter_auto_promotion_allowed"] is False
    assert safety["live_parameter_apply_allowed"] is False
    assert safety["broker_private_api_allowed"] is False
    assert safety["autotrade_trigger_allowed"] is False
    assert safety["order_intent_submitted"] is False
