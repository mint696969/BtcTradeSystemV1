# path: ./tools/test_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard_guard.py
# desc: Focused guard for PS-Q16P disabled CLI report integration guard.

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
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16P_DISABLED_CLI_REPORT_INTEGRATION_GUARD_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16p_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard_guard.py",
}
FORBIDDEN_TOOL_TOKENS = (
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
)
REQUIRED_DOC_MARKERS = (
    "PS-Q16P consumes the PS-Q16O dry-run report and returns an operator handoff summary only",
    "dry_run_report_integration_only=true",
    "operator_handoff_summary_only=true",
    "no_hot_data_read=true",
    "no_runtime_write=true",
    "no_lock_io=true",
    "no_refresh_invocation=true",
    "requires_q16o_report_ok=true",
    "requires_q16o_report_false_boundaries=true",
    "ready_for_future_operator_handoff_summary_slice=true",
    "cli_enabled=false",
    "execution_enabled=false",
    "lock_file_created=false",
    "PS-Q16Q: final non-executing operator handoff checkpoint",
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
    for token in FORBIDDEN_TOOL_TOKENS:
        if token in tool_text:
            failures.append(f"forbidden tool token: {token}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard.v1":
        failures.append("checker version mismatch")
    ready = build_report()
    if ready.get("ok") is not True:
        failures.append(f"ready report should be ok: {ready}")
    if ready.get("q16o_report_ok") is not True:
        failures.append("q16o_report_ok should be true")
    _assert_false_boundaries(ready, failures)
    missing = build_report(human_handoff_record_present=False)
    if missing.get("ok") is not False or "human_handoff_record_required_for_ps_q16p" not in missing.get("blocked_reasons", []):
        failures.append("missing human handoff record must block")
    failed_q16o = build_report(supplied_q16o_report=build_q16o_report(request_execute_cli=True))
    if failed_q16o.get("ok") is not False or "q16o_report_not_ok" not in failed_q16o.get("blocked_reasons", []):
        failures.append("failed q16o report must block")
    unsafe_q16o = build_q16o_report()
    unsafe_q16o["decision"]["status_artifact_write_performed_by_this_cli_skeleton"] = True
    unsafe = build_report(supplied_q16o_report=unsafe_q16o)
    if "q16o_decision_status_artifact_write_performed_by_this_cli_skeleton_must_remain_false" not in unsafe.get("blocked_reasons", []):
        failures.append("unsafe q16o false boundary must block")
    forbidden = build_report(request_execute_cli=True, request_lock_file_create=True, request_status_artifact_write=True)
    for expected in (
        "forbidden_request_in_ps_q16p:request_execute_cli",
        "forbidden_request_in_ps_q16p:request_lock_file_create",
        "forbidden_request_in_ps_q16p:request_status_artifact_write",
    ):
        if expected not in forbidden.get("blocked_reasons", []):
            failures.append(f"missing forbidden blocker: {expected}")
    _assert_false_boundaries(forbidden, failures)
    if main() != 0:
        failures.append("main() should return 0")
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
        "guard": "ps_q16p_disabled_cli_report_integration_guard",
        "phase": "phase3_prediction_system_disabled_cli_report_integration_guard",
        "contract": {
            "dry_run_report_integration_only": True,
            "operator_handoff_summary_only": True,
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


def test_ps_q16p_disabled_cli_report_integration_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
