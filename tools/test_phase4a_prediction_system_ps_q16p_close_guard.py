# path: ./tools/test_phase4a_prediction_system_ps_q16p_close_guard.py
# desc: Close guard for PS-Q16P disabled CLI report integration guard.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard import CHECKER_VERSION, build_report, main
from check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool import build_report as build_q16o_report

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16P_DISABLED_CLI_REPORT_INTEGRATION_GUARD_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16P_DISABLED_CLI_REPORT_INTEGRATION_GUARD_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16p_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in (
        "dry_run_report_integration_only",
        "operator_handoff_summary_only",
        "no_hot_data_read",
        "no_runtime_write",
        "no_lock_io",
        "no_refresh_invocation",
        "no_scheduler_or_ui_trigger",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "ready_for_execution_enablement",
        "cli_enabled",
        "implementation_enabled",
        "execution_enabled",
        "manual_refresh_invoked",
        "latest_prediction_refresh_performed",
        "status_artifact_write_performed",
        "runtime_artifact_write_performed",
        "lock_file_created",
        "lock_file_deleted",
        "scheduler_enabled",
        "os_scheduler_registration_performed",
        "scheduled_loop_enabled",
        "enablement_command_generated",
        "warroom_ui_trigger_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")


def main_guard() -> int:
    failures: list[str] = []
    for path in (TOOL, UNIT, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    unit_text = _read(UNIT) if UNIT.exists() else ""
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "CHECKER = \"ps_q16p_disabled_cli_report_integration_guard\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard.v1\"",
        "Q16O_REPORT_BUILDER",
        "build_ps_q16o_report",
        "dry_run_report_integration_only",
        "operator_handoff_summary_only",
        "no_hot_data_read",
        "no_runtime_write",
        "no_lock_io",
        "no_refresh_invocation",
        "no_scheduler_or_ui_trigger",
        "ready_for_future_operator_handoff_summary_slice",
        "request_enable_cli",
        "request_execute_cli",
        "request_status_artifact_write",
        "request_lock_file_create",
        "request_scheduler_enable",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    for forbidden in (
        "argparse",
        "write_text(",
        "write_bytes(",
        "replace(",
        "open(",
        "mkdir(",
        "unlink(",
        "Path(",
        "exists(",
        "stat(",
        "build_prediction_warroom_bounded_manual_refresh_runner(",
        "build_prediction_warroom_latest_payload_actual_export_runner(",
        "send_order(",
        "create_order(",
        "append_decision(",
        "append_command(",
    ):
        if forbidden in tool_text:
            failures.append(f"forbidden tool token: {forbidden}")
    if "test_ps_q16p_ready_integrates_q16o_report_without_execution" not in unit_text:
        failures.append("unit test must cover ready Q16O integration")
    if "test_ps_q16p_blocks_q16o_safety_boundary_regression" not in unit_text:
        failures.append("unit test must cover Q16O false-boundary regression")
    for marker in (
        "dry_run_report_integration_only=true",
        "operator_handoff_summary_only=true",
        "no_hot_data_read=true",
        "no_runtime_write=true",
        "no_lock_io=true",
        "no_refresh_invocation=true",
        "no_scheduler_or_ui_trigger=true",
        "ready_for_future_operator_handoff_summary_slice=true",
        "consumes_q16o_report_only=true",
        "requires_q16o_report_ok=true",
        "requires_q16o_report_false_boundaries=true",
        "requires_human_handoff_record=true",
        "prints_operator_handoff_summary_only=true",
        "cli_enabled=false",
        "implementation_enabled=false",
        "execution_enabled=false",
        "manual_refresh_invoked=false",
        "latest_prediction_refresh=false",
        "status_artifact_write=false",
        "runtime_artifact_write=false",
        "lock_file_created=false",
        "lock_file_deleted=false",
        "PS-Q16Q: final non-executing operator handoff checkpoint",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "cli_enabled=true",
        "implementation_enabled=true",
        "execution_enabled=true",
        "scheduler_registration=true",
        "os_scheduler_registration=true",
        "scheduled_loop=true",
        "latest_prediction_refresh=true",
        "manual_refresh_invoked=true",
        "status_artifact_write=true",
        "runtime_artifact_write=true",
        "lock_file_created=true",
        "WarRoom UI trigger=true",
        "parameter_apply=true",
        "parameter_staging_write=true",
        "approval_or_ledger_or_autotrade_or_broker=true",
        "freshness_bypass_added=true",
        "force_ready_added=true",
    ):
        if forbidden in doc_text:
            failures.append(f"forbidden doc marker present: {forbidden}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard.v1":
        failures.append("checker version mismatch")

    ready = build_report()
    if ready.get("ok") is not True:
        failures.append(f"ready report should be ok: {ready}")
    if ready.get("q16o_report_ok") is not True:
        failures.append("q16o_report_ok must be true")
    if ready.get("q16o_decision_state") != "disabled_operator_shell_once_run_cli_skeleton_ready_for_future_dry_run_wrapper":
        failures.append("q16o decision state mismatch")
    if ready.get("ready_for_future_operator_handoff_summary_slice") is not True:
        failures.append("ready_for_future_operator_handoff_summary_slice must be true")
    _assert_false_boundaries(ready, failures)

    for kwargs, expected in (
        ({"human_handoff_record_present": False}, "human_handoff_record_required_for_ps_q16p"),
        ({"supplied_q16o_report": build_q16o_report(request_execute_cli=True)}, "q16o_report_not_ok"),
        ({"request_enable_cli": True}, "forbidden_request_in_ps_q16p:request_enable_cli"),
        ({"request_execute_cli": True}, "forbidden_request_in_ps_q16p:request_execute_cli"),
        ({"request_status_artifact_write": True}, "forbidden_request_in_ps_q16p:request_status_artifact_write"),
        ({"request_lock_file_create": True}, "forbidden_request_in_ps_q16p:request_lock_file_create"),
    ):
        report = build_report(**kwargs)
        if report.get("ok") is not False:
            failures.append(f"negative report should fail: {kwargs}")
        if expected not in report.get("blocked_reasons", []):
            failures.append(f"missing blocker {expected}: {kwargs}")
        _assert_false_boundaries(report, failures)
    unsafe_q16o = build_q16o_report()
    unsafe_q16o["decision"]["lock_file_created_by_this_cli_skeleton"] = True
    unsafe = build_report(supplied_q16o_report=unsafe_q16o)
    if "q16o_decision_lock_file_created_by_this_cli_skeleton_must_remain_false" not in unsafe.get("blocked_reasons", []):
        failures.append("unsafe Q16O lock boundary must block")
    _assert_false_boundaries(unsafe, failures)
    if main() != 0:
        failures.append("main() should return 0")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16p_close_guard",
        "phase": "phase3_prediction_system_disabled_cli_report_integration_guard_closed",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q16p_closed": not failures,
            "dry_run_report_integration_only": True,
            "operator_handoff_summary_only": True,
            "no_hot_data_read": True,
            "no_runtime_write": True,
            "no_lock_io": True,
            "no_refresh_invocation": True,
            "no_scheduler_or_ui_trigger": True,
            "cli_enabled": False,
            "implementation_enabled": False,
            "execution_enabled": False,
            "manual_refresh_invoked": False,
            "latest_prediction_refresh_performed": False,
            "status_artifact_write_performed": False,
            "runtime_artifact_write_performed": False,
            "lock_file_created": False,
            "lock_file_deleted": False,
            "scheduler_enabled": False,
            "os_scheduler_registration_performed": False,
            "scheduled_loop_enabled": False,
            "autotrade_trigger_candidate_deferred": True,
            "next_slice": "PS-Q16Q final non-executing operator handoff checkpoint or readiness ledger-free summary; still no execution/write/lock behavior unless separately approved",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16p_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
