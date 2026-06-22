# path: ./tools/test_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval.py
# desc: Unit tests for PS-Q16R stop checkpoint before approval.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q16r_stop_checkpoint_before_approval import CHECKER_VERSION, build_report, main
from check_phase4a_prediction_system_ps_q16q_final_non_executing_operator_handoff_checkpoint import build_report as build_q16q_report


def _assert_never_executes(report: dict) -> None:
    for key in (
        "stop_checkpoint_only",
        "human_review_gate_only",
        "approval_slice_required_before_any_execution",
        "no_approval_granted",
        "no_hot_data_read",
        "no_runtime_write",
        "no_status_write",
        "no_ledger_append",
        "no_lock_io",
        "no_refresh_invocation",
        "no_scheduler_or_ui_trigger",
    ):
        assert report[key] is True, key
    for key in (
        "ready_for_execution_enablement",
        "approval_or_authorization_allowed",
        "cli_enabled",
        "implementation_enabled",
        "execution_enabled",
        "manual_refresh_invoked",
        "latest_prediction_refresh_performed",
        "status_artifact_write_performed",
        "runtime_artifact_write_performed",
        "lock_file_created",
        "lock_file_deleted",
        "scheduler_enabled",
        "os_scheduler_registration_performed",
        "scheduled_loop_enabled",
        "enablement_command_generated",
        "warroom_ui_trigger_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        assert report[key] is False, key


def test_ps_q16r_ready_stop_checkpoint_without_approval_or_execution() -> None:
    report = build_report()
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["q16q_report_ok"] is True
    assert report["q16q_ready_for_human_review_checkpoint"] is True
    assert report["ready_for_stop_checkpoint_review"] is True
    _assert_never_executes(report)


def test_ps_q16r_blocks_missing_human_or_failed_q16q_report() -> None:
    missing = build_report(human_stop_checkpoint_record_present=False)
    assert missing["ok"] is False
    assert "human_stop_checkpoint_record_required_for_ps_q16r" in missing["blocked_reasons"]
    failed_q16q = build_q16q_report(request_execute_cli=True)
    report = build_report(supplied_q16q_report=failed_q16q)
    assert report["ok"] is False
    assert "q16q_report_not_ok" in report["blocked_reasons"]
    _assert_never_executes(missing)
    _assert_never_executes(report)


def test_ps_q16r_blocks_q16q_safety_boundary_regression() -> None:
    q16q = build_q16q_report()
    q16q["approval_or_authorization_allowed"] = True
    report = build_report(supplied_q16q_report=q16q)
    assert report["ok"] is False
    assert "q16q_report_approval_or_authorization_allowed_must_remain_false" in report["blocked_reasons"]
    _assert_never_executes(report)


def test_ps_q16r_rejects_approval_execution_write_lock_requests_and_main(capsys) -> None:
    report = build_report(request_approval=True, request_execute_cli=True, request_lock_file_create=True, request_ledger_append=True)
    assert report["ok"] is False
    assert "forbidden_request_in_ps_q16r:request_approval" in report["blocked_reasons"]
    assert "forbidden_request_in_ps_q16r:request_execute_cli" in report["blocked_reasons"]
    assert "forbidden_request_in_ps_q16r:request_lock_file_create" in report["blocked_reasons"]
    assert "forbidden_request_in_ps_q16r:request_ledger_append" in report["blocked_reasons"]
    _assert_never_executes(report)
    assert main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["stop_checkpoint_only"] is True
