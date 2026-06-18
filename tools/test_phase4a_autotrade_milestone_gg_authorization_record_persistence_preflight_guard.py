# path: ./tools/test_phase4a_autotrade_milestone_gg_authorization_record_persistence_preflight_guard.py
# desc: Guard S118 authorization record persistence schema/preflight remains status-only and never appends records, ledgers, modes, or broker actions.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_authorization_record_persistence_preflight_status.py"
S117 = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_authorization_grant_status.py"
TMP_ROOT = REPO_ROOT / "tmp" / "_s118_authorization_record_persistence_preflight_guard"
CHECK_FILES = (RUNNER, S117)
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
FORBIDDEN_TOKENS = (
    "place_order(",
    "send_order(",
    "broker_order(",
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
    "live_authorized=True",
    "authorization_record_appended=True",
    "authorization_record_persisted=True",
    "record_persistence_executed=True",
    "authorization_grant_recorded=True",
    "approval_ledger_appended=True",
    "command_ledger_appended=True",
    "mode_change_requested=True",
    "mode_apply_executed=True",
    "while True",
)
ACKS = (
    "confirm_s117_authorization_grant_status_reviewed",
    "confirm_authorization_grant_ready_is_not_append_permission",
    "confirm_record_persistence_schema_reviewed",
    "confirm_append_preflight_does_not_write_records",
    "confirm_approval_and_command_ledgers_are_not_appended",
    "confirm_mode_apply_requires_separate_slice",
    "confirm_broker_execution_requires_later_explicit_armed_or_live_boundary",
)


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return path


def _grant(*, ready: bool) -> dict:
    return {
        "ok": True,
        "report_version": "pre_armed_dry_run_authorization_grant_status.s117.v1",
        "decision": "authorization_grant_status_ready_not_granted_not_recorded_not_executed" if ready else "authorization_grant_status_blocked_not_granted_not_recorded_not_executed",
        "authorization_grant_ready": ready,
        "authorization_grant_blockers": [] if ready else ["grant_guard_forced_not_ready"],
        "read_only": True,
        "status_only": True,
        "dry_run_only": True,
        "non_authorizing": True,
        "source_summary": {
            "source_authorization_request_status_report_version": "pre_armed_dry_run_authorization_request_status.s114.v1",
            "source_authorization_request_status_decision": "authorization_request_status_ready_not_authorized_not_recorded_not_executed",
            "source_authorization_request_status_ready": True,
            "source_commit_head": "47113f7f",
        },
        "grant_summary": {
            "requested_scope": "PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_RECORD_APPEND_PRECHECK_ONLY",
            "operator_identity_present": True,
            "granted_by_present": True,
        },
        "checks": {"ready_is_not_approval": True},
        "authorization_grant_granted": False,
        "authorization_grant_executed": False,
        "authorization_grant_recorded": False,
        "approval_ledger_appended": False,
        "command_ledger_appended": False,
        "mode_change_requested": False,
        "mode_changed": False,
        "would_send_to_broker": False,
        "pre_armed_dry_run_authorized": False,
        "live_authorized": False,
        "autotrade_resume_authorized": False,
        "authorization_request_recorded": False,
        "authorization_record_appended": False,
        "record_persistence_executed": False,
        "mode_apply_executed": False,
    }


def _request(*, valid: bool) -> dict:
    return {
        "record_persistence_preflight_reviewed": bool(valid),
        "source_authorization_grant_status_path": "tmp/_s118_authorization_record_persistence_preflight_guard/grant.json" if valid else "",
        "source_authorization_grant_status_report_version": "pre_armed_dry_run_authorization_grant_status.s117.v1" if valid else "wrong",
        "source_authorization_grant_status_decision": "authorization_grant_status_ready_not_granted_not_recorded_not_executed" if valid else "wrong",
        "source_authorization_grant_ready": bool(valid),
        "record_kind": "pre_armed_dry_run_authorization_grant_record" if valid else "live_authorization_record",
        "requested_append_scope": "PRE_ARMED_DRY_RUN_AUTHORIZATION_GRANT_RECORD_APPEND_PRECHECK_ONLY" if valid else "LIVE_APPEND",
        "schema_version": "pre_armed_dry_run_authorization_record.v1" if valid else "wrong",
        "idempotency_key": "s118_guard_idempotency_001" if valid else "",
        "record_id": "s118_guard_record_001" if valid else "",
        "append_only_path": "tmp/autotrade/authorization_records/pre_armed_dry_run_authorization_records.jsonl" if valid else "../bad.jsonl",
        "requested_by": "guard_operator" if valid else "",
        "requested_at": "2026-06-18T00:10:00Z" if valid else "",
        "operator_identity": "guard_human_operator" if valid else "",
        "acknowledgements": list(ACKS) if valid else ["confirm_s117_authorization_grant_status_reviewed"],
        "append_execution_requested": False,
        "record_write_requested": False,
        "approval_ledger_append_requested": False,
        "command_ledger_append_requested": False,
        "mode_change_requested": False,
        "mode_apply_requested": False,
        "broker_execution_requested": False,
        "restricted_api_requested": False,
        "real_order_requested": False,
        "ui_command_button_requested": False,
        "watchdog_autonomous_execution_requested": False,
    }


def _run_case(name: str, *, grant_ready: bool, request_valid: bool) -> dict:
    case = TMP_ROOT / name
    grant_path = _write_json(case / "grant.json", _grant(ready=grant_ready))
    request_path = _write_json(case / "request.json", _request(valid=request_valid))
    out_path = case / "preflight.json"
    proc = subprocess.run(
        [sys.executable, str(RUNNER), "--authorization-grant-status", str(grant_path), "--record-persistence-request", str(request_path), "--out", str(out_path)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=60,
    )
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

    ready = _run_case("ready_valid_request", grant_ready=True, request_valid=True)
    missing_request = _run_case("ready_missing_request", grant_ready=True, request_valid=False)
    blocked_grant = _run_case("blocked_grant_valid_request", grant_ready=False, request_valid=True)
    checks = {
        "ready_case_returncode_zero": ready.get("returncode") == 0 and ready.get("ok") is True,
        "ready_case_preflight_ready_not_appended": ready.get("record_persistence_preflight_ready") is True and ready.get("decision") == "authorization_record_persistence_preflight_ready_not_appended" and ready.get("authorization_record_appended") is False,
        "ready_case_schema_and_draft_visible": isinstance(ready.get("authorization_record_schema"), dict) and isinstance(ready.get("authorization_record_draft"), dict) and ready.get("authorization_record_draft", {}).get("persisted") is False,
        "ready_case_no_append_ledger_mode_broker": ready.get("record_persistence_executed") is False and ready.get("authorization_record_persisted") is False and ready.get("approval_ledger_appended") is False and ready.get("command_ledger_appended") is False and ready.get("mode_change_requested") is False and ready.get("would_send_to_broker") is False and ready.get("pre_armed_dry_run_authorized") is False and ready.get("live_authorized") is False,
        "missing_request_blocks_visible": missing_request.get("returncode") == 0 and missing_request.get("record_persistence_preflight_ready") is False and "record_persistence_preflight_review_not_confirmed" in (missing_request.get("record_persistence_blockers") or []),
        "blocked_grant_blocks_visible": blocked_grant.get("returncode") == 0 and blocked_grant.get("record_persistence_preflight_ready") is False and "authorization_grant_status_not_ready" in (blocked_grant.get("record_persistence_blockers") or []),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    for line in proc.stdout.splitlines():
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone GG: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_gg_authorization_record_persistence_preflight_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "record_persistence_preflight_runner_present": RUNNER.exists(),
            "ready_case_preflight_ready_not_appended": checks.get("ready_case_preflight_ready_not_appended", False),
            "schema_and_draft_visible": checks.get("ready_case_schema_and_draft_visible", False),
            "missing_request_blocks_status": checks.get("missing_request_blocks_visible", False),
            "blocked_grant_blocks_status": checks.get("blocked_grant_blocks_visible", False),
            "no_append_ledger_mode_broker_or_authorization": checks.get("ready_case_no_append_ledger_mode_broker", False),
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "checks": checks,
        "cases": {
            "ready": {"ok": ready.get("ok"), "decision": ready.get("decision"), "record_persistence_preflight_ready": ready.get("record_persistence_preflight_ready"), "authorization_record_appended": ready.get("authorization_record_appended"), "authorization_record_persisted": ready.get("authorization_record_persisted"), "mode_change_requested": ready.get("mode_change_requested")},
            "missing_request": {"ok": missing_request.get("ok"), "decision": missing_request.get("decision"), "record_persistence_preflight_ready": missing_request.get("record_persistence_preflight_ready"), "record_persistence_blockers": missing_request.get("record_persistence_blockers")},
            "blocked_grant": {"ok": blocked_grant.get("ok"), "decision": blocked_grant.get("decision"), "record_persistence_preflight_ready": blocked_grant.get("record_persistence_preflight_ready"), "record_persistence_blockers": blocked_grant.get("record_persistence_blockers")},
        },
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
