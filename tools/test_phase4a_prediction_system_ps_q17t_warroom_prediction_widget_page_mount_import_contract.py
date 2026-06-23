# path: ./tools/test_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract.py
# desc: Unit tests for PS-Q17T WarRoom prediction widget page mount/import contract.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract import CHECKER_VERSION, PAGE_MOUNT_IMPORT_CONTRACT_VERSION, WARROOM_PAGE_TARGET, WIDGET_FAMILY_ORDER, build_report, main


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "page_mount_import_contract_only", "contract_only", "diagnostic_only", "warroom_widget_design_premise", "warroom_page_target_observed"):
        assert report[key] is True, key
    for key in (
        "warroom_page_import_patch_allowed",
        "warroom_page_mutation_allowed",
        "warroom_mount_patch_allowed",
        "component_import_allowed_by_warroom_page",
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


def test_ps_q17t_builds_page_import_and_mount_contract_from_q17s_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["page_mount_import_contract_version"] == PAGE_MOUNT_IMPORT_CONTRACT_VERSION
    assert report["target_page_path"] == WARROOM_PAGE_TARGET
    assert report["page_import_row_count"] == 12
    assert report["page_mount_row_count"] == 12
    assert report["page_zone_row_count"] == 3
    assert report["widget_family_order"] == list(WIDGET_FAMILY_ORDER)
    rows = {row["widget_family_id"]: row for row in report["page_mount_rows"]}
    assert rows["latest_prediction_summary_widget"]["mount_zone_id"] == "prediction_overview_zone"
    assert rows["prediction_delta_widget"]["mount_zone_id"] == "prediction_realtime_review_zone"
    assert rows["parameter_candidate_comparison_widget"]["mount_zone_id"] == "prediction_operator_support_zone"
    imports = {row["widget_family_id"]: row for row in report["page_import_rows"]}
    assert "render_latest_prediction_summary_widget" in imports["latest_prediction_summary_widget"]["future_import_statement"]
    _assert_safe(report)


def test_ps_q17t_keeps_page_patch_import_mount_and_render_disabled() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["page_import_patch_blockers"] == list(WIDGET_FAMILY_ORDER)
    assert report["warroom_mount_patch_blockers"] == list(WIDGET_FAMILY_ORDER)
    assert report["streamlit_render_blockers"] == list(WIDGET_FAMILY_ORDER)
    for row in report["page_import_rows"]:
        assert row["page_import_patch_allowed"] is False
        assert row["component_import_allowed_by_warroom_page"] is False
        assert row["import_contract_state"] == "future_import_contract_defined_patch_disabled"
    for row in report["page_mount_rows"]:
        assert row["page_import_patch_allowed"] is False
        assert row["warroom_page_mutation_allowed"] is False
        assert row["warroom_mount_patch_allowed"] is False
        assert row["streamlit_render_allowed"] is False
        assert row["actual_source_read_allowed"] is False
        assert row["refresh_invocation_allowed"] is False
    _assert_safe(report)


def test_ps_q17t_blocks_missing_q17s_source() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert "q17s_checker_version_mismatch" in blocked["source_q17s_validation_failures"]
    assert blocked["page_import_rows"] == []
    assert blocked["page_mount_rows"] == []
    _assert_safe(blocked)


def test_ps_q17t_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "warroom_prediction_widget_page_mount_import_contract_before_warroom_page_patch_and_rendering"
    assert printed["recommended_next_slice"].startswith("PS-Q17U")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)
