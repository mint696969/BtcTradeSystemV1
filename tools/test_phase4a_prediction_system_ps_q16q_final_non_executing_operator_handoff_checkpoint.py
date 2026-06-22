# path: ./tools/test_phase4a_prediction_system_ps_q16q_final_non_executing_operator_handoff_checkpoint.py
# desc: Unit tests for PS-Q16Q final non-executing operator handoff checkpoint.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q16q_final_non_executing_operator_handoff_checkpoint import CHECKER_VERSION, build_report, main
from check_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard import build_report as build_q16p_report


def _assert_never_executes(report: dict) -> None:
    for key in (
        "final_handoff_checkpoint_only",
        "ledger_free_summary_only",
        "operator_review_summary_only",
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
        "approval_or_authorization_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        assert report[key] is False, key


def test_ps_q16q_ready_final_checkpoint_without_execution_or_ledger() -> None:
    report = build_report()
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["q16p_report_ok"] is True
    assert report["q16p_ready_for_future_operator_handoff_summary_slice"] is True
    assert report["ready_for_human_review_checkpoint"] is True
    _assert_never_executes(report)


def test_ps_q16q_blocks_missing_human_or_failed_q16p_report() -> None:
    missing = build_report(human_final_checkpoint_record_present=False)
    assert missing["ok"] is False
    assert "human_final_checkpoint_record_required_for_ps_q16q" in missing["blocked_reasons"]
    failed_q16p = build_q16p_report(request_execute_cli=True)
    report = build_report(supplied_q16p_report=failed_q16p)
    assert report["ok"] is False
    assert "q16p_report_not_ok" in report["blocked_reasons"]
    _assert_never_executes(missing)
    _assert_never_executes(report)


def test_ps_q16q_blocks_q16p_safety_boundary_regression() -> None:
    q16p = build_q16p_report()
    q16p["ledger_append_allowed"] = True
    report = build_report(supplied_q16p_report=q16p)
    assert report["ok"] is False
    assert "q16p_report_ledger_append_allowed_must_remain_false" in report["blocked_reasons"]
    _assert_never_executes(report)


def test_ps_q16q_rejects_forbidden_requests_and_main_prints_json(capsys) -> None:
    report = build_report(request_execute_cli=True, request_lock_file_create=True, request_ledger_append=True)
    assert report["ok"] is False
    assert "forbidden_request_in_ps_q16q:request_execute_cli" in report["blocked_reasons"]
    assert "forbidden_request_in_ps_q16q:request_lock_file_create" in report["blocked_reasons"]
    assert "forbidden_request_in_ps_q16q:request_ledger_append" in report["blocked_reasons"]
    _assert_never_executes(report)
    assert main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["ledger_free_summary_only"] is True
