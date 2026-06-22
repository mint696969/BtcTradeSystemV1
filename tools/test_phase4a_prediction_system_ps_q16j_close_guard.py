# path: ./tools/test_phase4a_prediction_system_ps_q16j_close_guard.py
# desc: Close guard for PS-Q16J read-only operator-shell once-run dry-run CLI.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

import check_phase4a_prediction_system_ps_q16j_operator_shell_once_run_dry_run_cli as dryrun  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q16j_operator_shell_once_run_dry_run_cli.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16J_OPERATOR_SHELL_ONCE_RUN_DRY_RUN_CLI_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16j_operator_shell_once_run_dry_run_cli_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q16j_operator_shell_once_run_dry_run_cli.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16J_OPERATOR_SHELL_ONCE_RUN_DRY_RUN_CLI_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16j_operator_shell_once_run_dry_run_cli_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16j_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _preflight(*, hot_root: str, require_clean_tree: bool, human_approval_record_present: bool, allow_guard_test_root: bool) -> dict:
    _ = (hot_root, require_clean_tree, human_approval_record_present, allow_guard_test_root)
    return {
        "ok": True,
        "preflight_passed": True,
        "git_status_short": [],
        "ready_for_scheduler_enablement": False,
        "scheduler_registration_performed": False,
        "scheduled_loop_enabled": False,
        "scheduler_enablement_command_generated": False,
        "latest_prediction": {
            "prediction_run_id": "prediction_system.ps_q16j.close:BTC_JPY:bitFlyer:2026-06-22T12:00:00Z",
            "generated_at": "2026-06-22T12:00:00Z",
            "age_sec": 60,
        },
        "producer_status": {
            "status_artifact_relative_path": "prediction/status/non_ui_scheduled_producer_status.json",
            "panel_state": "producer_status_panel_loaded",
            "payload_decode_succeeded": True,
            "producer_enabled": False,
            "scheduler_enabled": False,
            "last_success_at": "2026-06-22T12:00:00Z",
            "last_success_generated_at": "2026-06-22T12:00:00Z",
            "last_prediction_run_id": "prediction_system.ps_q16j.close:BTC_JPY:bitFlyer:2026-06-22T12:00:00Z",
            "last_blocker_count": 0,
        },
        "blocked_reasons": [],
        "warning_reasons": ["latest_prediction_source_has_warnings:6"],
    }


def _preflight_blocked(*, hot_root: str, require_clean_tree: bool, human_approval_record_present: bool, allow_guard_test_root: bool) -> dict:
    payload = _preflight(
        hot_root=hot_root,
        require_clean_tree=require_clean_tree,
        human_approval_record_present=human_approval_record_present,
        allow_guard_test_root=allow_guard_test_root,
    )
    payload["ok"] = False
    payload["preflight_passed"] = False
    payload["blocked_reasons"] = ["working_tree_not_clean"]
    return payload


def _lock_absent(*, hot_root: str) -> dict:
    return {
        "lock_relative_path": dryrun.LOCK_RELATIVE_PATH,
        "lock_path": str(Path(hot_root) / dryrun.LOCK_RELATIVE_PATH),
        "lock_present": False,
        "lock_reason": "close_guard_absent",
        "lock_read_attempted": False,
        "lock_write_attempted": False,
        "lock_create_attempted": False,
        "lock_delete_attempted": False,
    }


def _lock_present(*, hot_root: str) -> dict:
    return {**_lock_absent(hot_root=hot_root), "lock_present": True, "lock_reason": "close_guard_present"}


def _assert_safe(payload: dict, failures: list[str]) -> None:
    decision = payload.get("decision", {})
    for key in (
        "wrapper_enabled",
        "scheduler_enabled",
        "os_scheduler_registration_performed",
        "scheduled_loop_enabled",
        "enablement_command_generated",
        "manual_refresh_invoked_by_this_checker",
        "latest_prediction_refresh_performed_by_this_checker",
        "status_artifact_write_performed_by_this_checker",
        "lock_file_created_by_this_checker",
        "warroom_ui_trigger_enabled",
        "ui_triggered_runner_execution",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        if decision.get(key) is not False:
            failures.append(f"decision {key} must remain false")
    for key, value in payload.get("safe_flags", {}).items():
        if value is not True:
            failures.append(f"safe flag failed: {key}")
    if payload.get("lock_observation", {}).get("lock_create_attempted") is not False:
        failures.append("lock_create_attempted must be false")
    if payload.get("lock_observation", {}).get("lock_write_attempted") is not False:
        failures.append("lock_write_attempted must be false")
    if payload.get("status_observation", {}).get("status_write_attempted") is not False:
        failures.append("status_write_attempted must be false")


def main() -> int:
    failures: list[str] = []
    for path in (TOOL, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "CHECKER = \"ps_q16j_operator_shell_once_run_dry_run_cli\"",
        "LOCK_RELATIVE_PATH = \"prediction/status/non_ui_scheduled_producer.lock\"",
        "build_ps_q16f_preflight_report",
        "build_prediction_warroom_disabled_once_run_checker",
        "lock_path.exists()",
        "lock_path.stat()",
        "lock_read_attempted\": False",
        "lock_write_attempted\": False",
        "lock_create_attempted\": False",
        "status_write_attempted\": False",
        "dry_run_only\": True",
        "operator_note",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    for forbidden in (
        "write_text(",
        "write_bytes(",
        "replace(",
        "unlink(",
        "mkdir(",
        "build_prediction_warroom_bounded_manual_refresh_runner(",
        "build_prediction_warroom_latest_payload_actual_export_runner(",
        "send_order(",
        "create_order(",
        "append_decision(",
        "append_command(",
        "request_execute_manual_refresh=True",
        "request_status_artifact_write=True",
        "request_lock_file_create=True",
        "request_scheduler_enable=True",
    ):
        if forbidden in tool_text:
            failures.append(f"forbidden tool token: {forbidden}")
    for marker in (
        "dry_run_only=true",
        "read_only=true",
        "non_executing=true",
        "prints_decision_only=true",
        "lock_read_attempted=false",
        "lock_write_attempted=false",
        "lock_create_attempted=false",
        "status_write_attempted=false",
        "manual_refresh_invoked=false",
        "latest_prediction_refresh=false",
        "status_artifact_write=false",
        "lock_file_created=false",
        "PS-Q16K: separate human-approved execution design checkpoint",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")

    ready = dryrun.build_report(
        hot_root="D:\\btc_ts_hot",
        preflight_builder=_preflight,
        lock_observation_builder=_lock_absent,
        require_clean_tree=True,
    )
    if ready.get("ok") is not True:
        failures.append(f"ready dry-run should pass: {ready}")
    if ready.get("decision", {}).get("simulated_decision") != "ready_no_lock_no_execution":
        failures.append("ready no-lock decision mismatch")
    _assert_safe(ready, failures)

    locked = dryrun.build_report(
        hot_root="D:\\btc_ts_hot",
        preflight_builder=_preflight,
        lock_observation_builder=_lock_present,
        require_clean_tree=True,
    )
    if locked.get("ok") is not True:
        failures.append(f"locked dry-run should still pass as skip decision: {locked}")
    if locked.get("decision", {}).get("simulated_decision") != "skip_existing_lock":
        failures.append("lock-present decision mismatch")
    if locked.get("decision", {}).get("would_skip_due_to_existing_lock") is not True:
        failures.append("lock-present should set would_skip_due_to_existing_lock")
    _assert_safe(locked, failures)

    blocked = dryrun.build_report(
        hot_root="D:\\btc_ts_hot",
        preflight_builder=_preflight_blocked,
        lock_observation_builder=_lock_absent,
        require_clean_tree=True,
    )
    if blocked.get("ok") is not False:
        failures.append("blocked preflight should make dry-run not ok")
    if "ps_q16f_preflight_not_passed" not in blocked.get("blocked_reasons", []):
        failures.append("blocked preflight should surface ps_q16f_preflight_not_passed")
    _assert_safe(blocked, failures)

    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16j_close_guard",
        "phase": "phase3_prediction_system_operator_shell_once_run_dry_run_cli_closed",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q16j_closed": not failures,
            "dry_run_only": True,
            "read_only_observations_only": True,
            "prints_decision_only": True,
            "manual_refresh_invoked": False,
            "latest_prediction_refresh_performed": False,
            "status_artifact_write_performed": False,
            "lock_file_created": False,
            "scheduler_enabled": False,
            "os_scheduler_registration_performed": False,
            "scheduled_loop_enabled": False,
            "autotrade_trigger_candidate_deferred": True,
            "next_slice": "PS-Q16K separate human-approved execution design checkpoint; still no automatic scheduler and no execution/write/lock behavior without explicit later approval",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16j_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
