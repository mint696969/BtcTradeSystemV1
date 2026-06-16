# path: ./tools/test_phase4a_autotrade_milestone_i_execution_safety_harness_guard.py
# desc: Guard AutoTrade milestone I execution safety harness and armed dry-run remain fail-closed and broker-free.

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next/src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.autotrade.execution import (  # noqa: E402
    CommandRequest,
    CommandType,
    OrderType,
    build_order_intent_from_decision,
    evaluate_armed_dry_run_intent,
    validate_command_request,
)
from btcts.autotrade.risk import KillSwitchState, RuntimeHealthState, evaluate_live_readiness  # noqa: E402

FORBIDDEN_TOKENS = (
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
)

CHECK_FILES = (
    "btcts_next/src/btcts/autotrade/execution/command_request.py",
    "btcts_next/src/btcts/autotrade/execution/dry_run.py",
    "btcts_next/src/btcts/autotrade/risk/safety_harness.py",
)

PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)


def imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def main() -> int:
    failures: list[str] = []

    active_ps = "params_fx_balanced_v0_1"
    intent = build_order_intent_from_decision(
        decision_id="dec_safe_001",
        snapshot_id="snap_safe_001",
        forecast_id="fcst_safe_001",
        parameter_set_id=active_ps,
        logic_version="autotrade_logic_v0_1",
        side="sell",
        size=0.01,
        price=10000000.0,
        reason_codes=("forecast_aligned_sell",),
        risk_gate_allowed=True,
        mode="ARMED_DRY_RUN",
        order_type=OrderType.LIMIT,
    )
    runtime_clean = RuntimeHealthState(
        heartbeat_fresh=True,
        market_data_fresh=True,
        account_state_fresh=True,
        order_state_fresh=True,
        position_state_fresh=True,
        ledger_writable=True,
        broker_reachable=False,
        reconciliation_clean=True,
    )
    runtime_bad = RuntimeHealthState(
        heartbeat_fresh=False,
        market_data_fresh=False,
        account_state_fresh=True,
        order_state_fresh=False,
        position_state_fresh=True,
        ledger_writable=False,
        broker_reachable=False,
        reconciliation_clean=False,
    )
    kill_clear = KillSwitchState(active=False, source="test")
    kill_active = KillSwitchState(active=True, reason="operator_halt", source="test")

    readiness_clean = evaluate_live_readiness(kill_switch=kill_clear, runtime=runtime_clean, active_parameter_set_id=active_ps, mode="ARMED_DRY_RUN")
    readiness_killed = evaluate_live_readiness(kill_switch=kill_active, runtime=runtime_clean, active_parameter_set_id=active_ps, mode="ARMED_DRY_RUN")
    readiness_bad = evaluate_live_readiness(kill_switch=kill_clear, runtime=runtime_bad, active_parameter_set_id=None, mode="LIVE_MIN_SIZE")
    dry_ok = evaluate_armed_dry_run_intent(intent, kill_switch=kill_clear, runtime=runtime_clean, active_parameter_set_id=active_ps)
    dry_killed = evaluate_armed_dry_run_intent(intent, kill_switch=kill_active, runtime=runtime_clean, active_parameter_set_id=active_ps)
    dry_mismatch = evaluate_armed_dry_run_intent(intent, kill_switch=kill_clear, runtime=runtime_clean, active_parameter_set_id="other_params")

    cmd = CommandRequest(
        command_id="cmd_001",
        command_type=CommandType.REQUEST_EMERGENCY_FLATTEN,
        requested_by="operator",
        requested_at="2026-06-12T12:00:00Z",
        current_mode="ARMED_DRY_RUN",
        target="flatten",
        confirmation=False,
        reason_codes=("manual_test",),
    )
    cmd_result = validate_command_request(cmd)
    cmd_confirmed = validate_command_request(
        CommandRequest(
            command_id="cmd_002",
            command_type=CommandType.REQUEST_EMERGENCY_FLATTEN,
            requested_by="operator",
            requested_at="2026-06-12T12:00:01Z",
            current_mode="ARMED_DRY_RUN",
            target="flatten",
            confirmation=True,
        )
    )

    no_forbidden_tokens = True
    no_broker_imports = True
    for rel in CHECK_FILES:
        path = REPO_ROOT / rel
        text = path.read_text(encoding="utf-8")
        if any(token in text for token in FORBIDDEN_TOKENS):
            no_forbidden_tokens = False
        imports = imports_from(path)
        if any("broker" in item.lower() or item in {"requests", "httpx", "ccxt", "pybitflyer"} for item in imports):
            no_broker_imports = False

    checks = {
        "clean_readiness_ready": readiness_clean.ready is True,
        "kill_switch_blocks": readiness_killed.ready is False and "kill_switch_active" in readiness_killed.blocked_by,
        "unknown_state_fail_closed": readiness_bad.ready is False and "active_parameter_set_missing" in readiness_bad.blocked_by and "ledger_not_writable" in readiness_bad.blocked_by,
        "dry_run_accepts_clean": dry_ok.accepted_for_dry_run is True,
        "dry_run_never_sends_broker": dry_ok.would_send_to_broker is False,
        "dry_run_blocks_kill": dry_killed.accepted_for_dry_run is False and "kill_switch_active" in dry_killed.blocked_by,
        "dry_run_blocks_parameter_mismatch": dry_mismatch.accepted_for_dry_run is False and "parameter_set_mismatch" in dry_mismatch.blocked_by,
        "dangerous_command_requires_confirmation": cmd_result.accepted is False and "confirmation_required" in cmd_result.blocked_by,
        "confirmed_command_validates": cmd_confirmed.accepted is True,
        "json_safe_dry_run": json.loads(json.dumps(dry_ok.to_dict(), ensure_ascii=False))["would_send_to_broker"] is False,
        "json_safe_command": json.loads(json.dumps(cmd.to_dict(), ensure_ascii=False))["confirmation_required"] is True,
        "no_forbidden_tokens": no_forbidden_tokens,
        "no_broker_imports": no_broker_imports,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    import subprocess
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone I: {hit}" for hit in protected_dirty_hits)

    result = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_i_execution_safety_harness_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "live_readiness_fail_closed": checks["clean_readiness_ready"] and checks["kill_switch_blocks"] and checks["unknown_state_fail_closed"],
            "armed_dry_run_never_sends_broker": checks["dry_run_accepts_clean"] and checks["dry_run_never_sends_broker"],
            "armed_dry_run_blocks_unsafe": checks["dry_run_blocks_kill"] and checks["dry_run_blocks_parameter_mismatch"],
            "command_request_validation_present": checks["dangerous_command_requires_confirmation"] and checks["confirmed_command_validates"],
            "simulation_only_no_broker": checks["no_forbidden_tokens"] and checks["no_broker_imports"],
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "readiness_clean": readiness_clean.to_dict(),
        "readiness_bad": readiness_bad.to_dict(),
        "dry_run_ok": dry_ok.to_dict(),
        "dry_run_killed": dry_killed.to_dict(),
        "checks": checks,
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
