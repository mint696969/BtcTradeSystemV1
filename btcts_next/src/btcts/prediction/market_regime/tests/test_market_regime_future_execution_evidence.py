# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_execution_evidence.py
# desc: Pure MR-F9.1A guards for horizon execution evidence, raw-output semantics, fallback truth, and immutable trace linkage.

from __future__ import annotations

from dataclasses import replace

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence, forecast_future_market_regime_baseline
from btcts.prediction.market_regime.future_execution_evidence import (
    FutureInferenceMode,
    RawOutputSemantics,
    build_market_regime_future_execution_evidence,
)
from btcts.prediction.market_regime.future_trace_identity import build_market_regime_future_trace_identity


def _forecast(horizon: int = 900, *, long_ready: bool = True):
    families = ("price_structure", "volatility", "liquidity", "microprice", "source_quality")
    if long_ready:
        families += ("session_context",)
    return forecast_future_market_regime_baseline(FutureBaselineEvidence(
        origin_timestamp="2026-07-16T00:00:00Z",
        origin_current_state=MarketRegimeCode.RANGE,
        target_horizon_sec=horizon,
        feature_snapshot_ref="snapshot:mr-f9.1a",
        regime_scores={MarketRegimeCode.BREAKOUT: 0.61, MarketRegimeCode.RANGE: 0.39},
        available_feature_families=families,
        source_timestamp_epoch_sec=100.0,
        origin_timestamp_epoch_sec=102.0,
    ))


def test_full_inference_preserves_trace_and_does_not_claim_probability() -> None:
    forecast = _forecast()
    evidence = build_market_regime_future_execution_evidence(
        forecast,
        inference_mode=FutureInferenceMode.FULL_INFERENCE,
        raw_output_semantics=RawOutputSemantics.UNSPECIFIED,
        source_freshness_state="FRESH",
        source_age_sec=2.0,
    )
    assert evidence.trace_id == build_market_regime_future_trace_identity(forecast).trace_id
    assert evidence.raw_output_semantics is RawOutputSemantics.UNSPECIFIED
    assert evidence.fallback_used is False
    assert evidence.fallback_reason == ""
    assert evidence.calculation_fingerprint.startswith("market_regime_future_calculation:")
    assert evidence.to_dict()["parameter_auto_promotion_allowed"] is False
    assert evidence.to_dict()["live_parameter_apply_allowed"] is False


def test_fallback_requires_reason_and_source_reference() -> None:
    forecast = _forecast()
    with pytest.raises(ValueError, match="fallback_reason_required"):
        build_market_regime_future_execution_evidence(
            forecast,
            inference_mode=FutureInferenceMode.FALLBACK,
            source_freshness_state="STALE",
            source_age_sec=120.0,
            fallback_source_ref="compat:l4",
        )
    with pytest.raises(ValueError, match="fallback_source_ref_required"):
        build_market_regime_future_execution_evidence(
            forecast,
            inference_mode=FutureInferenceMode.FALLBACK,
            source_freshness_state="STALE",
            source_age_sec=120.0,
            fallback_reason="forecast_records_stale",
        )


def test_full_inference_rejects_fallback_fields() -> None:
    with pytest.raises(ValueError, match="non_fallback_disallows_fallback_fields"):
        build_market_regime_future_execution_evidence(
            _forecast(),
            inference_mode=FutureInferenceMode.FULL_INFERENCE,
            source_freshness_state="FRESH",
            source_age_sec=2.0,
            fallback_reason="not_allowed",
            fallback_source_ref="not_allowed",
        )


def test_long_horizon_abstention_can_record_no_inference_without_fabricating_output() -> None:
    forecast = _forecast(21600, long_ready=False)
    assert forecast.status.value == "ABSTAIN"
    evidence = build_market_regime_future_execution_evidence(
        forecast,
        inference_mode=FutureInferenceMode.ABSTAINED_WITHOUT_INFERENCE,
        source_freshness_state="FRESH",
        source_age_sec=2.0,
    )
    assert evidence.abstention_decision is True
    assert evidence.abstain_reason
    assert evidence.fallback_used is False


def test_probability_semantics_requires_a_value() -> None:
    forecast = replace(_forecast(), raw_model_score_or_probability=None)
    with pytest.raises(ValueError, match="probability_value_missing"):
        build_market_regime_future_execution_evidence(
            forecast,
            inference_mode=FutureInferenceMode.FULL_INFERENCE,
            raw_output_semantics=RawOutputSemantics.PROBABILITY,
            source_freshness_state="FRESH",
            source_age_sec=2.0,
        )


def test_output_mapping_is_immutable() -> None:
    evidence = build_market_regime_future_execution_evidence(
        _forecast(),
        inference_mode=FutureInferenceMode.FULL_INFERENCE,
        source_freshness_state="FRESH",
        source_age_sec=2.0,
    )
    payload = evidence.to_dict()
    with pytest.raises(TypeError):
        payload["fallback_used"] = True
