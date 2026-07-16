# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_runtime_execution_bridge.py
# desc: MR-F9.12 guards for explicit-fact runtime preflight to execution-plan bridging without writes.

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, MarketRegimeCode, SourceCoverage
from btcts.prediction.market_regime.features import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.future_execution_evidence import FutureInferenceMode, RawOutputSemantics
from btcts.prediction.market_regime.future_origin_feature_runtime_bundle import build_market_regime_origin_feature_runtime_bundle
from btcts.prediction.market_regime.future_shadow_adapter import build_market_regime_future_shadow_packet
from btcts.prediction.market_regime.future_shadow_pair_execution_plan import FutureExecutionFacts
from btcts.prediction.market_regime.future_shadow_runtime_execution_bridge import build_future_shadow_runtime_execution_bridge
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
    return build_future_shadow_runtime_preflight_report(
        packet=packet,
        signal_score_report=report,
        runtime_bundle=runtime,
    )


def _facts(preflight=None):
    report = _preflight() if preflight is None else preflight
    return {
        str(row["trace_id"]): FutureExecutionFacts(
            inference_mode=FutureInferenceMode.FULL_INFERENCE,
            raw_output_semantics=RawOutputSemantics.SCORE,
            source_freshness_state="FRESH",
            source_age_sec=60.0,
        )
        for pair in report["pairs"]
        for row in pair["forecasts"]
    }


def test_builds_seven_plans_and_fourteen_evidence_rows() -> None:
    preflight = _preflight()
    result = build_future_shadow_runtime_execution_bridge(
        preflight_report=preflight,
        facts_by_trace_id=_facts(preflight),
    )
    assert result["pair_count"] == 7
    assert result["trace_count"] == 14
    assert result["evidence_count"] == 14
    assert len(result["pair_plans"]) == 7
    assert len(result["evidence_rows"]) == 14
    assert result["facts_are_explicit"] is True
    assert result["facts_inferred_from_preflight"] is False


def test_missing_extra_and_invalid_facts_fail_closed() -> None:
    preflight = _preflight()
    missing = _facts(preflight)
    missing.pop(next(iter(missing)))
    with pytest.raises(ValueError, match="facts_missing"):
        build_future_shadow_runtime_execution_bridge(preflight_report=preflight, facts_by_trace_id=missing)

    extra = _facts(preflight)
    extra["trace:extra"] = next(iter(extra.values()))
    with pytest.raises(ValueError, match="facts_extra"):
        build_future_shadow_runtime_execution_bridge(preflight_report=preflight, facts_by_trace_id=extra)

    invalid = _facts(preflight)
    invalid[next(iter(invalid))] = object()
    with pytest.raises(ValueError, match="fact_contract_invalid"):
        build_future_shadow_runtime_execution_bridge(preflight_report=preflight, facts_by_trace_id=invalid)


def test_tampered_preflight_pair_or_trace_plan_fails_closed() -> None:
    preflight = dict(_preflight())
    pairs = [dict(item) for item in preflight["pairs"]]
    pairs[0]["source_bundle_id"] = pairs[1]["source_bundle_id"]
    preflight["pairs"] = tuple(pairs)
    with pytest.raises(ValueError, match="source_bundle_id_duplicate"):
        build_future_shadow_runtime_execution_bridge(preflight_report=preflight, facts_by_trace_id=_facts(_preflight()))

    preflight = dict(_preflight())
    pairs = [dict(item) for item in preflight["pairs"]]
    trace_plan = dict(pairs[0]["trace_plan"])
    trace_plan["trace_ids"] = ("tampered",)
    pairs[0]["trace_plan"] = trace_plan
    preflight["pairs"] = tuple(pairs)
    with pytest.raises(ValueError, match="trace_plan_identity_mismatch"):
        build_future_shadow_runtime_execution_bridge(preflight_report=preflight, facts_by_trace_id=_facts(_preflight()))


def test_slot_forecast_and_report_identity_mismatches_fail_closed() -> None:
    preflight = dict(_preflight())
    pairs = [dict(item) for item in preflight["pairs"]]
    forecasts = [dict(row) for row in pairs[0]["forecasts"]]
    forecasts[0]["target_horizon_sec"] = int(pairs[1]["slot_identity"]["target_horizon_sec"])
    pairs[0]["forecasts"] = tuple(forecasts)
    preflight["pairs"] = tuple(pairs)
    with pytest.raises(ValueError, match="slot_forecast_horizon_mismatch"):
        build_future_shadow_runtime_execution_bridge(
            preflight_report=preflight,
            facts_by_trace_id=_facts(_preflight()),
        )

    preflight = dict(_preflight())
    preflight["prediction_origin"] = "2026-07-14T00:01:00Z"
    with pytest.raises(ValueError, match="report_origin_mismatch"):
        build_future_shadow_runtime_execution_bridge(
            preflight_report=preflight,
            facts_by_trace_id=_facts(_preflight()),
        )

    preflight = dict(_preflight())
    preflight["feature_snapshot_ref"] = "snapshot:tampered"
    with pytest.raises(ValueError, match="report_snapshot_mismatch"):
        build_future_shadow_runtime_execution_bridge(
            preflight_report=preflight,
            facts_by_trace_id=_facts(_preflight()),
        )


def test_unsafe_preflight_flags_fail_closed() -> None:
    preflight = dict(_preflight())
    preflight["writes_dhot"] = True
    with pytest.raises(ValueError, match="unsafe_preflight_flag:writes_dhot"):
        build_future_shadow_runtime_execution_bridge(preflight_report=preflight, facts_by_trace_id=_facts(_preflight()))


def test_output_is_read_only_and_never_promotes_or_writes() -> None:
    preflight = _preflight()
    result = build_future_shadow_runtime_execution_bridge(
        preflight_report=preflight,
        facts_by_trace_id=_facts(preflight),
    )
    with pytest.raises(TypeError):
        result["pair_count"] = 0
    safety = result["safety"]
    assert safety["legacy_confidence_promoted_to_probability"] is False
    assert safety["writer_invoked"] is False
    assert safety["writes_dhot"] is False
    assert safety["scheduler_enabled"] is False
    assert safety["parameter_auto_promotion_allowed"] is False
    assert safety["live_parameter_apply_allowed"] is False
    assert safety["broker_private_api_allowed"] is False
    assert safety["autotrade_trigger_allowed"] is False
    assert safety["order_intent_submitted"] is False
