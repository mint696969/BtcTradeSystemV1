# path: ./tools/test_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval_guard.py
# desc: Focused guard for PS-Q16R stop checkpoint before approval.

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
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval.py",
    "tools/test_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16R_STOP_CHECKPOINT_BEFORE_APPROVAL_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16r_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval_guard.py",
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
    "PS-Q16R consumes the PS-Q16Q final non-executing handoff report and returns a stop checkpoint before any approval slice",
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
    "ready_for_stop_checkpoint_review=true",
    "requires_q16q_report_ok=true",
    "requires_q16q_report_false_boundaries=true",
    "separate_explicit_approval_slice_required=true",
    "approval_or_authorization=false",
    "cli_enabled=false",
    "execution_enabled=false",
    "ledger_append=false",
    "Stop here for human review",
)
FORBIDDEN_DOC_MARKERS = (
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
)


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
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval.v1":
        failures.append("checker version mismatch")
    ready = build_report()
    if ready.get("ok") is not True:
        failures.append(f"ready report should be ok: {ready}")
    if ready.get("q16q_report_ok") is not True:
        failures.append("q16q_report_ok should be true")
    if ready.get("ready_for_stop_checkpoint_review") is not True:
        failures.append("ready_for_stop_checkpoint_review should be true")
    _assert_false_boundaries(ready, failures)
    missing = build_report(human_stop_checkpoint_record_present=False)
    if missing.get("ok") is not False or "human_stop_checkpoint_record_required_for_ps_q16r" not in missing.get("blocked_reasons", []):
        failures.append("missing human stop checkpoint record must block")
    failed_q16q = build_report(supplied_q16q_report=build_q16q_report(request_execute_cli=True))
    if failed_q16q.get("ok") is not False or "q16q_report_not_ok" not in failed_q16q.get("blocked_reasons", []):
        failures.append("failed q16q report must block")
    unsafe_q16q = build_q16q_report()
    unsafe_q16q["approval_or_authorization_allowed"] = True
    unsafe = build_report(supplied_q16q_report=unsafe_q16q)
    if "q16q_report_approval_or_authorization_allowed_must_remain_false" not in unsafe.get("blocked_reasons", []):
        failures.append("unsafe q16q approval boundary must block")
    forbidden = build_report(request_approval=True, request_execute_cli=True, request_lock_file_create=True, request_ledger_append=True)
    for expected in (
        "forbidden_request_in_ps_q16r:request_approval",
        "forbidden_request_in_ps_q16r:request_execute_cli",
        "forbidden_request_in_ps_q16r:request_lock_file_create",
        "forbidden_request_in_ps_q16r:request_ledger_append",
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
        "guard": "ps_q16r_stop_checkpoint_before_approval",
        "phase": "phase3_prediction_system_stop_checkpoint_before_approval",
        "contract": {
            "stop_checkpoint_only": True,
            "human_review_gate_only": True,
            "no_approval_granted": True,
            "no_hot_data_read": True,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_ledger_append": True,
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


def test_ps_q16r_stop_checkpoint_before_approval_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
