# path: ./tools/test_phase4a_autotrade_milestone_ea_pre_armed_dry_run_approval_record_append_request_dry_run_plan_guard.py
# desc: Guard S60 approval record append request dry-run plan remains plan/status-only and non-authorizing.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_record_append_request_dry_run_plan.py"
LEDGER_STATUS = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_record_ledger_status.py"
PREFLIGHT = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_record_append_preflight_status.py"
VALIDATOR = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_approval_evidence_dry_run_validator.py"
TMP_ROOT = REPO_ROOT / "tmp" / "_s60_pre_armed_dry_run_approval_record_append_request_dry_run_plan_guard"
PROTECTED_PREFIXES = ("btcts_next/src/btcts/collector_vnext/", "btcts_next/src/btcts/ingestion/", "btcts_next/src/btcts/processing/l3_market_semantics/", "btcts_next/src/btcts/processing/l4_consumer_models/")
CHECK_FILES = (PLAN, LEDGER_STATUS, PREFLIGHT, VALIDATOR, REPO_ROOT / "btcts_next/src/btcts/autotrade/execution/command_status.py")
FORBIDDEN_TOKENS = ("place_order(", "send_order(", "broker_order(", "private_api", "pybitflyer", "ccxt", "requests.post", "httpx.post", "append_command_ledger_record(", "validate_and_append_command", "submit_mode_change_command_request", "mode_changed=True", "would_send_to_broker=True", "pre_armed_dry_run_authorized=True", "armed_dry_run_authorized=True", "live_authorized=True", "approval_recorded=True", "human_approval_recorded=True", "operator_acknowledgement_recorded=True", "approval_ledger_appended=True", "command_ledger_appended=True", "mode_change_requested=True", "mode_change_authorized=True", "approval_record_append_request_submitted=True", "approval_record_append_request_persisted=True", "approval_record_persisted_by_this_tool=True", "while True")


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return path


def _preflight(*, ready: bool) -> dict:
    draft = {"record_kind": "pre_armed_dry_run_review_approval_record_draft", "evidence_id": "approval_evidence_guard_valid_001", "approval_scope": "PRE_ARMED_DRY_RUN_REVIEW_ONLY", "target_mode": "PRE_ARMED_DRY_RUN", "requested_by": "guard_operator", "requested_at": "2026-06-17T00:00:20Z", "operator_identity_present": True, "reason_codes": ["operator_final_human_review", "pre_armed_dry_run_review_only"], "persisted": False, "status_only": True}
    return {"ok": True, "report_version": "pre_armed_dry_run_approval_record_append_preflight_status.v1", "decision": "approval_record_append_preflight_ready_not_appended" if ready else "approval_record_append_preflight_blocked_not_appended", "approval_record_append_preflight_ready": ready, "preflight_blockers": [] if ready else ["approval_evidence_not_valid"], "approval_record_draft": draft, "source_summary": {"source_status_decision": "approval_request_status_ready_for_human_review_not_recorded", "source_ready_for_human_review": True}, "read_only": True, "would_send_to_broker": False, "mode_changed": False, "approval_record_persisted": False, "approval_ledger_appended": False, "command_ledger_appended": False, "mode_change_requested": False, "mode_change_authorized": False, "pre_armed_dry_run_authorized": False, "live_authorized": False, "autotrade_resume_authorized": False}


def _ledger(*, existing: bool) -> dict:
    latest = {"record_id": "approval_record_guard_valid_001", "evidence_id": "approval_evidence_guard_valid_001", "approval_scope": "PRE_ARMED_DRY_RUN_REVIEW_ONLY", "target_mode": "PRE_ARMED_DRY_RUN", "valid": True} if existing else {}
    return {"ok": True, "report_version": "pre_armed_dry_run_approval_record_ledger_status.v1", "decision": "approval_record_ledger_status_read_only_records_present" if existing else "approval_record_ledger_status_read_only_missing", "approval_record_ledger_status_ready": True, "ledger_human_approval_records_observed": existing, "valid_record_count": 1 if existing else 0, "latest_valid_approval_record": latest, "read_only": True, "would_send_to_broker": False, "mode_changed": False, "approval_record_persisted_by_this_tool": False, "approval_record_persisted": False, "approval_ledger_appended": False, "command_ledger_appended": False, "mode_change_requested": False, "mode_change_authorized": False, "pre_armed_dry_run_authorized": False, "live_authorized": False, "autotrade_resume_authorized": False}


def _run_case(name: str, *, ready: bool, existing: bool) -> dict:
    case = TMP_ROOT / name
    case.mkdir(parents=True, exist_ok=True)
    preflight_path = _write_json(case / "preflight.json", _preflight(ready=ready))
    ledger_path = _write_json(case / "ledger_status.json", _ledger(existing=existing))
    out = case / "plan.json"
    proc = subprocess.run([sys.executable, str(PLAN), "--append-preflight-status", str(preflight_path), "--approval-record-ledger-status", str(ledger_path), "--out", str(out)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=60)
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

    ready_missing = _run_case("ready_missing", ready=True, existing=False)
    ready_duplicate = _run_case("ready_duplicate", ready=True, existing=True)
    blocked_missing = _run_case("blocked_missing", ready=False, existing=False)
    checks = {
        "ready_missing_returncode_zero": ready_missing.get("returncode") == 0 and ready_missing.get("ok") is True,
        "ready_missing_plan_ready_not_submitted": ready_missing.get("approval_record_append_request_plan_ready") is True and ready_missing.get("decision") == "approval_record_append_request_dry_run_plan_ready_not_submitted" and ready_missing.get("approval_record_append_request_submitted") is False,
        "ready_missing_no_append_or_mode_request": ready_missing.get("approval_record_append_request_persisted") is False and ready_missing.get("approval_ledger_appended") is False and ready_missing.get("command_ledger_appended") is False and ready_missing.get("mode_change_requested") is False,
        "ready_duplicate_blocked_visible": ready_duplicate.get("returncode") == 0 and ready_duplicate.get("approval_record_append_request_plan_ready") is False and "approval_record_already_observed_in_ledger" in (ready_duplicate.get("plan_blockers") or []),
        "blocked_preflight_blocked_visible": blocked_missing.get("returncode") == 0 and blocked_missing.get("approval_record_append_request_plan_ready") is False and "append_preflight_not_ready" in (blocked_missing.get("plan_blockers") or []),
        "blocked_cases_no_append_or_mode_request": ready_duplicate.get("approval_record_append_request_persisted") is False and blocked_missing.get("approval_record_append_request_persisted") is False and ready_duplicate.get("mode_change_requested") is False and blocked_missing.get("mode_change_requested") is False,
        "read_only_no_broker_non_authorizing": ready_missing.get("read_only") is True and ready_missing.get("would_send_to_broker") is False and ready_missing.get("pre_armed_dry_run_authorized") is False and ready_missing.get("live_authorized") is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)
    protected_dirty_hits: list[str] = []
    for line in subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines():
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone EA: {hit}" for hit in protected_dirty_hits)
    payload = {"ok": not failures, "phase": "phase4a_autotrade_milestone_ea_pre_armed_dry_run_approval_record_append_request_dry_run_plan_guard", "status": "closed" if not failures else "open", "contract": {"approval_record_append_request_dry_run_plan_present": PLAN.exists(), "ready_missing_plan_ready_without_submit": checks.get("ready_missing_plan_ready_not_submitted", False), "duplicate_record_blocks_plan": checks.get("ready_duplicate_blocked_visible", False), "blocked_preflight_blocks_plan": checks.get("blocked_preflight_blocked_visible", False), "no_append_no_ledger_no_mode_request": checks.get("ready_missing_no_append_or_mode_request", False) and checks.get("blocked_cases_no_append_or_mode_request", False), "read_only_no_broker_non_authorizing": checks.get("read_only_no_broker_non_authorizing", False), "protected_lower_layers_untouched": not protected_dirty_hits}, "checks": checks, "cases": {"ready_missing": {"ok": ready_missing.get("ok"), "decision": ready_missing.get("decision"), "approval_record_append_request_plan_ready": ready_missing.get("approval_record_append_request_plan_ready"), "approval_record_append_request_submitted": ready_missing.get("approval_record_append_request_submitted"), "approval_record_append_request_persisted": ready_missing.get("approval_record_append_request_persisted"), "mode_change_requested": ready_missing.get("mode_change_requested")}, "ready_duplicate": {"ok": ready_duplicate.get("ok"), "decision": ready_duplicate.get("decision"), "approval_record_append_request_plan_ready": ready_duplicate.get("approval_record_append_request_plan_ready"), "plan_blockers": ready_duplicate.get("plan_blockers")}, "blocked_missing": {"ok": blocked_missing.get("ok"), "decision": blocked_missing.get("decision"), "approval_record_append_request_plan_ready": blocked_missing.get("approval_record_append_request_plan_ready"), "plan_blockers": blocked_missing.get("plan_blockers")}}, "protected_dirty_hits": protected_dirty_hits, "failures": failures}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
