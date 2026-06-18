# path: ./tools/test_phase4a_autotrade_milestone_gh_mode_apply_preview_guard.py
# desc: Guard S119 mode apply preview remains preview-only and never applies modes, appends ledgers, or touches brokers.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_mode_apply_preview_status.py"
S118 = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_authorization_record_persistence_preflight_status.py"
TMP_ROOT = REPO_ROOT / "tmp" / "_s119_mode_apply_preview_guard"
CHECK_FILES = (RUNNER, S118)
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
    "apply_latest_mode_change_command_once",
    "mode_changed=True",
    "would_send_to_broker=True",
    "pre_armed_dry_run_authorized=True",
    "live_authorized=True",
    "mode_apply_executed=True",
    "mode_state_appended=True",
    "command_ledger_appended=True",
    "approval_ledger_appended=True",
    "mode_change_requested=True",
    "while True",
)
ACKS = (
    "confirm_s118_record_persistence_preflight_reviewed",
    "confirm_record_persistence_preflight_ready_is_not_mode_permission",
    "confirm_mode_apply_preview_is_read_only",
    "confirm_preview_does_not_append_command_ledger",
    "confirm_preview_does_not_append_mode_state",
    "confirm_preview_does_not_send_orders",
    "confirm_actual_mode_apply_requires_separate_slice",
)


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return path


def _preflight(*, ready: bool) -> dict:
    return {
        "ok": True,
        "report_version": "pre_armed_dry_run_authorization_record_persistence_preflight_status.s118.v1",
        "decision": "authorization_record_persistence_preflight_ready_not_appended" if ready else "authorization_record_persistence_preflight_blocked_not_appended",
        "record_persistence_preflight_ready": ready,
        "record_persistence_blockers": [] if ready else ["preflight_guard_forced_not_ready"],
        "read_only": True,
        "status_only": True,
        "preflight_status_only": True,
        "dry_run_only": True,
        "non_authorizing": True,
        "authorization_record_draft": {
            "record_id": "s118_guard_record_001",
            "persisted": False,
            "executed": False,
            "append_executed": False,
        },
        "checks": {"grant_ready_is_not_append_permission": True},
        "authorization_record_appended": False,
        "authorization_record_persisted": False,
        "record_persistence_executed": False,
        "authorization_grant_recorded": False,
        "approval_ledger_appended": False,
        "command_ledger_appended": False,
        "mode_change_requested": False,
        "mode_changed": False,
        "would_send_to_broker": False,
        "pre_armed_dry_run_authorized": False,
        "live_authorized": False,
        "autotrade_resume_authorized": False,
        "broker_execution_requested": False,
        "mode_apply_executed": False,
    }


def _request(*, valid: bool) -> dict:
    return {
        "mode_apply_preview_reviewed": bool(valid),
        "source_record_persistence_preflight_path": "tmp/_s119_mode_apply_preview_guard/preflight.json" if valid else "",
        "source_record_persistence_preflight_report_version": "pre_armed_dry_run_authorization_record_persistence_preflight_status.s118.v1" if valid else "wrong",
        "source_record_persistence_preflight_decision": "authorization_record_persistence_preflight_ready_not_appended" if valid else "wrong",
        "source_record_persistence_preflight_ready": bool(valid),
        "preview_id": "s119_guard_preview_001" if valid else "",
        "current_mode": "SHADOW" if valid else "LIVE_MIN_SIZE",
        "target_mode": "PRE_ARMED_DRY_RUN" if valid else "LIVE_MIN_SIZE",
        "requested_by": "guard_operator" if valid else "",
        "requested_at": "2026-06-18T00:20:00Z" if valid else "",
        "operator_identity": "guard_human_operator" if valid else "",
        "acknowledgements": list(ACKS) if valid else ["confirm_s118_record_persistence_preflight_reviewed"],
        "mode_apply_requested": False,
        "mode_state_append_requested": False,
        "command_ledger_append_requested": False,
        "approval_ledger_append_requested": False,
        "broker_execution_requested": False,
        "restricted_api_requested": False,
        "real_order_requested": False,
        "ui_command_button_requested": False,
        "watchdog_autonomous_execution_requested": False,
    }


def _run_case(name: str, *, preflight_ready: bool, request_valid: bool) -> dict:
    case = TMP_ROOT / name
    preflight_path = _write_json(case / "preflight.json", _preflight(ready=preflight_ready))
    request_path = _write_json(case / "request.json", _request(valid=request_valid))
    out_path = case / "preview.json"
    proc = subprocess.run(
        [sys.executable, str(RUNNER), "--record-persistence-preflight", str(preflight_path), "--mode-apply-preview-request", str(request_path), "--out", str(out_path)],
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

    ready = _run_case("ready_valid_request", preflight_ready=True, request_valid=True)
    missing_request = _run_case("ready_missing_request", preflight_ready=True, request_valid=False)
    blocked_preflight = _run_case("blocked_preflight_valid_request", preflight_ready=False, request_valid=True)
    checks = {
        "ready_case_returncode_zero": ready.get("returncode") == 0 and ready.get("ok") is True,
        "ready_case_preview_ready_not_applied": ready.get("mode_apply_preview_ready") is True and ready.get("decision") == "mode_apply_preview_ready_not_applied" and ready.get("mode_apply_executed") is False,
        "ready_case_preview_visible": isinstance(ready.get("mode_transition_preview"), dict) and ready.get("mode_transition_preview", {}).get("target_mode") == "PRE_ARMED_DRY_RUN" and ready.get("mode_transition_preview", {}).get("apply_executed") is False,
        "ready_case_no_mode_command_broker": ready.get("mode_state_appended") is False and ready.get("command_ledger_appended") is False and ready.get("mode_changed") is False and ready.get("would_send_to_broker") is False and ready.get("pre_armed_dry_run_authorized") is False and ready.get("live_authorized") is False,
        "missing_request_blocks_visible": missing_request.get("returncode") == 0 and missing_request.get("mode_apply_preview_ready") is False and "mode_apply_preview_review_not_confirmed" in (missing_request.get("mode_apply_preview_blockers") or []),
        "blocked_preflight_blocks_visible": blocked_preflight.get("returncode") == 0 and blocked_preflight.get("mode_apply_preview_ready") is False and "record_persistence_preflight_not_ready" in (blocked_preflight.get("mode_apply_preview_blockers") or []),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    for line in proc.stdout.splitlines():
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone GH: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_gh_mode_apply_preview_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "mode_apply_preview_runner_present": RUNNER.exists(),
            "ready_case_preview_ready_not_applied": checks.get("ready_case_preview_ready_not_applied", False),
            "mode_transition_preview_visible": checks.get("ready_case_preview_visible", False),
            "missing_request_blocks_status": checks.get("missing_request_blocks_visible", False),
            "blocked_preflight_blocks_status": checks.get("blocked_preflight_blocks_visible", False),
            "no_mode_apply_command_append_broker_or_authorization": checks.get("ready_case_no_mode_command_broker", False),
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "checks": checks,
        "cases": {
            "ready": {"ok": ready.get("ok"), "decision": ready.get("decision"), "mode_apply_preview_ready": ready.get("mode_apply_preview_ready"), "mode_apply_executed": ready.get("mode_apply_executed"), "mode_state_appended": ready.get("mode_state_appended"), "command_ledger_appended": ready.get("command_ledger_appended")},
            "missing_request": {"ok": missing_request.get("ok"), "decision": missing_request.get("decision"), "mode_apply_preview_ready": missing_request.get("mode_apply_preview_ready"), "mode_apply_preview_blockers": missing_request.get("mode_apply_preview_blockers")},
            "blocked_preflight": {"ok": blocked_preflight.get("ok"), "decision": blocked_preflight.get("decision"), "mode_apply_preview_ready": blocked_preflight.get("mode_apply_preview_ready"), "mode_apply_preview_blockers": blocked_preflight.get("mode_apply_preview_blockers")},
        },
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
