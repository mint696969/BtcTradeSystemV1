# path: ./tools/test_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter.py
# desc: Unit tests for PS-Q17O parameter-candidate evidence adapter.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract import CHECKER_VERSION as PS_Q17N_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter import ADAPTER_VERSION, CHECKER_VERSION, adapt_parameter_candidate, build_report, main


def _q17n_report() -> dict:
    return {
        "ok": True,
        "checker_version": PS_Q17N_CHECKER_VERSION,
        "contract_only": True,
        "warroom_widget_implementation_allowed": False,
        "parameter_candidate_actual_read_allowed": False,
        "parameter_candidate_widget_rendering_allowed": False,
        "parameter_candidate_reliability_claim_allowed": False,
        "confidence_increase_allowed": False,
        "parameter_tuning_allowed": False,
        "d_hot_actual_read_allowed": False,
        "contract_rows": [
            {"contract_id": "parameter_candidate_source_contract", "priority": "P0", "blocks_parameter_staging": True, "blocks_parameter_apply": True},
            {"contract_id": "baseline_parameter_reference_contract", "priority": "P0", "blocks_parameter_staging": True, "blocks_parameter_apply": True},
            {"contract_id": "candidate_parameter_diff_contract", "priority": "P0", "blocks_parameter_staging": True, "blocks_parameter_apply": True},
            {"contract_id": "rollback_threshold_contract", "priority": "P0", "blocks_parameter_staging": True, "blocks_parameter_apply": True},
            {"contract_id": "parameter_evidence_completeness_release_gate_contract", "priority": "P0", "blocks_parameter_staging": True, "blocks_parameter_apply": True},
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


def _candidate() -> dict:
    return {
        "source_artifact_ref": "fixture://param",
        "generated_at": "2026-06-22T02:00:00Z",
        "baseline": {"ref_id": "baseline.ref", "parameter_set_id": "params.v1", "effective_at": "2026-06-01T00:00:00Z"},
        "candidate": {"candidate_id": "candidate.1", "changed_parameter_keys": ["signal_floor"], "diff_summary": "raise floor", "expected_effect_summary": "review only"},
        "evidence": {"source_quality_ref_id": "sq.ref", "calibration_ref_id": "cal.ref", "replay_feedback_ref_id": "replay.ref"},
        "rollback": {"rollback_threshold_ref_id": "rb.ref", "rollback_condition_summary": "rollback condition", "abort_condition_summary": "abort condition"},
    }


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "adapter_only", "contract_only", "diagnostic_only", "warroom_widget_design_premise"):
        assert report[key] is True, key
    for key in (
        "warroom_widget_implementation_allowed",
        "parameter_candidate_actual_read_allowed",
        "parameter_candidate_widget_rendering_allowed",
        "parameter_candidate_reliability_claim_allowed",
        "confidence_increase_allowed",
        "parameter_tuning_allowed",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "d_hot_actual_read_allowed",
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


def test_ps_q17o_adapts_supplied_parameter_candidate_to_review_packet() -> None:
    report = build_report(supplied_q17n_report=_q17n_report(), supplied_parameter_candidate=_candidate())
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["adapter_version"] == ADAPTER_VERSION
    packet = report["adapted_packet"]
    assert packet["parameter_candidate"]["baseline"]["ref_id"] == "baseline.ref"
    assert packet["parameter_candidate"]["candidate"]["candidate_id"] == "candidate.1"
    assert packet["parameter_candidate"]["candidate"]["changed_parameter_keys"] == ["signal_floor"]
    gate = packet["parameter_candidate_release_gate"]
    assert gate["evidence_complete"] is True
    assert gate["parameter_staging_allowed"] is False
    assert gate["parameter_apply_allowed"] is False
    assert gate["confidence_increase_allowed"] is False
    assert gate["parameter_tuning_allowed"] is False
    assert packet["warroom_parameter_candidate_widget"]["render_allowed"] is False
    _assert_safe(report)


def test_ps_q17o_blocks_invalid_source_contract_or_missing_candidate() -> None:
    invalid = build_report()
    assert invalid["ok"] is False
    assert "q17n_checker_version_mismatch" in invalid["source_q17n_validation_failures"]
    _assert_safe(invalid)
    unsafe = _q17n_report()
    unsafe["would_send_to_broker"] = True
    report = build_report(supplied_q17n_report=unsafe, supplied_parameter_candidate=_candidate())
    assert report["ok"] is False
    assert "q17n_boundary_not_false:would_send_to_broker" in report["source_q17n_validation_failures"]
    _assert_safe(report)
    missing = build_report(supplied_q17n_report=_q17n_report())
    assert missing["ok"] is False
    assert "parameter_candidate_missing_or_q17n_invalid" in missing["adapter_validation_failures"]


def test_ps_q17o_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["adapter_valid"] is True
    assert printed["adapted_packet"]["parameter_packet_version"] == "parameter_candidate_evidence_review_packet.v1"
    assert printed["adapted_packet"]["parameter_candidate_release_gate"]["parameter_apply_allowed"] is False
    assert printed["adapted_packet"]["warroom_parameter_candidate_widget"]["render_allowed"] is False
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)


def test_ps_q17o_adapter_function_is_pure_and_keeps_apply_false() -> None:
    packet = adapt_parameter_candidate(_candidate())
    assert packet["read_only"] is True
    assert packet["write_or_apply_allowed"] is False
    assert packet["parameter_candidate_actual_read_allowed"] is False
    assert packet["parameter_candidate_widget_rendering_allowed"] is False
    gate = packet["parameter_candidate_release_gate"]
    assert gate["evidence_complete"] is True
    assert gate["parameter_staging_allowed"] is False
    assert gate["parameter_apply_allowed"] is False
    assert gate["confidence_increase_allowed"] is False
    assert gate["parameter_tuning_allowed"] is False
