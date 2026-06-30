# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_single_producer_60s_disabled_contract_skeleton.py
# desc: Verify PS-Q25U disabled single-producer 60s contract/skeleton remains disabled, non-executing, and blocks all runtime/scheduler/write requests.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_single_producer_60s_disabled_contract_skeleton import (  # noqa: E402
    CANDIDATE_COMPONENTS,
    SELECTED_CADENCE_OPTION_ID,
    SELECTED_TARGET_CADENCE_SEC,
    SINGLE_PRODUCER_60S_DISABLED_CONTRACT_SKELETON_VERSION,
    build_prediction_warroom_single_producer_60s_disabled_contract_skeleton,
)


def _q25t_packet() -> dict:
    return {
        "selected_option_id": "single_producer_60s_candidate",
        "selected_target_cadence_sec": 60,
        "preflight_only": True,
        "implementation_allowed_by_this_packet": False,
        "manual_one_shot_run_allowed": False,
        "scheduler_enablement_allowed": False,
    }


def test_q25u_ready_packet_is_disabled_and_non_executing() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_contract_skeleton(q25t_preflight_packet=_q25t_packet()).to_dict()
    assert packet["skeleton_version"] == SINGLE_PRODUCER_60S_DISABLED_CONTRACT_SKELETON_VERSION
    assert packet["skeleton_state"] == "single_producer_60s_disabled_contract_skeleton_ready"
    assert packet["selected_option_id"] == SELECTED_CADENCE_OPTION_ID
    assert packet["selected_target_cadence_sec"] == SELECTED_TARGET_CADENCE_SEC == 60
    assert packet["minimum_cadence_sec"] == 60
    assert packet["q25t_preflight_packet_supplied"] is True
    assert packet["q25t_preflight_ready"] is True
    assert packet["ready_for_future_disabled_single_producer_60s_skeleton_validation"] is True
    assert packet["contract_skeleton_only"] is True
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["default_enabled"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["scheduled_loop_enabled"] is False
    assert packet["ready_for_manual_one_shot_run"] is False
    assert packet["ready_for_scheduler_enablement"] is False
    assert packet["ready_for_producer_enablement"] is False
    assert packet["manual_one_shot_run_invoked_by_this_skeleton"] is False
    assert packet["prediction_build_requested"] is False
    assert packet["actual_export_runner_invoked"] is False
    assert packet["bounded_manual_refresh_invoked"] is False
    assert packet["would_write_runtime_artifact"] is False
    assert packet["would_write_status_artifact"] is False
    assert packet["would_write_prediction_artifact"] is False
    assert packet["would_write_view_artifact"] is False
    assert packet["latest_manifest_written"] is False
    assert packet["run_sidecars_written"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["ledger_append_allowed"] is False
    assert packet["parameter_apply_allowed"] is False
    assert packet["mode_apply_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_q25u_candidate_mapping_and_paths_are_declared_only() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_contract_skeleton(q25t_preflight_packet=_q25t_packet()).to_dict()
    assert len(packet["candidate_components"]) == len(CANDIDATE_COMPONENTS) == 6
    assert "prediction_warroom_non_ui_scheduled_producer_runner.py" in "\n".join(packet["candidate_components"])
    assert packet["latest_prediction_artifact_relative_path"] == "prediction/latest_prediction_system_result.json"
    assert packet["producer_status_artifact_relative_path"] == "prediction/status/non_ui_scheduled_producer_status.json"
    assert packet["lock_relative_path"] == "prediction/status/non_ui_scheduled_producer.lock"
    assert packet["lock_file_created_by_this_skeleton"] is False
    assert packet["lock_file_deleted_by_this_skeleton"] is False


def test_q25u_blocks_all_runtime_enablement_requests() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_contract_skeleton(
        q25t_preflight_packet=_q25t_packet(),
        request_manual_one_shot_run=True,
        request_scheduler_enable=True,
        request_scheduler_action_change=True,
        request_producer_enable=True,
        request_runtime_artifact_write=True,
        request_status_artifact_write=True,
        request_prediction_artifact_write=True,
        request_view_artifact_write=True,
        request_latest_manifest_write=True,
        request_run_sidecars_write=True,
        request_warroom_ui_trigger=True,
        request_parameter_apply=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    assert packet["skeleton_state"] == "single_producer_60s_disabled_contract_skeleton_blocked_or_observation_only"
    assert packet["ready_for_future_disabled_single_producer_60s_skeleton_validation"] is False
    assert packet["requested_forbidden_flags"]
    assert packet["blocker_count"] == len(packet["requested_forbidden_flags"])
    assert all(str(reason).startswith("forbidden_request_in_ps_q25u:") for reason in packet["blocked_reasons"])
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["manual_one_shot_run_invoked_by_this_skeleton"] is False
    assert packet["would_write_runtime_artifact"] is False
    assert packet["would_send_to_broker"] is False


def test_q25u_missing_preflight_remains_disabled_observation_only() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_contract_skeleton().to_dict()
    assert packet["q25t_preflight_packet_supplied"] is False
    assert packet["ready_for_future_disabled_single_producer_60s_skeleton_validation"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert "q25t_preflight_packet_not_supplied_skeleton_still_disabled" in packet["warning_reasons"]
