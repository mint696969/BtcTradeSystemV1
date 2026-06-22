# path: ./tools/test_phase4a_prediction_system_ps_q16r_close_guard.py
# desc: Close guard for PS-Q16R stop checkpoint before approval.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval import CHECKER_VERSION, build_report, main
from check_phase4a_prediction_system_ps_q16q_final_non_executing_operator_handoff_checkpoint import build_report as build_q16q_report

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16R_STOP_CHECKPOINT_BEFORE_APPROVAL_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval.py",
    "tools/test_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16R_STOP_CHECKPOINT_BEFORE_APPROVAL_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16r_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in (
        "stop_checkpoint_only",
        "human_review_gate_only",
        "approval_slice_required_before_any_execution",
        "no_approval_granted",
        "no_hot_data_read",
        "no_runtime_write",
        "no_status_write",
        "no_ledger_append",
        "no_lock_io",
        "no_refresh_invocation",
        "no_scheduler_or_ui_trigger",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "ready_for_execution_enablement",
        "approval_or_authorization_allowed",
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
        "CHECKER = \"ps_q16r_stop_checkpoint_before_approval\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval.v1\"",
        "Q16Q_REPORT_BUILDER",
        "build_ps_q16q_report",
        "stop_checkpoint_only",
        "human_review_gate_only",
        "approval_slice_required_before_any_execution",
        "no_approval_granted",
        "no_hot_data_read",
        "no_runtime_write",
        "no_status_write",
        "no_ledger_append",
        "no_lock_io",
        "no_refresh_invocation",
        "no_scheduler_or_ui_trigger",
        "ready_for_stop_checkpoint_review",
        "request_approval",
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
    if "test_ps_q16r_ready_stop_checkpoint_without_approval_or_execution" not in unit_text:
        failures.append("unit test must cover ready stop checkpoint")
    if "test_ps_q16r_blocks_q16q_safety_boundary_regression" not in unit_text:
        failures.append("unit test must cover Q16Q false-boundary regression")
    for marker in (
        "stop_checkpoint_only=true",
        "human_review_gate_only=true",
        "approval_slice_required_before_any_execution=true",
        "no_approval_granted=true",
        "no_hot_data_read=true",
        "no_runtime_write=true",
        "no_status_write=true",
        "no_ledger_append=true",
        "no_lock_io=true",
        "no_refresh_invocation=true",
        "no_scheduler_or_ui_trigger=true",
        "ready_for_stop_checkpoint_review=true",
        "consumes_q16q_report_only=true",
        "requires_q16q_report_ok=true",
        "requires_q16q_report_false_boundaries=true",
        "requires_human_stop_checkpoint_record=true",
        "prints_stop_checkpoint_packet_only=true",
        "separate_explicit_approval_slice_required=true",
        "approval_or_authorization=false",
        "cli_enabled=false",
        "implementation_enabled=false",
        "execution_enabled=false",
        "manual_refresh_invoked=false",
        "latest_prediction_refresh=false",
        "status_artifact_write=false",
        "runtime_artifact_write=false",
        "lock_file_created=false",
        "lock_file_deleted=false",
        "ledger_append=false",
        "Stop here for human review",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "approval_or_authorization=true",
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
        "ledger_append_allowed=true",
        "freshness_bypass_added=true",
        "force_ready_added=true",
    ):
        if forbidden in doc_text:
            failures.append(f"forbidden doc marker present: {forbidden}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval.v1":
        failures.append("checker version mismatch")

    ready = build_report()
    if ready.get("ok") is not True:
        failures.append(f"ready report should be ok: {ready}")
    if ready.get("q16q_report_ok") is not True:
        failures.append("q16q_report_ok must be true")
    if ready.get("ready_for_stop_checkpoint_review") is not True:
        failures.append("ready_for_stop_checkpoint_review must be true")
    _assert_false_boundaries(ready, failures)

    for kwargs, expected in (
        ({"human_stop_checkpoint_record_present": False}, "human_stop_checkpoint_record_required_for_ps_q16r"),
        ({"supplied_q16q_report": build_q16q_report(request_execute_cli=True)}, "q16q_report_not_ok"),
        ({"request_approval": True}, "forbidden_request_in_ps_q16r:request_approval"),
        ({"request_enable_cli": True}, "forbidden_request_in_ps_q16r:request_enable_cli"),
        ({"request_execute_cli": True}, "forbidden_request_in_ps_q16r:request_execute_cli"),
        ({"request_status_artifact_write": True}, "forbidden_request_in_ps_q16r:request_status_artifact_write"),
        ({"request_lock_file_create": True}, "forbidden_request_in_ps_q16r:request_lock_file_create"),
        ({"request_ledger_append": True}, "forbidden_request_in_ps_q16r:request_ledger_append"),
    ):
        report = build_report(**kwargs)
        if report.get("ok") is not False:
            failures.append(f"negative report should fail: {kwargs}")
        if expected not in report.get("blocked_reasons", []):
            failures.append(f"missing blocker {expected}: {kwargs}")
        _assert_false_boundaries(report, failures)
    unsafe_q16q = build_q16q_report()
    unsafe_q16q["approval_or_authorization_allowed"] = True
    unsafe = build_report(supplied_q16q_report=unsafe_q16q)
    if "q16q_report_approval_or_authorization_allowed_must_remain_false" not in unsafe.get("blocked_reasons", []):
        failures.append("unsafe Q16Q approval boundary must block")
    _assert_false_boundaries(unsafe, failures)
    if main() != 0:
        failures.append("main() should return 0")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16r_close_guard",
        "phase": "phase3_prediction_system_stop_checkpoint_before_approval_closed",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q16r_closed": not failures,
            "stop_checkpoint_only": True,
            "human_review_gate_only": True,
            "approval_slice_required_before_any_execution": True,
            "no_approval_granted": True,
            "no_hot_data_read": True,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_ledger_append": True,
            "no_lock_io": True,
            "no_refresh_invocation": True,
            "no_scheduler_or_ui_trigger": True,
            "ready_for_execution_enablement": False,
            "approval_or_authorization_allowed": False,
            "cli_enabled": False,
            "implementation_enabled": False,
            "execution_enabled": False,
            "manual_refresh_invoked": False,
            "latest_prediction_refresh_performed": False,
            "status_artifact_write_performed": False,
            "runtime_artifact_write_performed": False,
            "lock_file_created": False,
            "lock_file_deleted": False,
            "ledger_append_allowed": False,
            "scheduler_enabled": False,
            "os_scheduler_registration_performed": False,
            "scheduled_loop_enabled": False,
            "autotrade_trigger_candidate_deferred": True,
            "next_slice": "STOP: human review required before any separate approval/execution/write/lock slice",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16r_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
