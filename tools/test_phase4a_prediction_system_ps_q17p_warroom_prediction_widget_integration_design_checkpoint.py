# path: ./tools/test_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint.py
# desc: Unit tests for PS-Q17P WarRoom prediction widget integration design checkpoint.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint import CHECKER_VERSION, SOURCE_CHECKER_VERSIONS, WIDGET_FAMILY_ORDER, build_report, main


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "design_checkpoint_only", "contract_only", "diagnostic_only", "warroom_widget_design_premise"):
        assert report[key] is True, key
    for key in (
        "warroom_widget_implementation_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_mount_patch_allowed",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "d_hot_actual_read_allowed",
        "confidence_increase_allowed",
        "signal_reliability_claim_allowed",
        "parameter_candidate_reliability_claim_allowed",
        "parameter_tuning_allowed",
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


def test_ps_q17p_maps_verified_packets_to_all_widget_families() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["widget_family_order"] == list(WIDGET_FAMILY_ORDER)
    assert report["widget_family_count"] == 12
    assert report["verified_source_packet_count"] == 9
    rows = {row["widget_family_id"]: row for row in report["integration_rows"]}
    assert rows["source_quality_freshness_widget"]["source_packet_id"] == "tier0_source_quality_gate_packet"
    assert rows["signal_strength_calibration_widget"]["source_packet_id"] == "calibration_reference_packet"
    assert rows["prediction_delta_widget"]["source_packet_id"] == "prediction_delta_review_packet"
    assert rows["scenario_trace_widget"]["source_packet_id"] == "scenario_trace_semantic_mapping_review_packet"
    assert rows["parameter_candidate_comparison_widget"]["source_packet_id"] == "parameter_candidate_evidence_review_packet"
    assert rows["replay_outcome_calibration_widget"]["source_packet_id"] == "replay_outcome_calibration_review_packet"
    assert rows["runtime_boundary_safety_widget"]["source_packet_state"] == "design_checkpoint_only"
    assert set(report["source_checker_versions"]) == set(SOURCE_CHECKER_VERSIONS)
    _assert_safe(report)


def test_ps_q17p_blocks_missing_source_packets_and_no_fixture_path() -> None:
    blocked = build_report()
    assert blocked["ok"] is False
    assert "source_report_missing:tier0_source_quality_gate_packet" in blocked["source_packet_validation_failures"]
    assert blocked["integration_rows"] == []
    _assert_safe(blocked)


def test_ps_q17p_keeps_all_rows_non_rendering_and_non_mutating() -> None:
    report = build_report(use_observed_fixture=True)
    assert report["render_blockers"] == list(WIDGET_FAMILY_ORDER)
    assert report["page_mutation_blockers"] == list(WIDGET_FAMILY_ORDER)
    for row in report["integration_rows"]:
        assert row["integration_state"] == "design_checkpoint_only"
        assert row["render_allowed"] is False
        assert row["page_mutation_allowed"] is False
        assert row["refresh_invocation_allowed"] is False
        assert row["write_or_apply_allowed"] is False
        assert row["next_validation"].endswith("_integration_guard")
    _assert_safe(report)


def test_ps_q17p_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["stage"] == "warroom_prediction_widget_integration_design_checkpoint_before_ui_mount_and_rendering"
    assert printed["recommended_next_slice"].startswith("PS-Q17Q")
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)
