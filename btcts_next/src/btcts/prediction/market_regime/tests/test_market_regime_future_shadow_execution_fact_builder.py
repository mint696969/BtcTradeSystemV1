# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_execution_fact_builder.py
# desc: MR-F9.13 guards for explicit 14-trace invocation observations to execution facts without inference or writes.

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, MarketRegimeCode, SourceCoverage
from btcts.prediction.market_regime.features import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.future_execution_evidence import FutureInferenceMode, RawOutputSemantics
from btcts.prediction.market_regime.future_forecast_contract import FutureForecastStatus
from btcts.prediction.market_regime.future_origin_feature_runtime_bundle import build_market_regime_origin_feature_runtime_bundle
from btcts.prediction.market_regime.future_shadow_adapter import build_market_regime_future_shadow_packet
from btcts.prediction.market_regime.future_shadow_execution_fact_builder import (
    FutureExecutionObservation,
    build_future_shadow_execution_facts,
)
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
    return build_future_shadow_runtime_preflight_report(packet=packet, signal_score_report=report, runtime_bundle=runtime)


def _observation_from_row(row):
    status = FutureForecastStatus(str(row["forecast_status"]))
    abstained = status is FutureForecastStatus.ABSTAIN
    return FutureExecutionObservation(
        trace_id=str(row["trace_id"]),
        prediction_origin=str(row["origin_timestamp"]),
        feature_snapshot_ref=str(row["feature_snapshot_ref"]),
        target_horizon_sec=int(row["target_horizon_sec"]),
        parameter_set_id=str(row["parameter_set_id"]),
        inference_mode=(
            FutureInferenceMode.ABSTAINED_WITHOUT_INFERENCE
            if abstained
            else FutureInferenceMode.FULL_INFERENCE
        ),
        raw_output_semantics=(
            RawOutputSemantics.UNSPECIFIED
            if abstained
            else RawOutputSemantics.SCORE
        ),
        source_freshness_state="FRESH",
        source_age_sec=60.0,
    )


def _observations(preflight=None):
    report = _preflight() if preflight is None else preflight
    return tuple(
        _observation_from_row(row)
        for pair in report["pairs"]
        for row in pair["forecasts"]
    )


def _first_predicted_observation_index(preflight):
    rows = [row for pair in preflight["pairs"] for row in pair["forecasts"]]
    for index, row in enumerate(rows):
        if FutureForecastStatus(str(row["forecast_status"])) is not FutureForecastStatus.ABSTAIN:
            return index
    raise AssertionError("predicted observation fixture missing")


def test_builds_exact_fourteen_facts_and_feeds_runtime_bridge() -> None:
    preflight = _preflight()
    built = build_future_shadow_execution_facts(preflight_report=preflight, observations=_observations(preflight))
    assert built["trace_count"] == 14
    assert len(built["facts_by_trace_id"]) == 14
    result = build_future_shadow_runtime_execution_bridge(
        preflight_report=preflight,
        facts_by_trace_id=built["facts_by_trace_id"],
    )
    assert result["pair_count"] == 7
    assert result["evidence_count"] == 14


def test_fixture_preserves_explicit_abstention_and_predicted_modes() -> None:
    preflight = _preflight()
    observations = _observations(preflight)
    rows = [row for pair in preflight["pairs"] for row in pair["forecasts"]]
    assert any(
        FutureForecastStatus(str(row["forecast_status"])) is FutureForecastStatus.ABSTAIN
        for row in rows
    )
    for row, observation in zip(rows, observations, strict=True):
        status = FutureForecastStatus(str(row["forecast_status"]))
        if status is FutureForecastStatus.ABSTAIN:
            assert observation.inference_mode is FutureInferenceMode.ABSTAINED_WITHOUT_INFERENCE
            assert observation.raw_output_semantics is RawOutputSemantics.UNSPECIFIED
        else:
            assert observation.inference_mode is FutureInferenceMode.FULL_INFERENCE
            assert observation.raw_output_semantics is RawOutputSemantics.SCORE


def test_missing_extra_duplicate_and_identity_mismatch_fail_closed() -> None:
    preflight = _preflight()
    observations = list(_observations(preflight))
    with pytest.raises(ValueError, match="observations_missing"):
        build_future_shadow_execution_facts(preflight_report=preflight, observations=observations[:-1])

    extra = FutureExecutionObservation(
        trace_id="trace:extra",
        prediction_origin=observations[0].prediction_origin,
        feature_snapshot_ref=observations[0].feature_snapshot_ref,
        target_horizon_sec=observations[0].target_horizon_sec,
        parameter_set_id=observations[0].parameter_set_id,
        inference_mode=FutureInferenceMode.FULL_INFERENCE,
        raw_output_semantics=RawOutputSemantics.SCORE,
        source_freshness_state="FRESH",
        source_age_sec=60.0,
    )
    with pytest.raises(ValueError, match="observations_extra"):
        build_future_shadow_execution_facts(preflight_report=preflight, observations=tuple(observations) + (extra,))

    with pytest.raises(ValueError, match="observation_trace_duplicate"):
        build_future_shadow_execution_facts(preflight_report=preflight, observations=tuple(observations) + (observations[0],))

    wrong = list(observations)
    first = wrong[0]
    wrong[0] = FutureExecutionObservation(
        trace_id=first.trace_id,
        prediction_origin=first.prediction_origin,
        feature_snapshot_ref=first.feature_snapshot_ref,
        target_horizon_sec=first.target_horizon_sec,
        parameter_set_id="candidate:wrong",
        inference_mode=first.inference_mode,
        raw_output_semantics=first.raw_output_semantics,
        source_freshness_state=first.source_freshness_state,
        source_age_sec=first.source_age_sec,
    )
    with pytest.raises(ValueError, match="observation_identity_mismatch"):
        build_future_shadow_execution_facts(preflight_report=preflight, observations=wrong)


def test_raw_semantics_and_forecast_mode_are_not_inferred() -> None:
    preflight = _preflight()
    observations = list(_observations(preflight))
    index = _first_predicted_observation_index(preflight)
    first = observations[index]
    observations[index] = FutureExecutionObservation(
        trace_id=first.trace_id,
        prediction_origin=first.prediction_origin,
        feature_snapshot_ref=first.feature_snapshot_ref,
        target_horizon_sec=first.target_horizon_sec,
        parameter_set_id=first.parameter_set_id,
        inference_mode=first.inference_mode,
        raw_output_semantics=RawOutputSemantics.UNSPECIFIED,
        source_freshness_state=first.source_freshness_state,
        source_age_sec=first.source_age_sec,
    )
    with pytest.raises(ValueError, match="raw_output_semantics_required"):
        build_future_shadow_execution_facts(preflight_report=preflight, observations=observations)

    observations = list(_observations(preflight))
    index = _first_predicted_observation_index(preflight)
    first = observations[index]
    observations[index] = FutureExecutionObservation(
        trace_id=first.trace_id,
        prediction_origin=first.prediction_origin,
        feature_snapshot_ref=first.feature_snapshot_ref,
        target_horizon_sec=first.target_horizon_sec,
        parameter_set_id=first.parameter_set_id,
        inference_mode=FutureInferenceMode.ABSTAINED_WITHOUT_INFERENCE,
        raw_output_semantics=first.raw_output_semantics,
        source_freshness_state=first.source_freshness_state,
        source_age_sec=first.source_age_sec,
    )
    with pytest.raises(ValueError, match="forecast_mode_mismatch"):
        build_future_shadow_execution_facts(preflight_report=preflight, observations=observations)


def test_fallback_requires_explicit_reason_and_source() -> None:
    with pytest.raises(ValueError, match="fallback_details_required"):
        FutureExecutionObservation(
            trace_id="trace:1",
            prediction_origin="2026-07-14T00:00:00Z",
            feature_snapshot_ref="snapshot:1",
            target_horizon_sec=300,
            parameter_set_id="candidate:1",
            inference_mode=FutureInferenceMode.FALLBACK,
            raw_output_semantics=RawOutputSemantics.SCORE,
            source_freshness_state="FRESH",
            source_age_sec=1.0,
        )


def test_output_is_immutable_and_never_writes_or_promotes() -> None:
    preflight = _preflight()
    built = build_future_shadow_execution_facts(preflight_report=preflight, observations=_observations(preflight))
    with pytest.raises(TypeError):
        built["trace_count"] = 0
    with pytest.raises(TypeError):
        built["facts_by_trace_id"][next(iter(built["facts_by_trace_id"]))] = object()
    assert built["observations_are_explicit"] is True
    assert built["facts_inferred_from_preflight"] is False
    assert built["facts_inferred_from_classifier_diagnostics"] is False
    assert built["legacy_confidence_promoted_to_probability"] is False
    safety = built["safety"]
    assert safety["writes_dhot"] is False
    assert safety["writer_invoked"] is False
    assert safety["scheduler_enabled"] is False
    assert safety["parameter_auto_promotion_allowed"] is False
    assert safety["live_parameter_apply_allowed"] is False
    assert safety["broker_private_api_allowed"] is False
    assert safety["autotrade_trigger_allowed"] is False
    assert safety["order_intent_submitted"] is False
