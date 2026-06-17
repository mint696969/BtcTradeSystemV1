# path: ./tools/test_phase4a_autotrade_milestone_eh_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_execution_authorization_request_record_preflight_status_guard.py
# desc: Guard S67 authorization request record execution authorization request record preflight/status remains preflight/status-only, non-recording, non-executing, and non-authorizing.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

REPO_ROOT = Path(__file__).resolve().parents[1]
RECORD_PREFLIGHT = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_execution_authorization_request_record_preflight_status.py"
AUTH_REQUEST = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_execution_authorization_request_status.py"
RECORD_GATE = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_execution_gate_dry_run_status.py"
RECORD_PLAN = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_dry_run_plan_status.py"
TMP_ROOT = REPO_ROOT / "tmp" / "_s67_pre_armed_dry_run_authorization_request_record_execution_authorization_request_record_preflight_status_guard"
PROTECTED_PREFIXES = ("btcts_next/src/btcts/collector_vnext/", "btcts_next/src/btcts/ingestion/", "btcts_next/src/btcts/processing/l3_market_semantics/", "btcts_next/src/btcts/processing/l4_consumer_models/")
CHECK_FILES = (RECORD_PREFLIGHT, AUTH_REQUEST, RECORD_GATE, RECORD_PLAN, REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/command_status.py")
FORBIDDEN_TOKENS = ("place_order(", "send_order(", "broker_order(", "private_api", "pybitflyer", "ccxt", "requests.post", "httpx.post", "append_command_ledger_record(", "validate_and_append_command", "submit_mode_change_command_request", "mode_changed=True", "would_send_to_broker=True", "pre_armed_dry_run_authorized=True", "armed_dry_run_authorized=True", "live_authorized=True", "approval_recorded=True", "human_approval_recorded=True", "operator_acknowledgement_recorded=True", "approval_ledger_appended=True", "command_ledger_appended=True", "mode_change_requested=True", "mode_change_authorized=True", "approval_record_append_execution_authorized=True", "approval_record_append_execution_requested=True", "approval_record_append_executed=True", "approval_record_append_request_submitted=True", "approval_record_append_request_persisted=True", "approval_record_persisted_by_this_tool=True", "authorization_request_recorded=True", "authorization_request_record_executed=True", "authorization_request_record_execution_requested=True", "authorization_request_record_execution_authorized=True", "authorization_request_record_execution_authorization_request_recorded=True", "while True")
ACKS = ("confirm_s66_record_execution_authorization_request_status_reviewed", "confirm_record_execution_authorization_request_record_preflight_is_review_only", "confirm_this_preflight_does_not_record_authorization_request", "confirm_no_record_execution_authorization_grant_append_or_mode_change_is_authorized", "confirm_separate_explicit_record_execution_slice_required_before_any_recording")


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return path


def _status(*, ready: bool) -> dict:
    source = {"record_execution_gate_decision": "authorization_request_record_execution_gate_dry_run_ready_not_executed", "record_execution_gate_ready": True, "record_dry_run_plan_decision": "authorization_request_record_dry_run_plan_ready_not_recorded", "record_dry_run_plan_ready": True, "record_preflight_decision": "authorization_request_record_preflight_ready_not_recorded", "record_preflight_ready": True, "evidence_id": "approval_evidence_guard_valid_001", "authorization_scope": "PRE_ARMED_DRY_RUN_APPROVAL_RECORD_APPEND_REVIEW_ONLY", "authorization_target": "APPROVAL_RECORD_APPEND_EXECUTION", "requested_by": "guard_operator", "requested_at": "2026-06-17T00:01:10Z"}
    draft = {"record_kind": "pre_armed_dry_run_append_execution_authorization_request_record_draft", "record_id": "authorization_request_record_dry_run_plan_approval_evidence_guard_valid_001", "evidence_id": "approval_evidence_guard_valid_001", "authorization_scope": "PRE_ARMED_DRY_RUN_APPROVAL_RECORD_APPEND_REVIEW_ONLY", "authorization_target": "APPROVAL_RECORD_APPEND_EXECUTION", "dry_run_only": True, "planned": True, "recorded": False, "persisted": False, "authorized": False, "executed": False}
    summary = {"authorization_scope": "PRE_ARMED_DRY_RUN_AUTHORIZATION_REQUEST_RECORD_EXECUTION_REVIEW_ONLY", "authorization_target": "APPROVAL_RECORD_APPEND_EXECUTION_AUTHORIZATION_REQUEST_RECORD_EXECUTION"}
    return {"ok": True, "report_version": "pre_armed_dry_run_approval_record_append_execution_authorization_request_record_execution_authorization_request_status.v1", "decision": "authorization_request_record_execution_authorization_request_ready_not_authorized_not_recorded_not_executed" if ready else "authorization_request_record_execution_authorization_request_blocked_not_authorized_not_recorded_not_executed", "authorization_request_record_execution_authorization_request_ready": ready, "record_execution_authorization_request_blockers": [] if ready else ["record_execution_gate_not_ready"], "authorization_request_record_execution_authorization_requested_observed": ready, "authorization_request_record_draft": draft, "source_summary": source, "record_execution_authorization_request_summary": summary, "read_only": True, "would_send_to_broker": False, "mode_changed": False, "authorization_request_record_execution_authorized": False, "authorization_request_record_execution_requested": False, "authorization_request_record_executed": False, "approval_record_append_execution_authorization_request_recorded": False, "authorization_request_recorded": False, "approval_record_append_execution_authorized": False, "approval_record_append_execution_requested": False, "approval_record_append_executed": False, "approval_record_append_request_submitted": False, "approval_record_append_request_persisted": False, "approval_record_persisted_by_this_tool": False, "approval_record_persisted": False, "approval_ledger_appended": False, "command_ledger_appended": False, "mode_change_requested": False, "mode_change_authorized": False, "pre_armed_dry_run_authorized": False, "live_authorized": False, "autotrade_resume_authorized": False, "status_only": True}


def _review(*, valid: bool) -> dict:
    return {"record_execution_authorization_request_record_preflight_reviewed": bool(valid), "record_execution_authorization_request_recording_requested": bool(valid), "record_preflight_scope": "PRE_ARMED_DRY_RUN_AUTHORIZATION_REQUEST_RECORD_EXECUTION_AUTHORIZATION_REQUEST_RECORD_REVIEW_ONLY" if valid else "LIVE", "record_preflight_target": "APPROVAL_RECORD_APPEND_EXECUTION_AUTHORIZATION_REQUEST_RECORD_EXECUTION_AUTHORIZATION_REQUEST_RECORD" if valid else "MODE_CHANGE", "requested_by": "guard_operator" if valid else "", "requested_at": "2026-06-17T00:01:20Z" if valid else "", "operator_identity": "guard_human_operator" if valid else "", "acknowledgements": list(ACKS) if valid else ["confirm_s66_record_execution_authorization_request_status_reviewed"], "authorization_request_record_execution_authorization_request_recorded": False, "authorization_request_record_execution_authorized": False, "authorization_request_record_execution_requested": False, "authorization_request_record_executed": False, "authorization_request_recorded": False, "approval_record_append_execution_authorized": False, "approval_record_append_execution_requested": False, "approval_record_append_executed": False, "approval_ledger_append_requested": False, "command_ledger_append_requested": False, "mode_change_requested": False}


def _run_case(name: str, *, status_ready: bool, review_valid: bool) -> dict:
    case = TMP_ROOT / name
    case.mkdir(parents=True, exist_ok=True)
    status_path = _write_json(case / "record_execution_authorization_request_status.json", _status(ready=status_ready))
    review_path = _write_json(case / "record_execution_authorization_request_record_preflight_review.json", _review(valid=review_valid))
    out = case / "record_execution_authorization_request_record_preflight_status.json"
    proc = subprocess.run([sys.executable, str(RECORD_PREFLIGHT), "--record-execution-authorization-request-status", str(status_path), "--record-execution-authorization-request-record-preflight-review", str(review_path), "--out", str(out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=60)
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
            for alias in node.names:
                out.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def main() -> int:
    failures: list[str] = []
    for path in CHECK_FILES:
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}"); continue
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

    ready_record_requested = _run_case("ready_record_requested", status_ready=True, review_valid=True)
    ready_missing_record_review = _run_case("ready_missing_record_review", status_ready=True, review_valid=False)
    blocked_status_record_requested = _run_case("blocked_status_record_requested", status_ready=False, review_valid=True)
    checks = {
        "ready_record_requested_returncode_zero": ready_record_requested.get("returncode") == 0 and ready_record_requested.get("ok") is True,
        "ready_record_requested_preflight_ready_not_recorded": ready_record_requested.get("authorization_request_record_execution_authorization_request_record_preflight_ready") is True and ready_record_requested.get("decision") == "authorization_request_record_execution_authorization_request_record_preflight_ready_not_recorded",
        "ready_record_requested_no_record_execution_grant_append_or_mode_request": ready_record_requested.get("record_execution_authorization_request_recording_requested_observed") is True and ready_record_requested.get("authorization_request_record_execution_authorization_request_recorded") is False and ready_record_requested.get("authorization_request_record_execution_authorized") is False and ready_record_requested.get("authorization_request_record_execution_requested") is False and ready_record_requested.get("authorization_request_record_executed") is False and ready_record_requested.get("authorization_request_recorded") is False and ready_record_requested.get("approval_record_append_execution_authorized") is False and ready_record_requested.get("approval_record_append_executed") is False and ready_record_requested.get("approval_ledger_appended") is False and ready_record_requested.get("command_ledger_appended") is False and ready_record_requested.get("mode_change_requested") is False,
        "ready_missing_record_review_blocked_visible": ready_missing_record_review.get("returncode") == 0 and ready_missing_record_review.get("authorization_request_record_execution_authorization_request_record_preflight_ready") is False and "record_execution_authorization_request_record_preflight_review_not_confirmed" in (ready_missing_record_review.get("record_execution_authorization_request_record_preflight_blockers") or []),
        "blocked_status_record_requested_blocked_visible": blocked_status_record_requested.get("returncode") == 0 and blocked_status_record_requested.get("authorization_request_record_execution_authorization_request_record_preflight_ready") is False and "record_execution_authorization_request_not_ready" in (blocked_status_record_requested.get("record_execution_authorization_request_record_preflight_blockers") or []),
        "blocked_cases_no_record_execution_grant_append_or_mode_request": ready_missing_record_review.get("authorization_request_record_execution_authorization_request_recorded") is False and blocked_status_record_requested.get("authorization_request_record_execution_authorization_request_recorded") is False and ready_missing_record_review.get("authorization_request_record_execution_authorized") is False and blocked_status_record_requested.get("authorization_request_record_execution_authorized") is False and ready_missing_record_review.get("authorization_request_record_executed") is False and blocked_status_record_requested.get("authorization_request_record_executed") is False and ready_missing_record_review.get("authorization_request_recorded") is False and blocked_status_record_requested.get("authorization_request_recorded") is False and ready_missing_record_review.get("mode_change_requested") is False and blocked_status_record_requested.get("mode_change_requested") is False,
        "read_only_no_broker_non_authorizing": ready_record_requested.get("read_only") is True and ready_record_requested.get("would_send_to_broker") is False and ready_record_requested.get("pre_armed_dry_run_authorized") is False and ready_record_requested.get("live_authorized") is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    protected_dirty_hits: list[str] = []
    for line in subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines():
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone EH: {hit}" for hit in protected_dirty_hits)
    payload = {"ok": not failures, "phase": "phase4a_autotrade_milestone_eh_pre_armed_dry_run_approval_record_append_execution_authorization_request_record_execution_authorization_request_record_preflight_status_guard", "status": "closed" if not failures else "open", "contract": {"authorization_request_record_execution_authorization_request_record_preflight_status_present": RECORD_PREFLIGHT.exists(), "ready_record_requested_preflight_ready_without_recording": checks.get("ready_record_requested_preflight_ready_not_recorded", False), "missing_record_review_blocks_preflight": checks.get("ready_missing_record_review_blocked_visible", False), "blocked_authorization_request_status_blocks_preflight": checks.get("blocked_status_record_requested_blocked_visible", False), "no_record_execution_no_grant_no_append_no_mode_request": checks.get("ready_record_requested_no_record_execution_grant_append_or_mode_request", False) and checks.get("blocked_cases_no_record_execution_grant_append_or_mode_request", False), "read_only_no_broker_non_authorizing": checks.get("read_only_no_broker_non_authorizing", False), "protected_lower_layers_untouched": not protected_dirty_hits}, "checks": checks, "cases": {"ready_record_requested": {"ok": ready_record_requested.get("ok"), "decision": ready_record_requested.get("decision"), "authorization_request_record_execution_authorization_request_record_preflight_ready": ready_record_requested.get("authorization_request_record_execution_authorization_request_record_preflight_ready"), "record_execution_authorization_request_recording_requested_observed": ready_record_requested.get("record_execution_authorization_request_recording_requested_observed"), "authorization_request_record_execution_authorization_request_recorded": ready_record_requested.get("authorization_request_record_execution_authorization_request_recorded"), "authorization_request_record_execution_authorized": ready_record_requested.get("authorization_request_record_execution_authorized"), "authorization_request_record_executed": ready_record_requested.get("authorization_request_record_executed"), "authorization_request_recorded": ready_record_requested.get("authorization_request_recorded"), "approval_record_append_execution_authorized": ready_record_requested.get("approval_record_append_execution_authorized"), "mode_change_requested": ready_record_requested.get("mode_change_requested")}, "ready_missing_record_review": {"ok": ready_missing_record_review.get("ok"), "decision": ready_missing_record_review.get("decision"), "authorization_request_record_execution_authorization_request_record_preflight_ready": ready_missing_record_review.get("authorization_request_record_execution_authorization_request_record_preflight_ready"), "record_execution_authorization_request_record_preflight_blockers": ready_missing_record_review.get("record_execution_authorization_request_record_preflight_blockers")}, "blocked_status_record_requested": {"ok": blocked_status_record_requested.get("ok"), "decision": blocked_status_record_requested.get("decision"), "authorization_request_record_execution_authorization_request_record_preflight_ready": blocked_status_record_requested.get("authorization_request_record_execution_authorization_request_record_preflight_ready"), "record_execution_authorization_request_record_preflight_blockers": blocked_status_record_requested.get("record_execution_authorization_request_record_preflight_blockers")}}, "protected_dirty_hits": protected_dirty_hits, "failures": failures}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
