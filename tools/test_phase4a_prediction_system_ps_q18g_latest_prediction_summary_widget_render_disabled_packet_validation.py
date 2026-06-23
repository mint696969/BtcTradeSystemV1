# path: ./tools/test_phase4a_prediction_system_ps_q18g_latest_prediction_summary_widget_render_disabled_packet_validation.py
# desc: Unit tests for PS-Q18G latest_prediction_summary_widget render-disabled component packet validation.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18g_latest_prediction_summary_widget_render_disabled_packet_validation import CHECKER_VERSION, LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_VALIDATION_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_render_disabled_packet_validation import build_latest_prediction_summary_widget_render_disabled_packet_validation


def _assert_safe(report: dict) -> None:
    for key in (
        "read_only",
        "non_executing",
        "latest_prediction_summary_widget_render_disabled_packet_validation_only",
        "render_disabled_component_packet_validation_only",
        "component_skeleton_packet_only",
        "props_candidate_supplied_to_packet_builder",
        "props_value_binding_deferred",
    ):
        assert report[key] is True, key
    for key in (
        "real_payload_values_bound",
        "streamlit_render_allowed",
        "streamlit_render_invoked",
        "real_prediction_widget_rendering_allowed",
        "component_runtime_binding_allowed",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_ui_trigger_enabled",
        "actual_source_read_invoked_by_validation",
        "actual_source_read_allowed_by_validation",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "confidence_increase_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
    ):
        assert report[key] is False, key


def test_ps_q18g_validates_render_disabled_component_packet_from_q18e_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["latest_prediction_summary_widget_render_disabled_packet_validation_check_version"] == LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_VALIDATION_CHECK_VERSION
    assert report["source_q18e_report_valid"] is True
    assert report["validation_packet_valid"] is True
    assert report["component_packet_builder_invoked"] is True
    assert report["component_packet_valid"] is True
    assert report["component_packet_state"] == "read_only_component_skeleton_render_disabled"
    assert report["component_missing_props"] == []
    assert report["component_source_generated_at"] == "schema_verified_value_not_bound"
    assert report["component_source_artifact_ref"] == "schema_verified_value_not_bound"
    _assert_safe(report)


def test_ps_q18g_component_validation_blocks_missing_candidate() -> None:
    blocked = build_latest_prediction_summary_widget_render_disabled_packet_validation()
    assert blocked["ok"] is False
    assert blocked["component_packet_builder_invoked"] is False
    assert blocked["component_packet_valid"] is False
    assert blocked["streamlit_render_invoked"] is False
    assert blocked["actual_source_read_invoked_by_validation"] is False


def test_ps_q18g_blocks_without_q18e_source() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert blocked["source_q18e_report_valid"] is False
    assert blocked["component_packet_builder_invoked"] is False
    assert blocked["streamlit_render_invoked"] is False


def test_ps_q18g_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "latest_prediction_summary_widget_render_disabled_component_packet_validation_before_real_rendering_refresh_and_writes"
    assert printed["recommended_next_slice"].startswith("PS-Q18H")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
