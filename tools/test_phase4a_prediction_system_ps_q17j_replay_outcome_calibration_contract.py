# path: ./tools/test_phase4a_prediction_system_ps_q17j_replay_outcome_calibration_contract.py
# desc: Unit tests for PS-Q17J replay-outcome calibration contract.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import CHECKER_VERSION as PS_Q17B_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17j_replay_outcome_calibration_contract import CHECKER_VERSION, CONTRACT_ORDER, REQUIRED_REPLAY_FIELDS, build_report, main


def _q17b_report() -> dict:
    return {
        "ok": True,
        "checker_version": PS_Q17B_CHECKER_VERSION,
        "plan_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "plan_rows": [{
            "gap_id": "replay_outcome_calibration",
            "priority": "P0",
            "state": "open",
            "reasons": ["replay_feedback_present=false", "replay_outcome_calibration_widget=gap"],
            "blocks_before_warroom_widget_implementation": True,
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
        "replay_history_actual_read_allowed",
        "replay_outcome_widget_rendering_allowed",
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


def test_ps_q17j_builds_replay_outcome_contract_from_q17b_gap() -> None:
    report = build_report(supplied_q17b_report=_q17b_report())
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["source_gap_id"] == "replay_outcome_calibration"
    assert report["contract_count"] == 6
    assert report["p0_contract_count"] == 4
    assert report["p1_contract_count"] == 2
    assert [row["contract_id"] for row in report["contract_rows"]] == list(CONTRACT_ORDER)
    assert report["recommended_first_validation"] == "replay_feedback_reference_contract"
    assert "replay_outcome_calibration.replay_feedback.run_id" in report["required_replay_fields"]
    assert report["replay_feedback_required_before_confidence_claim"] is True
    _assert_safe(report)


def test_ps_q17j_blocks_invalid_or_nonblocking_q17b_report() -> None:
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
    assert "replay_outcome_calibration_gap_not_blocking_widgets" in blocked["source_q17b_validation_failures"]


def test_ps_q17j_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["p0_contract_count"] == 4
    assert "replay_feedback_reference_contract" in printed["blocks_confidence_reliability_claim"]
    assert "replay_feedback_present=false" in printed["replay_reason_codes"]
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)


def test_ps_q17j_keeps_replay_contract_out_of_live_read_and_ui_scope() -> None:
    report = build_report(supplied_q17b_report=_q17b_report())
    assert report["replay_history_actual_read_allowed"] is False
    assert report["replay_outcome_widget_rendering_allowed"] is False
    assert report["confidence_increase_allowed"] is False
    assert report["recommended_next_slice"].startswith("PS-Q17K")
    for row in report["contract_rows"]:
        assert row["read_only"] is True
        assert row["write_or_apply_allowed"] is False
        assert row["state"] == "required"
        assert row["next_validation"].endswith("_guard")
    assert len(REQUIRED_REPLAY_FIELDS) >= 12
