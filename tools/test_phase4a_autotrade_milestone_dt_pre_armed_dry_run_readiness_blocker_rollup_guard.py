# path: ./tools/test_phase4a_autotrade_milestone_dt_pre_armed_dry_run_readiness_blocker_rollup_guard.py
# desc: Guard S54 Pre-Armed Dry Run readiness blocker rollup remains broker-free, informational, and non-authorizing.

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
TMP_ROOT = REPO_ROOT / "tmp" / "_s54_pre_armed_dry_run_readiness_blocker_rollup_guard"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
CHECK_FILES = (
    ROLLUP,
    CLEARANCE,
    EVIDENCE,
    WRAPPER,
    REPO_ROOT / "btcts_next/src/btcts/apps/sr_fx_final_review_package_once.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/sr_fx_data_ui_gate_handoff_once.py",
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
    "mode_changed=True",
    "would_send_to_broker=True",
    "pre_armed_dry_run_authorized=True",
    "armed_dry_run_authorized=True",
    "live_authorized=True",
    "while True",
)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _seed_state(state_root: Path) -> None:
    state = state_root / "collector_vnext"
    _write_json(
        state / "operator_ui" / "sr_fx_final_readiness_checkpoint.json",
        {
            "ok": True,
            "data_ui_integrity_ready_for_final_human_review": True,
            "autotrade_resume_authorized": False,
            "blocked_by": [],
            "summary": {"primary_lineage": "continuous_ws", "service_stale": False},
            "context": {"product_code": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"},
            "read_only": True,
            "would_send_to_broker": False,
        },
    )
    _write_json(
        state / "public" / "bitflyer_fx_public_market_readiness.json",
        {
            "public_market_readiness": {
                "ok": True,
                "product_code": "FX_BTC_JPY",
                "market_uid": "bitflyer.fx.FX_BTC_JPY",
                "blocked_by": [],
                "warnings": [],
                "read_only": True,
                "would_send_to_broker": False,
            }
        },
    )
    _write_json(
        state / "private" / "bitflyer_fx_readiness.json",
        {
            "readiness": {
                "product_code": "FX_BTC_JPY",
                "market_uid": "bitflyer.fx.FX_BTC_JPY",
                "private_state_known_and_fresh": True,
                "account_clear_for_new_auto_entry": True,
                "blocked_by": [],
                "read_only": True,
                "would_send_to_broker": False,
            }
        },
    )
    _write_json(
        state / "private" / "bitflyer_fx_live_readiness_contract.json",
        {
            "live_readiness_contract": {
                "ready": False,
                "product_code": "FX_BTC_JPY",
                "market_uid": "bitflyer.fx.FX_BTC_JPY",
                "blocked_by": ["order_sender_not_implemented"],
                "read_only": True,
                "would_send_to_broker": False,
            }
        },
    )


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
    wrapper_proc = subprocess.run(
        [
            sys.executable, str(WRAPPER),
            "--data-root", str(data_root),
            "--logs-root", str(logs_root),
            "--state-root", str(state_root),
            "--runtime-root", str(runtime_root),
            "--now", "2026-06-17T00:00:10Z",
            "--out", str(wrapper_out),
            *extra_args,
        ],
        cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120,
    )
    evidence_proc = subprocess.run(
        [sys.executable, str(EVIDENCE), "--wrapper-out", str(wrapper_out), "--out", str(evidence_out)],
        cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120,
    )
    clearance_proc = subprocess.run(
        [sys.executable, str(CLEARANCE), "--evidence-report", str(evidence_out), "--out", str(clearance_out)],
        cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120,
    )
    rollup_proc = subprocess.run(
        [sys.executable, str(ROLLUP), "--clearance-runbook", str(clearance_out), "--out", str(rollup_out)],
        cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120,
    )
    try:
        rollup = json.loads(rollup_proc.stdout)
    except Exception as exc:
        rollup = {"ok": False, "error": f"rollup stdout was not JSON: {exc}", "stdout_tail": rollup_proc.stdout[-1600:]}
    return {
        "case": case_name,
        "wrapper_returncode": wrapper_proc.returncode,
        "evidence_returncode": evidence_proc.returncode,
        "clearance_returncode": clearance_proc.returncode,
        "rollup_returncode": rollup_proc.returncode,
        "rollup": rollup,
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
    blocked = _run_case(
        "blocked",
        [
            "--heartbeat-observed-at", "2026-06-17T00:00:00Z",
            "--heartbeat-max-age-sec", "5",
            "--incident-open", "1",
            "--incident-reason", "guard_open_incident",
            "--kill-switch-active", "1",
            "--kill-switch-action", "HALT_AND_CANCEL",
            "--kill-switch-reason", "guard_kill_switch",
        ],
    )
    clear_rollup = clear["rollup"]
    blocked_rollup = blocked["rollup"]
    clear_blockers = clear_rollup.get("blocker_rollup") or []
    blocked_blockers = blocked_rollup.get("blocker_rollup") or []
    blocked_actions = blocked_rollup.get("operator_required_actions") or []

    checks = {
        "clear_pipeline_returncode_zero": clear["wrapper_returncode"] == 0 and clear["evidence_returncode"] == 0 and clear["clearance_returncode"] == 0 and clear["rollup_returncode"] == 0,
        "clear_rollup_ok": clear_rollup.get("ok") is True,
        "clear_runtime_control_prereqs_met_visible": clear_rollup.get("runtime_control_clearance_prerequisites_met") is True,
        "clear_rollup_informational_not_authorizing": clear_rollup.get("pre_armed_dry_run_authorized") is False and clear_rollup.get("live_authorized") is False and clear_rollup.get("autotrade_resume_authorized") is False,
        "clear_remaining_execution_blockers_visible": any("order_sender_not_implemented" in item for item in clear_blockers) and "armed_dry_run_authorization:not_in_this_slice" in clear_blockers,
        "blocked_pipeline_returncode_zero": blocked["wrapper_returncode"] == 0 and blocked["evidence_returncode"] == 0 and blocked["clearance_returncode"] == 0 and blocked["rollup_returncode"] == 0,
        "blocked_rollup_ok": blocked_rollup.get("ok") is True,
        "blocked_runtime_control_prereqs_not_met_visible": blocked_rollup.get("runtime_control_clearance_prerequisites_met") is False,
        "blocked_runtime_control_blockers_visible": any("heartbeat_stale" in item for item in blocked_blockers) and any("kill_switch_active" in item for item in blocked_blockers) and any("open_incident_present" in item for item in blocked_blockers),
        "blocked_actions_include_clearance_chain": "observe_fresh_runtime_heartbeat_and_rerun_runtime_control_sequence" in blocked_actions and "clear_or_acknowledge_kill_switch_with_explicit_human_protocol" in blocked_actions and "resolve_or_explicitly_close_runtime_incident_before_live_review" in blocked_actions,
        "blocked_rollup_informational_not_authorizing": blocked_rollup.get("pre_armed_dry_run_authorized") is False and blocked_rollup.get("live_authorized") is False and blocked_rollup.get("autotrade_resume_authorized") is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DT: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_dt_pre_armed_dry_run_readiness_blocker_rollup_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "pre_armed_rollup_present": ROLLUP.exists(),
            "clear_case_rollup_complete_without_authorization": checks.get("clear_rollup_ok", False) and checks.get("clear_rollup_informational_not_authorizing", False),
            "clear_case_remaining_execution_blockers_visible": checks.get("clear_remaining_execution_blockers_visible", False),
            "blocked_case_runtime_control_blockers_visible": checks.get("blocked_runtime_control_blockers_visible", False),
            "blocked_case_clearance_chain_visible": checks.get("blocked_actions_include_clearance_chain", False),
            "read_only_no_broker_non_authorizing": checks.get("clear_rollup_informational_not_authorizing", False) and checks.get("blocked_rollup_informational_not_authorizing", False),
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "checks": checks,
        "cases": {
            "clear": {
                "rollup_ok": clear_rollup.get("ok"),
                "decision": clear_rollup.get("decision"),
                "runtime_control_clearance_prerequisites_met": clear_rollup.get("runtime_control_clearance_prerequisites_met"),
                "blocker_rollup": clear_blockers,
                "operator_required_actions": clear_rollup.get("operator_required_actions"),
            },
            "blocked": {
                "rollup_ok": blocked_rollup.get("ok"),
                "decision": blocked_rollup.get("decision"),
                "runtime_control_clearance_prerequisites_met": blocked_rollup.get("runtime_control_clearance_prerequisites_met"),
                "blocker_rollup": blocked_blockers,
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
