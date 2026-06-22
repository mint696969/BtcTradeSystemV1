# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_guarded_once_run_execution_plan_packet.py
# desc: Unit tests for PS-Q16L guarded once-run execution plan packet.

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from btcts.apps.operator_ui.components.prediction_warroom_guarded_once_run_execution_plan_packet import (
    GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION,
    LOCK_RELATIVE_PATH,
    build_prediction_warroom_guarded_once_run_execution_plan_packet,
)
from btcts.apps.operator_ui.components.prediction_warroom_once_run_execution_design_checkpoint import (
    ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION,
)


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


def _assert_never_executed(packet: dict) -> None:
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
    assert packet["plan_only"] is True
    assert packet["read_only"] is True
    assert packet["non_executing"] is True


def test_ps_q16l_ready_plan_from_q16k_checkpoint_but_does_not_execute() -> None:
    packet = build_prediction_warroom_guarded_once_run_execution_plan_packet(
        ps_q16k_checkpoint_packet=_checkpoint(),
        human_execution_plan_record_present=True,
        human_execution_plan_source="operator_confirmed_ps_q16k_checkpoint",
    ).to_dict()
    assert packet["plan_version"] == GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION
    assert packet["plan_state"] == "guarded_once_run_execution_plan_ready_for_future_implementation_slice"
    assert packet["ready_for_future_guarded_once_run_execution_implementation_slice"] is True
    assert packet["lock_relative_path"] == LOCK_RELATIVE_PATH
    assert "future_step_05_create_single_run_lock_in_future_slice_only" in packet["plan_steps"]
    _assert_never_executed(packet)


def test_ps_q16l_requires_human_execution_plan_record() -> None:
    packet = build_prediction_warroom_guarded_once_run_execution_plan_packet(
        ps_q16k_checkpoint_packet=_checkpoint(),
    ).to_dict()
    assert packet["plan_state"] == "guarded_once_run_execution_plan_blocked"
    assert "human_execution_plan_record_required_for_ps_q16l" in packet["blocked_reasons"]
    _assert_never_executed(packet)


def test_ps_q16l_blocks_unready_or_unsafe_checkpoint() -> None:
    unready = build_prediction_warroom_guarded_once_run_execution_plan_packet(
        ps_q16k_checkpoint_packet=_checkpoint(ready=False),
        human_execution_plan_record_present=True,
        human_execution_plan_source="guard",
    ).to_dict()
    assert "ps_q16k_checkpoint_not_ready_for_guarded_execution_plan" in unready["blocked_reasons"]
    unsafe = _checkpoint()
    unsafe["lock_file_created_by_this_checkpoint"] = True
    packet = build_prediction_warroom_guarded_once_run_execution_plan_packet(
        ps_q16k_checkpoint_packet=unsafe,
        human_execution_plan_record_present=True,
        human_execution_plan_source="guard",
    ).to_dict()
    assert "ps_q16k_lock_file_created_by_this_checkpoint_must_remain_false" in packet["blocked_reasons"]
    _assert_never_executed(packet)


def test_ps_q16l_rejects_execution_write_lock_and_scheduler_requests() -> None:
    packet = build_prediction_warroom_guarded_once_run_execution_plan_packet(
        ps_q16k_checkpoint_packet=_checkpoint(),
        human_execution_plan_record_present=True,
        human_execution_plan_source="guard",
        request_execute_plan=True,
        request_execute_manual_refresh=True,
        request_status_artifact_write=True,
        request_lock_file_create=True,
        request_scheduler_enable=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    assert packet["ready_for_future_guarded_once_run_execution_implementation_slice"] is False
    assert "forbidden_request_in_ps_q16l:request_execute_plan" in packet["blocked_reasons"]
    assert "forbidden_request_in_ps_q16l:request_lock_file_create" in packet["blocked_reasons"]
    _assert_never_executed(packet)
