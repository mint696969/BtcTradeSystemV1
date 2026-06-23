# path: ./tools/test_phase4a_prediction_system_ps_q18f_latest_prediction_summary_widget_props_candidate_status_row_mount.py
# desc: Unit tests for PS-Q18F latest_prediction_summary_widget props candidate status row mount.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18f_latest_prediction_summary_widget_props_candidate_status_row_mount import CHECKER_VERSION, PROPS_CANDIDATE_STATUS_ROW_MOUNT_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_props_candidate_status_panel import build_latest_prediction_summary_widget_props_candidate_status_packet


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_props_candidate_status_row_mount_only", "warroom_status_rows_ready", "props_preflight_report_display_only", "props_candidate_status_display_only"):
        assert report[key] is True, key
    assert report["warroom_page_mutation_allowed"] is True
    for key in (
        "component_props_binding_allowed",
        "component_props_bound_by_mount",
        "widget_props_binding_allowed",
        "widget_props_bound_to_component",
        "render_invocation_allowed",
        "real_prediction_widget_rendering_allowed",
        "actual_source_read_invoked_by_mount",
        "actual_source_read_allowed_by_mount",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "warroom_widget_rendering_allowed",
        "warroom_ui_trigger_enabled",
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


def test_ps_q18f_validates_props_candidate_status_row_mount_from_q18e_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["props_candidate_status_row_mount_version"] == PROPS_CANDIDATE_STATUS_ROW_MOUNT_VERSION
    assert report["source_q18e_report_valid"] is True
    assert report["status_packet_valid"] is True
    assert report["page_status_packet_valid"] is True
    assert report["status_row_count"] == 8
    assert report["page_status_row_count"] == 8
    assert report["page_validation_failures"] == []
    _assert_safe(report)


def test_ps_q18f_page_safe_status_packet_does_not_bind_or_render() -> None:
    packet = build_latest_prediction_summary_widget_props_candidate_status_packet()
    assert packet["ok"] is True
    assert packet["status_row_count"] == 8
    assert packet["supplied_props_preflight_report"] is False
    assert packet["observed_props_candidate_ready"] is False
    assert packet["component_props_bound_by_mount"] is False
    assert packet["widget_props_bound_to_component"] is False
    assert packet["render_invocation_allowed"] is False
    assert packet["actual_source_read_invoked_by_mount"] is False


def test_ps_q18f_blocks_missing_q18e_source() -> None:
    blocked = build_report(page_text="")
    assert blocked["ok"] is False
    assert blocked["status_row_count"] == 0
    assert blocked["source_q18e_report_valid"] is False
    assert blocked["component_props_bound_by_mount"] is False


def test_ps_q18f_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "latest_prediction_summary_widget_props_candidate_status_row_mount_before_component_binding_rendering_refresh_and_writes"
    assert printed["recommended_next_slice"].startswith("PS-Q18G")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
