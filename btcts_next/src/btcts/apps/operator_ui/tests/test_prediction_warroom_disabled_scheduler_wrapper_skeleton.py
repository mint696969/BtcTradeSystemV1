# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_disabled_scheduler_wrapper_skeleton.py
# desc: Unit tests for PS-Q16H disabled scheduler wrapper skeleton.

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from btcts.apps.operator_ui.components.prediction_warroom_disabled_scheduler_wrapper_skeleton import (
    DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION,
    build_prediction_warroom_disabled_scheduler_wrapper_skeleton,
)
from btcts.apps.operator_ui.components.prediction_warroom_disabled_scheduler_design_packet import (
    DISABLED_SCHEDULER_DESIGN_PACKET_VERSION,
)


def _design() -> dict:
    return {
        "design_version": DISABLED_SCHEDULER_DESIGN_PACKET_VERSION,
        "ready_for_disabled_scheduler_wrapper_slice": True,
        "ready_for_scheduler_enablement": False,
        "scheduler_registration_performed": False,
        "scheduled_loop_enabled": False,
        "scheduler_enablement_command_generated": False,
    }


def _assert_never_enabled(packet: dict) -> None:
    for key in (
        "ready_for_scheduler_enablement",
        "ready_for_runtime_artifact_write_automation",
        "wrapper_enabled",
        "scheduler_enabled",
        "os_scheduler_registration_performed",
        "scheduled_loop_enabled",
        "enablement_command_generated",
        "manual_refresh_invoked_by_this_skeleton",
        "latest_prediction_refresh_performed_by_this_skeleton",
        "status_artifact_write_performed_by_this_skeleton",
        "lock_file_created_by_this_skeleton",
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
        assert packet[key] is False, key
    assert packet["skeleton_only"] is True
    assert packet["read_only"] is True
    assert packet["non_executing"] is True


def test_ps_q16h_blocks_without_human_wrapper_skeleton_record() -> None:
    packet = build_prediction_warroom_disabled_scheduler_wrapper_skeleton(ps_q16g_design_packet=_design()).to_dict()
    assert packet["skeleton_version"] == DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION
    assert packet["skeleton_state"] == "disabled_scheduler_wrapper_skeleton_blocked"
    assert "human_wrapper_skeleton_record_required_for_ps_q16h" in packet["blocked_reasons"]
    assert packet["ready_for_future_disabled_operator_shell_wrapper_implementation"] is False
    _assert_never_enabled(packet)


def test_ps_q16h_ready_for_future_disabled_operator_shell_wrapper_implementation() -> None:
    packet = build_prediction_warroom_disabled_scheduler_wrapper_skeleton(
        ps_q16g_design_packet=_design(),
        human_wrapper_skeleton_record_present=True,
        human_wrapper_skeleton_source="operator_chat_next_go_2026_06_22",
    ).to_dict()
    assert packet["skeleton_state"] == "disabled_scheduler_wrapper_skeleton_ready_for_future_disabled_implementation"
    assert packet["ready_for_future_disabled_operator_shell_wrapper_implementation"] is True
    assert "future_entrypoint_default=disabled" in packet["future_entrypoint_contract"]
    assert "lock_file_created_by_this_skeleton=false" in packet["lock_policy"]
    _assert_never_enabled(packet)


def test_ps_q16h_rejects_unready_or_wrong_design_packet() -> None:
    wrong = _design()
    wrong["design_version"] = "wrong"
    packet = build_prediction_warroom_disabled_scheduler_wrapper_skeleton(
        ps_q16g_design_packet=wrong,
        human_wrapper_skeleton_record_present=True,
        human_wrapper_skeleton_source="operator_chat_next_go_2026_06_22",
    ).to_dict()
    assert "ps_q16g_design_packet_version_mismatch" in packet["blocked_reasons"]
    _assert_never_enabled(packet)

    unready = _design()
    unready["ready_for_disabled_scheduler_wrapper_slice"] = False
    packet = build_prediction_warroom_disabled_scheduler_wrapper_skeleton(
        ps_q16g_design_packet=unready,
        human_wrapper_skeleton_record_present=True,
        human_wrapper_skeleton_source="operator_chat_next_go_2026_06_22",
    ).to_dict()
    assert "ps_q16g_design_not_ready_for_disabled_scheduler_wrapper_slice" in packet["blocked_reasons"]
    _assert_never_enabled(packet)


def test_ps_q16h_rejects_any_enablement_or_execution_request() -> None:
    packet = build_prediction_warroom_disabled_scheduler_wrapper_skeleton(
        ps_q16g_design_packet=_design(),
        human_wrapper_skeleton_record_present=True,
        human_wrapper_skeleton_source="operator_chat_next_go_2026_06_22",
        request_scheduler_enable=True,
        request_os_scheduler_registration=True,
        request_scheduled_loop_enable=True,
        request_runtime_artifact_write_automation_enable=True,
        request_generate_enablement_command=True,
        request_execute_manual_refresh=True,
        request_status_artifact_write=True,
        request_warroom_ui_trigger=True,
        request_parameter_apply=True,
        request_parameter_staging_write=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    assert packet["skeleton_state"] == "disabled_scheduler_wrapper_skeleton_blocked"
    assert "forbidden_request_in_ps_q16h:request_scheduler_enable" in packet["blocked_reasons"]
    assert "forbidden_request_in_ps_q16h:request_execute_manual_refresh" in packet["blocked_reasons"]
    assert packet["ready_for_future_disabled_operator_shell_wrapper_implementation"] is False
    _assert_never_enabled(packet)
