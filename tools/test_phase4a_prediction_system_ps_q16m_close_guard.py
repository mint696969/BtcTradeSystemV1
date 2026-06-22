# path: ./tools/test_phase4a_prediction_system_ps_q16m_close_guard.py
# desc: Close guard for PS-Q16M disabled guarded once-run implementation skeleton.

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
)
from btcts.apps.operator_ui.components.prediction_warroom_guarded_once_run_implementation_skeleton import (  # noqa: E402
    GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_VERSION,
    build_prediction_warroom_guarded_once_run_implementation_skeleton,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_guarded_once_run_implementation_skeleton.py"
UNIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_guarded_once_run_implementation_skeleton.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16M_GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q16m_guarded_once_run_implementation_skeleton_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_guarded_once_run_implementation_skeleton.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_guarded_once_run_implementation_skeleton.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16M_GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16m_guarded_once_run_implementation_skeleton_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16m_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _plan(*, ready: bool = True) -> dict:
    return {
        "plan_version": GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION,
        "ready_for_future_guarded_once_run_execution_implementation_slice": ready,
        "plan_only": True,
        "read_only": True,
        "non_executing": True,
        "lock_relative_path": LOCK_RELATIVE_PATH,
        "ready_for_execution_enablement": False,
        "execution_enabled": False,
        "manual_refresh_invoked_by_this_plan": False,
        "latest_prediction_refresh_performed_by_this_plan": False,
        "status_artifact_write_performed_by_this_plan": False,
        "runtime_artifact_write_performed_by_this_plan": False,
        "lock_file_created_by_this_plan": False,
        "lock_file_deleted_by_this_plan": False,
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
        "implementation_enabled",
        "execution_enabled",
        "manual_refresh_invoked_by_this_skeleton",
        "latest_prediction_refresh_performed_by_this_skeleton",
        "status_artifact_write_performed_by_this_skeleton",
        "runtime_artifact_write_performed_by_this_skeleton",
        "lock_file_created_by_this_skeleton",
        "lock_file_deleted_by_this_skeleton",
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
    for key in ("skeleton_only", "read_only", "non_executing"):
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
        "GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_VERSION",
        "future_entrypoint_default=disabled",
        "future_entrypoint_operator_shell_only=true",
        "future_entrypoint_requires_clean_tree=true",
        "future_entrypoint_requires_no_existing_lock=true",
        "future_entrypoint_requires_explicit_execution_approval=false_in_ps_q16m",
        "declare_single_run_lock_lifecycle_contract_without_io",
        "declare_bounded_manual_refresh_adapter_boundary_without_invocation",
        "declare_status_write_boundary_without_write",
        "declare_stdout_report_boundary_without_execution",
        "skeleton_only: bool = True",
        "read_only: bool = True",
        "non_executing: bool = True",
        "ready_for_execution_enablement: bool = False",
        "implementation_enabled: bool = False",
        "execution_enabled: bool = False",
        "manual_refresh_invoked_by_this_skeleton: bool = False",
        "latest_prediction_refresh_performed_by_this_skeleton: bool = False",
        "status_artifact_write_performed_by_this_skeleton: bool = False",
        "runtime_artifact_write_performed_by_this_skeleton: bool = False",
        "lock_file_created_by_this_skeleton: bool = False",
        "lock_file_deleted_by_this_skeleton: bool = False",
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
        "skeleton_only=true",
        "read_only=true",
        "non_executing=true",
        "ready_for_future_disabled_once_run_operator_shell_cli_slice=true",
        "ready_for_execution_enablement=false",
        "implementation_enabled=false",
        "execution_enabled=false",
        "future_entrypoint_default=disabled",
        "future_entrypoint_requires_explicit_execution_approval=false_in_ps_q16m",
        "manual_refresh_invoked=false",
        "latest_prediction_refresh=false",
        "status_artifact_write=false",
        "runtime_artifact_write=false",
        "lock_file_created=false",
        "lock_file_deleted=false",
        "PS-Q16N: disabled operator-shell once-run CLI skeleton/dry-run wrapper",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
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
    if GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_VERSION != "prediction_warroom_guarded_once_run_implementation_skeleton.ps_q16m.v1":
        failures.append("version mismatch")

    ready = build_prediction_warroom_guarded_once_run_implementation_skeleton(
        ps_q16l_plan_packet=_plan(),
        human_implementation_skeleton_record_present=True,
        human_implementation_skeleton_source="close_guard",
    ).to_dict()
    if ready.get("skeleton_state") != "guarded_once_run_implementation_skeleton_ready_for_future_disabled_cli_slice":
        failures.append(f"ready state mismatch: {ready}")
    if ready.get("ready_for_future_disabled_once_run_operator_shell_cli_slice") is not True:
        failures.append("ready_for_future_disabled_once_run_operator_shell_cli_slice must be true")
    if "future_entrypoint_default=disabled" not in ready.get("future_entrypoint_contract", []):
        failures.append("disabled future entrypoint marker missing")
    _assert_never_executed(ready, failures)

    missing_human = build_prediction_warroom_guarded_once_run_implementation_skeleton(ps_q16l_plan_packet=_plan()).to_dict()
    if "human_implementation_skeleton_record_required_for_ps_q16m" not in missing_human.get("blocked_reasons", []):
        failures.append("missing human implementation skeleton record blocker")
    _assert_never_executed(missing_human, failures)

    unready = build_prediction_warroom_guarded_once_run_implementation_skeleton(
        ps_q16l_plan_packet=_plan(ready=False),
        human_implementation_skeleton_record_present=True,
        human_implementation_skeleton_source="close_guard",
    ).to_dict()
    if "ps_q16l_plan_not_ready_for_disabled_implementation_skeleton" not in unready.get("blocked_reasons", []):
        failures.append("unready plan blocker missing")
    unsafe = _plan()
    unsafe["status_artifact_write_performed_by_this_plan"] = True
    unsafe_packet = build_prediction_warroom_guarded_once_run_implementation_skeleton(
        ps_q16l_plan_packet=unsafe,
        human_implementation_skeleton_record_present=True,
        human_implementation_skeleton_source="close_guard",
    ).to_dict()
    if "ps_q16l_status_artifact_write_performed_by_this_plan_must_remain_false" not in unsafe_packet.get("blocked_reasons", []):
        failures.append("unsafe plan write blocker missing")
    forbidden = build_prediction_warroom_guarded_once_run_implementation_skeleton(
        ps_q16l_plan_packet=_plan(),
        human_implementation_skeleton_record_present=True,
        human_implementation_skeleton_source="close_guard",
        request_enable_implementation=True,
        request_execute_once_run=True,
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
    if forbidden.get("ready_for_future_disabled_once_run_operator_shell_cli_slice") is not False:
        failures.append("forbidden requests must block skeleton readiness")
    _assert_never_executed(forbidden, failures)

    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q16m_close_guard",
        "phase": "phase3_prediction_system_guarded_once_run_implementation_skeleton_closed",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q16m_closed": not failures,
            "skeleton_only": True,
            "read_only": True,
            "non_executing": True,
            "ready_for_future_disabled_once_run_operator_shell_cli_slice": True,
            "ready_for_execution_enablement": False,
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
            "next_slice": "PS-Q16N disabled operator-shell once-run CLI skeleton/dry-run wrapper; still non-executing and no write behavior unless separately approved",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16m_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
