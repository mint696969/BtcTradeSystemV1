# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_origin_receipt.py
# desc: MR-F9.4 guards for identical trace and execution-evidence sets in an origin receipt.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence
from btcts.prediction.market_regime.future_execution_evidence import FutureInferenceMode, RawOutputSemantics
from btcts.prediction.market_regime.future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from btcts.prediction.market_regime.future_shadow_candidate_pairing import build_future_shadow_candidate_pair
from btcts.prediction.market_regime.future_shadow_origin_execution_suite import build_future_shadow_origin_execution_suite
from btcts.prediction.market_regime.future_shadow_origin_receipt import build_future_shadow_origin_receipt
from btcts.prediction.market_regime.future_shadow_pair_execution_plan import FutureExecutionFacts


def _suite():
    evidence = {}
    facts = {}
    for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC:
        item = FutureBaselineEvidence(
            origin_timestamp="2026-07-16T04:00:00Z",
            origin_current_state=MarketRegimeCode.RANGE,
            target_horizon_sec=int(horizon),
            feature_snapshot_ref="snapshot:mr-f9.4",
            regime_scores={MarketRegimeCode.BREAKOUT: 0.61, MarketRegimeCode.RANGE: 0.39},
            available_feature_families=(
                "price_structure", "volatility", "liquidity", "source_quality",
                "microprice", "session_context",
            ),
            source_timestamp_epoch_sec=100.0,
            origin_timestamp_epoch_sec=102.0,
        )
        evidence[int(horizon)] = item
        pair = build_future_shadow_candidate_pair(evidence=item)
        for row in pair["forecasts"]:
            facts[row["trace_id"]] = FutureExecutionFacts(
                inference_mode=FutureInferenceMode.FULL_INFERENCE,
                raw_output_semantics=RawOutputSemantics.SCORE,
                source_freshness_state="FRESH",
                source_age_sec=2.0,
            )
    return build_future_shadow_origin_execution_suite(
        evidence_by_horizon=evidence,
        facts_by_trace_id=facts,
    )


def test_receipt_binds_seven_trace_plans_and_fourteen_execution_rows() -> None:
    result = build_future_shadow_origin_receipt(origin_suite=_suite())
    assert result["horizon_count"] == 7
    assert result["pair_count"] == 7
    assert result["trace_count"] == 14
    assert result["execution_evidence_count"] == 14
    assert len(result["trace_ids"]) == 14
    assert len(result["receipt_id"].rsplit(":", 1)[-1]) == 32
    assert result["safety"]["trace_and_execution_sets_identical"] is True
    assert result["would_write"] is False


def test_each_trace_plan_is_disabled_and_has_two_rows() -> None:
    result = build_future_shadow_origin_receipt(origin_suite=_suite())
    assert all(plan["trace_count"] == 2 for plan in result["trace_persistence_plans"])
    assert all(plan["persistence_plan"]["disabled_by_default"] is True for plan in result["trace_persistence_plans"])
    assert result["execution_evidence_persistence_plan"]["disabled_by_default"] is True


def test_tampered_suite_trace_set_fails_closed() -> None:
    suite = dict(_suite())
    suite["trace_ids"] = tuple(reversed(suite["trace_ids"]))
    with pytest.raises(ValueError, match="trace_set_mismatch"):
        build_future_shadow_origin_receipt(origin_suite=suite)


def test_tampered_pair_count_fails_closed() -> None:
    suite = dict(_suite())
    suite["pair_count"] = 6
    with pytest.raises(ValueError, match="pair_count_mismatch"):
        build_future_shadow_origin_receipt(origin_suite=suite)


def test_missing_pair_row_fails_closed() -> None:
    suite = dict(_suite())
    plans = list(suite["pair_plans"])
    first = dict(plans[0])
    first["rows"] = tuple(first["rows"][:-1])
    plans[0] = first
    suite["pair_plans"] = tuple(plans)
    with pytest.raises(ValueError):
        build_future_shadow_origin_receipt(origin_suite=suite)
