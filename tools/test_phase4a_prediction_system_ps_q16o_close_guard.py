# path: ./tools/test_phase4a_prediction_system_ps_q16o_close_guard.py
# desc: Close guard for PS-Q16O disabled operator-shell CLI dry-run report tool.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool import (
    CHECKER_VERSION,
    build_report,
    main,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16O_DISABLED_OPERATOR_SHELL_CLI_DRY_RUN_REPORT_TOOL_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool.py",
    "tools/test_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16O_DISABLED_OPERATOR_SHELL_CLI_DRY_RUN_REPORT_TOOL_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16o_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_report_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in (
        "dry_run_report_only",
        "no_hot_data_read",
        "no_runtime_write",
        "no_lock_io",
        "no_refresh_invocation",
        "no_scheduler_or_ui_trigger",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    decision = report.get("decision", {})
    for key in (
        "ready_for_execution_enablement",
        "cli_enabled",
        "implementation_enabled",
        "execution_enabled",
        "manual_refresh_invoked_by_this_cli_skeleton",
        "latest_prediction_refresh_performed_by_this_cli_skeleton",
        "status_artifact_write_performed_by_this_cli_skeleton",
        "runtime_artifact_write_performed_by_this_cli_skeleton",
        "lock_file_created_by_this_cli_skeleton",
        "lock_file_deleted_by_this_cli_skeleton",
        "wrapper_enabled",
        "scheduler_enabled",
        "os_scheduler_registration_performed",
        "scheduled_loop_enabled",
        "enablement_command_generated",
        "warroom_ui_trigger_enabled",
        "ui_triggered_runner_execution",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "would_send_to_broker",
        "would_write_collector_state",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        if decision.get(key) is not False:
            failures.append(f"{key} must stay false")
    for key in ("cli_skeleton_only", "dry_run_wrapper_only", "operator_shell_only", "read_only", "non_executing"):
        if decision.get(key) is not True:
            failures.append(f"{key} must be true")


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
        "CHECKER = \"ps_q16o_disabled_operator_shell_cli_dry_run_report_tool\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool.v1\"",
        "dry_run_report_only",
        "no_hot_data_read",
        "no_runtime_write",
        "no_lock_io",
        "no_refresh_invocation",
        "no_scheduler_or_ui_trigger",
        "_synthetic_ps_q16m_skeleton",
        "build_prediction_warroom_disabled_operator_shell_once_run_cli_skeleton",
        "request_enable_cli",
        "request_execute_cli",
        "request_status_artifact_write",
        "request_lock_file_create",
        "request_scheduler_enable",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    for forbidden in (
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
    if "test_ps_q16o_main_prints_json_and_returns_zero_only_when_ok" not in unit_text:
        failures.append("unit test must cover main return code and JSON output")
    for marker in (
        "dry_run_report_only=true",
        "no_hot_data_read=true",
        "no_runtime_write=true",
        "no_lock_io=true",
        "no_refresh_invocation=true",
        "no_scheduler_or_ui_trigger=true",
        "prints_q16n_skeleton_decision_only=true",
        "uses_synthetic_ps_q16m_skeleton_packet=true",
        "supports_negative_simulation_flags_only=true",
        "returns_zero_only_when_q16n_decision_ok=true",
        "cli_enabled=false",
        "implementation_enabled=false",
        "execution_enabled=false",
        "manual_refresh_invoked=false",
        "latest_prediction_refresh=false",
        "status_artifact_write=false",
        "runtime_artifact_write=false",
        "lock_file_created=false",
        "lock_file_deleted=false",
        "PS-Q16P: disabled CLI report integration guard",
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
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool.v1":
        failures.append("checker version mismatch")

    ready = build_report()
    if ready.get("ok") is not True:
        failures.append(f"ready report should be ok: {ready}")
    if ready.get("decision", {}).get("cli_skeleton_state") != "disabled_operator_shell_once_run_cli_skeleton_ready_for_future_dry_run_wrapper":
        failures.append("Q16N ready state mismatch")
    _assert_report_false_boundaries(ready, failures)

    for kwargs, expected in (
        ({"human_cli_skeleton_record_present": False}, "human_cli_skeleton_record_required_for_ps_q16n"),
        ({"simulate_unready_ps_q16m_skeleton": True}, "ps_q16m_implementation_skeleton_not_ready_for_cli_skeleton"),
        ({"simulate_unsafe_ps_q16m_write": True}, "ps_q16m_status_artifact_write_performed_by_this_skeleton_must_remain_false"),
        ({"request_enable_cli": True}, "forbidden_request_in_ps_q16n:request_enable_cli"),
        ({"request_execute_cli": True}, "forbidden_request_in_ps_q16n:request_execute_cli"),
        ({"request_status_artifact_write": True}, "forbidden_request_in_ps_q16n:request_status_artifact_write"),
        ({"request_lock_file_create": True}, "forbidden_request_in_ps_q16n:request_lock_file_create"),
    ):
        report = build_report(**kwargs)
        if report.get("ok") is not False:
            failures.append(f"negative report should fail: {kwargs}")
        if expected not in report.get("blocked_reasons", []):
            failures.append(f"missing blocker {expected}: {kwargs}")
        _assert_report_false_boundaries(report, failures)
    if main([]) != 0:
        failures.append("main([]) should return 0")
    if main(["--request-execute-cli"]) != 1:
        failures.append("main forbidden request should return 1")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16o_close_guard",
        "phase": "phase3_prediction_system_disabled_operator_shell_cli_dry_run_report_tool_closed",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q16o_closed": not failures,
            "dry_run_report_only": True,
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
            "next_slice": "PS-Q16P disabled CLI report integration guard or operator handoff summary; still no execution/write/lock behavior unless separately approved",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16o_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
