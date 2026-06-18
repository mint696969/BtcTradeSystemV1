# path: ./tools/test_phase4a_autotrade_milestone_gi_runtime_integration_readiness_guard.py
# desc: Guard S120 runtime integration readiness remains summary-only and never executes, appends, applies modes, or touches brokers.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_runtime_integration_readiness_status.py"
S117 = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_authorization_grant_status.py"
S118 = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_authorization_record_persistence_preflight_status.py"
S119 = REPO_ROOT / "tools/run_sr_fx_pre_armed_dry_run_mode_apply_preview_status.py"
TMP_ROOT = REPO_ROOT / "tmp" / "_s120_runtime_integration_readiness_guard"
CHECK_FILES = (RUNNER, S117, S118, S119)
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
    "authorization_record_appended=True",
    "authorization_record_persisted=True",
    "record_persistence_executed=True",
    "mode_apply_executed=True",
    "mode_state_appended=True",
    "command_ledger_appended=True",
    "approval_ledger_appended=True",
    "mode_change_requested=True",
    "while True",
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
        "authorization_grant_granted": False,
        "authorization_grant_executed": False,
        "authorization_grant_recorded": False,
        "authorization_record_appended": False,
        "record_persistence_executed": False,
        "mode_apply_executed": False,
        "mode_changed": False,
        "command_ledger_appended": False,
        "approval_ledger_appended": False,
        "would_send_to_broker": False,
        "pre_armed_dry_run_authorized": False,
        "live_authorized": False,
    }


def _record(*, ready: bool, linked: bool = True) -> dict:
    grant_decision = "authorization_grant_status_ready_not_granted_not_recorded_not_executed" if linked else "wrong"
    return {
        "ok": True,
        "report_version": "pre_armed_dry_run_authorization_record_persistence_preflight_status.s118.v1",
        "decision": "authorization_record_persistence_preflight_ready_not_appended" if ready else "authorization_record_persistence_preflight_blocked_not_appended",
        "record_persistence_preflight_ready": ready,
        "record_persistence_blockers": [] if ready else ["record_guard_forced_not_ready"],
        "read_only": True,
        "preflight_status_only": True,
        "dry_run_only": True,
        "source_summary": {"authorization_grant_status_decision": grant_decision},
        "authorization_record_appended": False,
        "authorization_record_persisted": False,
        "record_persistence_executed": False,
        "authorization_grant_recorded": False,
        "mode_apply_executed": False,
        "mode_changed": False,
        "command_ledger_appended": False,
        "approval_ledger_appended": False,
        "would_send_to_broker": False,
        "pre_armed_dry_run_authorized": False,
        "live_authorized": False,
    }


def _mode(*, ready: bool, linked: bool = True) -> dict:
    record_decision = "authorization_record_persistence_preflight_ready_not_appended" if linked else "wrong"
    return {
        "ok": True,
        "report_version": "pre_armed_dry_run_mode_apply_preview_status.s119.v1",
        "decision": "mode_apply_preview_ready_not_applied" if ready else "mode_apply_preview_blocked_not_applied",
        "mode_apply_preview_ready": ready,
        "mode_apply_preview_blockers": [] if ready else ["mode_guard_forced_not_ready"],
        "read_only": True,
        "preview_only": True,
        "dry_run_only": True,
        "source_summary": {"record_persistence_preflight_decision": record_decision},
        "mode_transition_preview": {"current_mode": "SHADOW", "target_mode": "PRE_ARMED_DRY_RUN", "apply_executed": False},
        "mode_apply_executed": False,
        "mode_state_appended": False,
        "mode_changed": False,
        "mode_change_requested": False,
        "command_ledger_appended": False,
        "approval_ledger_appended": False,
        "would_send_to_broker": False,
        "pre_armed_dry_run_authorized": False,
        "live_authorized": False,
    }


def _run_case(name: str, *, grant_ready: bool, record_ready: bool, mode_ready: bool, linked: bool = True) -> dict:
    case = TMP_ROOT / name
    grant_path = _write_json(case / "grant.json", _grant(ready=grant_ready))
    record_path = _write_json(case / "record.json", _record(ready=record_ready, linked=linked))
    mode_path = _write_json(case / "mode.json", _mode(ready=mode_ready, linked=linked))
    out_path = case / "runtime_readiness.json"
    proc = subprocess.run(
        [sys.executable, str(RUNNER), "--authorization-grant-status", str(grant_path), "--record-persistence-preflight", str(record_path), "--mode-apply-preview", str(mode_path), "--out", str(out_path)],
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

    ready = _run_case("ready_all", grant_ready=True, record_ready=True, mode_ready=True)
    blocked_grant = _run_case("blocked_grant", grant_ready=False, record_ready=True, mode_ready=True)
    broken_link = _run_case("broken_link", grant_ready=True, record_ready=True, mode_ready=True, linked=False)
    checks = {
        "ready_case_returncode_zero": ready.get("returncode") == 0 and ready.get("ok") is True,
        "ready_case_runtime_ready_not_authorized": ready.get("runtime_integration_readiness_ready") is True and ready.get("decision") == "runtime_integration_readiness_ready_not_authorized_not_executed" and ready.get("pre_armed_dry_run_authorized") is False,
        "ready_case_operator_summary_visible": isinstance(ready.get("operator_readiness_summary"), dict) and ready.get("operator_readiness_summary", {}).get("target_mode") == "PRE_ARMED_DRY_RUN",
        "ready_case_no_execution_append_broker": ready.get("mode_apply_executed") is False and ready.get("record_persistence_executed") is False and ready.get("command_ledger_appended") is False and ready.get("would_send_to_broker") is False,
        "blocked_grant_blocks_visible": blocked_grant.get("returncode") == 0 and blocked_grant.get("runtime_integration_readiness_ready") is False and "authorization_grant_status_not_ready" in (blocked_grant.get("runtime_integration_blockers") or []),
        "broken_link_blocks_visible": broken_link.get("returncode") == 0 and broken_link.get("runtime_integration_readiness_ready") is False and "record_preflight_does_not_reference_grant_status_decision" in (broken_link.get("runtime_integration_blockers") or []),
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    for line in proc.stdout.splitlines():
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone GI: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_gi_runtime_integration_readiness_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "runtime_integration_readiness_runner_present": RUNNER.exists(),
            "ready_case_runtime_ready_not_authorized": checks.get("ready_case_runtime_ready_not_authorized", False),
            "operator_summary_visible": checks.get("ready_case_operator_summary_visible", False),
            "blocked_grant_blocks_status": checks.get("blocked_grant_blocks_visible", False),
            "broken_chain_link_blocks_status": checks.get("broken_link_blocks_visible", False),
            "no_execution_append_broker_or_authorization": checks.get("ready_case_no_execution_append_broker", False),
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "checks": checks,
        "cases": {
            "ready": {"ok": ready.get("ok"), "decision": ready.get("decision"), "runtime_integration_readiness_ready": ready.get("runtime_integration_readiness_ready"), "pre_armed_dry_run_authorized": ready.get("pre_armed_dry_run_authorized")},
            "blocked_grant": {"ok": blocked_grant.get("ok"), "decision": blocked_grant.get("decision"), "runtime_integration_readiness_ready": blocked_grant.get("runtime_integration_readiness_ready"), "runtime_integration_blockers": blocked_grant.get("runtime_integration_blockers")},
            "broken_link": {"ok": broken_link.get("ok"), "decision": broken_link.get("decision"), "runtime_integration_readiness_ready": broken_link.get("runtime_integration_readiness_ready"), "runtime_integration_blockers": broken_link.get("runtime_integration_blockers")},
        },
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_runtime_integration_readiness_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
