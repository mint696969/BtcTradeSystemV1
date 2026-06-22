# path: ./tools/test_phase4a_prediction_system_ps_q17g_calibration_reference_adapter.py
# desc: Unit tests for PS-Q17G calibration reference adapter.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17f_calibration_reference_contract import CHECKER_VERSION as PS_Q17F_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17g_calibration_reference_adapter import ADAPTER_VERSION, CHECKER_VERSION, adapt_calibration_refs, build_report, main


def _q17f_report() -> dict:
    return {
        "ok": True,
        "checker_version": PS_Q17F_CHECKER_VERSION,
        "contract_only": True,
        "confidence_increase_allowed": False,
        "signal_reliability_claim_allowed": False,
        "parameter_tuning_allowed": False,
        "d_hot_actual_read_allowed": False,
        "warroom_widget_implementation_allowed": False,
        "contract_rows": [
            {"contract_id": "signal_strength_calibration_reference_contract", "priority": "P0", "blocks_confidence_increase": True},
            {"contract_id": "reference_hit_rate_calibration_reference_contract", "priority": "P0", "blocks_confidence_increase": True},
            {"contract_id": "calibration_sample_window_contract", "priority": "P0", "blocks_confidence_increase": True},
            {"contract_id": "confidence_band_release_contract", "priority": "P0", "blocks_confidence_increase": True},
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


def _refs() -> dict:
    return {
        "calibration_ref_id": "unit.calibration.ref",
        "market_uid": "BTC_JPY:bitFlyer",
        "sample_window": {"start_at": "2026-06-01T00:00:00Z", "end_at": "2026-06-22T00:00:00Z", "market_uid": "BTC_JPY:bitFlyer", "horizon_keys": ["short"]},
        "signal_strength": {"model_version": "unit.signal.v1", "sample_count": 20, "sample_window": {"start_at": "2026-06-01T00:00:00Z"}, "bucket_metrics": {"low": {"record_count": 20, "observed_hit_rate": 0.4}}},
        "reference_hit_rate": {"model_version": "unit.refhit.v1", "sample_count": 20, "sample_window": {"start_at": "2026-06-01T00:00:00Z"}, "bucket_metrics": {"low": {"record_count": 20, "observed_reference_hit_rate": 0.38}}},
    }


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "adapter_only", "contract_only", "diagnostic_only", "warroom_widget_design_premise"):
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


def test_ps_q17g_adapts_supplied_refs_to_calibration_packet() -> None:
    report = build_report(supplied_q17f_report=_q17f_report(), supplied_calibration_refs=_refs())
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["adapter_version"] == ADAPTER_VERSION
    packet = report["adapted_packet"]
    assert packet["calibration_ref_id"] == "unit.calibration.ref"
    assert packet["calibration_release_gate"]["calibration_refs_present"] is True
    assert packet["calibration_release_gate"]["confidence_band_claim_allowed"] is False
    assert packet["calibration_release_gate"]["parameter_tuning_allowed"] is False
    assert packet["warroom_calibration_explanation_packet"]["render_allowed"] is False
    assert packet["contract_completeness"]["has_signal_strength_ref"] is True
    assert packet["contract_completeness"]["has_reference_hit_rate_ref"] is True
    _assert_safe(report)


def test_ps_q17g_blocks_invalid_source_contract_or_missing_refs() -> None:
    invalid = build_report()
    assert invalid["ok"] is False
    assert "q17f_checker_version_mismatch" in invalid["source_q17f_validation_failures"]
    _assert_safe(invalid)
    unsafe = _q17f_report()
    unsafe["would_send_to_broker"] = True
    report = build_report(supplied_q17f_report=unsafe, supplied_calibration_refs=_refs())
    assert report["ok"] is False
    assert "q17f_boundary_not_false:would_send_to_broker" in report["source_q17f_validation_failures"]
    _assert_safe(report)
    missing_refs = build_report(supplied_q17f_report=_q17f_report())
    assert missing_refs["ok"] is False
    assert "calibration_refs_missing_or_q17f_invalid" in missing_refs["adapter_validation_failures"]


def test_ps_q17g_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["adapter_valid"] is True
    assert printed["adapted_packet"]["adapter_version"] == ADAPTER_VERSION
    assert printed["adapted_packet"]["calibration_release_gate"]["confidence_band_claim_allowed"] is False
    assert printed["adapted_packet"]["calibration_release_gate"]["parameter_tuning_allowed"] is False
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)


def test_ps_q17g_adapter_function_is_pure_and_keeps_release_false() -> None:
    packet = adapt_calibration_refs(_refs())
    assert packet["read_only"] is True
    assert packet["write_or_apply_allowed"] is False
    assert packet["confidence_increase_allowed"] is False
    assert packet["signal_reliability_claim_allowed"] is False
    assert packet["parameter_tuning_allowed"] is False
    assert packet["calibration_release_gate"]["confidence_band_claim_allowed"] is False
    assert packet["warroom_calibration_explanation_packet"]["render_allowed"] is False
