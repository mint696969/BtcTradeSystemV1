# path: ./tools/test_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter.py
# desc: Unit tests for PS-Q17K replay-outcome calibration adapter.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17j_replay_outcome_calibration_contract import CHECKER_VERSION as PS_Q17J_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter import ADAPTER_VERSION, CHECKER_VERSION, adapt_replay_feedback, build_report, main


def _q17j_report() -> dict:
    return {
        "ok": True,
        "checker_version": PS_Q17J_CHECKER_VERSION,
        "contract_only": True,
        "warroom_widget_implementation_allowed": False,
        "replay_history_actual_read_allowed": False,
        "replay_outcome_widget_rendering_allowed": False,
        "confidence_increase_allowed": False,
        "signal_reliability_claim_allowed": False,
        "parameter_tuning_allowed": False,
        "d_hot_actual_read_allowed": False,
        "contract_rows": [
            {"contract_id": "replay_feedback_reference_contract", "priority": "P0", "blocks_confidence_reliability_claim": True},
            {"contract_id": "outcome_window_contract", "priority": "P0", "blocks_confidence_reliability_claim": True},
            {"contract_id": "forecast_to_outcome_join_key_contract", "priority": "P0", "blocks_confidence_reliability_claim": True},
            {"contract_id": "replay_calibration_release_gate_contract", "priority": "P0", "blocks_confidence_reliability_claim": True},
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


def _feedback() -> dict:
    return {
        "replay_feedback": {"run_id": "rf", "generated_at": "2026-06-22T01:00:00Z", "source_artifact_ref": "fixture://rf"},
        "outcome_window": {"start_at": "2026-06-01T00:00:00Z", "end_at": "2026-06-22T00:00:00Z", "market_uid": "BTC_JPY:bitFlyer", "horizon_keys": ["short"]},
        "rows": [{"record_id": "r1", "market_uid": "BTC_JPY:bitFlyer", "family": "trend", "horizon_key": "short", "predicted_direction_hit": True, "actual_return_bps": 10.0, "magnitude_error_bps": 4.0}],
    }


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "adapter_only", "contract_only", "diagnostic_only", "warroom_widget_design_premise"):
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


def test_ps_q17k_adapts_supplied_replay_feedback_to_review_packet() -> None:
    report = build_report(supplied_q17j_report=_q17j_report(), supplied_replay_feedback=_feedback())
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["adapter_version"] == ADAPTER_VERSION
    packet = report["adapted_packet"]
    replay = packet["replay_outcome_calibration"]
    assert replay["replay_feedback"]["run_id"] == "rf"
    assert replay["sample_count"] == 1
    assert replay["summary_metrics"]["predicted_direction_hit_rate"] == 1.0
    assert packet["replay_calibration_release_gate"]["replay_feedback_present"] is True
    assert packet["replay_calibration_release_gate"]["confidence_reliability_claim_allowed"] is False
    assert packet["replay_calibration_release_gate"]["parameter_tuning_allowed"] is False
    assert packet["warroom_replay_outcome_widget"]["render_allowed"] is False
    _assert_safe(report)


def test_ps_q17k_blocks_invalid_source_contract_or_missing_feedback() -> None:
    invalid = build_report()
    assert invalid["ok"] is False
    assert "q17j_checker_version_mismatch" in invalid["source_q17j_validation_failures"]
    _assert_safe(invalid)
    unsafe = _q17j_report()
    unsafe["would_send_to_broker"] = True
    report = build_report(supplied_q17j_report=unsafe, supplied_replay_feedback=_feedback())
    assert report["ok"] is False
    assert "q17j_boundary_not_false:would_send_to_broker" in report["source_q17j_validation_failures"]
    _assert_safe(report)
    missing = build_report(supplied_q17j_report=_q17j_report())
    assert missing["ok"] is False
    assert "replay_feedback_missing_or_q17j_invalid" in missing["adapter_validation_failures"]


def test_ps_q17k_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["adapter_valid"] is True
    assert printed["adapted_packet"]["replay_packet_version"] == "replay_outcome_calibration_review_packet.v1"
    assert printed["adapted_packet"]["replay_calibration_release_gate"]["confidence_reliability_claim_allowed"] is False
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)


def test_ps_q17k_adapter_function_is_pure_and_keeps_release_false() -> None:
    packet = adapt_replay_feedback(_feedback())
    assert packet["read_only"] is True
    assert packet["write_or_apply_allowed"] is False
    assert packet["replay_history_actual_read_allowed"] is False
    assert packet["replay_outcome_widget_rendering_allowed"] is False
    gate = packet["replay_calibration_release_gate"]
    assert gate["confidence_reliability_claim_allowed"] is False
    assert gate["signal_reliability_claim_allowed"] is False
    assert gate["parameter_tuning_allowed"] is False
    assert packet["warroom_replay_outcome_widget"]["render_allowed"] is False
