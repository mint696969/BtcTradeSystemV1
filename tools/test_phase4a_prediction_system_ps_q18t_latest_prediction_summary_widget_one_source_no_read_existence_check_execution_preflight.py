# path: ./tools/test_phase4a_prediction_system_ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.py
# desc: Unit tests for PS-Q18T latest_prediction_summary_widget one-source no-read existence-check execution preflight.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import EXPECTED_PATH_SHAPE_PREVIEW
from check_phase4a_prediction_system_ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight import CHECKER_VERSION, ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight import EXISTENCE_EXECUTION_PREFLIGHT_KIND, EXISTENCE_EXECUTION_PREFLIGHT_STATE, ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ACK, build_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_packet


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_only", "one_source_no_read_existence_check_execution_preflight_ready", "existence_check_execution_preflight_declared", "one_source_candidate_preserved", "source_candidate_count_fixed_to_one", "explicit_execution_preflight_ack_matched", "path_shape_preview_string_only"):
        assert report[key] is True, key
    for key in ("existence_check_execution_preflight_would_open_gate", "warroom_page_mutation_allowed", "source_artifact_resolver_invoked", "source_artifact_resolution_allowed", "source_artifact_resolved", "source_artifact_path_materialized", "source_artifact_exists_check_allowed", "source_artifact_exists_checked", "source_artifact_exists_result_available", "source_artifact_schema_check_allowed", "source_artifact_schema_checked", "actual_source_read_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18s_validation_invoked_by_mount", "q18r_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        assert report[key] is False, key


def test_ps_q18t_validates_execution_preflight_from_q18s_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["one_source_no_read_existence_check_execution_preflight_check_version"] == ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_CHECK_VERSION
    assert report["one_source_no_read_existence_check_execution_preflight_ack"] == ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ACK
    assert report["source_q18s_report_valid"] is True
    assert report["execution_preflight_packet_valid"] is True
    assert report["execution_preflight_row_count"] == 14
    assert report["source_candidate_count"] == 1
    assert report["execution_preflight_candidate_ready"] is True
    assert report["existence_execution_preflight_kind"] == EXISTENCE_EXECUTION_PREFLIGHT_KIND
    assert report["existence_execution_preflight_state"] == EXISTENCE_EXECUTION_PREFLIGHT_STATE
    assert report["existence_check_execution_preflight_would_open_gate"] is False
    assert report["path_shape_preview"] == EXPECTED_PATH_SHAPE_PREVIEW
    assert report["selected_candidate_generated_at"] == "2026-06-22T00:00:00Z"
    assert report["selected_candidate_source_artifact_ref"] == "fixture://ps_q18i/latest_prediction.json"
    assert report["selected_candidate_market_uid"] == "BTC-USD"
    _assert_safe(report)


def test_ps_q18t_packet_without_source_is_preflight_only_but_candidate_not_ready() -> None:
    packet = build_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_packet()
    assert packet["ok"] is True
    assert packet["execution_preflight_row_count"] == 14
    assert packet["source_candidate_count"] == 1
    assert packet["one_source_no_read_existence_check_execution_preflight_ack"] == ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ACK
    assert packet["supplied_execution_gate_report"] is False
    assert packet["execution_preflight_candidate_ready"] is False
    assert packet["existence_check_execution_preflight_would_open_gate"] is False
    assert packet["source_artifact_exists_check_allowed"] is False
    assert packet["source_artifact_exists_checked"] is False
    assert packet["actual_source_read_invoked"] is False


def test_ps_q18t_blocks_missing_q18s_source() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert blocked["execution_preflight_row_count"] == 0
    assert blocked["source_q18s_report_valid"] is False
    assert blocked["source_artifact_exists_checked"] is False
    assert blocked["actual_source_read_invoked"] is False


def test_ps_q18t_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_before_gate_open_exists_schema_read_render_refresh_and_writes"
    assert printed["recommended_next_slice"].startswith("PS-Q18U")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
