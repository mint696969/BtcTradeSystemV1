# path: ./tools/test_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract.py
# desc: Unit tests for PS-Q17N parameter-candidate evidence contract.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import CHECKER_VERSION as PS_Q17B_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract import CHECKER_VERSION, CONTRACT_ORDER, REQUIRED_PARAMETER_FIELDS, build_report, main


def _q17b_report() -> dict:
    return {
        "ok": True,
        "checker_version": PS_Q17B_CHECKER_VERSION,
        "plan_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "plan_rows": [{
            "gap_id": "parameter_candidate_evidence",
            "priority": "P1",
            "state": "open",
            "reasons": ["parameter_candidate_comparison_widget=partial", "baseline_candidate_rollback_comparison_not_confirmed"],
            "blocks_before_warroom_widget_implementation": False,
            "read_only": True,
            "write_or_apply_allowed": False,
        }],
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
    for key in ("read_only", "non_executing", "contract_only", "diagnostic_only", "plan_only", "warroom_widget_design_premise"):
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


def test_ps_q17n_builds_parameter_candidate_contract_from_q17b_gap() -> None:
    report = build_report(supplied_q17b_report=_q17b_report())
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["source_gap_id"] == "parameter_candidate_evidence"
    assert report["contract_count"] == 6
    assert report["p0_contract_count"] == 5
    assert report["p1_contract_count"] == 1
    assert [row["contract_id"] for row in report["contract_rows"]] == list(CONTRACT_ORDER)
    assert report["recommended_first_validation"] == "parameter_candidate_source_contract"
    assert "parameter_candidate.baseline.ref_id" in report["required_parameter_fields"]
    assert report["baseline_candidate_rollback_evidence_required_before_staging"] is True
    _assert_safe(report)


def test_ps_q17n_blocks_invalid_or_wrong_priority_q17b_report() -> None:
    invalid = build_report()
    assert invalid["ok"] is False
    assert "q17b_checker_version_mismatch" in invalid["source_q17b_validation_failures"]
    assert invalid["contract_rows"] == []
    _assert_safe(invalid)
    unsafe = _q17b_report()
    unsafe["would_send_to_broker"] = True
    report = build_report(supplied_q17b_report=unsafe)
    assert report["ok"] is False
    assert "q17b_boundary_not_false:would_send_to_broker" in report["source_q17b_validation_failures"]
    _assert_safe(report)
    wrong_priority = _q17b_report()
    wrong_priority["plan_rows"][0]["priority"] = "P0"
    blocked = build_report(supplied_q17b_report=wrong_priority)
    assert blocked["ok"] is False
    assert "parameter_candidate_evidence_gap_not_p1" in blocked["source_q17b_validation_failures"]


def test_ps_q17n_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["p0_contract_count"] == 5
    assert "parameter_candidate_source_contract" in printed["blocks_parameter_staging"]
    assert "baseline_candidate_rollback_comparison_not_confirmed" in printed["parameter_reason_codes"]
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)


def test_ps_q17n_keeps_parameter_evidence_out_of_apply_and_ui_scope() -> None:
    report = build_report(supplied_q17b_report=_q17b_report())
    assert report["parameter_candidate_actual_read_allowed"] is False
    assert report["parameter_candidate_widget_rendering_allowed"] is False
    assert report["parameter_candidate_reliability_claim_allowed"] is False
    assert report["parameter_staging_write_allowed"] is False
    assert report["parameter_apply_allowed"] is False
    assert report["recommended_next_slice"].startswith("PS-Q17O")
    for row in report["contract_rows"]:
        assert row["read_only"] is True
        assert row["write_or_apply_allowed"] is False
        assert row["state"] == "required"
        assert row["next_validation"].endswith("_guard")
    assert len(REQUIRED_PARAMETER_FIELDS) >= 14
