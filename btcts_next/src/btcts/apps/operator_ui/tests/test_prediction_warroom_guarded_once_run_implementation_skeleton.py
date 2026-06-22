# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_guarded_once_run_implementation_skeleton.py
# desc: Unit tests for PS-Q16M disabled guarded once-run implementation skeleton.

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from btcts.apps.operator_ui.components.prediction_warroom_guarded_once_run_execution_plan_packet import (
    GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION,
    LOCK_RELATIVE_PATH,
)
from btcts.apps.operator_ui.components.prediction_warroom_guarded_once_run_implementation_skeleton import (
    GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_VERSION,
    build_prediction_warroom_guarded_once_run_implementation_skeleton,
)


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


def _assert_never_executed(packet: dict) -> None:
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
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        assert packet[key] is False, key
    assert packet["skeleton_only"] is True
    assert packet["read_only"] is True
    assert packet["non_executing"] is True


def test_ps_q16m_ready_skeleton_from_q16l_plan_but_does_not_execute() -> None:
    packet = build_prediction_warroom_guarded_once_run_implementation_skeleton(
        ps_q16l_plan_packet=_plan(),
        human_implementation_skeleton_record_present=True,
        human_implementation_skeleton_source="operator_confirmed_ps_q16l_plan",
    ).to_dict()
    assert packet["skeleton_version"] == GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_VERSION
    assert packet["skeleton_state"] == "guarded_once_run_implementation_skeleton_ready_for_future_disabled_cli_slice"
    assert packet["ready_for_future_disabled_once_run_operator_shell_cli_slice"] is True
    assert "future_entrypoint_default=disabled" in packet["future_entrypoint_contract"]
    _assert_never_executed(packet)


def test_ps_q16m_requires_human_implementation_skeleton_record() -> None:
    packet = build_prediction_warroom_guarded_once_run_implementation_skeleton(ps_q16l_plan_packet=_plan()).to_dict()
    assert packet["skeleton_state"] == "guarded_once_run_implementation_skeleton_blocked"
    assert "human_implementation_skeleton_record_required_for_ps_q16m" in packet["blocked_reasons"]
    _assert_never_executed(packet)


def test_ps_q16m_blocks_unready_or_unsafe_plan() -> None:
    unready = build_prediction_warroom_guarded_once_run_implementation_skeleton(
        ps_q16l_plan_packet=_plan(ready=False),
        human_implementation_skeleton_record_present=True,
        human_implementation_skeleton_source="guard",
    ).to_dict()
    assert "ps_q16l_plan_not_ready_for_disabled_implementation_skeleton" in unready["blocked_reasons"]
    unsafe = _plan()
    unsafe["lock_file_created_by_this_plan"] = True
    packet = build_prediction_warroom_guarded_once_run_implementation_skeleton(
        ps_q16l_plan_packet=unsafe,
        human_implementation_skeleton_record_present=True,
        human_implementation_skeleton_source="guard",
    ).to_dict()
    assert "ps_q16l_lock_file_created_by_this_plan_must_remain_false" in packet["blocked_reasons"]
    _assert_never_executed(packet)


def test_ps_q16m_rejects_enable_execute_write_lock_and_scheduler_requests() -> None:
    packet = build_prediction_warroom_guarded_once_run_implementation_skeleton(
        ps_q16l_plan_packet=_plan(),
        human_implementation_skeleton_record_present=True,
        human_implementation_skeleton_source="guard",
        request_enable_implementation=True,
        request_execute_once_run=True,
        request_execute_manual_refresh=True,
        request_status_artifact_write=True,
        request_lock_file_create=True,
        request_scheduler_enable=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    assert packet["ready_for_future_disabled_once_run_operator_shell_cli_slice"] is False
    assert "forbidden_request_in_ps_q16m:request_enable_implementation" in packet["blocked_reasons"]
    assert "forbidden_request_in_ps_q16m:request_execute_once_run" in packet["blocked_reasons"]
    assert "forbidden_request_in_ps_q16m:request_lock_file_create" in packet["blocked_reasons"]
    _assert_never_executed(packet)
