# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_pair_writer.py
# desc: MR-F8.6 tests for dedicated append-only paired shadow evidence writer safety and idempotency.

from __future__ import annotations

import json

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence
from btcts.prediction.market_regime.future_shadow_candidate_pairing import build_future_shadow_candidate_pair
from btcts.prediction.market_regime.future_shadow_pair_trace_plan import build_future_shadow_pair_trace_plan
from btcts.prediction.market_regime.future_shadow_pair_writer import (
    MR_F8_PAIR_NAMESPACE,
    build_mr_f8_shadow_pair_write_plan,
    persist_mr_f8_shadow_pair_once,
)


def pair() -> dict:
    evidence = FutureBaselineEvidence(
        origin_timestamp="2026-07-15T00:00:00Z",
        origin_current_state=MarketRegimeCode.RANGE,
        target_horizon_sec=900,
        feature_snapshot_ref="snapshot:writer",
        regime_scores={MarketRegimeCode.BREAKOUT: 0.44, MarketRegimeCode.RANGE: 0.34, MarketRegimeCode.UP_TREND: 0.22},
        available_feature_families=("price_structure", "volatility", "liquidity", "source_quality", "microprice"),
        source_timestamp_epoch_sec=100.0,
        origin_timestamp_epoch_sec=100.0,
    )
    payload = dict(build_future_shadow_candidate_pair(evidence=evidence))
    payload["trace_plan"] = build_future_shadow_pair_trace_plan(pair=payload)
    return payload


def test_plan_uses_dedicated_namespace_and_stays_disabled() -> None:
    plan = build_mr_f8_shadow_pair_write_plan(pair=pair())
    assert plan["namespace"] == MR_F8_PAIR_NAMESPACE
    assert plan["artifact_relpath"].startswith(MR_F8_PAIR_NAMESPACE + "/date=2026-07-15/")
    assert plan["would_write"] is False


def test_writer_requires_all_three_acknowledgements(tmp_path) -> None:
    plan = build_mr_f8_shadow_pair_write_plan(pair=pair())
    with pytest.raises(PermissionError, match="disabled_by_default"):
        persist_mr_f8_shadow_pair_once(tmp_path, plan=plan)
    with pytest.raises(PermissionError, match="once_ack_required"):
        persist_mr_f8_shadow_pair_once(tmp_path, plan=plan, enabled=True)
    with pytest.raises(PermissionError, match="explicit_write_ack_required"):
        persist_mr_f8_shadow_pair_once(tmp_path, plan=plan, enabled=True, once=True)


def test_write_is_atomic_verified_and_idempotent(tmp_path) -> None:
    plan = build_mr_f8_shadow_pair_write_plan(pair=pair())
    first = persist_mr_f8_shadow_pair_once(
        tmp_path, plan=plan, enabled=True, once=True, explicit_write_ack=True
    )
    assert first == {
        "written": True,
        "duplicate": False,
        "verified": True,
        "artifact_relpath": plan["artifact_relpath"],
    }
    path = tmp_path / plan["artifact_relpath"]
    assert json.loads(path.read_text(encoding="utf-8"))["pair_id"] == plan["payload"]["pair_id"]
    second = persist_mr_f8_shadow_pair_once(
        tmp_path, plan=plan, enabled=True, once=True, explicit_write_ack=True
    )
    assert second["written"] is False
    assert second["duplicate"] is True
    assert second["verified"] is True


def test_existing_conflict_fails_closed(tmp_path) -> None:
    plan = build_mr_f8_shadow_pair_write_plan(pair=pair())
    path = tmp_path / plan["artifact_relpath"]
    path.parent.mkdir(parents=True)
    path.write_text("{}\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="existing_conflict"):
        persist_mr_f8_shadow_pair_once(
            tmp_path, plan=plan, enabled=True, once=True, explicit_write_ack=True
        )


def test_path_escape_is_rejected(tmp_path) -> None:
    plan = dict(build_mr_f8_shadow_pair_write_plan(pair=pair()))
    plan["artifact_relpath"] = "../escape.json"
    with pytest.raises(ValueError, match="relpath_invalid"):
        persist_mr_f8_shadow_pair_once(
            tmp_path, plan=plan, enabled=True, once=True, explicit_write_ack=True
        )
