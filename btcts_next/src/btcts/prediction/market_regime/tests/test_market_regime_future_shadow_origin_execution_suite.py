# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_origin_execution_suite.py
# desc: MR-F9.2 guards for canonical seven-horizon, fourteen-row origin execution completeness.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence
from btcts.prediction.market_regime.future_execution_evidence import FutureInferenceMode, RawOutputSemantics
from btcts.prediction.market_regime.future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from btcts.prediction.market_regime.future_shadow_candidate_pairing import build_future_shadow_candidate_pair
from btcts.prediction.market_regime.future_shadow_origin_execution_suite import build_future_shadow_origin_execution_suite
from btcts.prediction.market_regime.future_shadow_pair_execution_plan import FutureExecutionFacts


def _evidence_by_horizon(*, origin: str = "2026-07-16T02:00:00Z", snapshot: str = "snapshot:mr-f9.2"):
    result = {}
    for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC:
        families = ("price_structure", "volatility", "liquidity", "source_quality", "microprice", "session_context")
        result[int(horizon)] = FutureBaselineEvidence(
            origin_timestamp=origin,
            origin_current_state=MarketRegimeCode.RANGE,
            target_horizon_sec=int(horizon),
            feature_snapshot_ref=snapshot,
            regime_scores={MarketRegimeCode.BREAKOUT: 0.61, MarketRegimeCode.RANGE: 0.39},
            available_feature_families=families,
            source_timestamp_epoch_sec=100.0,
            origin_timestamp_epoch_sec=102.0,
        )
    return result


def _facts(evidence_by_horizon):
    result = {}
    for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC:
        pair = build_future_shadow_candidate_pair(evidence=evidence_by_horizon[int(horizon)])
        for row in pair["forecasts"]:
            result[row["trace_id"]] = FutureExecutionFacts(
                inference_mode=FutureInferenceMode.FULL_INFERENCE,
                raw_output_semantics=RawOutputSemantics.SCORE,
                source_freshness_state="FRESH",
                source_age_sec=2.0,
            )
    return result


def test_builds_seven_horizon_fourteen_evidence_origin_suite() -> None:
    evidence = _evidence_by_horizon()
    result = build_future_shadow_origin_execution_suite(
        evidence_by_horizon=evidence,
        facts_by_trace_id=_facts(evidence),
    )
    assert result["horizon_count"] == 7
    assert result["pair_count"] == 7
    assert result["candidate_count"] == 2
    assert result["evidence_count"] == 14
    assert len(result["trace_persistence_plans"]) == 7
    assert len(result["trace_ids"]) == 14
    assert result["would_write"] is False


def test_missing_horizon_fails_closed() -> None:
    evidence = _evidence_by_horizon()
    evidence.pop(86400)
    with pytest.raises(ValueError, match="horizon_set_mismatch"):
        build_future_shadow_origin_execution_suite(evidence_by_horizon=evidence, facts_by_trace_id={})


def test_mixed_origin_fails_closed() -> None:
    evidence = _evidence_by_horizon()
    evidence[300] = _evidence_by_horizon(origin="2026-07-16T02:01:00Z")[300]
    with pytest.raises(ValueError, match="origin_mismatch"):
        build_future_shadow_origin_execution_suite(evidence_by_horizon=evidence, facts_by_trace_id={})


def test_mixed_snapshot_fails_closed() -> None:
    evidence = _evidence_by_horizon()
    evidence[900] = _evidence_by_horizon(snapshot="snapshot:other")[900]
    with pytest.raises(ValueError, match="snapshot_mismatch"):
        build_future_shadow_origin_execution_suite(evidence_by_horizon=evidence, facts_by_trace_id={})


def test_missing_trace_fact_fails_closed() -> None:
    evidence = _evidence_by_horizon()
    facts = _facts(evidence)
    facts.pop(next(iter(facts)))
    with pytest.raises(ValueError, match="facts_missing"):
        build_future_shadow_origin_execution_suite(evidence_by_horizon=evidence, facts_by_trace_id=facts)


def test_extra_trace_fact_fails_closed() -> None:
    evidence = _evidence_by_horizon()
    facts = _facts(evidence)
    facts["extra"] = next(iter(facts.values()))
    with pytest.raises(ValueError, match="facts_extra"):
        build_future_shadow_origin_execution_suite(evidence_by_horizon=evidence, facts_by_trace_id=facts)
