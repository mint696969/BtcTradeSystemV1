# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_outcome.py
# desc: MR-F5.6 pure outcome-resolution contract tests.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence, forecast_future_market_regime_baseline
from btcts.prediction.market_regime.future_shadow_outcome import FutureShadowOutcomeEvidence, FutureShadowOutcomeStatus, resolve_market_regime_future_shadow_outcome
from btcts.prediction.market_regime.future_trace_identity import build_market_regime_future_trace_identity


def _trace(*, horizon: int = 300, missing_session: bool = False):
    families = ("price_structure", "volatility", "liquidity", "microprice", "source_quality")
    if not missing_session:
        families += ("session_context",)
    forecast = forecast_future_market_regime_baseline(FutureBaselineEvidence(
        origin_timestamp="2026-07-12T00:00:00Z", origin_current_state=MarketRegimeCode.LOW_VOL_COMPRESSION,
        target_horizon_sec=horizon, feature_snapshot_ref="snapshot:abc",
        regime_scores={MarketRegimeCode.BREAKOUT: 0.8, MarketRegimeCode.RANGE: 0.2},
        available_feature_families=families, source_timestamp_epoch_sec=100.0, origin_timestamp_epoch_sec=100.0,
    ))
    return build_market_regime_future_trace_identity(forecast)


def _evidence(**overrides):
    values = dict(resolved_at="2026-07-12T00:06:00Z", observation_available=True, observed_at="2026-07-12T00:05:30Z", observed_future_state=MarketRegimeCode.BREAKOUT, observation_source_ref="observation:test")
    values.update(overrides)
    return FutureShadowOutcomeEvidence(**values)


def test_correct_outcome_and_evaluation_row_preserve_full_identity() -> None:
    outcome = resolve_market_regime_future_shadow_outcome(trace=_trace(), evidence=_evidence())
    assert outcome.status is FutureShadowOutcomeStatus.CORRECT
    row = outcome.to_evaluation_row()
    assert row["target_definition_version"] == "market_regime_target.300s.v1"
    assert row["feature_snapshot_ref"] == "snapshot:abc"
    assert row["ledger_append_allowed"] is False
    with pytest.raises(TypeError): row["outcome_status"] = "tampered"


def test_unexpired_or_missing_observation_is_unresolved() -> None:
    assert resolve_market_regime_future_shadow_outcome(trace=_trace(), evidence=_evidence(resolved_at="2026-07-12T00:04:59Z", observed_at="2026-07-12T00:04:30Z")).status is FutureShadowOutcomeStatus.UNRESOLVED
    assert resolve_market_regime_future_shadow_outcome(trace=_trace(), evidence=_evidence(observation_available=False, observed_at="", observed_future_state=MarketRegimeCode.UNKNOWN, observation_source_ref="")).reason == "observation_unavailable"


def test_abstained_forecast_is_not_scored() -> None:
    outcome = resolve_market_regime_future_shadow_outcome(trace=_trace(horizon=21600, missing_session=True), evidence=FutureShadowOutcomeEvidence(resolved_at="2026-07-12T07:00:00Z", observation_available=False))
    assert outcome.status is FutureShadowOutcomeStatus.ABSTAINED


def test_invalidated_and_outside_tolerance_are_distinct() -> None:
    explicit = resolve_market_regime_future_shadow_outcome(trace=_trace(), evidence=_evidence(invalidated=True, invalidation_reason="source_gap"))
    assert explicit.status is FutureShadowOutcomeStatus.INVALIDATED
    assert explicit.reason == "source_gap"
    late = resolve_market_regime_future_shadow_outcome(trace=_trace(), evidence=_evidence(resolved_at="2026-07-12T00:06:30Z", observed_at="2026-07-12T00:06:01Z"))
    assert late.status is FutureShadowOutcomeStatus.INVALIDATED
    assert late.reason == "observation_outside_target_tolerance"


def test_transition_adjacent_is_partial_and_nonadjacent_is_incorrect() -> None:
    partial = resolve_market_regime_future_shadow_outcome(trace=_trace(), evidence=_evidence(observed_future_state=MarketRegimeCode.UP_TREND))
    assert partial.status is FutureShadowOutcomeStatus.PARTIAL
    incorrect = resolve_market_regime_future_shadow_outcome(trace=_trace(), evidence=_evidence(observed_future_state=MarketRegimeCode.PANIC_SPIKE))
    assert incorrect.status is FutureShadowOutcomeStatus.INCORRECT


def test_noncanonical_or_future_observation_timestamps_fail_closed() -> None:
    with pytest.raises(ValueError, match="future_shadow_outcome_resolved_at_not_canonical_utc"):
        _evidence(resolved_at="2026-07-12T09:06:00+09:00")
    with pytest.raises(ValueError, match="future_shadow_outcome_observed_at_not_canonical_utc"):
        _evidence(observed_at="2026-07-12T09:05:30+09:00")
    with pytest.raises(ValueError, match="future_shadow_outcome_observed_after_resolved"):
        _evidence(resolved_at="2026-07-12T00:05:10Z", observed_at="2026-07-12T00:05:30Z")


def test_unknown_observation_and_invalid_evidence_fail_closed() -> None:
    unknown = resolve_market_regime_future_shadow_outcome(trace=_trace(), evidence=_evidence(observed_future_state=MarketRegimeCode.UNKNOWN))
    assert unknown.status is FutureShadowOutcomeStatus.UNRESOLVED
    with pytest.raises(ValueError, match="future_shadow_outcome_invalidation_reason_missing"):
        _evidence(invalidated=True, invalidation_reason="")
