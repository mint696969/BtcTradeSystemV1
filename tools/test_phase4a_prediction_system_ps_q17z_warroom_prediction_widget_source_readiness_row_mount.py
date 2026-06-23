# path: ./tools/test_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount.py
# desc: Unit tests for PS-Q17Z WarRoom prediction widget source readiness row mount.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount import CHECKER_VERSION, SOURCE_READINESS_ROW_MOUNT_VERSION, build_report, main


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "source_readiness_row_mount_only", "source_binding_contract_ready", "readiness_row_visible_in_warroom", "streamlit_review_render_allowed"):
        assert report[key] is True, key
    for key in (
        "source_artifact_resolution_allowed",
        "actual_source_bound",
        "source_artifact_resolved",
        "freshness_checked_against_d_hot",
        "real_prediction_widget_rendering_allowed",
        "warroom_widget_rendering_allowed",
        "actual_source_read_allowed",
        "d_hot_actual_read_allowed",
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


def test_ps_q17z_validates_source_readiness_row_mount_from_q17y_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["source_readiness_row_mount_version"] == SOURCE_READINESS_ROW_MOUNT_VERSION
    assert report["source_q17y_report_valid"] is True
    assert report["panel_packet_valid"] is True
    assert report["readiness_row_count"] == 12
    assert report["unique_source_packet_count"] == 9
    assert report["page_validation_failures"] == []
    assert report["source_readiness_section_title"] == "Prediction WarRoom source readiness preflight"
    _assert_safe(report)


def test_ps_q17z_keeps_actual_source_resolution_read_render_refresh_and_writes_disabled() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["readiness_row_visible_in_warroom"] is True
    assert report["streamlit_review_render_allowed"] is True
    assert report["source_artifact_resolution_allowed"] is False
    assert report["actual_source_bound"] is False
    assert report["source_artifact_resolved"] is False
    assert report["freshness_checked_against_d_hot"] is False
    assert report["actual_source_read_allowed"] is False
    assert report["d_hot_actual_read_allowed"] is False
    assert report["real_prediction_widget_rendering_allowed"] is False
    assert report["refresh_invocation_allowed"] is False
    assert report["runtime_artifact_write_allowed"] is False
    assert report["parameter_apply_allowed"] is False
    _assert_safe(report)


def test_ps_q17z_blocks_missing_q17y_source() -> None:
    blocked = build_report(page_text="")
    assert blocked["ok"] is False
    assert blocked["readiness_row_count"] == 0
    assert blocked["source_q17y_report_valid"] is False


def test_ps_q17z_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "warroom_prediction_widget_source_readiness_row_mount_before_source_resolution_d_hot_read_and_real_widget_rendering"
    assert printed["recommended_next_slice"].startswith("PS-Q18A")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
