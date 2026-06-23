# path: ./tools/test_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation.py
# desc: Unit tests for PS-Q17S WarRoom prediction widget read-only component skeleton implementation.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation import CHECKER_VERSION, COMPONENT_SKELETON_IMPLEMENTATION_VERSION, WIDGET_FAMILY_ORDER, build_report, main


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "component_skeleton_implementation", "component_files_created", "diagnostic_only", "warroom_widget_design_premise"):
        assert report[key] is True, key
    assert report["contract_only"] is False
    for key in (
        "component_import_allowed_by_warroom_page",
        "streamlit_render_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_page_import_patch_allowed",
        "warroom_mount_patch_allowed",
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


def test_ps_q17s_imports_and_calls_all_component_skeleton_modules_from_q17r_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["component_skeleton_implementation_version"] == COMPONENT_SKELETON_IMPLEMENTATION_VERSION
    assert report["component_module_count"] == 12
    assert report["component_packet_count"] == 12
    assert report["component_module_validation_failures"] == []
    assert report["widget_family_order"] == list(WIDGET_FAMILY_ORDER)
    packets = {packet["widget_family_id"]: packet for packet in report["component_packets"]}
    assert packets["latest_prediction_summary_widget"]["component_function_name"] == "render_latest_prediction_summary_widget"
    assert packets["prediction_delta_widget"]["mount_zone_id"] == "prediction_realtime_review_zone"
    assert packets["parameter_candidate_comparison_widget"]["source_packet_id"] == "parameter_candidate_evidence_review_packet"
    _assert_safe(report)


def test_ps_q17s_component_packets_stay_render_disabled_and_read_only() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["streamlit_render_blockers"] == list(WIDGET_FAMILY_ORDER)
    assert report["warroom_page_import_blockers"] == list(WIDGET_FAMILY_ORDER)
    assert report["actual_source_read_blockers"] == list(WIDGET_FAMILY_ORDER)
    for packet in report["component_packets"]:
        assert packet["component_state"] == "read_only_component_skeleton_render_disabled"
        assert packet["read_only"] is True
        assert packet["non_executing"] is True
        assert packet["component_skeleton_only"] is True
        assert packet["fallback_component_only"] is True
        assert packet["streamlit_render_allowed"] is False
        assert packet["streamlit_render_invoked"] is False
        assert packet["warroom_page_import_patch_allowed"] is False
        assert packet["warroom_page_mutation_allowed"] is False
        assert packet["actual_source_read_allowed"] is False
        assert packet["actual_source_read_attempted"] is False
        assert packet["d_hot_actual_read_allowed"] is False
        assert packet["refresh_invocation_allowed"] is False
    _assert_safe(report)


def test_ps_q17s_blocks_missing_q17r_source() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert "q17r_checker_version_mismatch" in blocked["source_q17r_validation_failures"]
    assert blocked["component_packets"] == []
    assert blocked["component_files_created"] is False
    assert blocked["streamlit_render_allowed"] is False


def test_ps_q17s_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "warroom_prediction_widget_read_only_component_skeleton_implementation_before_warroom_import_mount_and_rendering"
    assert printed["recommended_next_slice"].startswith("PS-Q17T")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
