# path: ./tools/test_phase4a_prediction_system_ps_q18s_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_gate.py
# desc: Unit tests for PS-Q18S latest_prediction_summary_widget one-source no-read existence-check execution gate.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import EXPECTED_PATH_SHAPE_PREVIEW
from check_phase4a_prediction_system_ps_q18s_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_gate import CHECKER_VERSION, ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_GATE_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_gate import EXISTENCE_EXECUTION_GATE_KIND, EXISTENCE_EXECUTION_GATE_STATE, ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_GATE_ACK, build_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_gate_packet


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_one_source_no_read_existence_check_execution_gate_only", "one_source_no_read_existence_check_execution_gate_ready", "existence_check_execution_gate_declared", "one_source_candidate_preserved", "source_candidate_count_fixed_to_one", "explicit_execution_gate_ack_matched", "path_shape_preview_string_only"):
        assert report[key] is True, key
    for key in ("existence_check_execution_gate_open", "warroom_page_mutation_allowed", "source_artifact_resolver_invoked", "source_artifact_resolution_allowed", "source_artifact_resolved", "source_artifact_path_materialized", "source_artifact_exists_check_allowed", "source_artifact_exists_checked", "source_artifact_exists_result_available", "source_artifact_schema_check_allowed", "source_artifact_schema_checked", "actual_source_read_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18r_validation_invoked_by_mount", "q18q_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        assert report[key] is False, key


def test_ps_q18s_validates_closed_execution_gate_from_q18r_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["one_source_no_read_existence_check_execution_gate_check_version"] == ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_GATE_CHECK_VERSION
    assert report["one_source_no_read_existence_check_execution_gate_ack"] == ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_GATE_ACK
    assert report["source_q18r_report_valid"] is True
    assert report["execution_gate_packet_valid"] is True
    assert report["execution_gate_row_count"] == 14
    assert report["source_candidate_count"] == 1
    assert report["execution_gate_candidate_ready"] is True
    assert report["existence_execution_gate_kind"] == EXISTENCE_EXECUTION_GATE_KIND
    assert report["existence_execution_gate_state"] == EXISTENCE_EXECUTION_GATE_STATE
    assert report["path_shape_preview"] == EXPECTED_PATH_SHAPE_PREVIEW
    assert report["selected_candidate_generated_at"] == "2026-06-22T00:00:00Z"
    assert report["selected_candidate_source_artifact_ref"] == "fixture://ps_q18i/latest_prediction.json"
    assert report["selected_candidate_market_uid"] == "BTC-USD"
    _assert_safe(report)


def test_ps_q18s_packet_without_source_is_gate_only_but_candidate_not_ready() -> None:
    packet = build_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_gate_packet()
    assert packet["ok"] is True
    assert packet["execution_gate_row_count"] == 14
    assert packet["source_candidate_count"] == 1
    assert packet["one_source_no_read_existence_check_execution_gate_ack"] == ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_GATE_ACK
    assert packet["supplied_existence_contract_report"] is False
    assert packet["execution_gate_candidate_ready"] is False
    assert packet["existence_check_execution_gate_open"] is False
    assert packet["source_artifact_exists_check_allowed"] is False
    assert packet["source_artifact_exists_checked"] is False
    assert packet["actual_source_read_invoked"] is False


def test_ps_q18s_blocks_missing_q18r_source() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert blocked["execution_gate_row_count"] == 0
    assert blocked["source_q18r_report_valid"] is False
    assert blocked["source_artifact_exists_checked"] is False
    assert blocked["actual_source_read_invoked"] is False


def test_ps_q18s_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "latest_prediction_summary_widget_one_source_no_read_existence_check_execution_gate_before_exists_schema_read_render_refresh_and_writes"
    assert printed["recommended_next_slice"].startswith("PS-Q18T")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
