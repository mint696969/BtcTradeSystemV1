# path: ./tools/test_phase4a_autotrade_milestone_fd_pre_armed_dry_run_authorization_request_execution_authorization_request_execution_authorization_request_execution_gate_dry_run_status_guard.py
# desc: Guard S89 authorization request execution gate dry-run/status remains gate/status-only, non-recording, non-executing, and non-authorizing.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_authorization_request_execution_authorization_request_execution_authorization_request_execution_gate_dry_run_status.py"
PLAN = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_authorization_request_execution_authorization_request_execution_authorization_request_dry_run_plan_status.py"
TMP_ROOT = REPO_ROOT / "tmp" / "_s89_pre_armed_dry_run_authorization_request_execution_authorization_request_execution_gate_status_guard"
PROTECTED_PREFIXES = ("btcts_next/src/btcts/collector_vnext/", "btcts_next/src/btcts/ingestion/", "btcts_next/src/btcts/processing/l3_market_semantics/", "btcts_next/src/btcts/processing/l4_consumer_models/")
CHECK_FILES = (GATE, PLAN, REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/command_status.py")
FORBIDDEN_TOKENS = ("place_order(", "send_order(", "broker_order(", "private_api", "pybitflyer", "ccxt", "requests.post", "httpx.post", "append_command_ledger_record(", "validate_and_append_command", "submit_mode_change_command_request", "mode_changed=True", "would_send_to_broker=True", "pre_armed_dry_run_authorized=True", "live_authorized=True", "approval_ledger_appended=True", "command_ledger_appended=True", "mode_change_requested=True", "mode_change_authorized=True", "approval_record_append_execution_authorized=True", "authorization_request_recorded=True", "authorization_request_record_executed=True", "authorization_request_record_execution_requested=True", "authorization_request_record_execution_authorized=True", "authorization_request_execution_gate_authorized=True", "authorization_request_execution_gate_executed=True", "while True")
ACKS = ("confirm_s88_authorization_request_dry_run_plan_status_reviewed", "confirm_authorization_request_execution_gate_is_review_only", "confirm_this_gate_does_not_record_execute_or_authorize_authorization_request", "confirm_no_authorization_grant_append_or_mode_change_is_authorized", "confirm_separate_explicit_authorization_slice_required_before_any_authorization")


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return path


def _plan(*, ready: bool, safety: bool = True) -> dict:
    source = {"authorization_request_preflight_report_version": "pre_armed_dry_run_authorization_request_execution_authorization_request_execution_authorization_request_preflight_status.s87.v1", "authorization_request_preflight_decision": "authorization_request_preflight_status_ready_not_authorized_not_recorded_not_executed", "authorization_request_preflight_ready": True, "authorization_request_status_decision": "authorization_request_status_ready_not_authorized_not_recorded_not_executed", "authorization_request_status_ready": True, "evidence_id": "approval_evidence_guard_valid_001"}
    payload = {"ok": True, "report_version": "pre_armed_dry_run_authorization_request_execution_authorization_request_execution_authorization_request_dry_run_plan_status.s88.v1", "decision": "authorization_request_dry_run_plan_status_ready_not_authorized_not_recorded_not_executed" if ready else "authorization_request_dry_run_plan_status_blocked_not_authorized_not_recorded_not_executed", "authorization_request_dry_run_plan_status_ready": ready, "authorization_request_dry_run_plan_requested_observed": ready, "authorization_request_dry_run_plan_blockers": [] if ready else ["authorization_request_preflight_status_not_ready"], "source_summary": source, "read_only": True, "would_send_to_broker": False, "mode_changed": False, "dry_run_plan_only": True, "operator_safety_lock": {"non_authorizing": True, "dry_run_plan_only": True, "read_only": True, "would_send_to_broker": False, "mode_changed": False, "final_human_review_required": True}}
    for key in ("authorization_request_execution_gate_authorized", "authorization_request_execution_gate_requested", "authorization_request_execution_gate_executed", "authorization_request_dry_run_plan_authorized", "authorization_request_dry_run_plan_requested", "authorization_request_dry_run_plan_executed", "authorization_request_preflight_authorized", "authorization_request_preflight_requested", "authorization_request_preflight_executed", "authorization_request_record_execution_authorization_requested", "authorization_request_record_execution_authorized", "authorization_request_record_execution_requested", "authorization_request_record_executed", "authorization_request_recorded", "approval_record_append_execution_authorized", "approval_record_append_execution_requested", "approval_record_append_executed", "approval_ledger_appended", "command_ledger_appended", "mode_change_requested", "mode_change_authorized", "pre_armed_dry_run_authorized", "live_authorized", "autotrade_resume_authorized"):
        payload[key] = False
        payload["operator_safety_lock"][key] = False
    if not safety:
        payload["operator_safety_lock"]["non_authorizing"] = False
    return payload


def _review(*, valid: bool) -> dict:
    return {"authorization_request_execution_gate_reviewed": bool(valid), "authorization_request_execution_gate_requested": bool(valid), "requested_by": "guard_operator" if valid else "", "requested_at": "2026-06-18T00:06:20Z" if valid else "", "operator_identity": "guard_human_operator" if valid else "", "acknowledgements": list(ACKS) if valid else ["confirm_s88_authorization_request_dry_run_plan_status_reviewed"], "authorization_request_execution_gate_authorized": False, "authorization_request_execution_gate_executed": False, "authorization_request_dry_run_plan_authorized": False, "authorization_request_dry_run_plan_executed": False, "authorization_request_preflight_authorized": False, "authorization_request_preflight_executed": False, "authorization_request_record_execution_authorized": False, "authorization_request_record_execution_requested": False, "authorization_request_record_executed": False, "authorization_request_recorded": False, "approval_record_append_execution_authorized": False, "approval_record_append_execution_requested": False, "approval_record_append_executed": False, "approval_ledger_append_requested": False, "command_ledger_append_requested": False, "mode_change_requested": False}


def _run_case(name: str, *, plan_ready: bool, review_valid: bool, plan_safety: bool = True) -> dict:
    case = TMP_ROOT / name
    case.mkdir(parents=True, exist_ok=True)
    plan_path = _write_json(case / "plan.json", _plan(ready=plan_ready, safety=plan_safety))
    review_path = _write_json(case / "review.json", _review(valid=review_valid))
    out = case / "gate_status.json"
    proc = subprocess.run([sys.executable, str(GATE), "--authorization-request-dry-run-plan-status", str(plan_path), "--authorization-request-execution-gate-review", str(review_path), "--out", str(out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=60)
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

    ready_reviewed = _run_case("ready_reviewed", plan_ready=True, review_valid=True)
    ready_missing_review = _run_case("ready_missing_review", plan_ready=True, review_valid=False)
    blocked_plan_reviewed = _run_case("blocked_plan_reviewed", plan_ready=False, review_valid=True)
    unsafe_plan_reviewed = _run_case("unsafe_plan_reviewed", plan_ready=True, review_valid=True, plan_safety=False)
    checks = {
        "ready_reviewed_returncode_zero": ready_reviewed.get("returncode") == 0 and ready_reviewed.get("ok") is True,
        "ready_reviewed_gate_ready_without_authorization": ready_reviewed.get("authorization_request_execution_gate_ready") is True and ready_reviewed.get("decision") == "authorization_request_execution_gate_dry_run_ready_not_authorized_not_recorded_not_executed",
        "ready_reviewed_no_record_execution_grant_append_or_mode_request": ready_reviewed.get("authorization_request_execution_gate_authorized") is False and ready_reviewed.get("authorization_request_execution_gate_requested") is False and ready_reviewed.get("authorization_request_execution_gate_executed") is False and ready_reviewed.get("authorization_request_recorded") is False and ready_reviewed.get("approval_record_append_execution_authorized") is False and ready_reviewed.get("approval_ledger_appended") is False and ready_reviewed.get("command_ledger_appended") is False and ready_reviewed.get("mode_change_requested") is False,
        "ready_missing_review_blocked_visible": ready_missing_review.get("returncode") == 0 and ready_missing_review.get("authorization_request_execution_gate_ready") is False and "authorization_request_execution_gate_review_not_confirmed" in (ready_missing_review.get("authorization_request_execution_gate_blockers") or []),
        "blocked_plan_reviewed_blocked_visible": blocked_plan_reviewed.get("returncode") == 0 and blocked_plan_reviewed.get("authorization_request_execution_gate_ready") is False and "authorization_request_dry_run_plan_status_not_ready" in (blocked_plan_reviewed.get("authorization_request_execution_gate_blockers") or []),
        "unsafe_plan_reviewed_blocks_and_returns_nonzero": unsafe_plan_reviewed.get("returncode") != 0 and unsafe_plan_reviewed.get("authorization_request_execution_gate_ready") is False and "authorization_request_dry_run_plan_operator_safety_lock_not_clear" in (unsafe_plan_reviewed.get("authorization_request_execution_gate_blockers") or []),
        "read_only_no_broker_non_authorizing": ready_reviewed.get("read_only") is True and ready_reviewed.get("would_send_to_broker") is False and ready_reviewed.get("pre_armed_dry_run_authorized") is False and ready_reviewed.get("live_authorized") is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    protected_dirty_hits: list[str] = []
    for line in subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines():
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone FD: {hit}" for hit in protected_dirty_hits)
    payload = {"ok": not failures, "phase": "phase4a_autotrade_milestone_fd_pre_armed_dry_run_authorization_request_execution_authorization_request_execution_authorization_request_execution_gate_dry_run_status_guard", "status": "closed" if not failures else "open", "contract": {"authorization_request_execution_gate_status_present": GATE.exists(), "ready_reviewed_gate_ready_without_authorization": checks.get("ready_reviewed_gate_ready_without_authorization", False), "missing_review_blocks_gate": checks.get("ready_missing_review_blocked_visible", False), "blocked_plan_blocks_gate": checks.get("blocked_plan_reviewed_blocked_visible", False), "unsafe_plan_blocks_gate": checks.get("unsafe_plan_reviewed_blocks_and_returns_nonzero", False), "no_record_execution_no_grant_no_append_no_mode_request": checks.get("ready_reviewed_no_record_execution_grant_append_or_mode_request", False), "read_only_no_broker_non_authorizing": checks.get("read_only_no_broker_non_authorizing", False), "protected_lower_layers_untouched": not protected_dirty_hits}, "checks": checks, "cases": {"ready_reviewed": {"ok": ready_reviewed.get("ok"), "decision": ready_reviewed.get("decision"), "authorization_request_execution_gate_ready": ready_reviewed.get("authorization_request_execution_gate_ready"), "authorization_request_execution_gate_authorized": ready_reviewed.get("authorization_request_execution_gate_authorized"), "authorization_request_execution_gate_requested": ready_reviewed.get("authorization_request_execution_gate_requested"), "authorization_request_execution_gate_executed": ready_reviewed.get("authorization_request_execution_gate_executed"), "authorization_request_recorded": ready_reviewed.get("authorization_request_recorded"), "mode_change_requested": ready_reviewed.get("mode_change_requested")}, "ready_missing_review": {"ok": ready_missing_review.get("ok"), "decision": ready_missing_review.get("decision"), "authorization_request_execution_gate_ready": ready_missing_review.get("authorization_request_execution_gate_ready"), "authorization_request_execution_gate_blockers": ready_missing_review.get("authorization_request_execution_gate_blockers")}, "blocked_plan_reviewed": {"ok": blocked_plan_reviewed.get("ok"), "decision": blocked_plan_reviewed.get("decision"), "authorization_request_execution_gate_ready": blocked_plan_reviewed.get("authorization_request_execution_gate_ready"), "authorization_request_execution_gate_blockers": blocked_plan_reviewed.get("authorization_request_execution_gate_blockers")}, "unsafe_plan_reviewed": {"ok": unsafe_plan_reviewed.get("ok"), "decision": unsafe_plan_reviewed.get("decision"), "authorization_request_execution_gate_ready": unsafe_plan_reviewed.get("authorization_request_execution_gate_ready"), "authorization_request_execution_gate_blockers": unsafe_plan_reviewed.get("authorization_request_execution_gate_blockers"), "returncode": unsafe_plan_reviewed.get("returncode")}}, "protected_dirty_hits": protected_dirty_hits, "failures": failures}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
