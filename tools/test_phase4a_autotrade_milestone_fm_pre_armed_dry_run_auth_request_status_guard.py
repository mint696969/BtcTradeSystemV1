# path: ./tools/test_phase4a_autotrade_milestone_fm_pre_armed_dry_run_auth_request_status_guard.py
# desc: Guard S98 authorization request/status remains request/status-only, non-recording, non-executing, and non-authorizing. Short path avoids Windows MAX_PATH.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_auth_request_status_s98.py"
GATE = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_auth_request_execution_gate_dry_run_status_s97.py"
TMP_ROOT = REPO_ROOT / "tmp" / "_s98_pre_armed_dry_run_authorization_request_status_guard"
PROTECTED_PREFIXES = ("btcts_next/src/btcts/collector_vnext/", "btcts_next/src/btcts/ingestion/", "btcts_next/src/btcts/processing/l3_market_semantics/", "btcts_next/src/btcts/processing/l4_consumer_models/")
CHECK_FILES = (STATUS, GATE, REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/command_status.py")
FORBIDDEN_TOKENS = ("place_order(", "send_order(", "broker_order(", "private_api", "pybitflyer", "ccxt", "requests.post", "httpx.post", "append_command_ledger_record(", "validate_and_append_command", "submit_mode_change_command_request", "mode_changed=True", "would_send_to_broker=True", "pre_armed_dry_run_authorized=True", "live_authorized=True", "approval_ledger_appended=True", "command_ledger_appended=True", "mode_change_requested=True", "mode_change_authorized=True", "approval_record_append_execution_authorized=True", "authorization_request_recorded=True", "authorization_request_record_executed=True", "authorization_request_record_execution_requested=True", "authorization_request_record_execution_authorized=True", "authorization_request_status_authorized=True", "authorization_request_status_executed=True", "while True")
ACKS = ("confirm_s97_authorization_request_execution_gate_status_reviewed", "confirm_authorization_request_status_is_review_only", "confirm_this_status_does_not_record_execute_or_authorize_authorization_request", "confirm_no_authorization_grant_append_or_mode_change_is_authorized", "confirm_separate_explicit_authorization_slice_required_before_any_authorization")


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return path


def _gate(*, ready: bool, safety: bool = True) -> dict:
    source = {"authorization_request_dry_run_plan_decision": "authorization_request_dry_run_plan_status_ready_not_authorized_not_recorded_not_executed", "authorization_request_dry_run_plan_ready": True, "authorization_request_preflight_decision": "authorization_request_preflight_status_ready_not_authorized_not_recorded_not_executed", "authorization_request_preflight_ready": True, "authorization_request_status_decision": "authorization_request_status_ready_not_authorized_not_recorded_not_executed", "authorization_request_status_ready": True, "evidence_id": "approval_evidence_guard_valid_001"}
    payload = {"ok": True, "report_version": "pre_armed_dry_run_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_execution_gate_dry_run_status.s97.v1", "decision": "authorization_request_execution_gate_dry_run_ready_not_authorized_not_recorded_not_executed" if ready else "authorization_request_execution_gate_dry_run_blocked_not_authorized_not_recorded_not_executed", "authorization_request_execution_gate_ready": ready, "authorization_request_execution_gate_blockers": [] if ready else ["authorization_request_dry_run_plan_status_not_ready"], "source_summary": source, "read_only": True, "would_send_to_broker": False, "mode_changed": False, "dry_run_gate_only": True, "operator_safety_lock": {"non_authorizing": True, "dry_run_gate_only": True, "read_only": True, "would_send_to_broker": False, "mode_changed": False, "final_human_review_required": True}}
    for key in ("authorization_request_status_authorized", "authorization_request_status_requested", "authorization_request_status_executed", "authorization_request_execution_gate_authorized", "authorization_request_execution_gate_requested", "authorization_request_execution_gate_executed", "authorization_request_dry_run_plan_authorized", "authorization_request_dry_run_plan_requested", "authorization_request_dry_run_plan_executed", "authorization_request_preflight_authorized", "authorization_request_preflight_requested", "authorization_request_preflight_executed", "authorization_request_record_execution_authorization_requested", "authorization_request_record_execution_authorized", "authorization_request_record_execution_requested", "authorization_request_record_executed", "authorization_request_recorded", "approval_record_append_execution_authorized", "approval_record_append_execution_requested", "approval_record_append_executed", "approval_ledger_appended", "command_ledger_appended", "mode_change_requested", "mode_change_authorized", "pre_armed_dry_run_authorized", "live_authorized", "autotrade_resume_authorized"):
        payload[key] = False
        payload["operator_safety_lock"][key] = False
    if not safety:
        payload["operator_safety_lock"]["non_authorizing"] = False
    return payload


def _request(*, valid: bool) -> dict:
    return {"authorization_request_status_reviewed": bool(valid), "authorization_request_status_requested": bool(valid), "authorization_scope": "PRE_ARMED_DRY_RUN_AUTHORIZATION_REQUEST_STATUS_REVIEW_ONLY" if valid else "LIVE", "authorization_target": "PRE_ARMED_DRY_RUN_AUTHORIZATION_REQUEST_EXECUTION_GATE_REVIEW" if valid else "MODE_CHANGE", "requested_by": "guard_operator" if valid else "", "requested_at": "2026-06-18T00:07:20Z" if valid else "", "operator_identity": "guard_human_operator" if valid else "", "acknowledgements": list(ACKS) if valid else ["confirm_s97_authorization_request_execution_gate_status_reviewed"], "authorization_request_status_authorized": False, "authorization_request_status_executed": False, "authorization_request_execution_gate_authorized": False, "authorization_request_execution_gate_executed": False, "authorization_request_dry_run_plan_authorized": False, "authorization_request_dry_run_plan_executed": False, "authorization_request_record_execution_authorized": False, "authorization_request_record_execution_requested": False, "authorization_request_record_executed": False, "authorization_request_recorded": False, "approval_record_append_execution_authorized": False, "approval_record_append_execution_requested": False, "approval_record_append_executed": False, "approval_ledger_append_requested": False, "command_ledger_append_requested": False, "mode_change_requested": False}


def _run_case(name: str, *, gate_ready: bool, request_valid: bool, gate_safety: bool = True) -> dict:
    case = TMP_ROOT / name
    case.mkdir(parents=True, exist_ok=True)
    gate_path = _write_json(case / "gate.json", _gate(ready=gate_ready, safety=gate_safety))
    request_path = _write_json(case / "request.json", _request(valid=request_valid))
    out = case / "status.json"
    proc = subprocess.run([sys.executable, str(STATUS), "--authorization-request-execution-gate-status", str(gate_path), "--authorization-request-status-request", str(request_path), "--out", str(out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=60)
    try:
        payload = json.loads(proc.stdout)
    except Exception as exc:
        payload = {"ok": False, "error": f"stdout was not JSON: {exc}", "stdout_tail": proc.stdout[-1600:]}
    payload["returncode"] = proc.returncode
    return payload


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


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

    ready_requested = _run_case("ready_requested", gate_ready=True, request_valid=True)
    ready_missing_request = _run_case("ready_missing_request", gate_ready=True, request_valid=False)
    blocked_gate_requested = _run_case("blocked_gate_requested", gate_ready=False, request_valid=True)
    unsafe_gate_requested = _run_case("unsafe_gate_requested", gate_ready=True, request_valid=True, gate_safety=False)
    checks = {
        "ready_requested_returncode_zero": ready_requested.get("returncode") == 0 and ready_requested.get("ok") is True,
        "ready_requested_status_ready_without_authorization": ready_requested.get("authorization_request_status_ready") is True and ready_requested.get("decision") == "authorization_request_status_ready_not_authorized_not_recorded_not_executed",
        "ready_requested_no_record_execution_grant_append_or_mode_request": ready_requested.get("authorization_request_status_authorized") is False and ready_requested.get("authorization_request_status_requested") is False and ready_requested.get("authorization_request_status_executed") is False and ready_requested.get("authorization_request_recorded") is False and ready_requested.get("approval_record_append_execution_authorized") is False and ready_requested.get("approval_ledger_appended") is False and ready_requested.get("command_ledger_appended") is False and ready_requested.get("mode_change_requested") is False,
        "ready_missing_request_blocked_visible": ready_missing_request.get("returncode") == 0 and ready_missing_request.get("authorization_request_status_ready") is False and "authorization_request_status_review_not_confirmed" in (ready_missing_request.get("authorization_request_status_blockers") or []),
        "blocked_gate_requested_blocked_visible": blocked_gate_requested.get("returncode") == 0 and blocked_gate_requested.get("authorization_request_status_ready") is False and "authorization_request_execution_gate_not_ready" in (blocked_gate_requested.get("authorization_request_status_blockers") or []),
        "unsafe_gate_requested_blocks_and_returns_nonzero": unsafe_gate_requested.get("returncode") != 0 and unsafe_gate_requested.get("authorization_request_status_ready") is False and "authorization_request_execution_gate_operator_safety_lock_not_clear" in (unsafe_gate_requested.get("authorization_request_status_blockers") or []),
        "read_only_no_broker_non_authorizing": ready_requested.get("read_only") is True and ready_requested.get("would_send_to_broker") is False and ready_requested.get("pre_armed_dry_run_authorized") is False and ready_requested.get("live_authorized") is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    protected_dirty_hits: list[str] = []
    for line in subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines():
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone FM: {hit}" for hit in protected_dirty_hits)
    payload = {"ok": not failures, "phase": "phase4a_autotrade_milestone_fm_pre_armed_dry_run_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_execution_authorization_request_status_guard", "status": "closed" if not failures else "open", "contract": {"authorization_request_status_present": STATUS.exists(), "ready_requested_status_ready_without_authorization": checks.get("ready_requested_status_ready_without_authorization", False), "missing_request_blocks_status": checks.get("ready_missing_request_blocked_visible", False), "blocked_gate_blocks_status": checks.get("blocked_gate_requested_blocked_visible", False), "unsafe_gate_blocks_status": checks.get("unsafe_gate_requested_blocks_and_returns_nonzero", False), "no_record_execution_no_grant_no_append_no_mode_request": checks.get("ready_requested_no_record_execution_grant_append_or_mode_request", False), "read_only_no_broker_non_authorizing": checks.get("read_only_no_broker_non_authorizing", False), "protected_lower_layers_untouched": not protected_dirty_hits}, "checks": checks, "cases": {"ready_requested": {"ok": ready_requested.get("ok"), "decision": ready_requested.get("decision"), "authorization_request_status_ready": ready_requested.get("authorization_request_status_ready"), "authorization_request_status_authorized": ready_requested.get("authorization_request_status_authorized"), "authorization_request_status_requested": ready_requested.get("authorization_request_status_requested"), "authorization_request_status_executed": ready_requested.get("authorization_request_status_executed"), "authorization_request_recorded": ready_requested.get("authorization_request_recorded"), "mode_change_requested": ready_requested.get("mode_change_requested")}, "ready_missing_request": {"ok": ready_missing_request.get("ok"), "decision": ready_missing_request.get("decision"), "authorization_request_status_ready": ready_missing_request.get("authorization_request_status_ready"), "authorization_request_status_blockers": ready_missing_request.get("authorization_request_status_blockers")}, "blocked_gate_requested": {"ok": blocked_gate_requested.get("ok"), "decision": blocked_gate_requested.get("decision"), "authorization_request_status_ready": blocked_gate_requested.get("authorization_request_status_ready"), "authorization_request_status_blockers": blocked_gate_requested.get("authorization_request_status_blockers")}, "unsafe_gate_requested": {"ok": unsafe_gate_requested.get("ok"), "decision": unsafe_gate_requested.get("decision"), "authorization_request_status_ready": unsafe_gate_requested.get("authorization_request_status_ready"), "authorization_request_status_blockers": unsafe_gate_requested.get("authorization_request_status_blockers"), "returncode": unsafe_gate_requested.get("returncode")}}, "protected_dirty_hits": protected_dirty_hits, "failures": failures}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
