# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet.py
# desc: Verify PS-Q25W disabled dry-run planning packet remains planning-only and blocks execution/write/lock/scheduler requests.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet import (  # noqa: E402
    SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_PLANNING_PACKET_VERSION,
    build_prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet,
)


def test_q25w_planning_ready_and_non_executing() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet().to_dict()
    assert packet["planning_version"] == SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_PLANNING_PACKET_VERSION
    assert packet["planning_state"] == "single_producer_60s_disabled_dry_run_planning_ready"
    assert packet["selected_option_id"] == "single_producer_60s_candidate"
    assert packet["selected_target_cadence_sec"] == 60
    assert packet["q25v_validation_packet_supplied"] is True
    assert packet["q25v_validation_ready"] is True
    assert packet["ready_for_future_disabled_dry_run_design_checkpoint"] is True
    assert packet["dry_run_planning_only"] is True
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["execute_dry_run_enabled"] is False
    assert packet["manual_one_shot_run_invoked_by_this_planning"] is False
    assert packet["future_dry_run_invoked_by_this_planning"] is False
    assert packet["q16l_execution_plan_invoked_by_this_planning"] is False
    assert packet["status_artifact_write_performed_by_this_planning"] is False
    assert packet["runtime_artifact_write_performed_by_this_planning"] is False
    assert packet["prediction_artifact_write_performed_by_this_planning"] is False
    assert packet["latest_manifest_written"] is False
    assert packet["run_sidecars_written"] is False
    assert packet["lock_file_created_by_this_planning"] is False
    assert packet["lock_file_deleted_by_this_planning"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["ledger_append_allowed"] is False
    assert packet["mode_apply_allowed"] is False
    assert packet["parameter_apply_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_q25w_references_q16l_plan_without_invoking_it() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet().to_dict()
    assert packet["referenced_q16l_plan_version"] == "prediction_warroom_guarded_once_run_execution_plan_packet.ps_q16l.v1"
    assert "future_step_04_check_lock_absent_before_start" in packet["referenced_q16l_plan_steps"]
    assert "future_step_06_invoke_bounded_manual_refresh_runner_in_future_slice_only" in packet["referenced_q16l_plan_steps"]
    assert packet["lock_relative_path"] == "prediction/status/non_ui_scheduled_producer.lock"
    assert packet["q16l_execution_plan_invoked_by_this_planning"] is False


def test_q25w_blocks_execution_write_lock_and_scheduler_requests() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet(
        request_execute_dry_run=True,
        request_manual_one_shot_run=True,
        request_scheduler_enable=True,
        request_producer_enable=True,
        request_status_artifact_write=True,
        request_runtime_artifact_write=True,
        request_prediction_artifact_write=True,
        request_latest_manifest_write=True,
        request_run_sidecars_write=True,
        request_lock_file_create=True,
        request_lock_file_delete=True,
        request_warroom_ui_trigger=True,
        request_parameter_apply=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    assert packet["planning_state"] == "single_producer_60s_disabled_dry_run_planning_blocked"
    assert packet["ready_for_future_disabled_dry_run_design_checkpoint"] is False
    assert packet["requested_forbidden_flags"]
    assert packet["blocker_count"] == len(packet["requested_forbidden_flags"])
    assert all(str(item).startswith("forbidden_request_in_ps_q25w:") for item in packet["blocked_reasons"])
    assert packet["execute_dry_run_enabled"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["would_send_to_broker"] is False
