# path: ./tools/test_phase4a_autotrade_milestone_d_strategy_risk_ledger_guard.py
# desc: Guard AutoTrade milestone D strategy candidates, risk gates, reason codes, and shadow ledger.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.config import initial_parameter_set_v0_1  # noqa: E402
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
from btcts.autotrade.strategy import CandidateAction, build_action_candidate  # noqa: E402
from btcts.autotrade.ledger import append_decision_jsonl, build_shadow_decision_record  # noqa: E402

PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)


def snapshot(*, direction: GroundDirection, temporal: bool = True, trade: bool = True, spread: float = 4500.0) -> AutoTradeSnapshot:
    ps = initial_parameter_set_v0_1()
    created_at = "2026-06-12T12:00:00Z"
    sid = build_snapshot_id(market_uid="bitflyer:BTC_JPY_FX", created_at=created_at, parameter_set_id=ps.parameter_set_id, effective_event_ts="2026-06-12T11:59:59Z")
    return AutoTradeSnapshot(
        snapshot_id=sid,
        created_at=created_at,
        market_uid="bitflyer:BTC_JPY_FX",
        parameter_set_id=ps.parameter_set_id,
        logic_version=ps.logic_version,
        effective_event_ts="2026-06-12T11:59:59Z",
        ground=GroundState(direction=direction, confidence=Confidence.MEDIUM),
        usability=SnapshotUsability(regime=True, liquidity=True, trade=trade, l4=True, temporal=temporal),
        inputs=CurrentMarketInputs(spread=spread, imbalance=-0.1 if direction == GroundDirection.SELL_LEANING else 0.1, wall_ratio=-0.12 if direction == GroundDirection.SELL_LEANING else 0.12, trade_delta=-2.0 if direction == GroundDirection.SELL_LEANING else 2.0, mid_price=10000000.0),
        temporal_flow=TemporalFlowFeatures(
            windows_sec=ps.temporal_flow.windows_sec,
            generated_at=created_at,
            max_feature_age_sec=4.0 if temporal else 30.0,
            usable=temporal,
            blocked_by=() if temporal else ("temporal_stale",),
            temporal_pressure_flow={"pressure_acceleration": "sell" if direction == GroundDirection.SELL_LEANING else "buy"},
            temporal_price_flow={"mid_return_300s": -0.001 if direction == GroundDirection.SELL_LEANING else 0.001},
            temporal_pattern_flags={"liquidity_vacuum_candidate": False},
        ),
        stale_reasons=() if temporal and trade else ("trade_stale",),
    )


def main() -> int:
    failures: list[str] = []
    ps = initial_parameter_set_v0_1()
    sell_snapshot = snapshot(direction=GroundDirection.SELL_LEANING)
    sell_forecast = build_rule_based_forecast_5m(sell_snapshot, ps)
    sell_candidate = build_action_candidate(sell_snapshot, sell_forecast, ps)
    sell_risk = evaluate_risk_gate(sell_snapshot, sell_candidate, mode=AutoTradeMode.SHADOW)
    sell_record = build_shadow_decision_record(mode=AutoTradeMode.SHADOW, snapshot=sell_snapshot, forecast_5m=sell_forecast, candidate=sell_candidate, risk_gate=sell_risk)

    stale_snapshot = snapshot(direction=GroundDirection.SELL_LEANING, temporal=False, trade=False)
    stale_forecast = build_rule_based_forecast_5m(stale_snapshot, ps)
    stale_candidate = build_action_candidate(stale_snapshot, stale_forecast, ps)
    stale_risk = evaluate_risk_gate(stale_snapshot, stale_candidate, mode=AutoTradeMode.SHADOW)
    stale_record = build_shadow_decision_record(mode=AutoTradeMode.SHADOW, snapshot=stale_snapshot, forecast_5m=stale_forecast, candidate=stale_candidate, risk_gate=stale_risk)

    watch_snapshot = snapshot(direction=GroundDirection.BUY_LEANING, spread=9000.0)
    watch_forecast = build_rule_based_forecast_5m(watch_snapshot, ps)
    watch_candidate = build_action_candidate(watch_snapshot, watch_forecast, ps)

    tmp = REPO_ROOT / "tmp/_autotrade_guard_milestone_d/decisions.jsonl"
    append_decision_jsonl(tmp, sell_record)
    append_decision_jsonl(tmp, stale_record)
    lines = [json.loads(line) for line in tmp.read_text(encoding="utf-8").splitlines()]

    checks = {
        "fresh_sell_entry_candidate": sell_candidate.action == CandidateAction.ENTRY_SELL,
        "fresh_sell_has_forecast_link": sell_candidate.forecast_id == sell_forecast.forecast_id,
        "fresh_sell_reason_codes": "forecast_aligned_sell" in sell_candidate.reason_codes and "entry_threshold_met" in sell_candidate.reason_codes,
        "shadow_entry_allowed_but_not_executable": sell_risk.allowed is True and sell_risk.executable is False,
        "shadow_warning_present": "risk_no_real_orders_in_shadow" in sell_risk.warnings,
        "stale_no_new_entry": stale_candidate.action == CandidateAction.NO_NEW_ENTRY,
        "stale_risk_not_allowed": stale_risk.allowed is False,
        "stale_record_final_wait": stale_record.final_action == "WAIT",
        "watch_or_entry_candidate_exists": watch_candidate.action in {CandidateAction.WATCH_BUY, CandidateAction.ENTRY_BUY},
        "ledger_two_lines": len(lines) == 2,
        "ledger_has_decision_id": all(row.get("decision_id", "").startswith("dec_") for row in lines),
        "ledger_has_parameter_set_id": all(row.get("parameter_set_id") == ps.parameter_set_id for row in lines),
        "ledger_has_forecast_id": lines[0].get("forecast_id") == sell_forecast.forecast_id,
        "ledger_would_order_none": all(row.get("would_order") is None for row in lines),
        "ledger_stale_blocked": "stale_input" in lines[1].get("candidate", {}).get("blocked_hint", []),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    import shutil
    shutil.rmtree(tmp.parent, ignore_errors=True)

    protected_dirty_hits: list[str] = []
    import subprocess
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone D: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_d_strategy_risk_ledger_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "fresh_candidate_path_present": checks["fresh_sell_entry_candidate"] and checks["fresh_sell_has_forecast_link"],
            "reason_codes_present": checks["fresh_sell_reason_codes"],
            "shadow_no_real_orders": checks["shadow_entry_allowed_but_not_executable"] and checks["ledger_would_order_none"],
            "stale_blocks_entry": checks["stale_no_new_entry"] and checks["stale_risk_not_allowed"],
            "shadow_ledger_present": checks["ledger_two_lines"] and checks["ledger_has_decision_id"] and checks["ledger_has_parameter_set_id"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "fresh_candidate": sell_candidate.to_dict(),
        "fresh_risk": sell_risk.to_dict(),
        "stale_candidate": stale_candidate.to_dict(),
        "stale_risk": stale_risk.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
