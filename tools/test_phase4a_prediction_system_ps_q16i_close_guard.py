# path: ./tools/test_phase4a_prediction_system_ps_q16i_close_guard.py
# desc: Close guard for PS-Q16I disabled once-run checker.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_disabled_once_run_checker import (  # noqa: E402
    DISABLED_ONCE_RUN_CHECKER_VERSION,
    build_prediction_warroom_disabled_once_run_checker,
)
from btcts.apps.operator_ui.components.prediction_warroom_disabled_scheduler_wrapper_skeleton import (  # noqa: E402
    DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_once_run_checker.py"
UNIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_disabled_once_run_checker.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16I_DISABLED_ONCE_RUN_CHECKER_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16i_disabled_once_run_checker_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_once_run_checker.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_disabled_once_run_checker.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16I_DISABLED_ONCE_RUN_CHECKER_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16i_disabled_once_run_checker_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16i_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _skeleton(*, ready: bool = True) -> dict:
    return {
        "skeleton_version": DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION,
        "ready_for_future_disabled_operator_shell_wrapper_implementation": ready,
        "wrapper_enabled": False,
        "scheduler_enabled": False,
        "os_scheduler_registration_performed": False,
        "scheduled_loop_enabled": False,
        "enablement_command_generated": False,
    }


def _preflight(*, ok: bool = True, age: int = 60) -> dict:
    return {"ok": ok, "preflight_passed": ok, "ready_for_scheduler_enablement": False, "latest_prediction": {"age_sec": age}}


def _assert_all_disabled(packet: dict, failures: list[str]) -> None:
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
        "would_send_to_broker",
        "would_write_collector_state",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        if packet.get(key) is not False:
            failures.append(f"{key} must remain false")
    for key in ("checker_only", "read_only", "non_executing"):
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")


def main() -> int:
    failures: list[str] = []
    for path in (MODULE, UNIT, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    module_text = _read(MODULE) if MODULE.exists() else ""
    unit_text = _read(UNIT) if UNIT.exists() else ""
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "DISABLED_ONCE_RUN_CHECKER_VERSION",
        "consume_supplied_lock_observation_without_reading_or_creating_lock",
        "consume_supplied_status_observation_without_writing_status",
        "simulate_skip_when_lock_present",
        "declare_no_manual_refresh_execution_in_ps_q16i",
        "declare_no_status_write_in_ps_q16i",
        "declare_no_lock_creation_in_ps_q16i",
        "ready_for_future_disabled_once_run_checker_implementation",
        "manual_refresh_invoked_by_this_checker: bool = False",
        "latest_prediction_refresh_performed_by_this_checker: bool = False",
        "status_artifact_write_performed_by_this_checker: bool = False",
        "lock_file_created_by_this_checker: bool = False",
    ):
        if marker not in module_text:
            failures.append(f"missing module marker: {marker}")
    if "sys.path.insert(0, str(Path(__file__).resolve().parents[4]))" not in unit_text:
        failures.append("unit test must bootstrap btcts_next/src for direct pytest path")
    for forbidden in (
        "write_text(",
        "write_bytes(",
        "open(",
        "build_prediction_warroom_bounded_manual_refresh_runner(",
        "build_prediction_warroom_latest_payload_actual_export_runner(",
        "send_order(",
        "create_order(",
        "append_decision(",
        "append_command(",
    ):
        if forbidden in module_text:
            failures.append(f"forbidden module token: {forbidden}")
    for marker in (
        "checker_only=true",
        "read_only=true",
        "non_executing=true",
        "ready_for_future_disabled_once_run_checker_implementation=true",
        "wrapper_enabled=false",
        "scheduler_enabled=false",
        "os_scheduler_registration_performed=false",
        "scheduled_loop_enabled=false",
        "manual_refresh_invoked=false",
        "latest_prediction_refresh=false",
        "status_artifact_write_performed_by_this_checker=false",
        "lock_file_created_by_this_checker=false",
        "PS-Q16J: operator-shell once-run dry-run CLI",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    if DISABLED_ONCE_RUN_CHECKER_VERSION != "prediction_warroom_disabled_once_run_checker.ps_q16i.v1":
        failures.append("version mismatch")

    ready = build_prediction_warroom_disabled_once_run_checker(
        ps_q16h_wrapper_skeleton_packet=_skeleton(),
        ps_q16f_preflight_report=_preflight(),
        supplied_lock_observation={"lock_present": False},
        supplied_status_observation={"status_ready": True, "last_success_at": "2026-06-22T12:00:00Z"},
    ).to_dict()
    if ready.get("checker_state") != "once_run_checker_disabled_ready_no_lock":
        failures.append(f"ready state mismatch: {ready}")
    if ready.get("simulated_decision") != "ready_no_lock_no_execution":
        failures.append("ready simulated decision mismatch")
    _assert_all_disabled(ready, failures)

    locked = build_prediction_warroom_disabled_once_run_checker(
        ps_q16h_wrapper_skeleton_packet=_skeleton(),
        ps_q16f_preflight_report=_preflight(),
        supplied_lock_observation={"lock_present": True, "lock_reason": "existing_lock"},
        supplied_status_observation={"status_ready": True},
    ).to_dict()
    if locked.get("checker_state") != "once_run_checker_disabled_skip_existing_lock":
        failures.append("lock present must simulate skip")
    if locked.get("would_skip_due_to_existing_lock") is not True:
        failures.append("would_skip_due_to_existing_lock should be true for lock-present simulation")
    _assert_all_disabled(locked, failures)

    stale = build_prediction_warroom_disabled_once_run_checker(
        ps_q16h_wrapper_skeleton_packet=_skeleton(),
        ps_q16f_preflight_report=_preflight(age=4000),
        supplied_lock_observation={"lock_present": False},
        supplied_status_observation={"status_ready": True},
    ).to_dict()
    if "ps_q16f_latest_prediction_stale" not in stale.get("blocked_reasons", []):
        failures.append("missing stale preflight blocker")
    bad_skeleton = build_prediction_warroom_disabled_once_run_checker(
        ps_q16h_wrapper_skeleton_packet=_skeleton(ready=False),
        ps_q16f_preflight_report=_preflight(),
        supplied_lock_observation={"lock_present": False},
        supplied_status_observation={"status_ready": True},
    ).to_dict()
    if "ps_q16h_wrapper_skeleton_not_ready" not in bad_skeleton.get("blocked_reasons", []):
        failures.append("missing unready skeleton blocker")
    forbidden = build_prediction_warroom_disabled_once_run_checker(
        ps_q16h_wrapper_skeleton_packet=_skeleton(),
        ps_q16f_preflight_report=_preflight(),
        supplied_lock_observation={"lock_present": False},
        supplied_status_observation={"status_ready": True},
        request_enable_wrapper=True,
        request_scheduler_enable=True,
        request_os_scheduler_registration=True,
        request_scheduled_loop_enable=True,
        request_execute_manual_refresh=True,
        request_latest_prediction_refresh=True,
        request_status_artifact_write=True,
        request_lock_file_create=True,
        request_generate_enablement_command=True,
        request_warroom_ui_trigger=True,
        request_parameter_apply=True,
        request_parameter_staging_write=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    if forbidden.get("ready_for_future_disabled_once_run_checker_implementation") is not False:
        failures.append("forbidden requests must block readiness")
    _assert_all_disabled(forbidden, failures)

    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16i_close_guard",
        "phase": "phase3_prediction_system_disabled_once_run_checker_closed",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q16i_closed": not failures,
            "checker_only": True,
            "simulates_lock_skip": True,
            "manual_refresh_invoked_by_this_checker": False,
            "latest_prediction_refresh_performed_by_this_checker": False,
            "status_artifact_write_performed_by_this_checker": False,
            "lock_file_created_by_this_checker": False,
            "scheduler_enabled": False,
            "os_scheduler_registration_performed": False,
            "scheduled_loop_enabled": False,
            "autotrade_trigger_candidate_deferred": True,
            "next_slice": "PS-Q16J operator-shell once-run dry-run CLI; read-only D-hot observations only and still no refresh/status write/lock creation/scheduler registration",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16i_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
