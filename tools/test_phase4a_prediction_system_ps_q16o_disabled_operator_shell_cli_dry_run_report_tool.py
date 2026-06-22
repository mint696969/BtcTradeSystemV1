# path: ./tools/test_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool.py
# desc: Unit tests for PS-Q16O disabled operator-shell CLI dry-run report tool.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool import (
    CHECKER_VERSION,
    build_report,
    main,
)


def _assert_report_never_executes(report: dict) -> None:
    assert report["dry_run_report_only"] is True
    assert report["no_hot_data_read"] is True
    assert report["no_runtime_write"] is True
    assert report["no_lock_io"] is True
    assert report["no_refresh_invocation"] is True
    decision = report["decision"]
    for key in (
        "cli_enabled",
        "implementation_enabled",
        "execution_enabled",
        "manual_refresh_invoked_by_this_cli_skeleton",
        "latest_prediction_refresh_performed_by_this_cli_skeleton",
        "status_artifact_write_performed_by_this_cli_skeleton",
        "runtime_artifact_write_performed_by_this_cli_skeleton",
        "lock_file_created_by_this_cli_skeleton",
        "lock_file_deleted_by_this_cli_skeleton",
        "scheduler_enabled",
        "os_scheduler_registration_performed",
        "scheduled_loop_enabled",
        "warroom_ui_trigger_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        assert decision[key] is False, key


def test_ps_q16o_build_report_ok_prints_q16n_decision_only() -> None:
    report = build_report()
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["stage"] == "disabled_operator_shell_cli_dry_run_report_only"
    assert report["decision"]["cli_skeleton_state"] == "disabled_operator_shell_once_run_cli_skeleton_ready_for_future_dry_run_wrapper"
    assert report["decision"]["ready_for_future_disabled_operator_shell_dry_run_cli_slice"] is True
    _assert_report_never_executes(report)


def test_ps_q16o_blocks_missing_human_or_unready_skeleton_without_execution() -> None:
    missing = build_report(human_cli_skeleton_record_present=False)
    assert missing["ok"] is False
    assert "human_cli_skeleton_record_required_for_ps_q16n" in missing["blocked_reasons"]
    unready = build_report(simulate_unready_ps_q16m_skeleton=True)
    assert unready["ok"] is False
    assert "ps_q16m_implementation_skeleton_not_ready_for_cli_skeleton" in unready["blocked_reasons"]
    _assert_report_never_executes(missing)
    _assert_report_never_executes(unready)


def test_ps_q16o_rejects_forbidden_execution_write_lock_requests() -> None:
    report = build_report(
        request_enable_cli=True,
        request_execute_cli=True,
        request_execute_once_run=True,
        request_status_artifact_write=True,
        request_lock_file_create=True,
        request_scheduler_enable=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    )
    assert report["ok"] is False
    assert "forbidden_request_in_ps_q16n:request_enable_cli" in report["blocked_reasons"]
    assert "forbidden_request_in_ps_q16n:request_execute_cli" in report["blocked_reasons"]
    assert "forbidden_request_in_ps_q16n:request_lock_file_create" in report["blocked_reasons"]
    _assert_report_never_executes(report)


def test_ps_q16o_main_prints_json_and_returns_zero_only_when_ok(capsys) -> None:
    assert main([]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["dry_run_report_only"] is True
    assert main(["--request-execute-cli"]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    assert "forbidden_request_in_ps_q16n:request_execute_cli" in blocked["blocked_reasons"]
