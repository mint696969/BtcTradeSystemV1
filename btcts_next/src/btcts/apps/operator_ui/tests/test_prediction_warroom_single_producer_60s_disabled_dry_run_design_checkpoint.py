# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint.py
# desc: Verify PS-Q25X disabled dry-run design checkpoint remains checkpoint-only and blocks execution/write/lock/scheduler requests.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint import (  # noqa: E402
    SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_DESIGN_CHECKPOINT_VERSION,
    build_prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint,
)


def test_q25x_checkpoint_ready_and_non_executing() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint().to_dict()
    assert packet["checkpoint_version"] == SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_DESIGN_CHECKPOINT_VERSION
    assert packet["checkpoint_state"] == "single_producer_60s_disabled_dry_run_design_checkpoint_ready"
    assert packet["selected_option_id"] == "single_producer_60s_candidate"
    assert packet["selected_target_cadence_sec"] == 60
    assert packet["q25w_planning_packet_supplied"] is True
    assert packet["q25w_planning_ready"] is True
    assert packet["ready_for_future_disabled_dry_run_execution_gate_planning"] is True
    assert packet["checkpoint_only"] is True
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["execute_dry_run_enabled"] is False
    assert packet["manual_one_shot_run_invoked_by_this_checkpoint"] is False
    assert packet["future_dry_run_invoked_by_this_checkpoint"] is False
    assert packet["q16k_checkpoint_invoked_by_this_checkpoint"] is False
    assert packet["status_artifact_write_performed_by_this_checkpoint"] is False
    assert packet["runtime_artifact_write_performed_by_this_checkpoint"] is False
    assert packet["prediction_artifact_write_performed_by_this_checkpoint"] is False
    assert packet["latest_manifest_written"] is False
    assert packet["run_sidecars_written"] is False
    assert packet["lock_file_created_by_this_checkpoint"] is False
    assert packet["lock_file_deleted_by_this_checkpoint"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["ledger_append_allowed"] is False
    assert packet["mode_apply_allowed"] is False
    assert packet["parameter_apply_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_q25x_references_q16k_boundary_without_invoking_it() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint().to_dict()
    assert packet["referenced_q16k_checkpoint_version"] == "prediction_warroom_once_run_execution_design_checkpoint.ps_q16k.v1"
    assert "future_slice_requires_clean_tree=true" in packet["referenced_q16k_future_execution_boundary"]
    assert "future_slice_warroom_ui_trigger_allowed=false" in packet["referenced_q16k_future_execution_boundary"]
    assert "future_execution_gate_required=true" in packet["future_dry_run_execution_gate"]
    assert packet["q16k_checkpoint_invoked_by_this_checkpoint"] is False


def test_q25x_blocks_execution_write_lock_and_scheduler_requests() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint(
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
    assert packet["checkpoint_state"] == "single_producer_60s_disabled_dry_run_design_checkpoint_blocked"
    assert packet["ready_for_future_disabled_dry_run_execution_gate_planning"] is False
    assert packet["requested_forbidden_flags"]
    assert packet["blocker_count"] == len(packet["requested_forbidden_flags"])
    assert all(str(item).startswith("forbidden_request_in_ps_q25x:") for item in packet["blocked_reasons"])
    assert packet["execute_dry_run_enabled"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["would_send_to_broker"] is False
