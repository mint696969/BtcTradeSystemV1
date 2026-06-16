# path: ./tools/test_phase4a_autotrade_milestone_dv_pre_armed_dry_run_approval_request_status_guard.py
# desc: Guard S56 Pre-Armed Dry Run approval-request/status packet remains broker-free, request/status only, and non-authorizing.

from __future__ import annotations

import ast
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "tools/run_sr_fx_runtime_control_report_sequence_once.py"
EVIDENCE = REPO_ROOT / "tools/run_sr_fx_runtime_control_operational_evidence_report.py"
CLEARANCE = REPO_ROOT / "tools/run_sr_fx_runtime_control_clearance_runbook_report.py"
ROLLUP = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_readiness_blocker_rollup.py"
PACKET = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_human_review_packet.py"
STATUS = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_request_status.py"
TMP_ROOT = REPO_ROOT / "tmp" / "_s56_pre_armed_dry_run_approval_request_status_guard"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
CHECK_FILES = (
    STATUS,
    PACKET,
    ROLLUP,
    CLEARANCE,
    EVIDENCE,
    WRAPPER,
    REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/command_status.py",
)
FORBIDDEN_TOKENS = (
    "place_order(",
    "send_order(",
    "broker_order(",
    "private_api",
    "pybitflyer",
    "ccxt",
    "requests.post",
    "httpx.post",
    "append_command_ledger_record(",
    "validate_and_append_command",
    "submit_mode_change_command_request",
    "mode_changed=True",
    "would_send_to_broker=True",
    "pre_armed_dry_run_authorized=True",
    "armed_dry_run_authorized=True",
    "live_authorized=True",
    "approval_recorded=True",
    "human_approval_recorded=True",
    "operator_acknowledgement_recorded=True",
    "approval_ledger_appended=True",
    "command_ledger_appended=True",
    "mode_change_requested=True",
    "mode_change_authorized=True",
    "while True",
)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _seed_state(state_root: Path) -> None:
    state = state_root / "collector_vnext"
    _write_json(state / "operator_ui" / "sr_fx_final_readiness_checkpoint.json", {"ok": True, "data_ui_integrity_ready_for_final_human_review": True, "autotrade_resume_authorized": False, "blocked_by": [], "summary": {"primary_lineage": "continuous_ws", "service_stale": False}, "context": {"product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"}, "read_only": True, "would_send_to_broker": False})
    _write_json(state / "public" / "bitflyer_fx_public_market_readiness.json", {"public_market_readiness": {"ok": True, "product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY", "blocked_by": [], "warnings": [], "read_only": True, "would_send_to_broker": False}})
    _write_json(state / "private" / "bitflyer_fx_readiness.json", {"readiness": {"product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY", "private_state_known_and_fresh": True, "account_clear_for_new_auto_entry": True, "blocked_by": [], "read_only": True, "would_send_to_broker": False}})
    _write_json(state / "private" / "bitflyer_fx_live_readiness_contract.json", {"live_readiness_contract": {"ready": False, "product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY", "blocked_by": ["order_sender_not_implemented"], "read_only": True, "would_send_to_broker": False}})


def _run_case(case_name: str, extra_args: list[str]) -> dict[str, Any]:
    case_root = TMP_ROOT / case_name
    if case_root.exists():
        shutil.rmtree(case_root)
    data_root = case_root / "data"
    logs_root = case_root / "logs"
    state_root = case_root / "state"
    runtime_root = case_root / "runtime_hot"
    for path in (data_root, logs_root, state_root, runtime_root):
        path.mkdir(parents=True, exist_ok=True)
    _seed_state(state_root)
    wrapper_out = case_root / "wrapper_out.json"
    evidence_out = case_root / "evidence_report.json"
    clearance_out = case_root / "clearance_runbook.json"
    rollup_out = case_root / "pre_armed_rollup.json"
    packet_out = case_root / "human_review_packet.json"
    status_out = case_root / "approval_request_status.json"
    wrapper_proc = subprocess.run([sys.executable, str(WRAPPER), "--data-root", str(data_root), "--logs-root", str(logs_root), "--state-root", str(state_root), "--runtime-root", str(runtime_root), "--now", "2026-06-17T00:00:10Z", "--out", str(wrapper_out), *extra_args], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    evidence_proc = subprocess.run([sys.executable, str(EVIDENCE), "--wrapper-out", str(wrapper_out), "--out", str(evidence_out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    clearance_proc = subprocess.run([sys.executable, str(CLEARANCE), "--evidence-report", str(evidence_out), "--out", str(clearance_out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    rollup_proc = subprocess.run([sys.executable, str(ROLLUP), "--clearance-runbook", str(clearance_out), "--out", str(rollup_out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    packet_proc = subprocess.run([sys.executable, str(PACKET), "--readiness-rollup", str(rollup_out), "--out", str(packet_out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    status_proc = subprocess.run([sys.executable, str(STATUS), "--human-review-packet", str(packet_out), "--out", str(status_out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    try:
        status_payload = json.loads(status_proc.stdout)
    except Exception as exc:
        status_payload = {"ok": False, "error": f"status stdout was not JSON: {exc}", "stdout_tail": status_proc.stdout[-1600:]}
    return {
        "case": case_name,
        "wrapper_returncode": wrapper_proc.returncode,
        "evidence_returncode": evidence_proc.returncode,
        "clearance_returncode": clearance_proc.returncode,
        "rollup_returncode": rollup_proc.returncode,
        "packet_returncode": packet_proc.returncode,
        "status_returncode": status_proc.returncode,
        "status": status_payload,
    }


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def main() -> int:
    failures: list[str] = []
    for path in CHECK_FILES:
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except Exception as exc:
            failures.append(f"compile failed: {path.relative_to(REPO_ROOT)}: {exc}")
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_TOKENS:
            if token in text:
                failures.append(f"forbidden token in {path.relative_to(REPO_ROOT)}: {token}")
        blocked_imports = _imports_from(path).intersection({"requests", "httpx", "ccxt", "pybitflyer"})
        if blocked_imports:
            failures.append(f"forbidden imports in {path.relative_to(REPO_ROOT)}: {sorted(blocked_imports)}")

    clear = _run_case("clear", [])
    blocked = _run_case("blocked", ["--heartbeat-observed-at", "2026-06-17T00:00:00Z", "--heartbeat-max-age-sec", "5", "--incident-open", "1", "--incident-reason", "guard_open_incident", "--kill-switch-active", "1", "--kill-switch-action", "HALT_AND_CANCEL", "--kill-switch-reason", "guard_kill_switch"])
    clear_status = clear["status"]
    blocked_status = blocked["status"]
    blocked_runtime = blocked_status.get("runtime_control_blockers") or []
    blocked_actions = blocked_status.get("operator_required_actions") or []
    clear_request = clear_status.get("approval_request") or {}
    blocked_request = blocked_status.get("approval_request") or {}

    checks = {
        "clear_pipeline_returncode_zero": all(clear[name] == 0 for name in ("wrapper_returncode", "evidence_returncode", "clearance_returncode", "rollup_returncode", "packet_returncode", "status_returncode")),
        "clear_status_ok": clear_status.get("ok") is True,
        "clear_status_ready_not_recorded": clear_status.get("approval_request_status_packet_ready") is True and clear_request.get("ready_for_human_review") is True and clear_status.get("human_approval_recorded") is False and clear_status.get("operator_acknowledgement_recorded") is False,
        "clear_status_not_authorizing": clear_status.get("pre_armed_dry_run_authorized") is False and clear_status.get("live_authorized") is False and clear_status.get("autotrade_resume_authorized") is False and clear_status.get("mode_change_authorized") is False,
        "clear_no_ledger_or_mode_request": clear_status.get("approval_ledger_appended") is False and clear_status.get("command_ledger_appended") is False and clear_status.get("mode_change_requested") is False,
        "blocked_pipeline_returncode_zero": all(blocked[name] == 0 for name in ("wrapper_returncode", "evidence_returncode", "clearance_returncode", "rollup_returncode", "packet_returncode", "status_returncode")),
        "blocked_status_ok": blocked_status.get("ok") is True,
        "blocked_status_blocked_not_recorded": blocked_request.get("ready_for_human_review") is False and blocked_status.get("decision") == "approval_request_status_blocked_not_recorded" and blocked_status.get("human_approval_recorded") is False and blocked_status.get("operator_acknowledgement_recorded") is False,
        "blocked_runtime_control_blockers_visible": any("heartbeat_stale" in item for item in blocked_runtime) and any("kill_switch_active" in item for item in blocked_runtime) and any("open_incident_present" in item for item in blocked_runtime),
        "blocked_actions_include_clearance_chain": "observe_fresh_runtime_heartbeat_and_rerun_runtime_control_sequence" in blocked_actions and "clear_or_acknowledge_kill_switch_with_explicit_human_protocol" in blocked_actions and "resolve_or_explicitly_close_runtime_incident_before_live_review" in blocked_actions,
        "blocked_status_not_authorizing": blocked_status.get("pre_armed_dry_run_authorized") is False and blocked_status.get("live_authorized") is False and blocked_status.get("autotrade_resume_authorized") is False and blocked_status.get("mode_change_authorized") is False,
        "blocked_no_ledger_or_mode_request": blocked_status.get("approval_ledger_appended") is False and blocked_status.get("command_ledger_appended") is False and blocked_status.get("mode_change_requested") is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status_lines = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status_lines:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DV: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_dv_pre_armed_dry_run_approval_request_status_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "approval_request_status_present": STATUS.exists(),
            "clear_case_ready_status_without_approval_record": checks.get("clear_status_ready_not_recorded", False),
            "blocked_case_blocked_status_without_approval_record": checks.get("blocked_status_blocked_not_recorded", False),
            "blocked_case_runtime_control_blockers_visible": checks.get("blocked_runtime_control_blockers_visible", False),
            "blocked_case_clearance_chain_visible": checks.get("blocked_actions_include_clearance_chain", False),
            "no_ledger_append_no_mode_request": checks.get("clear_no_ledger_or_mode_request", False) and checks.get("blocked_no_ledger_or_mode_request", False),
            "read_only_no_broker_non_authorizing": checks.get("clear_status_not_authorizing", False) and checks.get("blocked_status_not_authorizing", False),
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "checks": checks,
        "cases": {
            "clear": {
                "status_ok": clear_status.get("ok"),
                "decision": clear_status.get("decision"),
                "ready_for_human_review": clear_request.get("ready_for_human_review"),
                "human_approval_recorded": clear_status.get("human_approval_recorded"),
                "operator_acknowledgement_recorded": clear_status.get("operator_acknowledgement_recorded"),
                "approval_ledger_appended": clear_status.get("approval_ledger_appended"),
                "command_ledger_appended": clear_status.get("command_ledger_appended"),
                "mode_change_requested": clear_status.get("mode_change_requested"),
            },
            "blocked": {
                "status_ok": blocked_status.get("ok"),
                "decision": blocked_status.get("decision"),
                "ready_for_human_review": blocked_request.get("ready_for_human_review"),
                "human_approval_recorded": blocked_status.get("human_approval_recorded"),
                "operator_acknowledgement_recorded": blocked_status.get("operator_acknowledgement_recorded"),
                "runtime_control_blockers": blocked_runtime,
                "operator_required_actions": blocked_actions,
            },
        },
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
