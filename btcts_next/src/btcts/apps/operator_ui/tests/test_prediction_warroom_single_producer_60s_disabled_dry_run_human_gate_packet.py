# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet.py
# desc: Verify PS-Q25Y dry-run human gate packet remains gate-marker-only and never grants execution.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet import (  # noqa: E402
    DRY_RUN_HUMAN_GATE_TOKEN,
    SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_HUMAN_GATE_PACKET_VERSION,
    build_prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet,
)


def _assert_never_executed(packet: dict) -> None:
    assert packet["gate_marker_only"] is True
    assert packet["decision_packet_only"] is True
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["human_gate_granted_by_this_packet"] is False
    assert packet["execute_dry_run_allowed_by_this_packet"] is False
    for key in (
        "execute_dry_run_enabled",
        "manual_one_shot_run_invoked_by_this_gate",
        "future_dry_run_invoked_by_this_gate",
        "status_artifact_write_performed_by_this_gate",
        "runtime_artifact_write_performed_by_this_gate",
        "prediction_artifact_write_performed_by_this_gate",
        "latest_manifest_written",
        "run_sidecars_written",
        "lock_file_created_by_this_gate",
        "lock_file_deleted_by_this_gate",
        "scheduler_enabled",
        "producer_enabled",
        "warroom_ui_trigger_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "mode_apply_allowed",
        "parameter_apply_allowed",
        "would_send_to_broker",
    ):
        assert packet[key] is False, key


def test_q25y_default_gate_packet_awaits_human_and_is_non_executing() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet().to_dict()
    assert packet["gate_version"] == SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_HUMAN_GATE_PACKET_VERSION
    assert packet["gate_state"] == "awaiting_human_dry_run_gate_decision"
    assert packet["selected_option_id"] == "single_producer_60s_candidate"
    assert packet["selected_target_cadence_sec"] == 60
    assert packet["q25x_checkpoint_packet_supplied"] is True
    assert packet["q25x_checkpoint_ready"] is True
    assert packet["gate_token_candidate"] == DRY_RUN_HUMAN_GATE_TOKEN
    assert packet["gate_token_detected"] is False
    assert packet["human_gate_required_before_any_dry_run"] is True
    assert packet["separate_execution_slice_required"] is True
    assert packet["ready_for_future_disabled_manual_dry_run_gate_decision"] is True
    _assert_never_executed(packet)


def test_q25y_token_intent_still_does_not_grant_execution() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet(
        supplied_gate_token=DRY_RUN_HUMAN_GATE_TOKEN
    ).to_dict()
    assert packet["gate_state"] == "human_gate_intent_detected_separate_execution_slice_required"
    assert packet["gate_token_detected"] is True
    assert "gate_token_detected_but_execution_requires_separate_future_slice" in packet["blocked_reasons"]
    assert packet["ready_for_future_disabled_manual_dry_run_gate_decision"] is True
    _assert_never_executed(packet)


def test_q25y_blocks_execution_write_lock_and_scheduler_requests() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet(
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
    assert packet["gate_state"] == "disabled_dry_run_human_gate_packet_blocked"
    assert packet["requested_forbidden_flags"]
    assert packet["blocker_count"] == len(packet["requested_forbidden_flags"])
    assert all(str(item).startswith("forbidden_request_in_ps_q25y:") for item in packet["blocked_reasons"])
    _assert_never_executed(packet)
