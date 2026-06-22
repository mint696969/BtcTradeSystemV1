# path: ./tools/test_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool_guard.py
# desc: Focused guard for PS-Q16O disabled operator-shell CLI dry-run report tool.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool import CHECKER_VERSION, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16O_DISABLED_OPERATOR_SHELL_CLI_DRY_RUN_REPORT_TOOL_2026-06-22.md"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool.py",
    "tools/test_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16O_DISABLED_OPERATOR_SHELL_CLI_DRY_RUN_REPORT_TOOL_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16o_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool_guard.py",
}
FORBIDDEN_TOOL_TOKENS = (
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
)
REQUIRED_DOC_MARKERS = (
    "PS-Q16O adds an operator-shell tool that prints the PS-Q16N skeleton decision only",
    "dry_run_report_only=true",
    "no_hot_data_read=true",
    "no_runtime_write=true",
    "no_lock_io=true",
    "no_refresh_invocation=true",
    "prints_q16n_skeleton_decision_only=true",
    "cli_enabled=false",
    "execution_enabled=false",
    "manual_refresh_invoked=false",
    "lock_file_created=false",
    "PS-Q16P: disabled CLI report integration guard",
)
FORBIDDEN_DOC_MARKERS = (
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
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_report_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in ("dry_run_report_only", "no_hot_data_read", "no_runtime_write", "no_lock_io", "no_refresh_invocation", "no_scheduler_or_ui_trigger"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    decision = report.get("decision", {})
    for key in (
        "cli_enabled",
        "implementation_enabled",
        "execution_enabled",
        "manual_refresh_invoked_by_this_cli_skeleton",
        "latest_prediction_refresh_performed_by_this_cli_skeleton",
        "status_artifact_write_performed_by_this_cli_skeleton",
        "runtime_artifact_write_performed_by_this_cli_skeleton",
        "lock_file_created_by_this_cli_skeleton",
        "lock_file_deleted_by_this_cli_skeleton",
        "scheduler_enabled",
        "os_scheduler_registration_performed",
        "scheduled_loop_enabled",
        "warroom_ui_trigger_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        if decision.get(key) is not False:
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
    for token in FORBIDDEN_TOOL_TOKENS:
        if token in tool_text:
            failures.append(f"forbidden tool token: {token}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool.v1":
        failures.append("checker version mismatch")
    ready = build_report()
    if ready.get("ok") is not True:
        failures.append(f"ready report should be ok: {ready}")
    if ready.get("decision", {}).get("cli_skeleton_state") != "disabled_operator_shell_once_run_cli_skeleton_ready_for_future_dry_run_wrapper":
        failures.append("Q16N decision state mismatch")
    _assert_report_false_boundaries(ready, failures)
    missing = build_report(human_cli_skeleton_record_present=False)
    if missing.get("ok") is not False or "human_cli_skeleton_record_required_for_ps_q16n" not in missing.get("blocked_reasons", []):
        failures.append("missing human record must block")
    forbidden = build_report(request_execute_cli=True, request_lock_file_create=True, request_status_artifact_write=True)
    if forbidden.get("ok") is not False:
        failures.append("forbidden request report must fail closed")
    for expected in (
        "forbidden_request_in_ps_q16n:request_execute_cli",
        "forbidden_request_in_ps_q16n:request_lock_file_create",
        "forbidden_request_in_ps_q16n:request_status_artifact_write",
    ):
        if expected not in forbidden.get("blocked_reasons", []):
            failures.append(f"missing blocker: {expected}")
    _assert_report_false_boundaries(forbidden, failures)
    if main([]) != 0:
        failures.append("main([]) should return 0")
    if main(["--request-execute-cli"]) != 1:
        failures.append("main forbidden request should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for marker in FORBIDDEN_DOC_MARKERS:
        if marker in doc_text:
            failures.append(f"forbidden doc marker present: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16o_disabled_operator_shell_cli_dry_run_report_tool",
        "phase": "phase3_prediction_system_disabled_operator_shell_cli_dry_run_report_tool",
        "contract": {
            "dry_run_report_only": True,
            "no_hot_data_read": True,
            "no_runtime_write": True,
            "no_lock_io": True,
            "no_refresh_invocation": True,
            "cli_enabled": False,
            "execution_enabled": False,
            "scheduler_enabled": False,
            "autotrade_trigger_candidate_deferred": True,
            "expected_dirty_only": not unexpected,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
