# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_execution_evidence_persistence.py
# desc: MR-F9.3 guards for disabled-by-default, duplicate-safe origin execution evidence persistence.

from __future__ import annotations

import json
from pathlib import Path

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence
from btcts.prediction.market_regime.future_execution_evidence import FutureInferenceMode, RawOutputSemantics
from btcts.prediction.market_regime.future_execution_evidence_persistence import (
    build_future_execution_evidence_persistence_plan,
    persist_future_execution_evidence_once,
)
from btcts.prediction.market_regime.future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from btcts.prediction.market_regime.future_shadow_candidate_pairing import build_future_shadow_candidate_pair
from btcts.prediction.market_regime.future_shadow_origin_execution_suite import build_future_shadow_origin_execution_suite
from btcts.prediction.market_regime.future_shadow_pair_execution_plan import FutureExecutionFacts


def _suite():
    evidence = {}
    facts = {}
    for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC:
        item = FutureBaselineEvidence(
            origin_timestamp="2026-07-16T03:00:00Z",
            origin_current_state=MarketRegimeCode.RANGE,
            target_horizon_sec=int(horizon),
            feature_snapshot_ref="snapshot:mr-f9.3",
            regime_scores={MarketRegimeCode.BREAKOUT: 0.61, MarketRegimeCode.RANGE: 0.39},
            available_feature_families=("price_structure", "volatility", "liquidity", "source_quality", "microprice", "session_context"),
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
    return build_future_shadow_origin_execution_suite(evidence_by_horizon=evidence, facts_by_trace_id=facts)


def test_plan_contains_fourteen_rows_and_logical_hot_root_only() -> None:
    suite = _suite()
    plan = build_future_execution_evidence_persistence_plan(origin_suite=suite)
    assert plan["evidence_count"] == 14
    assert plan["trace_ids"] == tuple(sorted(plan["trace_ids"]))
    assert plan["artifact_relpath"].startswith(
        "prediction/market_regime/future_shadow/execution_evidence/date=2026-07-16/"
    )
    assert plan["would_write"] is False
    assert plan["writer_registered"] is False
    assert len(Path(plan["artifact_relpath"]).name) < 80


def test_writer_is_disabled_by_default_and_duplicate_safe(tmp_path) -> None:
    plan = build_future_execution_evidence_persistence_plan(origin_suite=_suite())
    with pytest.raises(PermissionError, match="disabled_by_default"):
        persist_future_execution_evidence_once(tmp_path, plan=plan)
    with pytest.raises(PermissionError, match="once_ack_required"):
        persist_future_execution_evidence_once(tmp_path, plan=plan, enabled=True)
    first = persist_future_execution_evidence_once(tmp_path, plan=plan, enabled=True, once=True)
    second = persist_future_execution_evidence_once(tmp_path, plan=plan, enabled=True, once=True)
    assert first["written"] is True
    assert second["duplicate"] is True
    payload = json.loads((tmp_path / first["artifact_relpath"]).read_text(encoding="utf-8"))
    assert payload["evidence_count"] == 14
    assert payload["canonical_replacement"] is False


def test_tampered_count_trace_set_and_path_fail_closed(tmp_path) -> None:
    original = build_future_execution_evidence_persistence_plan(origin_suite=_suite())
    wrong_count = dict(original)
    wrong_count["evidence_count"] = 13
    with pytest.raises(ValueError, match="count_mismatch"):
        persist_future_execution_evidence_once(tmp_path, plan=wrong_count, enabled=True, once=True)
    wrong_ids = dict(original)
    wrong_ids["trace_ids"] = tuple(reversed(original["trace_ids"]))
    with pytest.raises(ValueError, match="trace_set_mismatch"):
        persist_future_execution_evidence_once(tmp_path, plan=wrong_ids, enabled=True, once=True)
    escaped = dict(original)
    escaped["artifact_relpath"] = (
        "prediction/market_regime/future_shadow/execution_evidence/date=2026-07-16/../../escape.json"
    )
    with pytest.raises(ValueError, match="relpath_invalid"):
        persist_future_execution_evidence_once(tmp_path, plan=escaped, enabled=True, once=True)


def test_conflicting_existing_file_is_rejected(tmp_path) -> None:
    plan = build_future_execution_evidence_persistence_plan(origin_suite=_suite())
    path = tmp_path / plan["artifact_relpath"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("conflict\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="existing_conflict"):
        persist_future_execution_evidence_once(tmp_path, plan=plan, enabled=True, once=True)
