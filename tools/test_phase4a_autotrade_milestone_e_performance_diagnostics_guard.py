# path: ./tools/test_phase4a_autotrade_milestone_e_performance_diagnostics_guard.py
# desc: Guard AutoTrade milestone E expectancy metrics, abstention diagnostics, and missed-opportunity schema.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.config import initial_parameter_set_v0_1  # noqa: E402
from btcts.autotrade.ledger import (  # noqa: E402
    MissedOpportunityRecord,
    abstention_from_decision,
    group_by_ground,
    group_by_parameter_set,
    group_by_reason_code,
    outcome_from_decision,
    summarize_outcomes,
)
from btcts.autotrade.modes import AutoTradeMode  # noqa: E402
from btcts.autotrade.read_model import build_rule_based_forecast_5m, build_snapshot_id  # noqa: E402
from btcts.autotrade.read_model.models import (  # noqa: E402
    AutoTradeSnapshot,
    Confidence,
    CurrentMarketInputs,
    GroundDirection,
    GroundState,
    SnapshotUsability,
    TemporalFlowFeatures,
)
from btcts.autotrade.risk import evaluate_risk_gate  # noqa: E402
from btcts.autotrade.strategy import build_action_candidate  # noqa: E402
from btcts.autotrade.ledger import build_shadow_decision_record  # noqa: E402

PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)


def make_record(*, direction: GroundDirection, temporal: bool, trade: bool, pnl: float | None):
    ps = initial_parameter_set_v0_1()
    created_at = "2026-06-12T12:00:00Z"
    sid = build_snapshot_id(market_uid="bitflyer:BTC_JPY_FX", created_at=created_at, parameter_set_id=ps.parameter_set_id, effective_event_ts="2026-06-12T11:59:59Z")
    snap = AutoTradeSnapshot(
        snapshot_id=sid,
        created_at=created_at,
        market_uid="bitflyer:BTC_JPY_FX",
        parameter_set_id=ps.parameter_set_id,
        logic_version=ps.logic_version,
        effective_event_ts="2026-06-12T11:59:59Z",
        ground=GroundState(direction=direction, confidence=Confidence.MEDIUM),
        usability=SnapshotUsability(regime=True, liquidity=True, trade=trade, l4=True, temporal=temporal),
        inputs=CurrentMarketInputs(spread=4500.0, trade_delta=-2.0 if direction == GroundDirection.SELL_LEANING else 2.0, mid_price=10000000.0),
        temporal_flow=TemporalFlowFeatures(
            windows_sec=ps.temporal_flow.windows_sec,
            generated_at=created_at,
            usable=temporal,
            temporal_pressure_flow={"pressure_acceleration": "sell" if direction == GroundDirection.SELL_LEANING else "buy"},
            temporal_price_flow={"mid_return_300s": -0.001 if direction == GroundDirection.SELL_LEANING else 0.001},
        ),
        stale_reasons=() if temporal and trade else ("trade_stale",),
    )
    forecast = build_rule_based_forecast_5m(snap, ps)
    cand = build_action_candidate(snap, forecast, ps)
    risk = evaluate_risk_gate(snap, cand, mode=AutoTradeMode.SHADOW)
    decision = build_shadow_decision_record(mode=AutoTradeMode.SHADOW, snapshot=snap, forecast_5m=forecast, candidate=cand, risk_gate=risk)
    outcome = outcome_from_decision(decision, realized_pnl=pnl, fees=10.0 if pnl is not None else 0.0, slippage=5.0 if pnl is not None else 0.0, outcome_label="resolved" if pnl is not None else "unresolved")
    return decision, outcome


def main() -> int:
    failures: list[str] = []
    ps = initial_parameter_set_v0_1()
    d1, o1 = make_record(direction=GroundDirection.SELL_LEANING, temporal=True, trade=True, pnl=120.0)
    d2, o2 = make_record(direction=GroundDirection.BUY_LEANING, temporal=True, trade=True, pnl=-60.0)
    d3, o3 = make_record(direction=GroundDirection.SELL_LEANING, temporal=False, trade=False, pnl=None)
    records = [o1, o2, o3]

    summary = summarize_outcomes(records)
    by_param = group_by_parameter_set(records)
    by_ground = group_by_ground(records)
    by_reason = group_by_reason_code(records)
    abstention = abstention_from_decision(d3)
    missed = MissedOpportunityRecord(
        decision_id=d3.decision_id,
        parameter_set_id=ps.parameter_set_id,
        snapshot_id=d3.snapshot.snapshot_id,
        forecast_id=d3.forecast_5m.forecast_id if d3.forecast_5m else None,
        action=d3.final_action,
        side=d3.candidate.side,
        evaluation_horizon_sec=300,
        actual_move=-1000.0,
        cost_adjusted_move=850.0,
        would_have_been_profitable=True,
        blocking_reasons=tuple(d3.risk_gate.blocked_by),
    )

    checks = {
        "cost_adjusted_pnl": o1.cost_adjusted_pnl() == 105.0 and o2.cost_adjusted_pnl() == -75.0,
        "summary_decision_count": summary.decision_count == 3,
        "summary_resolved_count": summary.resolved_trade_count == 2,
        "summary_win_rate": summary.win_rate == 0.5,
        "summary_expectancy_after_cost": summary.expectancy == 15.0,
        "summary_profit_factor": summary.profit_factor == 105.0 / 75.0,
        "group_by_parameter_set": f"parameter_set:{ps.parameter_set_id}" in [v.group_key for v in by_param.values()],
        "group_by_ground_present": any(key.startswith("ground:") for key in by_ground.keys()),
        "group_by_reason_present": bool(by_reason),
        "abstention_present": abstention is not None,
        "abstention_safety_blocked": abstention is not None and abstention.safety_blocked and not abstention.tunable,
        "missed_opportunity_schema": missed.would_have_been_profitable is True and missed.evaluation_horizon_sec == 300,
        "json_safe_summary": json.loads(json.dumps(summary.to_dict(), ensure_ascii=False))["resolved_trade_count"] == 2,
        "json_safe_missed": json.loads(json.dumps(missed.to_dict(), ensure_ascii=False))["parameter_set_id"] == ps.parameter_set_id,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    import subprocess
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone E: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_e_performance_diagnostics_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "expectancy_first_metrics_present": checks["summary_expectancy_after_cost"] and checks["summary_profit_factor"],
            "parameter_set_grouping_present": checks["group_by_parameter_set"],
            "ground_reason_grouping_present": checks["group_by_ground_present"] and checks["group_by_reason_present"],
            "abstention_diagnostics_present": checks["abstention_present"] and checks["abstention_safety_blocked"],
            "missed_opportunity_schema_present": checks["missed_opportunity_schema"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "summary": summary.to_dict(),
        "abstention": abstention.to_dict() if abstention is not None else None,
        "missed_opportunity": missed.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
