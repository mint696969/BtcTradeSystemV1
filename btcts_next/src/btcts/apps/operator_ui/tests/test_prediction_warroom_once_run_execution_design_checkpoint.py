# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_once_run_execution_design_checkpoint.py
# desc: Unit tests for PS-Q16K once-run execution design checkpoint.

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from btcts.apps.operator_ui.components.prediction_warroom_disabled_once_run_checker import DISABLED_ONCE_RUN_CHECKER_VERSION
from btcts.apps.operator_ui.components.prediction_warroom_once_run_execution_design_checkpoint import (
    ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION,
    build_prediction_warroom_once_run_execution_design_checkpoint,
)


def _dry_run(*, ok: bool = True, lock_present: bool = False, status_ready: bool = True, age: int = 1) -> dict:
    simulated = "ready_no_lock_no_execution" if ok and not lock_present else "skip_existing_lock" if lock_present else "blocked"
    blocker_count = 0 if ok else 1
    return {
        "ok": ok,
        "dry_run_only": True,
        "decision": {
            "checker_version": DISABLED_ONCE_RUN_CHECKER_VERSION,
            "checker_state": "once_run_checker_disabled_ready_no_lock" if simulated == "ready_no_lock_no_execution" else "once_run_checker_disabled_blocked",
            "simulated_decision": simulated,
            "blocker_count": blocker_count,
            "ready_for_future_disabled_once_run_checker_implementation": ok,
            "preflight_latest_age_sec": age,
            "lock_present": lock_present,
            "status_ready": status_ready,
            "manual_refresh_invoked_by_this_checker": False,
            "latest_prediction_refresh_performed_by_this_checker": False,
            "status_artifact_write_performed_by_this_checker": False,
            "lock_file_created_by_this_checker": False,
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
        },
        "lock_observation": {"lock_present": lock_present},
        "status_observation": {"status_ready": status_ready},
    }


def _assert_never_executed(packet: dict) -> None:
    for key in (
        "ready_for_execution_enablement",
        "execution_enabled",
        "manual_refresh_invoked_by_this_checkpoint",
        "latest_prediction_refresh_performed_by_this_checkpoint",
        "status_artifact_write_performed_by_this_checkpoint",
        "runtime_artifact_write_performed_by_this_checkpoint",
        "lock_file_created_by_this_checkpoint",
        "lock_file_deleted_by_this_checkpoint",
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
    assert packet["checkpoint_only"] is True
    assert packet["read_only"] is True
    assert packet["non_executing"] is True


def test_ps_q16k_ready_from_q16j_success_but_does_not_execute() -> None:
    packet = build_prediction_warroom_once_run_execution_design_checkpoint(
        ps_q16j_dry_run_report=_dry_run(),
        human_execution_design_record_present=True,
        human_execution_design_source="operator_confirmed_ps_q16j_success",
    ).to_dict()
    assert packet["checkpoint_version"] == ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION
    assert packet["checkpoint_state"] == "once_run_execution_design_checkpoint_ready_for_future_guarded_slice"
    assert packet["ready_for_future_guarded_once_run_execution_design_slice"] is True
    _assert_never_executed(packet)


def test_ps_q16k_requires_human_execution_design_record() -> None:
    packet = build_prediction_warroom_once_run_execution_design_checkpoint(
        ps_q16j_dry_run_report=_dry_run(),
    ).to_dict()
    assert packet["checkpoint_state"] == "once_run_execution_design_checkpoint_blocked"
    assert "human_execution_design_record_required_for_ps_q16k" in packet["blocked_reasons"]
    _assert_never_executed(packet)


def test_ps_q16k_blocks_lock_present_or_stale_dry_run() -> None:
    locked = build_prediction_warroom_once_run_execution_design_checkpoint(
        ps_q16j_dry_run_report=_dry_run(lock_present=True),
        human_execution_design_record_present=True,
        human_execution_design_source="guard",
    ).to_dict()
    assert "ps_q16j_decision_not_ready_no_lock_no_execution" in locked["blocked_reasons"]
    assert "ps_q16j_lock_present_or_unconfirmed_absent" in locked["blocked_reasons"]
    _assert_never_executed(locked)
    stale = build_prediction_warroom_once_run_execution_design_checkpoint(
        ps_q16j_dry_run_report=_dry_run(age=4000),
        human_execution_design_record_present=True,
        human_execution_design_source="guard",
    ).to_dict()
    assert "ps_q16j_latest_age_stale" in stale["blocked_reasons"]
    _assert_never_executed(stale)


def test_ps_q16k_rejects_execution_or_write_requests() -> None:
    packet = build_prediction_warroom_once_run_execution_design_checkpoint(
        ps_q16j_dry_run_report=_dry_run(),
        human_execution_design_record_present=True,
        human_execution_design_source="guard",
        request_execute_manual_refresh=True,
        request_status_artifact_write=True,
        request_lock_file_create=True,
        request_scheduler_enable=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    assert packet["ready_for_future_guarded_once_run_execution_design_slice"] is False
    assert "forbidden_request_in_ps_q16k:request_execute_manual_refresh" in packet["blocked_reasons"]
    assert "forbidden_request_in_ps_q16k:request_lock_file_create" in packet["blocked_reasons"]
    _assert_never_executed(packet)
