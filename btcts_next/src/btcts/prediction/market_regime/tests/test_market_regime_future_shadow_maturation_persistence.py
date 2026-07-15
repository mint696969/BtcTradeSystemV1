# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_maturation_persistence.py
# desc: MR-F9.6 guards for immutable duplicate-safe maturation snapshot persistence.

from __future__ import annotations

import json
from pathlib import Path

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence
from btcts.prediction.market_regime.future_execution_evidence import FutureInferenceMode, RawOutputSemantics
from btcts.prediction.market_regime.future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from btcts.prediction.market_regime.future_shadow_candidate_pairing import build_future_shadow_candidate_pair
from btcts.prediction.market_regime.future_shadow_maturation_cycle import build_future_shadow_maturation_cycle
from btcts.prediction.market_regime.future_shadow_maturation_persistence import (
    build_future_shadow_maturation_persistence_plan,
    persist_future_shadow_maturation_once,
)
from btcts.prediction.market_regime.future_shadow_origin_execution_suite import build_future_shadow_origin_execution_suite
from btcts.prediction.market_regime.future_shadow_origin_receipt import build_future_shadow_origin_receipt
from btcts.prediction.market_regime.future_shadow_pair_execution_plan import FutureExecutionFacts
from btcts.prediction.market_regime.future_shadow_runtime_outcome_intake import FutureShadowPointObservation


def _receipt():
    evidence = {}
    facts = {}
    for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC:
        item = FutureBaselineEvidence(
            origin_timestamp="2026-07-16T00:00:00Z",
            origin_current_state=MarketRegimeCode.RANGE,
            target_horizon_sec=int(horizon),
            feature_snapshot_ref="snapshot:mr-f9.6",
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
    suite = build_future_shadow_origin_execution_suite(evidence_by_horizon=evidence, facts_by_trace_id=facts)
    return build_future_shadow_origin_receipt(origin_suite=suite)


def _cycle():
    observation = FutureShadowPointObservation(
        target_horizon_sec=300,
        observed_at="2026-07-16T00:05:30Z",
        observed_future_state=MarketRegimeCode.RANGE,
        observation_source_ref="source:canonical:300",
    )
    return build_future_shadow_maturation_cycle(
        origin_receipt=_receipt(),
        observations_by_horizon={300: observation},
        polled_at="2026-07-16T00:10:00Z",
    )


def test_plan_keeps_shadow_status_contract_separate_from_canonical_ledger() -> None:
    plan = build_future_shadow_maturation_persistence_plan(maturation_cycle=_cycle())
    assert plan["trace_count"] == 14
    assert plan["status_counts"]["UNRESOLVED"] == 12
    assert all("outcome_status" in row for row in plan["outcome_rows"])
    assert all("status" not in row for row in plan["outcome_rows"])
    assert plan["canonical_outcome_ledger_append"] is False
    assert plan["artifact_relpath"].startswith(
        "prediction/market_regime/future_shadow/maturation/date=2026-07-16/"
    )
    assert len(Path(plan["artifact_relpath"]).name) < 80


def test_writer_is_disabled_and_duplicate_safe(tmp_path) -> None:
    plan = build_future_shadow_maturation_persistence_plan(maturation_cycle=_cycle())
    with pytest.raises(PermissionError, match="disabled_by_default"):
        persist_future_shadow_maturation_once(tmp_path, plan=plan)
    with pytest.raises(PermissionError, match="once_ack_required"):
        persist_future_shadow_maturation_once(tmp_path, plan=plan, enabled=True)
    first = persist_future_shadow_maturation_once(tmp_path, plan=plan, enabled=True, once=True)
    second = persist_future_shadow_maturation_once(tmp_path, plan=plan, enabled=True, once=True)
    assert first["written"] is True
    assert second["duplicate"] is True
    payload = json.loads((tmp_path / first["artifact_relpath"]).read_text(encoding="utf-8"))
    assert payload["trace_count"] == 14
    assert payload["canonical_outcome_ledger_append"] is False


def test_tampered_trace_set_and_path_fail_closed(tmp_path) -> None:
    original = build_future_shadow_maturation_persistence_plan(maturation_cycle=_cycle())
    reversed_ids = dict(original)
    reversed_ids["trace_ids"] = tuple(reversed(original["trace_ids"]))
    with pytest.raises(ValueError, match="trace_set_mismatch"):
        persist_future_shadow_maturation_once(tmp_path, plan=reversed_ids, enabled=True, once=True)
    escaped = dict(original)
    escaped["artifact_relpath"] = (
        "prediction/market_regime/future_shadow/maturation/date=2026-07-16/../../escape.json"
    )
    with pytest.raises(ValueError, match="relpath_invalid"):
        persist_future_shadow_maturation_once(tmp_path, plan=escaped, enabled=True, once=True)


def test_conflicting_existing_file_is_rejected(tmp_path) -> None:
    plan = build_future_shadow_maturation_persistence_plan(maturation_cycle=_cycle())
    path = tmp_path / plan["artifact_relpath"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("conflict\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="existing_conflict"):
        persist_future_shadow_maturation_once(tmp_path, plan=plan, enabled=True, once=True)
