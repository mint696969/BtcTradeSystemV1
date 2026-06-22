# path: ./tools/test_phase4a_prediction_system_ps_q16l_close_guard.py
# desc: Close guard for PS-Q16L guarded once-run execution plan packet.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_guarded_once_run_execution_plan_packet import (  # noqa: E402
    GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION,
    LOCK_RELATIVE_PATH,
    build_prediction_warroom_guarded_once_run_execution_plan_packet,
)
from btcts.apps.operator_ui.components.prediction_warroom_once_run_execution_design_checkpoint import (  # noqa: E402
    ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_guarded_once_run_execution_plan_packet.py"
UNIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_guarded_once_run_execution_plan_packet.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16L_GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16l_guarded_once_run_execution_plan_packet_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_guarded_once_run_execution_plan_packet.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_guarded_once_run_execution_plan_packet.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16L_GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16l_guarded_once_run_execution_plan_packet_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16l_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _checkpoint(*, ready: bool = True) -> dict:
    return {
        "checkpoint_version": ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION,
        "ready_for_future_guarded_once_run_execution_design_slice": ready,
        "checkpoint_only": True,
        "read_only": True,
        "non_executing": True,
        "ready_for_execution_enablement": False,
        "execution_enabled": False,
        "manual_refresh_invoked_by_this_checkpoint": False,
        "latest_prediction_refresh_performed_by_this_checkpoint": False,
        "status_artifact_write_performed_by_this_checkpoint": False,
        "runtime_artifact_write_performed_by_this_checkpoint": False,
        "lock_file_created_by_this_checkpoint": False,
        "lock_file_deleted_by_this_checkpoint": False,
        "scheduler_enabled": False,
        "os_scheduler_registration_performed": False,
        "scheduled_loop_enabled": False,
        "warroom_ui_trigger_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "freshness_bypass_added": False,
        "force_ready_added": False,
    }


def _assert_never_executed(packet: dict, failures: list[str]) -> None:
    for key in (
        "ready_for_execution_enablement",
        "execution_enabled",
        "manual_refresh_invoked_by_this_plan",
        "latest_prediction_refresh_performed_by_this_plan",
        "status_artifact_write_performed_by_this_plan",
        "runtime_artifact_write_performed_by_this_plan",
        "lock_file_created_by_this_plan",
        "lock_file_deleted_by_this_plan",
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
        if packet.get(key) is not False:
            failures.append(f"{key} must remain false")
    for key in ("plan_only", "read_only", "non_executing"):
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
        "GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION",
        "LOCK_RELATIVE_PATH = \"prediction/status/non_ui_scheduled_producer.lock\"",
        "future_step_01_require_clean_tree",
        "future_step_04_check_lock_absent_before_start",
        "future_step_05_create_single_run_lock_in_future_slice_only",
        "future_step_06_invoke_bounded_manual_refresh_runner_in_future_slice_only",
        "future_step_07_write_status_artifact_via_bounded_runner_in_future_slice_only",
        "future_step_09_release_or_delete_lock_in_finally_future_slice_only",
        "future_step_10_do_not_register_scheduler_or_enable_loop",
        "plan_only: bool = True",
        "read_only: bool = True",
        "non_executing: bool = True",
        "ready_for_execution_enablement: bool = False",
        "execution_enabled: bool = False",
        "manual_refresh_invoked_by_this_plan: bool = False",
        "latest_prediction_refresh_performed_by_this_plan: bool = False",
        "status_artifact_write_performed_by_this_plan: bool = False",
        "runtime_artifact_write_performed_by_this_plan: bool = False",
        "lock_file_created_by_this_plan: bool = False",
        "lock_file_deleted_by_this_plan: bool = False",
    ):
        if marker not in module_text:
            failures.append(f"missing module marker: {marker}")
    for forbidden in (
        "subprocess",
        "write_text(",
        "write_bytes(",
        "replace(",
        "open(",
        "mkdir(",
        "unlink(",
        "build_prediction_warroom_bounded_manual_refresh_runner(",
        "build_prediction_warroom_latest_payload_actual_export_runner(",
        "send_order(",
        "create_order(",
        "append_decision(",
        "append_command(",
    ):
        if forbidden in module_text:
            failures.append(f"forbidden module token: {forbidden}")
    if "sys.path.insert(0, str(Path(__file__).resolve().parents[4]))" not in unit_text:
        failures.append("unit test must bootstrap btcts_next/src for direct pytest path")
    for marker in (
        "plan_only=true",
        "read_only=true",
        "non_executing=true",
        "ready_for_future_guarded_once_run_execution_implementation_slice=true",
        "ready_for_execution_enablement=false",
        "execution_enabled=false",
        "future_step_05_create_single_run_lock_in_future_slice_only",
        "future_step_06_invoke_bounded_manual_refresh_runner_in_future_slice_only",
        "future_step_09_release_or_delete_lock_in_finally_future_slice_only",
        "manual_refresh_invoked=false",
        "latest_prediction_refresh=false",
        "status_artifact_write=false",
        "runtime_artifact_write=false",
        "lock_file_created=false",
        "lock_file_deleted=false",
        "PS-Q16M: guarded once-run implementation skeleton",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
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
    if GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION != "prediction_warroom_guarded_once_run_execution_plan_packet.ps_q16l.v1":
        failures.append("version mismatch")
    if LOCK_RELATIVE_PATH != "prediction/status/non_ui_scheduled_producer.lock":
        failures.append("lock relative path mismatch")

    ready = build_prediction_warroom_guarded_once_run_execution_plan_packet(
        ps_q16k_checkpoint_packet=_checkpoint(),
        human_execution_plan_record_present=True,
        human_execution_plan_source="close_guard",
    ).to_dict()
    if ready.get("plan_state") != "guarded_once_run_execution_plan_ready_for_future_implementation_slice":
        failures.append(f"ready state mismatch: {ready}")
    if ready.get("ready_for_future_guarded_once_run_execution_implementation_slice") is not True:
        failures.append("ready_for_future_guarded_once_run_execution_implementation_slice must be true")
    if "future_step_05_create_single_run_lock_in_future_slice_only" not in ready.get("plan_steps", []):
        failures.append("future lock step missing from plan")
    _assert_never_executed(ready, failures)

    missing_human = build_prediction_warroom_guarded_once_run_execution_plan_packet(
        ps_q16k_checkpoint_packet=_checkpoint(),
    ).to_dict()
    if "human_execution_plan_record_required_for_ps_q16l" not in missing_human.get("blocked_reasons", []):
        failures.append("missing human execution plan record blocker")
    _assert_never_executed(missing_human, failures)

    unready = build_prediction_warroom_guarded_once_run_execution_plan_packet(
        ps_q16k_checkpoint_packet=_checkpoint(ready=False),
        human_execution_plan_record_present=True,
        human_execution_plan_source="close_guard",
    ).to_dict()
    if "ps_q16k_checkpoint_not_ready_for_guarded_execution_plan" not in unready.get("blocked_reasons", []):
        failures.append("unready checkpoint blocker missing")
    unsafe = _checkpoint()
    unsafe["status_artifact_write_performed_by_this_checkpoint"] = True
    unsafe_packet = build_prediction_warroom_guarded_once_run_execution_plan_packet(
        ps_q16k_checkpoint_packet=unsafe,
        human_execution_plan_record_present=True,
        human_execution_plan_source="close_guard",
    ).to_dict()
    if "ps_q16k_status_artifact_write_performed_by_this_checkpoint_must_remain_false" not in unsafe_packet.get("blocked_reasons", []):
        failures.append("unsafe checkpoint write blocker missing")
    forbidden = build_prediction_warroom_guarded_once_run_execution_plan_packet(
        ps_q16k_checkpoint_packet=_checkpoint(),
        human_execution_plan_record_present=True,
        human_execution_plan_source="close_guard",
        request_execute_plan=True,
        request_execute_manual_refresh=True,
        request_latest_prediction_refresh=True,
        request_status_artifact_write=True,
        request_runtime_artifact_write=True,
        request_lock_file_create=True,
        request_lock_file_delete=True,
        request_scheduler_enable=True,
        request_os_scheduler_registration=True,
        request_scheduled_loop_enable=True,
        request_generate_enablement_command=True,
        request_warroom_ui_trigger=True,
        request_parameter_apply=True,
        request_parameter_staging_write=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    if forbidden.get("ready_for_future_guarded_once_run_execution_implementation_slice") is not False:
        failures.append("forbidden requests must block plan readiness")
    _assert_never_executed(forbidden, failures)

    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16l_close_guard",
        "phase": "phase3_prediction_system_guarded_once_run_execution_plan_packet_closed",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q16l_closed": not failures,
            "plan_only": True,
            "read_only": True,
            "non_executing": True,
            "ready_for_future_guarded_once_run_execution_implementation_slice": True,
            "ready_for_execution_enablement": False,
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
            "next_slice": "PS-Q16M guarded once-run implementation skeleton; disabled by default and non-executing unless separate explicit approval introduces guarded write behavior",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16l_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
