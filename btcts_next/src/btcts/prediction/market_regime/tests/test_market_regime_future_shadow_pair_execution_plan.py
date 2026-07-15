# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_pair_execution_plan.py
# desc: MR-F9.1B guards for explicit, complete, fail-closed execution facts joined to paired forecasts.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence
from btcts.prediction.market_regime.future_execution_evidence import FutureInferenceMode, RawOutputSemantics
from btcts.prediction.market_regime.future_shadow_candidate_pairing import build_future_shadow_candidate_pair
from btcts.prediction.market_regime.future_shadow_pair_execution_plan import (
    FutureExecutionFacts,
    build_future_shadow_pair_execution_plan,
)


def _pair(*, low_scores: bool = False) -> dict:
    scores = (
        {MarketRegimeCode.BREAKOUT: 0.34, MarketRegimeCode.RANGE: 0.33, MarketRegimeCode.UP_TREND: 0.33}
        if low_scores
        else {MarketRegimeCode.BREAKOUT: 0.61, MarketRegimeCode.RANGE: 0.25, MarketRegimeCode.UP_TREND: 0.14}
    )
    evidence = FutureBaselineEvidence(
        origin_timestamp="2026-07-16T01:00:00Z",
        origin_current_state=MarketRegimeCode.RANGE,
        target_horizon_sec=900,
        feature_snapshot_ref="snapshot:mr-f9.1b",
        regime_scores=scores,
        available_feature_families=("price_structure", "volatility", "liquidity", "source_quality", "microprice"),
        source_timestamp_epoch_sec=100.0,
        origin_timestamp_epoch_sec=102.0,
    )
    return dict(build_future_shadow_candidate_pair(evidence=evidence))


def _facts(pair: dict, *, mode: FutureInferenceMode = FutureInferenceMode.FULL_INFERENCE):
    result = {}
    for row in pair["forecasts"]:
        result[row["trace_id"]] = FutureExecutionFacts(
            inference_mode=mode,
            raw_output_semantics=RawOutputSemantics.SCORE,
            source_freshness_state="FRESH",
            source_age_sec=2.0,
            fallback_reason="compatibility_fallback" if mode is FutureInferenceMode.FALLBACK else "",
            fallback_source_ref="compat:l4" if mode is FutureInferenceMode.FALLBACK else "",
        )
    return result


def test_builds_complete_pair_execution_plan_without_writes() -> None:
    pair = _pair()
    result = build_future_shadow_pair_execution_plan(pair=pair, facts_by_trace_id=_facts(pair))
    assert result["evidence_count"] == 2
    assert result["pair_id"] == pair["pair_id"]
    assert result["would_write"] is False
    assert result["safety"]["facts_are_explicit"] is True
    assert result["safety"]["facts_inferred_from_display"] is False
    assert all(row["raw_output_semantics"] == "SCORE" for row in result["rows"])


def test_missing_fact_fails_closed() -> None:
    pair = _pair()
    facts = _facts(pair)
    facts.pop(next(iter(facts)))
    with pytest.raises(ValueError, match="facts_missing"):
        build_future_shadow_pair_execution_plan(pair=pair, facts_by_trace_id=facts)


def test_extra_fact_fails_closed() -> None:
    pair = _pair()
    facts = _facts(pair)
    facts["extra"] = next(iter(facts.values()))
    with pytest.raises(ValueError, match="facts_extra"):
        build_future_shadow_pair_execution_plan(pair=pair, facts_by_trace_id=facts)


def test_fallback_is_explicit_for_each_trace() -> None:
    pair = _pair()
    result = build_future_shadow_pair_execution_plan(
        pair=pair,
        facts_by_trace_id=_facts(pair, mode=FutureInferenceMode.FALLBACK),
    )
    assert all(row["fallback_used"] is True for row in result["rows"])
    assert all(row["fallback_reason"] == "compatibility_fallback" for row in result["rows"])


def test_abstention_cannot_be_mislabeled_as_abstained_without_inference() -> None:
    pair = _pair(low_scores=True)
    facts = _facts(pair)
    abstained = [row for row in pair["forecasts"] if row["forecast_status"] == "ABSTAIN"]
    assert abstained
    facts[abstained[0]["trace_id"]] = FutureExecutionFacts(
        inference_mode=FutureInferenceMode.ABSTAINED_WITHOUT_INFERENCE,
        raw_output_semantics=RawOutputSemantics.UNSPECIFIED,
        source_freshness_state="FRESH",
        source_age_sec=2.0,
    )
    result = build_future_shadow_pair_execution_plan(pair=pair, facts_by_trace_id=facts)
    selected = next(row for row in result["rows"] if row["trace_id"] == abstained[0]["trace_id"])
    assert selected["abstention_decision"] is True
    assert selected["inference_mode"] == "ABSTAINED_WITHOUT_INFERENCE"


def test_tampered_slot_identity_fails_closed() -> None:
    pair = _pair()
    facts = _facts(pair)
    rows = [dict(item) for item in pair["forecasts"]]
    rows[0]["feature_snapshot_ref"] = "tampered"
    pair["forecasts"] = tuple(rows)
    with pytest.raises(ValueError, match="slot_identity_mismatch"):
        build_future_shadow_pair_execution_plan(pair=pair, facts_by_trace_id=facts)
