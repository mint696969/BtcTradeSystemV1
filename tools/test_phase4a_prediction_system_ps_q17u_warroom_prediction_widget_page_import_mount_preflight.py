# path: ./tools/test_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight.py
# desc: Unit tests for PS-Q17U WarRoom prediction widget page import/mount implementation preflight.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight import CHECKER_VERSION, PAGE_IMPORT_MOUNT_PREFLIGHT_VERSION, WARROOM_PAGE_TARGET, WIDGET_FAMILY_ORDER, build_report, main


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "page_import_mount_preflight_only", "preflight_only", "diagnostic_only", "warroom_widget_design_premise"):
        assert report[key] is True, key
    for key in (
        "warroom_page_patch_allowed",
        "warroom_page_import_patch_allowed",
        "warroom_page_mutation_allowed",
        "warroom_mount_patch_allowed",
        "component_import_allowed_by_warroom_page",
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
        "would_write_warroom_page",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
    ):
        assert report[key] is False, key


def test_ps_q17u_builds_patch_fragments_from_q17t_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["page_import_mount_preflight_version"] == PAGE_IMPORT_MOUNT_PREFLIGHT_VERSION
    assert report["target_page_path"] == WARROOM_PAGE_TARGET
    assert report["future_import_line_count"] == 12
    assert report["future_mount_invocation_count"] == 12
    assert report["preflight_patch_fragment_count"] == 3
    assert report["page_patch_preflight_ready"] is True
    assert report["widget_family_order"] == list(WIDGET_FAMILY_ORDER)
    assert any("render_latest_prediction_summary_widget" in line for line in report["future_import_block"])
    assert report["future_section_stub"][0].startswith("def _render_prediction_warroom_prediction_widgets_skeleton_section")
    _assert_safe(report)


def test_ps_q17u_invocation_rows_stay_disabled() -> None:
    report = build_report(use_observed_fixture=True)
    rows = {row["widget_family_id"]: row for row in report["mount_invocation_rows"]}
    assert rows["latest_prediction_summary_widget"]["mount_zone_id"] == "prediction_overview_zone"
    assert rows["prediction_delta_widget"]["mount_zone_id"] == "prediction_realtime_review_zone"
    assert rows["parameter_candidate_comparison_widget"]["mount_zone_id"] == "prediction_operator_support_zone"
    for row in report["mount_invocation_rows"]:
        assert row["page_patch_preflight_only"] is True
        assert row["page_import_patch_allowed"] is False
        assert row["page_body_call_patch_allowed"] is False
        assert row["warroom_mount_patch_allowed"] is False
        assert row["streamlit_render_allowed"] is False
        assert row["actual_source_read_allowed"] is False
        assert row["refresh_invocation_allowed"] is False
    _assert_safe(report)


def test_ps_q17u_blocks_missing_q17t_source() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert "q17t_checker_version_mismatch" in blocked["source_q17t_validation_failures"]
    assert blocked["future_import_block"] == []
    assert blocked["mount_invocation_rows"] == []
    assert blocked["page_patch_preflight_ready"] is False
    _assert_safe(blocked)


def test_ps_q17u_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "warroom_prediction_widget_page_import_mount_preflight_before_warroom_page_patch_and_rendering"
    assert printed["recommended_next_slice"].startswith("PS-Q17V")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)
