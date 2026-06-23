# path: ./tools/test_phase4a_prediction_system_ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.py
# desc: Unit tests for PS-Q18O latest_prediction_summary_widget one-source handoff design checkpoint.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint import CHECKER_VERSION, ONE_SOURCE_HANDOFF_DESIGN_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_handoff_design_checkpoint import ONE_SOURCE_HANDOFF_DESIGN_ACK, build_latest_prediction_summary_widget_one_source_handoff_design_checkpoint_packet


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_one_source_handoff_design_checkpoint_only", "one_source_handoff_design_checkpoint_ready", "one_source_candidate_declared", "source_candidate_count_fixed_to_one", "explicit_design_ack_matched"):
        assert report[key] is True, key
    for key in (
        "warroom_page_mutation_allowed",
        "real_source_handoff_invoked",
        "source_artifact_resolution_allowed",
        "source_artifact_resolved",
        "source_artifact_path_materialized",
        "source_artifact_exists_checked",
        "source_artifact_schema_checked",
        "actual_source_read_allowed",
        "actual_source_read_invoked",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "q18n_validation_invoked_by_mount",
        "q18m_validation_invoked_by_mount",
        "q18j_validation_invoked_by_mount",
        "component_packet_builder_invoked_by_mount",
        "streamlit_render_invoked",
        "real_prediction_widget_rendering_allowed",
        "refresh_invocation_allowed",
        "runtime_artifact_write_allowed",
        "parameter_apply_allowed",
        "broker_private_api_allowed",
    ):
        assert report[key] is False, key


def test_ps_q18o_validates_one_source_handoff_design_from_q18n_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["one_source_handoff_design_check_version"] == ONE_SOURCE_HANDOFF_DESIGN_CHECK_VERSION
    assert report["one_source_handoff_design_ack"] == ONE_SOURCE_HANDOFF_DESIGN_ACK
    assert report["source_q18n_report_valid"] is True
    assert report["design_packet_valid"] is True
    assert report["design_row_count"] == 8
    assert report["source_candidate_count"] == 1
    assert report["handoff_candidate_ready"] is True
    assert report["selected_candidate_generated_at"] == "2026-06-22T00:00:00Z"
    assert report["selected_candidate_source_artifact_ref"] == "fixture://ps_q18i/latest_prediction.json"
    assert report["selected_candidate_market_uid"] == "BTC-USD"
    _assert_safe(report)


def test_ps_q18o_packet_without_source_is_design_only_but_candidate_not_ready() -> None:
    packet = build_latest_prediction_summary_widget_one_source_handoff_design_checkpoint_packet()
    assert packet["ok"] is True
    assert packet["design_row_count"] == 8
    assert packet["source_candidate_count"] == 1
    assert packet["one_source_handoff_design_ack"] == ONE_SOURCE_HANDOFF_DESIGN_ACK
    assert packet["supplied_handoff_preflight_report"] is False
    assert packet["handoff_candidate_ready"] is False
    assert packet["source_artifact_resolution_allowed"] is False
    assert packet["actual_source_read_invoked"] is False
    assert packet["d_hot_actual_read_allowed"] is False


def test_ps_q18o_blocks_missing_q18n_source() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert blocked["design_row_count"] == 0
    assert blocked["source_q18n_report_valid"] is False
    assert blocked["actual_source_read_invoked"] is False


def test_ps_q18o_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "latest_prediction_summary_widget_one_source_handoff_design_checkpoint_before_resolution_read_render_refresh_and_writes"
    assert printed["recommended_next_slice"].startswith("PS-Q18P")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
