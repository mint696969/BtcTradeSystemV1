# path: ./tools/test_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.py
# desc: Unit tests for PS-Q17W WarRoom prediction widget disabled section review panel.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel import CHECKER_VERSION, DISABLED_SECTION_REVIEW_PANEL_VERSION, WIDGET_FAMILY_ORDER, build_report, main


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "disabled_section_review_only", "pure_data_review_packet"):
        assert report[key] is True, key
    for key in (
        "warroom_page_mutation_allowed",
        "page_body_call_enabled",
        "future_section_call_enabled",
        "streamlit_render_allowed",
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


def test_ps_q17w_builds_disabled_section_review_packet_from_q17s_and_q17v_fixtures() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["disabled_section_review_panel_version"] == DISABLED_SECTION_REVIEW_PANEL_VERSION
    assert report["source_q17s_report_valid"] is True
    assert report["source_q17v_report_valid"] is True
    assert report["review_row_count"] == 12
    assert report["review_zone_count"] == 3
    packet = report["panel_packet"]
    assert packet["ok"] is True
    assert packet["review_row_count"] == 12
    assert [row["widget_family_id"] for row in packet["review_rows"]] == list(WIDGET_FAMILY_ORDER)
    _assert_safe(report)


def test_ps_q17w_review_rows_keep_render_source_refresh_and_write_disabled() -> None:
    report = build_report(use_observed_fixture=True)
    for row in report["panel_packet"]["review_rows"]:
        assert row["read_only"] is True
        assert row["non_executing"] is True
        assert row["component_skeleton_only"] is True
        assert row["streamlit_render_allowed"] is False
        assert row["actual_source_read_allowed"] is False
        assert row["refresh_invocation_allowed"] is False
        assert row["runtime_artifact_write_allowed"] is False
        assert row["status_artifact_write_allowed"] is False
        assert row["parameter_apply_allowed"] is False
        assert row["ledger_append_allowed"] is False
        assert row["autotrade_trigger_allowed"] is False
        assert row["broker_private_api_allowed"] is False
    _assert_safe(report)


def test_ps_q17w_blocks_missing_sources() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert blocked["panel_packet"] == {}
    assert blocked["review_row_count"] == 0
    _assert_safe(blocked)


def test_ps_q17w_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "warroom_prediction_widget_disabled_section_review_panel_before_page_body_call_and_visible_rendering"
    assert printed["recommended_next_slice"].startswith("PS-Q17X")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)
