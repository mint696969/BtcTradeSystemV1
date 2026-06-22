# path: ./tools/test_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter.py
# desc: Unit tests for PS-Q17E tier0 source-quality gate contract adapter.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract import CHECKER_VERSION as PS_Q17D_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter import ADAPTER_VERSION, CHECKER_VERSION, adapt_payload, build_report, main


def _q17d_report() -> dict:
    return {
        "ok": True,
        "checker_version": PS_Q17D_CHECKER_VERSION,
        "contract_only": True,
        "confidence_increase_allowed": False,
        "d_hot_actual_read_allowed": False,
        "warroom_widget_implementation_allowed": False,
        "contract_rows": [
            {"contract_id": "tier0_gate_state_reason_contract", "priority": "P0", "blocks_confidence_increase": True},
            {"contract_id": "required_usable_source_count_contract", "priority": "P0", "blocks_confidence_increase": True},
            {"contract_id": "record_cap_provenance_contract", "priority": "P0", "blocks_confidence_increase": True},
            {"contract_id": "confidence_release_gate_contract", "priority": "P0", "blocks_confidence_increase": True},
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


def _payload() -> dict:
    return {
        "forecast_batch": {
            "records": [
                {"record_id": "r1", "family": "trend", "horizon_key": "short", "warnings": ["tier0_source_quality_gate_not_passed"], "values_snapshot": {"estimated_signal_strength_percent": 42}},
                {"record_id": "r2", "family": "breakout", "horizon_key": "mid", "warnings": ["low_usable_venue_count_liquidity_caution"], "values_snapshot": {"estimated_signal_strength_percent": 31}},
            ]
        },
        "source_artifact_coverage": {"required_source_count": 5, "usable_source_count": 3, "missing_source_count": 2, "by_family": {"trend": {"usable": 3}}, "by_horizon": {"short": {"usable": 3}}},
        "source_quality_warning_taxonomy": {"by_code": {"tier0_source_quality_gate_not_passed": {"severity": "blocking", "operator_action": "restore tier0 coverage"}}},
    }


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "adapter_only", "contract_only", "diagnostic_only", "warroom_widget_design_premise"):
        assert report[key] is True, key
    for key in (
        "warroom_widget_implementation_allowed",
        "confidence_increase_allowed",
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


def test_ps_q17e_adapts_supplied_payload_to_tier0_contract_packet() -> None:
    report = build_report(supplied_q17d_report=_q17d_report(), supplied_payload=_payload())
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["adapter_version"] == ADAPTER_VERSION
    packet = report["adapted_packet"]
    assert packet["tier0_source_quality_gate"]["state"] == "fail"
    assert "tier0_source_quality_gate_not_passed" in packet["tier0_source_quality_gate"]["reason_codes"]
    assert packet["source_artifact_coverage"]["required_source_count"] == 5
    assert packet["source_artifact_coverage"]["usable_source_count"] == 3
    assert packet["confidence_release_gate"]["confidence_increase_allowed"] is False
    assert packet["contract_completeness"]["has_cap_provenance"] is True
    _assert_safe(report)


def test_ps_q17e_blocks_invalid_source_contract_or_missing_payload() -> None:
    invalid = build_report()
    assert invalid["ok"] is False
    assert "q17d_checker_version_mismatch" in invalid["source_q17d_validation_failures"]
    _assert_safe(invalid)
    unsafe = _q17d_report()
    unsafe["would_send_to_broker"] = True
    report = build_report(supplied_q17d_report=unsafe, supplied_payload=_payload())
    assert report["ok"] is False
    assert "q17d_boundary_not_false:would_send_to_broker" in report["source_q17d_validation_failures"]
    _assert_safe(report)
    missing_payload = build_report(supplied_q17d_report=_q17d_report())
    assert missing_payload["ok"] is False
    assert "payload_missing_or_q17d_invalid" in missing_payload["adapter_validation_failures"]


def test_ps_q17e_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["adapter_valid"] is True
    assert printed["adapted_packet"]["adapter_version"] == ADAPTER_VERSION
    assert printed["adapted_packet"]["confidence_release_gate"]["confidence_increase_allowed"] is False
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)


def test_ps_q17e_adapter_function_is_pure_and_keeps_confidence_false() -> None:
    packet = adapt_payload(_payload())
    assert packet["read_only"] is True
    assert packet["write_or_apply_allowed"] is False
    assert packet["confidence_increase_allowed"] is False
    assert packet["confidence_release_gate"]["confidence_increase_allowed"] is False
    assert packet["signal_strength_cap_reason"]["by_record"]
    assert packet["contract_completeness"]["has_required_usable_counts"] is True
