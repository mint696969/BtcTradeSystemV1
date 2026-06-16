# path: ./tools/test_phase4a_autotrade_milestone_dr_runtime_control_operational_evidence_report_guard.py
# desc: Guard S52 runtime_control operational evidence report remains broker-free and proves heartbeat/incident/kill-switch visibility after S51 wrapper.

from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "tools/run_sr_fx_runtime_control_report_sequence_once.py"
REPORT = REPO_ROOT / "tools/run_sr_fx_runtime_control_operational_evidence_report.py"
TMP_ROOT = REPO_ROOT / "tmp" / "_s52_runtime_control_operational_evidence_guard"
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/ingestion/",
    "btcts_next/src/btcts/processing/l3_market_semantics/",
    "btcts_next/src/btcts/processing/l4_consumer_models/",
)
CHECK_FILES = (
    REPORT,
    WRAPPER,
    REPO_ROOT / "btcts_next/src/btcts/apps/sr_fx_runtime_control_report_sequence_once.py",
    REPO_ROOT / "btcts_next/src/btcts/apps/sr_fx_runtime_control_snapshot_once.py",
)
TEXT_SCAN_FILES = CHECK_FILES
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
    report_out = case_root / "evidence_report.json"
    base_args = [
        sys.executable,
        str(WRAPPER),
        "--data-root",
        str(data_root),
        "--logs-root",
        str(logs_root),
        "--state-root",
        str(state_root),
        "--runtime-root",
        str(runtime_root),
        "--now",
        "2026-06-17T00:00:10Z",
        "--out",
        str(wrapper_out),
    ]
    wrapper_proc = subprocess.run([*base_args, *extra_args], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    report_proc = subprocess.run(
        [sys.executable, str(REPORT), "--wrapper-out", str(wrapper_out), "--out", str(report_out)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=120,
    )
    try:
        report = json.loads(report_proc.stdout)
    except Exception as exc:
        report = {"ok": False, "error": f"report stdout was not JSON: {exc}", "stdout_tail": report_proc.stdout[-1600:]}
    return {
        "case": case_name,
        "wrapper_returncode": wrapper_proc.returncode,
        "report_returncode": report_proc.returncode,
        "wrapper_stdout_tail": wrapper_proc.stdout[-1200:],
        "wrapper_stderr_tail": wrapper_proc.stderr[-1200:],
        "report_stdout_tail": report_proc.stdout[-1200:],
        "report_stderr_tail": report_proc.stderr[-1200:],
        "report": report,
        "wrapper_out_exists": wrapper_out.exists(),
        "report_out_exists": report_out.exists(),
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
    for path in TEXT_SCAN_FILES:
        if not path.exists():
            continue
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
            "--heartbeat-observed-at",
            "2026-06-17T00:00:00Z",
            "--heartbeat-max-age-sec",
            "5",
            "--incident-open",
            "1",
            "--incident-reason",
            "guard_open_incident",
            "--kill-switch-active",
            "1",
            "--kill-switch-action",
            "HALT_AND_CANCEL",
            "--kill-switch-reason",
            "guard_kill_switch",
        ],
    )
    clear_report = clear["report"]
    blocked_report = blocked["report"]
    blocked_evidence = blocked_report.get("evidence", {}) if isinstance(blocked_report, dict) else {}
    blocked_kill = (blocked_evidence.get("kill_switch") or {}) if isinstance(blocked_evidence, dict) else {}
    blocked_heartbeat = (blocked_evidence.get("heartbeat") or {}) if isinstance(blocked_evidence, dict) else {}
    blocked_incidents = (blocked_evidence.get("incidents") or {}) if isinstance(blocked_evidence, dict) else {}
    blocked_propagation = (blocked_evidence.get("propagation") or {}) if isinstance(blocked_evidence, dict) else {}

    checks = {
        "clear_wrapper_returncode_zero": clear["wrapper_returncode"] == 0,
        "clear_report_returncode_zero": clear["report_returncode"] == 0,
        "clear_report_ok": clear_report.get("ok") is True,
        "clear_runtime_control_clear": clear_report.get("runtime_control_clear") is True,
        "clear_non_authorizing": clear_report.get("autotrade_resume_authorized") is False and clear_report.get("would_send_to_broker") is False,
        "blocked_wrapper_returncode_zero": blocked["wrapper_returncode"] == 0,
        "blocked_report_returncode_zero": blocked["report_returncode"] == 0,
        "blocked_report_ok": blocked_report.get("ok") is True,
        "blocked_runtime_control_not_clear": blocked_report.get("runtime_control_clear") is False,
        "blocked_heartbeat_visible": "heartbeat_stale" in (blocked_report.get("runtime_control_blocked_by") or []) and blocked_heartbeat.get("fresh") is False,
        "blocked_kill_switch_visible": blocked_kill.get("active") is True and blocked_kill.get("action") == "HALT_AND_CANCEL",
        "blocked_incident_visible": int(blocked_incidents.get("open_count") or 0) >= 1,
        "blocked_final_review_propagation": "runtime_control_not_clear" in (blocked_propagation.get("final_review_blocked_by") or []),
        "blocked_handoff_action_visible": "clear_runtime_control_heartbeat_kill_switch_incident_blockers" in (blocked_propagation.get("handoff_next_actions") or []),
        "blocked_non_authorizing": blocked_report.get("autotrade_resume_authorized") is False and blocked_report.get("would_send_to_broker") is False,
    }
    failures.extend(f"check failed: {name}" for name, ok in checks.items() if not ok)

    protected_dirty_hits: list[str] = []
    status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    for line in status:
        rel = line[3:] if len(line) > 3 else line
        if any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            protected_dirty_hits.append(line)
    failures.extend(f"protected lower-layer dirty during milestone DR: {hit}" for hit in protected_dirty_hits)

    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_dr_runtime_control_operational_evidence_report_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "operational_evidence_report_present": REPORT.exists(),
            "clear_case_evidence_collected": checks.get("clear_report_ok", False),
            "blocked_runtime_control_evidence_visible": checks.get("blocked_heartbeat_visible", False) and checks.get("blocked_kill_switch_visible", False) and checks.get("blocked_incident_visible", False),
            "blocked_evidence_propagates_to_final_and_handoff": checks.get("blocked_final_review_propagation", False) and checks.get("blocked_handoff_action_visible", False),
            "read_only_no_broker_non_authorizing": checks.get("clear_non_authorizing", False) and checks.get("blocked_non_authorizing", False),
            "protected_lower_layers_untouched": not protected_dirty_hits,
        },
        "checks": checks,
        "cases": {
            "clear": {
                "wrapper_returncode": clear["wrapper_returncode"],
                "report_returncode": clear["report_returncode"],
                "report_ok": clear_report.get("ok"),
                "runtime_control_clear": clear_report.get("runtime_control_clear"),
            },
            "blocked": {
                "wrapper_returncode": blocked["wrapper_returncode"],
                "report_returncode": blocked["report_returncode"],
                "report_ok": blocked_report.get("ok"),
                "runtime_control_clear": blocked_report.get("runtime_control_clear"),
                "runtime_control_blocked_by": blocked_report.get("runtime_control_blocked_by"),
                "kill_switch": blocked_kill,
                "heartbeat": blocked_heartbeat,
                "incidents": blocked_incidents,
                "handoff_next_actions": blocked_propagation.get("handoff_next_actions"),
            },
        },
        "protected_dirty_hits": protected_dirty_hits,
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
