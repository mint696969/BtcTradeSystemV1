# path: ./tools/test_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract.py
# desc: Unit tests for PS-Q17Q WarRoom prediction widget mount contract.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract import CHECKER_VERSION, MOUNT_ZONE_ORDER, WIDGET_FAMILY_ORDER, build_report, main


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "mount_contract_only", "contract_only", "diagnostic_only", "warroom_widget_design_premise", "fallback_display_only"):
        assert report[key] is True, key
    for key in (
        "warroom_widget_implementation_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_page_import_patch_allowed",
        "warroom_mount_patch_allowed",
        "component_import_allowed",
        "streamlit_render_allowed",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "d_hot_actual_read_allowed",
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


def test_ps_q17q_builds_mount_contract_from_q17p_fixture() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["mount_row_count"] == 12
    assert report["mount_zone_count"] == 3
    assert report["widget_family_order"] == list(WIDGET_FAMILY_ORDER)
    assert report["mount_zone_order"] == list(MOUNT_ZONE_ORDER)
    rows = {row["widget_family_id"]: row for row in report["mount_rows"]}
    assert rows["latest_prediction_summary_widget"]["mount_zone_id"] == "prediction_overview_zone"
    assert rows["prediction_delta_widget"]["mount_zone_id"] == "prediction_realtime_review_zone"
    assert rows["parameter_candidate_comparison_widget"]["mount_zone_id"] == "prediction_operator_support_zone"
    assert rows["replay_outcome_calibration_widget"]["source_packet_id"] == "replay_outcome_calibration_review_packet"
    assert report["fallback_display_required_count"] == 12
    _assert_safe(report)


def test_ps_q17q_keeps_import_render_and_page_patch_false() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["component_import_blockers"] == list(WIDGET_FAMILY_ORDER)
    assert report["streamlit_render_blockers"] == list(WIDGET_FAMILY_ORDER)
    assert report["page_mutation_blockers"] == list(WIDGET_FAMILY_ORDER)
    for row in report["mount_rows"]:
        assert row["mount_contract_state"] == "ready_for_future_mount_contract_render_disabled"
        assert row["component_import_allowed"] is False
        assert row["streamlit_render_allowed"] is False
        assert row["page_mutation_allowed"] is False
        assert row["warroom_mount_patch_allowed"] is False
        assert row["refresh_invocation_allowed"] is False
        assert row["fallback_display_required"] is True
        assert row["next_validation"].endswith("_mount_contract_guard")
    for zone in report["mount_zone_rows"]:
        assert zone["component_import_allowed"] is False
        assert zone["streamlit_render_allowed"] is False
        assert zone["page_mutation_allowed"] is False
        assert zone["warroom_mount_patch_allowed"] is False
    _assert_safe(report)


def test_ps_q17q_blocks_missing_q17p_source() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert "q17p_checker_version_mismatch" in blocked["source_q17p_validation_failures"]
    assert blocked["mount_rows"] == []
    assert blocked["mount_zone_rows"] == []
    _assert_safe(blocked)


def test_ps_q17q_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "warroom_prediction_widget_mount_contract_before_ui_import_page_patch_and_rendering"
    assert printed["recommended_next_slice"].startswith("PS-Q17R")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)
