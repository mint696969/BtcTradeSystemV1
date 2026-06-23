# path: ./tools/test_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.py
# desc: Unit tests for PS-Q17X WarRoom prediction widget disabled section page-body review mount.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount import CHECKER_VERSION, PAGE_BODY_REVIEW_MOUNT_VERSION, build_report, main


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "page_body_review_mount_applied", "disabled_section_page_body_review_mount_enabled", "visible_review_rows_rendered", "streamlit_review_render_allowed"):
        assert report[key] is True, key
    for key in (
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


def test_ps_q17x_validates_page_body_review_mount_from_q17w_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["page_body_review_mount_version"] == PAGE_BODY_REVIEW_MOUNT_VERSION
    assert report["source_q17w_report_valid"] is True
    assert report["review_row_count"] == 12
    assert report["review_zone_count"] == 3
    assert report["page_validation_failures"] == []
    assert report["review_folded_section_title"] == "Prediction WarRoom disabled widget skeleton review"
    _assert_safe(report)


def test_ps_q17x_keeps_real_widget_render_source_refresh_and_writes_disabled() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["visible_review_rows_rendered"] is True
    assert report["streamlit_review_render_allowed"] is True
    assert report["real_prediction_widget_rendering_allowed"] is False
    assert report["warroom_widget_rendering_allowed"] is False
    assert report["actual_source_read_allowed"] is False
    assert report["d_hot_actual_read_allowed"] is False
    assert report["refresh_invocation_allowed"] is False
    assert report["runtime_artifact_write_allowed"] is False
    assert report["status_artifact_write_allowed"] is False
    assert report["parameter_apply_allowed"] is False
    _assert_safe(report)


def test_ps_q17x_blocks_missing_q17w_source() -> None:
    blocked = build_report(page_text="")
    assert blocked["ok"] is False
    assert "q17w_checker_version_mismatch" in blocked["source_q17w_validation_failures"]
    assert blocked["page_validation_failures"] == []


def test_ps_q17x_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "warroom_prediction_widget_disabled_section_page_body_review_mount_before_visible_widget_rendering_and_actual_source_read"
    assert printed["recommended_next_slice"].startswith("PS-Q17Y")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
