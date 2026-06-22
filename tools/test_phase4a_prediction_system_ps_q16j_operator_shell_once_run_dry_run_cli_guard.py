# path: ./tools/test_phase4a_prediction_system_ps_q16j_operator_shell_once_run_dry_run_cli_guard.py
# desc: Focused guard for PS-Q16J read-only operator-shell once-run dry-run CLI.

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
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q16j_operator_shell_once_run_dry_run_cli.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16J_OPERATOR_SHELL_ONCE_RUN_DRY_RUN_CLI_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16j_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16j_operator_shell_once_run_dry_run_cli_guard.py",
}
FORBIDDEN_TOOL_TOKENS = (
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
)
REQUIRED_DOC_MARKERS = (
    "PS-Q16J adds an operator-shell dry-run CLI",
    "dry_run_only=true",
    "read_only=true",
    "non_executing=true",
    "prints_decision_only=true",
    "lock_read_attempted=false",
    "lock_write_attempted=false",
    "lock_create_attempted=false",
    "status_write_attempted=false",
    "manual_refresh_invoked=false",
    "PS-Q16K: separate human-approved execution design checkpoint",
)
FORBIDDEN_DOC_MARKERS = (
    "scheduler_registration=true",
    "os_scheduler_registration=true",
    "scheduled_loop=true",
    "latest_prediction_refresh=true",
    "manual_refresh_invoked=true",
    "status_artifact_write=true",
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
            "prediction_run_id": "prediction_system.ps_q16j.guard:BTC_JPY:bitFlyer:2026-06-22T12:00:00Z",
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
            "last_prediction_run_id": "prediction_system.ps_q16j.guard:BTC_JPY:bitFlyer:2026-06-22T12:00:00Z",
            "last_blocker_count": 0,
        },
        "blocked_reasons": [],
        "warning_reasons": ["latest_prediction_source_has_warnings:6"],
    }


def _lock_absent(*, hot_root: str) -> dict:
    return {
        "lock_relative_path": dryrun.LOCK_RELATIVE_PATH,
        "lock_path": str(Path(hot_root) / dryrun.LOCK_RELATIVE_PATH),
        "lock_present": False,
        "lock_reason": "guard_absent",
        "lock_read_attempted": False,
        "lock_write_attempted": False,
        "lock_create_attempted": False,
        "lock_delete_attempted": False,
    }


def _lock_present(*, hot_root: str) -> dict:
    return {**_lock_absent(hot_root=hot_root), "lock_present": True, "lock_reason": "guard_present"}


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
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        if decision.get(key) is not False:
            failures.append(f"decision {key} must stay false")
    for key, value in payload.get("safe_flags", {}).items():
        if value is not True:
            failures.append(f"safe flag failed: {key}")


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
    for token in FORBIDDEN_TOOL_TOKENS:
        if token in tool_text:
            failures.append(f"forbidden tool token: {token}")
    ready = dryrun.build_report(
        hot_root="D:\\btc_ts_hot",
        preflight_builder=_preflight,
        lock_observation_builder=_lock_absent,
        require_clean_tree=True,
    )
    if ready.get("ok") is not True:
        failures.append(f"ready dry-run should be ok: {ready}")
    if ready.get("decision", {}).get("simulated_decision") != "ready_no_lock_no_execution":
        failures.append("ready dry-run decision mismatch")
    if ready.get("lock_observation", {}).get("lock_create_attempted") is not False:
        failures.append("lock create attempted must be false")
    if ready.get("status_observation", {}).get("status_write_attempted") is not False:
        failures.append("status write attempted must be false")
    _assert_safe(ready, failures)
    locked = dryrun.build_report(
        hot_root="D:\\btc_ts_hot",
        preflight_builder=_preflight,
        lock_observation_builder=_lock_present,
        require_clean_tree=True,
    )
    if locked.get("decision", {}).get("simulated_decision") != "skip_existing_lock":
        failures.append("lock-present dry-run should simulate skip")
    _assert_safe(locked, failures)
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
        "guard": "ps_q16j_operator_shell_once_run_dry_run_cli",
        "phase": "phase3_prediction_system_operator_shell_once_run_dry_run_cli",
        "contract": {
            "dry_run_only": True,
            "read_only": True,
            "prints_decision_only": True,
            "manual_refresh_invoked": False,
            "status_artifact_write_performed": False,
            "lock_file_created": False,
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


def test_ps_q16j_operator_shell_once_run_dry_run_cli_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
