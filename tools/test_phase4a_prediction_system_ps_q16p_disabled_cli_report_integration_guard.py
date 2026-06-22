# path: ./tools/test_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard.py
# desc: Unit tests for PS-Q16P disabled CLI report integration guard.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard import CHECKER_VERSION, build_report, main
from check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool import build_report as build_q16o_report


def _assert_never_executes(report: dict) -> None:
    for key in (
        "dry_run_report_integration_only",
        "operator_handoff_summary_only",
        "no_hot_data_read",
        "no_runtime_write",
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
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        assert report[key] is False, key


def test_ps_q16p_ready_integrates_q16o_report_without_execution() -> None:
    report = build_report()
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["q16o_report_ok"] is True
    assert report["q16o_decision_state"] == "disabled_operator_shell_once_run_cli_skeleton_ready_for_future_dry_run_wrapper"
    assert report["ready_for_future_operator_handoff_summary_slice"] is True
    _assert_never_executes(report)


def test_ps_q16p_blocks_missing_handoff_record_or_failed_q16o_report() -> None:
    missing = build_report(human_handoff_record_present=False)
    assert missing["ok"] is False
    assert "human_handoff_record_required_for_ps_q16p" in missing["blocked_reasons"]
    failed_q16o = build_q16o_report(request_execute_cli=True)
    report = build_report(supplied_q16o_report=failed_q16o)
    assert report["ok"] is False
    assert "q16o_report_not_ok" in report["blocked_reasons"]
    _assert_never_executes(missing)
    _assert_never_executes(report)


def test_ps_q16p_blocks_q16o_safety_boundary_regression() -> None:
    q16o = build_q16o_report()
    q16o["decision"]["lock_file_created_by_this_cli_skeleton"] = True
    report = build_report(supplied_q16o_report=q16o)
    assert report["ok"] is False
    assert "q16o_decision_lock_file_created_by_this_cli_skeleton_must_remain_false" in report["blocked_reasons"]
    _assert_never_executes(report)


def test_ps_q16p_rejects_forbidden_requests_and_main_prints_json(capsys) -> None:
    report = build_report(request_execute_cli=True, request_lock_file_create=True, request_status_artifact_write=True)
    assert report["ok"] is False
    assert "forbidden_request_in_ps_q16p:request_execute_cli" in report["blocked_reasons"]
    assert "forbidden_request_in_ps_q16p:request_lock_file_create" in report["blocked_reasons"]
    assert "forbidden_request_in_ps_q16p:request_status_artifact_write" in report["blocked_reasons"]
    _assert_never_executes(report)
    assert main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["operator_handoff_summary_only"] is True
