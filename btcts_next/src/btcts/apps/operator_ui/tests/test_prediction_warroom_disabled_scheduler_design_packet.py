# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_disabled_scheduler_design_packet.py
# desc: Unit tests for PS-Q16G disabled scheduler design packet.

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from btcts.apps.operator_ui.components.prediction_warroom_disabled_scheduler_design_packet import (
    DISABLED_SCHEDULER_DESIGN_PACKET_VERSION,
    build_prediction_warroom_disabled_scheduler_design_packet,
)


def _preflight() -> dict:
    return {
        "ok": True,
        "preflight_passed": True,
        "ready_for_scheduler_enablement": False,
        "scheduler_registration_performed": False,
        "scheduled_loop_enabled": False,
        "latest_prediction": {
            "prediction_run_id": "prediction_system.ps_q16g.test:BTC_JPY:bitFlyer:2026-06-22T12:00:00Z",
            "generated_at": "2026-06-22T12:00:00Z",
            "age_sec": 60,
        },
        "producer_status": {
            "producer_state": "manual_refresh_exported_status_written",
            "last_success_at": "2026-06-22T12:00:00Z",
            "last_success_generated_at": "2026-06-22T12:00:00Z",
            "last_prediction_run_id": "prediction_system.ps_q16g.test:BTC_JPY:bitFlyer:2026-06-22T12:00:00Z",
        },
        "warning_reasons": ["latest_prediction_source_has_warnings:6"],
    }


def _assert_never_enabled(packet: dict) -> None:
    for key in (
        "ready_for_scheduler_enablement",
        "ready_for_runtime_artifact_write_automation",
        "scheduler_enablement_command_generated",
        "scheduler_registration_performed",
        "scheduled_loop_enabled",
        "runtime_artifact_write_automation_enabled",
        "latest_prediction_refresh_performed_by_this_design",
        "status_artifact_write_performed_by_this_design",
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
    assert packet["design_only"] is True
    assert packet["read_only"] is True
    assert packet["non_executing"] is True


def test_ps_q16g_blocks_without_human_decision_record() -> None:
    packet = build_prediction_warroom_disabled_scheduler_design_packet(ps_q16f_preflight_report=_preflight()).to_dict()
    assert packet["design_version"] == DISABLED_SCHEDULER_DESIGN_PACKET_VERSION
    assert packet["design_state"] == "disabled_scheduler_design_blocked"
    assert "human_decision_record_required_for_ps_q16g_design" in packet["blocked_reasons"]
    assert packet["ready_for_disabled_scheduler_wrapper_slice"] is False
    _assert_never_enabled(packet)


def test_ps_q16g_ready_for_future_disabled_wrapper_slice_with_human_decision_only() -> None:
    packet = build_prediction_warroom_disabled_scheduler_design_packet(
        ps_q16f_preflight_report=_preflight(),
        human_decision_record_present=True,
        human_decision_source="operator_chat_next_go_2026_06_22",
    ).to_dict()
    assert packet["design_state"] == "disabled_scheduler_design_ready_for_future_wrapper_slice"
    assert packet["ready_for_disabled_scheduler_wrapper_slice"] is True
    assert packet["ready_for_scheduler_enablement"] is False
    assert packet["scheduler_registration_performed"] is False
    assert packet["scheduled_loop_enabled"] is False
    assert packet["latest_prediction_run_id"].startswith("prediction_system.ps_q16g.test")
    assert "future_slice_must_start_disabled_by_default" in packet["runbook_steps"]
    _assert_never_enabled(packet)


def test_ps_q16g_rejects_forbidden_enablement_requests() -> None:
    packet = build_prediction_warroom_disabled_scheduler_design_packet(
        ps_q16f_preflight_report=_preflight(),
        human_decision_record_present=True,
        human_decision_source="operator_chat_next_go_2026_06_22",
        request_scheduler_enable=True,
        request_scheduled_loop_enable=True,
        request_runtime_artifact_write_automation_enable=True,
        request_generate_enablement_command=True,
        request_warroom_ui_trigger=True,
        request_parameter_apply=True,
        request_parameter_staging_write=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    assert packet["design_state"] == "disabled_scheduler_design_blocked"
    assert "forbidden_request_in_ps_q16g:request_scheduler_enable" in packet["blocked_reasons"]
    assert "forbidden_request_in_ps_q16g:request_generate_enablement_command" in packet["blocked_reasons"]
    assert packet["ready_for_disabled_scheduler_wrapper_slice"] is False
    _assert_never_enabled(packet)


def test_ps_q16g_blocks_failed_or_stale_preflight() -> None:
    failed = _preflight()
    failed["ok"] = False
    failed["preflight_passed"] = False
    packet = build_prediction_warroom_disabled_scheduler_design_packet(
        ps_q16f_preflight_report=failed,
        human_decision_record_present=True,
        human_decision_source="operator_chat_next_go_2026_06_22",
    ).to_dict()
    assert "ps_q16f_preflight_not_passed" in packet["blocked_reasons"]

    stale = _preflight()
    stale["latest_prediction"]["age_sec"] = 4000
    packet = build_prediction_warroom_disabled_scheduler_design_packet(
        ps_q16f_preflight_report=stale,
        human_decision_record_present=True,
        human_decision_source="operator_chat_next_go_2026_06_22",
    ).to_dict()
    assert "latest_prediction_too_stale_for_disabled_scheduler_design" in packet["blocked_reasons"]
    _assert_never_enabled(packet)
