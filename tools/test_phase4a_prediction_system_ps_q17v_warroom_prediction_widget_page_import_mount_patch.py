# path: ./tools/test_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.py
# desc: Unit tests for PS-Q17V WarRoom prediction widget page import/mount patch.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch import CHECKER_VERSION, PAGE_IMPORT_MOUNT_PATCH_VERSION, WIDGET_FAMILY_ORDER, build_report, main


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "warroom_page_patch_applied", "warroom_page_import_patch_applied", "disabled_section_defined_only"):
        assert report[key] is True, key
    for key in (
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


def test_ps_q17v_validates_page_imports_and_disabled_section_from_q17u_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["page_import_mount_patch_version"] == PAGE_IMPORT_MOUNT_PATCH_VERSION
    assert report["imported_widget_count"] == 12
    assert report["imported_widget_family_ids"] == list(WIDGET_FAMILY_ORDER)
    assert report["disabled_section_defined"] is True
    assert report["disabled_section_call_count"] == 1
    assert report["packet_builder_call_count"] == 2
    assert report["page_validation_failures"] == []
    _assert_safe(report)


def test_ps_q17v_keeps_page_body_call_and_rendering_disabled() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["page_body_call_enabled"] is False
    assert report["future_section_call_enabled"] is False
    assert report["streamlit_render_allowed"] is False
    assert report["warroom_widget_rendering_allowed"] is False
    assert report["actual_source_read_allowed"] is False
    assert report["d_hot_actual_read_allowed"] is False
    assert report["refresh_invocation_allowed"] is False
    _assert_safe(report)


def test_ps_q17v_blocks_missing_q17u_source() -> None:
    blocked = build_report(page_text="")
    assert blocked["ok"] is False
    assert "q17u_checker_version_mismatch" in blocked["source_q17u_validation_failures"]
    assert blocked["imported_widget_count"] == 0
    assert blocked["disabled_section_defined"] is False


def test_ps_q17v_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "warroom_prediction_widget_page_import_mount_patch_imports_and_disabled_section_before_render_enablement"
    assert printed["recommended_next_slice"].startswith("PS-Q17W")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
