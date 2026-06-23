# path: ./tools/test_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount.py
# desc: Unit tests for PS-Q18M latest_prediction_summary_widget operator value summary mount.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount import CHECKER_VERSION, EXPECTED_COMPACT_LINE, OPERATOR_VALUE_SUMMARY_MOUNT_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_operator_value_summary_panel import build_latest_prediction_summary_widget_operator_value_summary_packet


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_operator_value_summary_mount_only", "warroom_operator_summary_rows_ready", "operator_summary_display_only", "mapped_payload_values_display_only"):
        assert report[key] is True, key
    assert report["warroom_page_mutation_allowed"] is True
    for key in (
        "q18j_validation_invoked_by_mount",
        "component_packet_builder_invoked_by_mount",
        "component_packet_builder_allowed_by_mount",
        "component_runtime_binding_allowed",
        "streamlit_render_allowed",
        "streamlit_render_invoked",
        "real_prediction_widget_rendering_allowed",
        "actual_source_read_invoked_by_mount",
        "actual_source_read_allowed_by_mount",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "refresh_invocation_allowed",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "parameter_apply_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
    ):
        assert report[key] is False, key


def test_ps_q18m_validates_operator_value_summary_from_q18j_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["operator_value_summary_mount_version"] == OPERATOR_VALUE_SUMMARY_MOUNT_VERSION
    assert report["source_q18j_report_valid"] is True
    assert report["summary_packet_valid"] is True
    assert report["page_summary_packet_valid"] is True
    assert report["summary_row_count"] == 7
    assert report["page_summary_row_count"] == 7
    assert report["values_supplied"] is True
    assert report["page_values_supplied"] is False
    assert report["compact_line_ready"] is True
    assert report["page_compact_line_ready"] is False
    assert report["compact_line"] == EXPECTED_COMPACT_LINE
    assert report["observed_mapped_prediction_run_id"] == "ps_q18i_fixture_run"
    assert report["observed_mapped_market_uid"] == "BTC-USD"
    assert report["observed_component_source_artifact_ref"] == "fixture://ps_q18i/latest_prediction.json"
    assert report["page_validation_failures"] == []
    _assert_safe(report)


def test_ps_q18m_page_safe_summary_packet_has_no_values_and_no_invocation() -> None:
    packet = build_latest_prediction_summary_widget_operator_value_summary_packet()
    assert packet["ok"] is True
    assert packet["summary_row_count"] == 7
    assert packet["supplied_validation_report"] is False
    assert packet["values_supplied"] is False
    assert packet["compact_line_ready"] is False
    assert packet["q18j_validation_invoked_by_mount"] is False
    assert packet["component_packet_builder_invoked_by_mount"] is False
    assert packet["streamlit_render_invoked"] is False
    assert packet["actual_source_read_invoked_by_mount"] is False


def test_ps_q18m_blocks_missing_q18j_source() -> None:
    blocked = build_report(page_text="")
    assert blocked["ok"] is False
    assert blocked["summary_row_count"] == 0
    assert blocked["source_q18j_report_valid"] is False
    assert blocked["q18j_validation_invoked_by_mount"] is False


def test_ps_q18m_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "latest_prediction_summary_widget_operator_value_summary_mount_before_real_rendering_refresh_and_writes"
    assert printed["recommended_next_slice"].startswith("PS-Q18N")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
