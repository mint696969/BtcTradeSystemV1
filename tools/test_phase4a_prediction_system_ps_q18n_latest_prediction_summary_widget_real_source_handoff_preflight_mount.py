# path: ./tools/test_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.py
# desc: Unit tests for PS-Q18N latest_prediction_summary_widget real-source handoff preflight mount.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount import CHECKER_VERSION, REAL_SOURCE_HANDOFF_PREFLIGHT_MOUNT_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel import build_latest_prediction_summary_widget_real_source_handoff_preflight_packet


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_real_source_handoff_preflight_mount_only", "warroom_handoff_preflight_rows_ready", "operator_summary_report_display_only", "real_source_handoff_preflight_only"):
        assert report[key] is True, key
    assert report["warroom_page_mutation_allowed"] is True
    for key in (
        "real_source_handoff_invoked",
        "actual_source_resolution_allowed",
        "actual_source_resolved",
        "actual_source_read_allowed",
        "actual_source_read_invoked",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "q18j_validation_invoked_by_mount",
        "q18m_validation_invoked_by_mount",
        "component_packet_builder_invoked_by_mount",
        "streamlit_render_invoked",
        "real_prediction_widget_rendering_allowed",
        "refresh_invocation_allowed",
        "runtime_artifact_write_allowed",
        "parameter_apply_allowed",
        "broker_private_api_allowed",
    ):
        assert report[key] is False, key


def test_ps_q18n_validates_real_source_handoff_preflight_from_q18m_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["real_source_handoff_preflight_mount_version"] == REAL_SOURCE_HANDOFF_PREFLIGHT_MOUNT_VERSION
    assert report["source_q18m_report_valid"] is True
    assert report["handoff_packet_valid"] is True
    assert report["page_handoff_packet_valid"] is True
    assert report["handoff_row_count"] == 6
    assert report["page_handoff_row_count"] == 6
    assert report["handoff_candidate_ready"] is True
    assert report["page_handoff_candidate_ready"] is False
    assert report["candidate_generated_at"] == "2026-06-22T00:00:00Z"
    assert report["candidate_source_artifact_ref"] == "fixture://ps_q18i/latest_prediction.json"
    assert report["candidate_market_uid"] == "BTC-USD"
    assert report["page_validation_failures"] == []
    _assert_safe(report)


def test_ps_q18n_page_safe_packet_has_no_candidate_and_no_resolution_or_read() -> None:
    packet = build_latest_prediction_summary_widget_real_source_handoff_preflight_packet()
    assert packet["ok"] is True
    assert packet["handoff_row_count"] == 6
    assert packet["supplied_operator_summary_report"] is False
    assert packet["handoff_candidate_ready"] is False
    assert packet["real_source_handoff_invoked"] is False
    assert packet["actual_source_resolution_allowed"] is False
    assert packet["actual_source_read_invoked"] is False
    assert packet["d_hot_actual_read_allowed"] is False


def test_ps_q18n_blocks_missing_q18m_source() -> None:
    blocked = build_report(page_text="")
    assert blocked["ok"] is False
    assert blocked["handoff_row_count"] == 0
    assert blocked["source_q18m_report_valid"] is False
    assert blocked["actual_source_read_invoked"] is False


def test_ps_q18n_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "latest_prediction_summary_widget_real_source_handoff_preflight_mount_before_resolution_read_render_refresh_and_writes"
    assert printed["recommended_next_slice"].startswith("PS-Q18O")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
