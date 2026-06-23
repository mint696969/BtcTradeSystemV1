# path: ./tools/test_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract.py
# desc: Unit tests for PS-Q17R WarRoom prediction widget read-only component skeleton contract.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract import CHECKER_VERSION, COMPONENT_SKELETON_CONTRACT_VERSION, REQUIRED_COMPONENT_PROPS, WIDGET_FAMILY_ORDER, build_report, main


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "component_skeleton_contract_only", "contract_only", "diagnostic_only", "warroom_widget_design_premise", "fallback_component_only"):
        assert report[key] is True, key
    for key in (
        "component_file_creation_allowed",
        "component_import_allowed",
        "streamlit_render_allowed",
        "warroom_widget_implementation_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_page_import_patch_allowed",
        "warroom_mount_patch_allowed",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "d_hot_actual_read_allowed",
        "actual_source_read_allowed",
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


def test_ps_q17r_builds_component_skeleton_contract_from_q17q_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["component_skeleton_contract_version"] == COMPONENT_SKELETON_CONTRACT_VERSION
    assert report["component_row_count"] == 12
    assert report["fallback_component_required_count"] == 12
    assert report["widget_family_order"] == list(WIDGET_FAMILY_ORDER)
    rows = {row["widget_family_id"]: row for row in report["component_rows"]}
    latest = rows["latest_prediction_summary_widget"]
    assert latest["component_module_path"].endswith("prediction_widgets.latest_prediction_summary_widget")
    assert latest["component_function_name"] == "render_latest_prediction_summary_widget"
    assert latest["props_contract_fields"] == list(REQUIRED_COMPONENT_PROPS)
    assert rows["prediction_delta_widget"]["mount_zone_id"] == "prediction_realtime_review_zone"
    assert rows["parameter_candidate_comparison_widget"]["source_packet_id"] == "parameter_candidate_evidence_review_packet"
    _assert_safe(report)


def test_ps_q17r_keeps_component_file_import_render_and_actual_read_false() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["component_file_creation_blockers"] == list(WIDGET_FAMILY_ORDER)
    assert report["component_import_blockers"] == list(WIDGET_FAMILY_ORDER)
    assert report["streamlit_render_blockers"] == list(WIDGET_FAMILY_ORDER)
    assert report["actual_source_read_blockers"] == list(WIDGET_FAMILY_ORDER)
    for row in report["component_rows"]:
        assert row["component_contract_state"] == "ready_for_future_read_only_component_skeleton_render_disabled"
        assert row["fallback_component_required"] is True
        assert row["component_file_creation_allowed"] is False
        assert row["component_import_allowed"] is False
        assert row["streamlit_render_allowed"] is False
        assert row["page_mutation_allowed"] is False
        assert row["actual_source_read_allowed"] is False
        assert row["next_validation"].endswith("_component_skeleton_contract_guard")
    _assert_safe(report)


def test_ps_q17r_blocks_missing_q17q_source() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert "q17q_checker_version_mismatch" in blocked["source_q17q_validation_failures"]
    assert blocked["component_rows"] == []
    _assert_safe(blocked)


def test_ps_q17r_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "warroom_prediction_widget_read_only_component_skeleton_contract_before_component_file_creation_import_and_rendering"
    assert printed["recommended_next_slice"].startswith("PS-Q17S")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)
