# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_disabled_once_run_checker.py
# desc: Unit tests for PS-Q16I disabled once-run checker.

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from btcts.apps.operator_ui.components.prediction_warroom_disabled_once_run_checker import (
    DISABLED_ONCE_RUN_CHECKER_VERSION,
    build_prediction_warroom_disabled_once_run_checker,
)
from btcts.apps.operator_ui.components.prediction_warroom_disabled_scheduler_wrapper_skeleton import (
    DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION,
)


def _skeleton() -> dict:
    return {
        "skeleton_version": DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION,
        "ready_for_future_disabled_operator_shell_wrapper_implementation": True,
        "wrapper_enabled": False,
        "scheduler_enabled": False,
        "os_scheduler_registration_performed": False,
        "scheduled_loop_enabled": False,
        "enablement_command_generated": False,
    }


def _preflight(age: int = 60, ok: bool = True) -> dict:
    return {
        "ok": ok,
        "preflight_passed": ok,
        "ready_for_scheduler_enablement": False,
        "latest_prediction": {"age_sec": age},
    }


def _status() -> dict:
    return {"status_ready": True, "last_success_at": "2026-06-22T12:00:00Z"}


def _assert_never_enabled(packet: dict) -> None:
    for key in (
        "wrapper_enabled",
        "scheduler_enabled",
        "os_scheduler_registration_performed",
        "scheduled_loop_enabled",
        "enablement_command_generated",
        "manual_refresh_invoked_by_this_checker",
        "latest_prediction_refresh_performed_by_this_checker",
        "status_artifact_write_performed_by_this_checker",
        "lock_file_created_by_this_checker",
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
    assert packet["checker_only"] is True
    assert packet["read_only"] is True
    assert packet["non_executing"] is True


def test_ps_q16i_ready_no_lock_without_execution() -> None:
    packet = build_prediction_warroom_disabled_once_run_checker(
        ps_q16h_wrapper_skeleton_packet=_skeleton(),
        ps_q16f_preflight_report=_preflight(),
        supplied_lock_observation={"lock_present": False},
        supplied_status_observation=_status(),
    ).to_dict()
    assert packet["checker_version"] == DISABLED_ONCE_RUN_CHECKER_VERSION
    assert packet["checker_state"] == "once_run_checker_disabled_ready_no_lock"
    assert packet["simulated_decision"] == "ready_no_lock_no_execution"
    assert packet["ready_for_future_disabled_once_run_checker_implementation"] is True
    _assert_never_enabled(packet)


def test_ps_q16i_simulates_skip_when_lock_present() -> None:
    packet = build_prediction_warroom_disabled_once_run_checker(
        ps_q16h_wrapper_skeleton_packet=_skeleton(),
        ps_q16f_preflight_report=_preflight(),
        supplied_lock_observation={"lock_present": True, "lock_reason": "operator_shell_existing_lock"},
        supplied_status_observation=_status(),
    ).to_dict()
    assert packet["checker_state"] == "once_run_checker_disabled_skip_existing_lock"
    assert packet["simulated_decision"] == "skip_existing_lock"
    assert packet["would_skip_due_to_existing_lock"] is True
    _assert_never_enabled(packet)


def test_ps_q16i_blocks_failed_or_stale_preflight() -> None:
    failed = build_prediction_warroom_disabled_once_run_checker(
        ps_q16h_wrapper_skeleton_packet=_skeleton(),
        ps_q16f_preflight_report=_preflight(ok=False),
        supplied_lock_observation={"lock_present": False},
        supplied_status_observation=_status(),
    ).to_dict()
    assert "ps_q16f_preflight_not_passed" in failed["blocked_reasons"]
    _assert_never_enabled(failed)
    stale = build_prediction_warroom_disabled_once_run_checker(
        ps_q16h_wrapper_skeleton_packet=_skeleton(),
        ps_q16f_preflight_report=_preflight(age=4000),
        supplied_lock_observation={"lock_present": False},
        supplied_status_observation=_status(),
    ).to_dict()
    assert "ps_q16f_latest_prediction_stale" in stale["blocked_reasons"]
    _assert_never_enabled(stale)


def test_ps_q16i_rejects_execution_or_enablement_requests() -> None:
    packet = build_prediction_warroom_disabled_once_run_checker(
        ps_q16h_wrapper_skeleton_packet=_skeleton(),
        ps_q16f_preflight_report=_preflight(),
        supplied_lock_observation={"lock_present": False},
        supplied_status_observation=_status(),
        request_enable_wrapper=True,
        request_scheduler_enable=True,
        request_execute_manual_refresh=True,
        request_latest_prediction_refresh=True,
        request_status_artifact_write=True,
        request_lock_file_create=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    assert packet["checker_state"] == "once_run_checker_disabled_blocked"
    assert "forbidden_request_in_ps_q16i:request_execute_manual_refresh" in packet["blocked_reasons"]
    assert "forbidden_request_in_ps_q16i:request_lock_file_create" in packet["blocked_reasons"]
    assert packet["ready_for_future_disabled_once_run_checker_implementation"] is False
    _assert_never_enabled(packet)
