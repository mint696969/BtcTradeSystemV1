# path: ./btcts_next/src/btcts/autotrade/tests/test_decision_log_parameter_bundle_rationale.py
# desc: Guards parameter bundle identity and rationale payload in AutoTrade decision logs.

from __future__ import annotations

import json

from btcts.autotrade.config import initial_parameter_bundle_v0_1
from btcts.autotrade.ledger.decision_log import DECISION_RATIONALE_VERSION, append_decision_jsonl, build_shadow_decision_record
from btcts.autotrade.live_shadow import run_shadow_decision_from_snapshot
from btcts.autotrade.modes import AutoTradeMode
from btcts.autotrade.read_model.models import (
    AutoTradeSnapshot,
    Confidence,
    CurrentMarketInputs,
    GroundDirection,
    GroundState,
    SnapshotUsability,
    TemporalFlowFeatures,
)
from btcts.autotrade.risk.models import RiskGateResult
from btcts.autotrade.strategy.models import ActionCandidate, CandidateAction, StrategyProfile


def _snapshot(parameter_set_id: str, logic_version: str) -> AutoTradeSnapshot:
    return AutoTradeSnapshot(
        snapshot_id="snap_bundle_rationale_001",
        created_at="2026-06-16T12:00:00+09:00",
        market_uid="bitflyer.fx.FX_BTC_JPY",
        parameter_set_id=parameter_set_id,
        logic_version=logic_version,
        effective_event_ts="2026-06-16T12:00:00+09:00",
        ground=GroundState(
            direction=GroundDirection.BUY_LEANING,
            confidence=Confidence.MEDIUM,
            reason_codes=("unit_ground_buy",),
        ),
        usability=SnapshotUsability(regime=True, liquidity=True, trade=True, temporal=True),
        inputs=CurrentMarketInputs(
            spread=1.0,
            imbalance=0.42,
            wall_ratio=1.2,
            wall_side="bid",
            trade_delta=0.3,
            price=100.0,
            mid_price=100.0,
        ),
        temporal_flow=TemporalFlowFeatures(usable=True),
        source_refs={"unit": "decision_rationale"},
        stale_reasons=(),
    )


def test_decision_log_records_bundle_and_split_parameter_set_identity(tmp_path) -> None:
    bundle = initial_parameter_bundle_v0_1()
    snapshot = _snapshot(bundle.trade_parameter_set_id, bundle.logic_version)
    candidate = ActionCandidate(
        candidate_id="cand_bundle_rationale_entry",
        snapshot_id=snapshot.snapshot_id,
        forecast_id=None,
        parameter_set_id=bundle.trade_parameter_set_id,
        logic_version=bundle.logic_version,
        action=CandidateAction.ENTRY_BUY,
        strategy_profile=StrategyProfile.BUY_LEANING_MEDIUM,
        side="buy",
        entry_quality=74,
        reason_codes=("entry_quality_near_threshold", "buy_leaning_ground"),
        blocked_hint=("watch_only",),
    )
    risk = RiskGateResult(
        allowed=False,
        executable=False,
        blocked_by=("heartbeat_stale",),
        warnings=("unit_warning",),
    )

    decision = build_shadow_decision_record(
        mode=AutoTradeMode.SHADOW,
        snapshot=snapshot,
        forecast_5m=None,
        candidate=candidate,
        risk_gate=risk,
        parameter_bundle=bundle,
    )
    data = decision.to_dict()

    assert data["decision_rationale_version"] == DECISION_RATIONALE_VERSION
    assert data["parameter_bundle_id"] == bundle.parameter_bundle_id
    assert data["regime_parameter_set_id"] == bundle.regime_parameter_set_id
    assert data["trade_parameter_set_id"] == bundle.trade_parameter_set_id
    assert data["parameter_set_id"] == bundle.trade_parameter_set_id

    assert data["regime_result"]["source"] == "snapshot.ground"
    assert data["regime_result"]["direction"] == "buy_leaning"
    assert "regime" in data["used_thresholds"]
    assert "trade" in data["used_thresholds"]
    assert "entry_quality" in data["used_thresholds"]["trade"]

    assert data["trade_decision"]["final_action"] == "WAIT"
    assert data["trade_decision"]["candidate_action"] == "ENTRY_BUY"
    assert data["trade_decision"]["risk_allowed"] is False
    assert "heartbeat_stale" in data["blocked_reasons"]
    assert "entry_quality_near_threshold" in data["triggered_rules"]

    ledger_path = tmp_path / "shadow_decisions.jsonl"
    append_decision_jsonl(ledger_path, decision)
    row = json.loads(ledger_path.read_text(encoding="utf-8").strip())

    assert row["parameter_bundle_id"] == bundle.parameter_bundle_id
    assert row["regime_parameter_set_id"] == bundle.regime_parameter_set_id
    assert row["trade_parameter_set_id"] == bundle.trade_parameter_set_id
    assert row["decision_rationale_version"] == DECISION_RATIONALE_VERSION


def test_run_shadow_decision_from_snapshot_wires_parameter_bundle_identity() -> None:
    bundle = initial_parameter_bundle_v0_1()
    snapshot = _snapshot(bundle.trade_parameter_set_id, bundle.logic_version)

    result = run_shadow_decision_from_snapshot(
        snapshot=snapshot,
        parameter_set=bundle.trade_parameter_set,
        parameter_bundle=bundle,
        persist=False,
    )

    assert result.decision is not None
    data = result.decision.to_dict()
    assert data["parameter_bundle_id"] == bundle.parameter_bundle_id
    assert data["regime_parameter_set_id"] == bundle.regime_parameter_set_id
    assert data["trade_parameter_set_id"] == bundle.trade_parameter_set_id
    assert data["decision_rationale_version"] == DECISION_RATIONALE_VERSION

