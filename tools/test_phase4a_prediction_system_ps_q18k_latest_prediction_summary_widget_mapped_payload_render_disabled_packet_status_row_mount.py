# path: ./tools/test_phase4a_prediction_system_ps_q18k_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount.py
# desc: Unit tests for PS-Q18K latest_prediction_summary_widget mapped-payload render-disabled packet status row mount.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q18k_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount import CHECKER_VERSION, MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_STATUS_ROW_MOUNT_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_panel import build_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_packet


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount_only", "warroom_status_rows_ready", "validation_report_display_only", "mapped_payload_render_disabled_packet_status_display_only"):
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


def test_ps_q18k_validates_mapped_payload_packet_status_row_mount_from_q18j_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["mapped_payload_render_disabled_packet_status_row_mount_version"] == MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_STATUS_ROW_MOUNT_VERSION
    assert report["source_q18j_report_valid"] is True
    assert report["status_packet_valid"] is True
    assert report["page_status_packet_valid"] is True
    assert report["status_row_count"] == 12
    assert report["page_status_row_count"] == 12
    assert report["page_validation_failures"] == []
    assert report["observed_component_packet_builder_invoked"] is True
    assert report["observed_component_packet_valid"] is True
    assert report["observed_component_packet_state"] == "read_only_component_skeleton_render_disabled"
    assert report["observed_component_missing_props"] == []
    assert report["observed_component_source_generated_at"] == "2026-06-22T00:00:00Z"
    assert report["observed_component_source_artifact_ref"] == "fixture://ps_q18i/latest_prediction.json"
    _assert_safe(report)


def test_ps_q18k_page_safe_status_packet_does_not_invoke_validation_or_builder() -> None:
    packet = build_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_packet()
    assert packet["ok"] is True
    assert packet["status_row_count"] == 12
    assert packet["supplied_validation_report"] is False
    assert packet["observed_component_packet_builder_invoked"] is False
    assert packet["q18j_validation_invoked_by_mount"] is False
    assert packet["component_packet_builder_invoked_by_mount"] is False
    assert packet["streamlit_render_invoked"] is False
    assert packet["actual_source_read_invoked_by_mount"] is False


def test_ps_q18k_blocks_missing_q18j_source() -> None:
    blocked = build_report(page_text="")
    assert blocked["ok"] is False
    assert blocked["status_row_count"] == 0
    assert blocked["source_q18j_report_valid"] is False
    assert blocked["q18j_validation_invoked_by_mount"] is False


def test_ps_q18k_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount_before_real_rendering_refresh_and_writes"
    assert printed["recommended_next_slice"].startswith("PS-Q18L")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
