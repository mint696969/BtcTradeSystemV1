# path: ./tools/test_phase4a_prediction_system_ps_q17f_calibration_reference_contract.py
# desc: Unit tests for PS-Q17F calibration reference contract.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import CHECKER_VERSION as PS_Q17B_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17f_calibration_reference_contract import CHECKER_VERSION, CONTRACT_ORDER, REQUIRED_CALIBRATION_FIELDS, build_report, main


def _q17b_report() -> dict:
    return {
        "ok": True,
        "checker_version": PS_Q17B_CHECKER_VERSION,
        "plan_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "plan_rows": [
            {
                "gap_id": "calibration_refs_and_signal_strength_validation",
                "priority": "P0",
                "state": "open",
                "reasons": ["calibration_refs_present=false", "signal_strength_range=24..49", "reference_hit_rate_range=24..49"],
                "blocks_before_warroom_widget_implementation": True,
                "read_only": True,
                "write_or_apply_allowed": False,
            }
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
    for key in ("read_only", "non_executing", "contract_only", "diagnostic_only", "plan_only", "warroom_widget_design_premise"):
        assert report[key] is True, key
    for key in (
        "warroom_widget_implementation_allowed",
        "confidence_increase_allowed",
        "signal_reliability_claim_allowed",
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


def test_ps_q17f_builds_calibration_contract_from_q17b_gap() -> None:
    report = build_report(supplied_q17b_report=_q17b_report())
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["source_q17b_report_valid"] is True
    assert report["source_gap_id"] == "calibration_refs_and_signal_strength_validation"
    assert report["contract_count"] == 6
    assert report["p0_contract_count"] == 4
    assert report["p1_contract_count"] == 2
    contract_ids = [row["contract_id"] for row in report["contract_rows"]]
    for expected in CONTRACT_ORDER:
        assert expected in contract_ids
    assert report["recommended_first_validation"] == "signal_strength_calibration_reference_contract"
    assert "calibration_refs.signal_strength.sample_count" in report["required_calibration_fields"]
    assert report["calibration_refs_required_before_confidence_claim"] is True
    _assert_safe(report)


def test_ps_q17f_blocks_invalid_or_nonblocking_q17b_report() -> None:
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
    nonblocking = _q17b_report()
    nonblocking["plan_rows"][0]["blocks_before_warroom_widget_implementation"] = False
    blocked = build_report(supplied_q17b_report=nonblocking)
    assert blocked["ok"] is False
    assert "calibration_gap_not_blocking_widgets" in blocked["source_q17b_validation_failures"]


def test_ps_q17f_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["p0_contract_count"] == 4
    assert "reference_hit_rate_calibration_reference_contract" in printed["blocks_confidence_increase"]
    assert "parameter_candidate_calibration_dependency_contract" in printed["blocks_parameter_tuning"]
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)


def test_ps_q17f_keeps_calibration_out_of_live_read_confidence_and_parameter_scope() -> None:
    report = build_report(supplied_q17b_report=_q17b_report())
    assert report["warroom_widget_implementation_allowed"] is False
    assert report["confidence_increase_allowed"] is False
    assert report["parameter_tuning_allowed"] is False
    assert report["d_hot_actual_read_allowed"] is False
    assert report["recommended_next_slice"].startswith("PS-Q17G")
    for row in report["contract_rows"]:
        assert row["read_only"] is True
        assert row["write_or_apply_allowed"] is False
        assert row["state"] == "required"
        assert row["next_validation"].endswith("_guard")
    assert len(REQUIRED_CALIBRATION_FIELDS) >= 10
