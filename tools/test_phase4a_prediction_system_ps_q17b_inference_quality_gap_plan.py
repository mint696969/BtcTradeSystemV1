# path: ./tools/test_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.py
# desc: Unit tests for PS-Q17B inference quality gap plan.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit import CHECKER_VERSION as PS_Q17A_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import CHECKER_VERSION, TARGET_GAP_ORDER, build_report, main


def _q17a_report() -> dict:
    return {
        "ok": True,
        "checker_version": PS_Q17A_CHECKER_VERSION,
        "actual_read_audit_only": True,
        "warroom_widget_design_premise": True,
        "record_summary": {
            "source_quality_warning_record_count": 110,
            "signal_strength_min": 24,
            "signal_strength_max": 49,
            "reference_hit_rate_min": 24,
            "reference_hit_rate_max": 49,
        },
        "scenario_trace_summary": {
            "scenario_trace_present": True,
            "evidence_weighting_trace_present": False,
            "invalidation_rewrite_trace_present": False,
            "scenario_switch_trace_present": False,
            "scenario_trace_keys": ["context_evidence_profiles", "tier0_source_quality_gate"],
        },
        "calibration_summary": {
            "calibration_refs_present": False,
            "replay_feedback_present": False,
            "forecast_batch_present": True,
        },
        "safe_boundary_summary": {"unsafe_boundary_count": 0},
        "warning_reasons": [
            "source_quality_warnings_present_in_records",
            "calibration_refs_missing",
            "previous_payload_missing_delta_widget_gap",
        ],
        "widget_readiness_rows": [
            {"widget_id": "prediction_delta_widget", "state": "gap", "warnings": ["delta_widget_requires_previous_latest_snapshot_or_history"]},
            {"widget_id": "evidence_weighting_widget", "state": "partial", "warnings": ["evidence_weighting_trace_not_confirmed_in_payload"]},
            {"widget_id": "invalidation_rewrite_widget", "state": "partial", "warnings": ["invalidation_rewrite_trace_not_confirmed_in_payload"]},
            {"widget_id": "source_quality_freshness_widget", "state": "ready", "warnings": ["source_quality_warning_records_present"]},
            {"widget_id": "signal_strength_calibration_widget", "state": "partial", "warnings": ["calibration_refs_missing"]},
            {"widget_id": "parameter_candidate_comparison_widget", "state": "partial", "warnings": ["baseline_candidate_rollback_comparison_not_confirmed"]},
            {"widget_id": "replay_outcome_calibration_widget", "state": "gap", "warnings": []},
        ],
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "warroom_ui_trigger_enabled": False,
        "refresh_invocation_allowed": False,
        "scheduler_enabled": False,
    }


def _assert_safe(report: dict) -> None:
    assert report["read_only"] is True
    assert report["non_executing"] is True
    assert report["plan_only"] is True
    assert report["warroom_widget_design_premise"] is True
    for key in (
        "warroom_widget_implementation_allowed",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
    ):
        assert report[key] is False, key


def test_ps_q17b_builds_prioritized_plan_from_q17a_audit() -> None:
    report = build_report(supplied_q17a_report=_q17a_report())
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["source_q17a_report_valid"] is True
    assert report["gap_count"] >= 6
    assert report["p0_gap_count"] >= 4
    assert report["recommended_first_slice"] == "source_quality_cap_and_coverage"
    gap_ids = [row["gap_id"] for row in report["plan_rows"]]
    for expected in TARGET_GAP_ORDER:
        assert expected in gap_ids
    assert "prediction_delta_history" in report["blocks_before_warroom_widget_implementation"]
    _assert_safe(report)


def test_ps_q17b_blocks_invalid_or_unsafe_q17a_report() -> None:
    report = _q17a_report()
    report["would_send_to_broker"] = True
    unsafe = build_report(supplied_q17a_report=report)
    assert unsafe["ok"] is False
    assert "q17a_boundary_not_false:would_send_to_broker" in unsafe["source_q17a_validation_failures"]
    assert unsafe["plan_rows"] == []
    _assert_safe(unsafe)
    missing = build_report()
    assert missing["ok"] is False
    assert "q17a_checker_version_mismatch" in missing["source_q17a_validation_failures"]
    _assert_safe(missing)


def test_ps_q17b_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["p0_gap_count"] >= 4
    assert printed["recommended_first_slice"] == "source_quality_cap_and_coverage"
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)


def test_ps_q17b_keeps_warroom_widget_rendering_and_parameter_changes_out_of_scope() -> None:
    report = build_report(supplied_q17a_report=_q17a_report())
    assert report["warroom_widget_implementation_allowed"] is False
    assert report["parameter_apply_allowed"] is False
    assert report["parameter_staging_write_allowed"] is False
    assert report["recommended_next_slice"].startswith("PS-Q17C")
    for row in report["plan_rows"]:
        assert row["read_only"] is True
        assert row["write_or_apply_allowed"] is False
        assert row["next_validation"].endswith("_guard")
