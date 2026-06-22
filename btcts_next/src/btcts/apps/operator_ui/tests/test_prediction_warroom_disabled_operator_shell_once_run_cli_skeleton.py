# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_disabled_operator_shell_once_run_cli_skeleton.py
# desc: Unit tests for PS-Q16N disabled operator-shell once-run CLI skeleton.

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from btcts.apps.operator_ui.components.prediction_warroom_disabled_operator_shell_once_run_cli_skeleton import (
    DISABLED_OPERATOR_SHELL_ONCE_RUN_CLI_SKELETON_VERSION,
    build_prediction_warroom_disabled_operator_shell_once_run_cli_skeleton,
)
from btcts.apps.operator_ui.components.prediction_warroom_guarded_once_run_execution_plan_packet import LOCK_RELATIVE_PATH
from btcts.apps.operator_ui.components.prediction_warroom_guarded_once_run_implementation_skeleton import (
    GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_VERSION,
)


def _skeleton(*, ready: bool = True) -> dict:
    return {
        "skeleton_version": GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_VERSION,
        "ready_for_future_disabled_once_run_operator_shell_cli_slice": ready,
        "skeleton_only": True,
        "read_only": True,
        "non_executing": True,
        "lock_relative_path": LOCK_RELATIVE_PATH,
        "ready_for_execution_enablement": False,
        "implementation_enabled": False,
        "execution_enabled": False,
        "manual_refresh_invoked_by_this_skeleton": False,
        "latest_prediction_refresh_performed_by_this_skeleton": False,
        "status_artifact_write_performed_by_this_skeleton": False,
        "runtime_artifact_write_performed_by_this_skeleton": False,
        "lock_file_created_by_this_skeleton": False,
        "lock_file_deleted_by_this_skeleton": False,
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
        "cli_enabled",
        "implementation_enabled",
        "execution_enabled",
        "manual_refresh_invoked_by_this_cli_skeleton",
        "latest_prediction_refresh_performed_by_this_cli_skeleton",
        "status_artifact_write_performed_by_this_cli_skeleton",
        "runtime_artifact_write_performed_by_this_cli_skeleton",
        "lock_file_created_by_this_cli_skeleton",
        "lock_file_deleted_by_this_cli_skeleton",
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
    assert packet["cli_skeleton_only"] is True
    assert packet["dry_run_wrapper_only"] is True
    assert packet["operator_shell_only"] is True
    assert packet["read_only"] is True
    assert packet["non_executing"] is True


def test_ps_q16n_ready_cli_skeleton_from_q16m_skeleton_but_does_not_execute() -> None:
    packet = build_prediction_warroom_disabled_operator_shell_once_run_cli_skeleton(
        ps_q16m_implementation_skeleton_packet=_skeleton(),
        human_cli_skeleton_record_present=True,
        human_cli_skeleton_source="operator_confirmed_ps_q16m_skeleton",
    ).to_dict()
    assert packet["cli_skeleton_version"] == DISABLED_OPERATOR_SHELL_ONCE_RUN_CLI_SKELETON_VERSION
    assert packet["cli_skeleton_state"] == "disabled_operator_shell_once_run_cli_skeleton_ready_for_future_dry_run_wrapper"
    assert packet["ready_for_future_disabled_operator_shell_dry_run_cli_slice"] is True
    assert "future_cli_default=disabled" in packet["future_cli_contract"]
    assert "future_arg_execute=not_available_in_ps_q16n" in packet["future_argument_contract"]
    _assert_never_executed(packet)


def test_ps_q16n_requires_human_cli_skeleton_record() -> None:
    packet = build_prediction_warroom_disabled_operator_shell_once_run_cli_skeleton(
        ps_q16m_implementation_skeleton_packet=_skeleton()
    ).to_dict()
    assert packet["cli_skeleton_state"] == "disabled_operator_shell_once_run_cli_skeleton_blocked"
    assert "human_cli_skeleton_record_required_for_ps_q16n" in packet["blocked_reasons"]
    _assert_never_executed(packet)


def test_ps_q16n_blocks_unready_or_unsafe_implementation_skeleton() -> None:
    unready = build_prediction_warroom_disabled_operator_shell_once_run_cli_skeleton(
        ps_q16m_implementation_skeleton_packet=_skeleton(ready=False),
        human_cli_skeleton_record_present=True,
        human_cli_skeleton_source="guard",
    ).to_dict()
    assert "ps_q16m_implementation_skeleton_not_ready_for_cli_skeleton" in unready["blocked_reasons"]
    unsafe = _skeleton()
    unsafe["lock_file_created_by_this_skeleton"] = True
    packet = build_prediction_warroom_disabled_operator_shell_once_run_cli_skeleton(
        ps_q16m_implementation_skeleton_packet=unsafe,
        human_cli_skeleton_record_present=True,
        human_cli_skeleton_source="guard",
    ).to_dict()
    assert "ps_q16m_lock_file_created_by_this_skeleton_must_remain_false" in packet["blocked_reasons"]
    _assert_never_executed(packet)


def test_ps_q16n_rejects_enable_execute_write_lock_and_scheduler_requests() -> None:
    packet = build_prediction_warroom_disabled_operator_shell_once_run_cli_skeleton(
        ps_q16m_implementation_skeleton_packet=_skeleton(),
        human_cli_skeleton_record_present=True,
        human_cli_skeleton_source="guard",
        request_enable_cli=True,
        request_execute_cli=True,
        request_execute_once_run=True,
        request_status_artifact_write=True,
        request_lock_file_create=True,
        request_scheduler_enable=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    assert packet["ready_for_future_disabled_operator_shell_dry_run_cli_slice"] is False
    assert "forbidden_request_in_ps_q16n:request_enable_cli" in packet["blocked_reasons"]
    assert "forbidden_request_in_ps_q16n:request_execute_cli" in packet["blocked_reasons"]
    assert "forbidden_request_in_ps_q16n:request_lock_file_create" in packet["blocked_reasons"]
    _assert_never_executed(packet)
