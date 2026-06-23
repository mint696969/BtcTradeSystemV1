# path: ./tools/test_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.py
# desc: Unit tests for PS-Q18Y latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run result display contract.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import EXPECTED_PATH_SHAPE_PREVIEW
from check_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract import CHECKER_VERSION, ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract import FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_KIND, FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_STATE, ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ACK, build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_packet


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_only", "one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_ready", "filesystem_existence_check_dry_run_result_display_contract_declared", "filesystem_existence_check_dry_run_result_placeholder_preserved", "one_source_candidate_preserved", "source_candidate_count_fixed_to_one", "explicit_dry_run_result_display_contract_ack_matched", "path_shape_preview_string_only"):
        assert report[key] is True, key
    for key in ("filesystem_existence_check_dry_run_result_available", "filesystem_existence_check_dry_run_result_display_mount_allowed", "filesystem_existence_check_dry_run_result_display_mounted", "filesystem_existence_check_dry_run_execution_allowed", "filesystem_existence_check_dry_run_executed", "warroom_page_mutation_allowed", "source_artifact_exists_checked", "source_artifact_exists_result_available", "actual_source_read_invoked", "streamlit_render_allowed", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "runtime_artifact_write_allowed", "broker_private_api_allowed"):
        assert report[key] is False, key


def test_ps_q18y_validates_result_display_contract_from_q18x_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_check_version"] == ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_CHECK_VERSION
    assert report["one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_ack"] == ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ACK
    assert report["source_q18x_report_valid"] is True
    assert report["dry_run_result_display_contract_packet_valid"] is True
    assert report["dry_run_result_display_contract_row_count"] == 14
    assert report["source_candidate_count"] == 1
    assert report["dry_run_result_display_contract_candidate_ready"] is True
    assert report["filesystem_existence_check_dry_run_result_display_contract_kind"] == FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_KIND
    assert report["filesystem_existence_check_dry_run_result_display_contract_state"] == FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_STATE
    assert report["filesystem_existence_check_dry_run_result_available"] is False
    assert report["filesystem_existence_check_dry_run_result_display_mount_allowed"] is False
    assert report["streamlit_render_invoked"] is False
    assert report["path_shape_preview"] == EXPECTED_PATH_SHAPE_PREVIEW
    assert report["selected_candidate_generated_at"] == "2026-06-22T00:00:00Z"
    assert report["selected_candidate_source_artifact_ref"] == "fixture://ps_q18i/latest_prediction.json"
    assert report["selected_candidate_market_uid"] == "BTC-USD"
    _assert_safe(report)


def test_ps_q18y_packet_without_source_is_display_contract_only_but_candidate_not_ready() -> None:
    packet = build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_packet()
    assert packet["ok"] is True
    assert packet["dry_run_result_display_contract_row_count"] == 14
    assert packet["source_candidate_count"] == 1
    assert packet["one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_ack"] == ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ACK
    assert packet["supplied_result_placeholder_report"] is False
    assert packet["dry_run_result_display_contract_candidate_ready"] is False
    assert packet["filesystem_existence_check_dry_run_result_available"] is False
    assert packet["filesystem_existence_check_dry_run_result_display_mount_allowed"] is False
    assert packet["source_artifact_exists_checked"] is False
    assert packet["actual_source_read_invoked"] is False


def test_ps_q18y_blocks_missing_q18x_source() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert blocked["dry_run_result_display_contract_row_count"] == 0
    assert blocked["source_q18x_report_valid"] is False
    assert blocked["filesystem_existence_check_dry_run_result_available"] is False
    assert blocked["filesystem_existence_check_dry_run_result_display_mount_allowed"] is False
    assert blocked["streamlit_render_invoked"] is False
    assert blocked["actual_source_read_invoked"] is False


def test_ps_q18y_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_before_mount_render_exists_result_schema_read_refresh_and_writes"
    assert printed["recommended_next_slice"].startswith("PS-Q18Z")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
