# path: ./tools/test_phase4a_prediction_system_ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet.py
# desc: Unit tests for PS-Q18Z latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run result display packet.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import EXPECTED_PATH_SHAPE_PREVIEW
from check_phase4a_prediction_system_ps_q18z_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_packet import CHECKER_VERSION, build_report, main
from btcts.apps.operator_ui.prediction_warroom.contracts.latest_prediction_summary_widget_q18z_display_packet import (
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_ACK,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_KIND,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_STATE,
    TRUE_BOUNDARIES,
)
from btcts.apps.operator_ui.prediction_warroom.presenters.latest_prediction_summary_widget_q18z_display_rows import build_latest_prediction_summary_widget_q18z_display_packet


def _assert_safe(report: dict) -> None:
    for key in TRUE_BOUNDARIES:
        assert report[key] is True, key
    for key in FALSE_BOUNDARIES:
        assert report[key] is False, key


def test_ps_q18z_validates_display_packet_from_q18y_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["source_q18y_report_valid"] is True
    assert report["display_packet_valid"] is True
    assert report["display_packet_ack"] == LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_ACK
    assert report["display_packet_kind"] == LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_KIND
    assert report["display_packet_state"] == LATEST_PREDICTION_SUMMARY_WIDGET_Q18Z_DISPLAY_PACKET_STATE
    assert report["display_packet_row_count"] == 12
    assert report["source_candidate_count"] == 1
    assert report["path_shape_preview"] == EXPECTED_PATH_SHAPE_PREVIEW
    assert report["selected_candidate_generated_at"] == "2026-06-22T00:00:00Z"
    assert report["selected_candidate_source_artifact_ref"] == "fixture://ps_q18i/latest_prediction.json"
    assert report["selected_candidate_market_uid"] == "BTC-USD"
    _assert_safe(report)


def test_ps_q18z_packet_without_source_is_blocked_and_has_no_rows() -> None:
    packet = build_latest_prediction_summary_widget_q18z_display_packet()
    assert packet["ok"] is False
    assert packet["display_packet_ready"] is False
    assert packet["display_packet_row_count"] == 0
    assert "missing_q18y_display_contract_report" in packet["display_packet_validation_failures"]
    assert packet["source_artifact_exists_checked"] is False
    assert packet["actual_source_read_invoked"] is False
    assert packet["streamlit_render_invoked"] is False


def test_ps_q18z_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"].endswith("before_mount_render_exists_result_schema_read_refresh_and_writes")
    assert printed["recommended_next_slice"].startswith("WarRoom mount preflight/gate")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    assert blocked["display_packet_row_count"] == 0
