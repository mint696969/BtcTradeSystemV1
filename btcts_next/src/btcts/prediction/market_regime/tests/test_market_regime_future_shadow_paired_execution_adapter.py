# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_paired_execution_adapter.py
# desc: MR-F9.11 guards for pure 14-slot active/shadow execution adaptation with explicit facts only.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, MarketRegimeCode, SourceCoverage
from btcts.prediction.market_regime.features import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.future_execution_evidence import FutureInferenceMode, RawOutputSemantics
from btcts.prediction.market_regime.future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from btcts.prediction.market_regime.future_shadow_candidate_registry import (
    BASELINE_CANDIDATE,
    CONSERVATIVE_CANDIDATE,
)
from btcts.prediction.market_regime.future_shadow_pair_execution_plan import FutureExecutionFacts
from btcts.prediction.market_regime.future_shadow_paired_execution_adapter import (
    build_future_shadow_paired_execution_adapter,
)

CANDIDATES = (BASELINE_CANDIDATE, CONSERVATIVE_CANDIDATE)


def _bundle() -> MarketRegimeFeatureBundle:
    groups = (
        FeatureGroup.PRICE_STRUCTURE,
        FeatureGroup.VOLATILITY,
        FeatureGroup.LIQUIDITY,
        FeatureGroup.SOURCE_QUALITY,
    )
    coverage = tuple(
        SourceCoverage(group, True, FreshnessState.LIVE, used_sources=(f"source:{group.value}",))
        for group in groups
    )
    signals = tuple(
        FeatureSignal(group, f"signal_{group.value}", 1.0, True, source_refs=(f"ref:{group.value}",))
        for group in groups
    ) + (
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "session_context", "asia", True, source_refs=("ref:session",)),
    )
    return MarketRegimeFeatureBundle(
        generated_at="2026-07-16T03:00:00Z",
        signals=signals,
        coverage=coverage,
        source_snapshot_ok=True,
    )


def _report() -> dict:
    return {
        "market_regime_only": True,
        "horizons": [
            {
                "horizon_sec": horizon,
                "horizon_key": f"{horizon}s",
                "regime_scores": {"BREAKOUT": 0.61, "RANGE": 0.25, "UP_TREND": 0.14},
            }
            for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC
        ],
    }


def _facts() -> dict:
    return {
        (horizon, candidate.parameter_set_id): FutureExecutionFacts(
            inference_mode=FutureInferenceMode.FULL_INFERENCE,
            raw_output_semantics=RawOutputSemantics.SCORE,
            source_freshness_state="FRESH",
            source_age_sec=2.0,
        )
        for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC
        for candidate in CANDIDATES
    }


def _build(facts=None):
    return build_future_shadow_paired_execution_adapter(
        feature_bundle=_bundle(),
        signal_score_report=_report(),
        origin_current_state=MarketRegimeCode.RANGE,
        origin_timestamp_epoch_sec=102.0,
        source_timestamp_epoch_sec=100.0,
        facts_by_slot=_facts() if facts is None else facts,
        candidates=CANDIDATES,
    )


def test_builds_exact_seven_pairs_and_fourteen_execution_rows() -> None:
    result = _build()
    assert result["pair_count"] == 7
    assert result["trace_count"] == 14
    assert result["evidence_count"] == 14
    assert len(result["pair_plans"]) == 7
    assert len(result["evidence_rows"]) == 14
    assert {row["target_horizon_sec"] for row in result["evidence_rows"]} == set(FUTURE_MARKET_REGIME_HORIZONS_SEC)
    assert {row["parameter_set_id"] for row in result["evidence_rows"]} == {
        candidate.parameter_set_id for candidate in CANDIDATES
    }


def test_facts_are_explicit_and_score_is_not_promoted_to_probability() -> None:
    result = _build()
    assert all(row["raw_output_semantics"] == "SCORE" for row in result["evidence_rows"])
    assert result["safety"]["facts_are_explicit"] is True
    assert result["safety"]["facts_inferred_from_display"] is False
    assert result["safety"]["legacy_confidence_promoted_to_probability"] is False
    assert result["would_write"] is False
    assert result["safety"]["writes_dhot"] is False


def test_missing_and_extra_fact_slots_fail_closed() -> None:
    missing = _facts()
    missing.pop(next(iter(missing)))
    with pytest.raises(ValueError, match="facts_missing"):
        _build(missing)

    extra = _facts()
    extra[(999, BASELINE_CANDIDATE.parameter_set_id)] = next(iter(extra.values()))
    with pytest.raises(ValueError, match="facts_extra"):
        _build(extra)


def test_fact_contract_and_registry_fail_closed() -> None:
    invalid = _facts()
    invalid[next(iter(invalid))] = object()
    with pytest.raises(ValueError, match="fact_contract_invalid"):
        _build(invalid)

    with pytest.raises(ValueError, match="registry_invalid"):
        build_future_shadow_paired_execution_adapter(
            feature_bundle=_bundle(),
            signal_score_report=_report(),
            origin_current_state=MarketRegimeCode.RANGE,
            origin_timestamp_epoch_sec=102.0,
            source_timestamp_epoch_sec=100.0,
            facts_by_slot=_facts(),
            candidates=(BASELINE_CANDIDATE,),
        )


def test_registry_requires_exactly_one_active_and_one_shadow() -> None:
    extra_shadow = CONSERVATIVE_CANDIDATE.__class__(
        parameter_set_id="market_regime.future.transparent_baseline.params.extra_shadow.v1",
        short_horizon_minimum_top=0.45,
        short_horizon_minimum_margin=0.15,
        long_horizon_minimum_top=0.40,
        long_horizon_minimum_margin=0.12,
        transition_prior_fraction_of_top=0.10,
        registry_state="shadow",
    )
    facts = _facts()
    facts.update({
        (horizon, extra_shadow.parameter_set_id): FutureExecutionFacts(
            inference_mode=FutureInferenceMode.FULL_INFERENCE,
            raw_output_semantics=RawOutputSemantics.SCORE,
            source_freshness_state="FRESH",
            source_age_sec=2.0,
        )
        for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC
    })
    with pytest.raises(ValueError, match="candidate_pair_count_invalid"):
        build_future_shadow_paired_execution_adapter(
            feature_bundle=_bundle(),
            signal_score_report=_report(),
            origin_current_state=MarketRegimeCode.RANGE,
            origin_timestamp_epoch_sec=102.0,
            source_timestamp_epoch_sec=100.0,
            facts_by_slot=facts,
            candidates=(BASELINE_CANDIDATE, CONSERVATIVE_CANDIDATE, extra_shadow),
        )


def test_candidate_input_order_is_canonicalized_active_then_shadow() -> None:
    canonical = _build()
    reversed_result = build_future_shadow_paired_execution_adapter(
        feature_bundle=_bundle(),
        signal_score_report=_report(),
        origin_current_state=MarketRegimeCode.RANGE,
        origin_timestamp_epoch_sec=102.0,
        source_timestamp_epoch_sec=100.0,
        facts_by_slot=_facts(),
        candidates=tuple(reversed(CANDIDATES)),
    )
    assert reversed_result["candidate_ids"] == canonical["candidate_ids"]
    assert tuple(plan["pair_id"] for plan in reversed_result["pair_plans"]) == tuple(
        plan["pair_id"] for plan in canonical["pair_plans"]
    )
    assert tuple(row["trace_id"] for row in reversed_result["evidence_rows"]) == tuple(
        row["trace_id"] for row in canonical["evidence_rows"]
    )


def test_output_is_immutable_and_never_enables_runtime_paths() -> None:
    result = _build()
    with pytest.raises(TypeError):
        result["pair_count"] = 0
    safety = result["safety"]
    assert safety["scheduler_enabled"] is False
    assert safety["parameter_auto_promotion_allowed"] is False
    assert safety["live_parameter_apply_allowed"] is False
    assert safety["broker_private_api_allowed"] is False
    assert safety["autotrade_trigger_allowed"] is False
    assert safety["order_intent_submitted"] is False
