# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_single_producer_60s_disabled_validation_packet.py
# desc: Verify PS-Q25V disabled validation packet compares Q25U skeleton with Q16B default runner without runtime writes or enablement.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.prediction_warroom_single_producer_60s_disabled_validation_packet import (  # noqa: E402
    SINGLE_PRODUCER_60S_DISABLED_VALIDATION_PACKET_VERSION,
    build_prediction_warroom_single_producer_60s_disabled_validation_packet,
)


def test_q25v_validation_ready_and_non_executing() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_validation_packet().to_dict()
    assert packet["validation_version"] == SINGLE_PRODUCER_60S_DISABLED_VALIDATION_PACKET_VERSION
    assert packet["validation_state"] == "single_producer_60s_disabled_validation_ready"
    assert packet["selected_option_id"] == "single_producer_60s_candidate"
    assert packet["selected_target_cadence_sec"] == 60
    assert packet["ready_for_disabled_dry_run_planning"] is True
    assert packet["validation_only"] is True
    assert packet["read_only"] is True
    assert packet["non_executing"] is True
    assert packet["manual_one_shot_run_invoked_by_this_validation"] is False
    assert packet["q16b_runner_invoked_for_actual_refresh"] is False
    assert packet["q16b_status_artifact_written"] is False
    assert packet["q16b_latest_prediction_artifact_written"] is False
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["runtime_artifact_write_enabled"] is False
    assert packet["status_artifact_write_enabled"] is False
    assert packet["prediction_artifact_write_enabled"] is False
    assert packet["latest_manifest_written"] is False
    assert packet["run_sidecars_written"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["autotrade_trigger_allowed"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["ledger_append_allowed"] is False
    assert packet["mode_apply_allowed"] is False
    assert packet["parameter_apply_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_q25v_embeds_disabled_skeleton_and_runner_packets() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_validation_packet().to_dict()
    skeleton = packet["q25u_skeleton_packet"]
    runner = packet["q16b_default_runner_packet"]
    assert skeleton["skeleton_version"] == packet["q25u_skeleton_version"]
    assert skeleton["ready_for_future_disabled_single_producer_60s_skeleton_validation"] is True
    assert runner["runner_version"] == packet["q16b_runner_version"]
    assert runner["producer_enabled"] is False
    assert runner["scheduler_enabled"] is False
    assert runner["status_artifact_written"] is False
    assert runner["latest_prediction_artifact_written"] is False


def test_q25v_blocks_forbidden_requests() -> None:
    packet = build_prediction_warroom_single_producer_60s_disabled_validation_packet(
        request_manual_one_shot_run=True,
        request_scheduler_enable=True,
        request_producer_enable=True,
        request_status_artifact_write=True,
        request_runtime_artifact_write=True,
        request_prediction_artifact_write=True,
        request_latest_manifest_write=True,
        request_warroom_ui_trigger=True,
        request_parameter_apply=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    assert packet["validation_state"] == "single_producer_60s_disabled_validation_blocked"
    assert packet["ready_for_disabled_dry_run_planning"] is False
    assert packet["requested_forbidden_flags"]
    assert packet["blocker_count"] == len(packet["requested_forbidden_flags"])
    assert all(str(item).startswith("forbidden_request_in_ps_q25v:") for item in packet["blocked_reasons"])
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["would_send_to_broker"] is False
