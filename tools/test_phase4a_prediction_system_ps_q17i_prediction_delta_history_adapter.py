# path: ./tools/test_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter.py
# desc: Unit tests for PS-Q17I prediction-delta history adapter.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17h_prediction_delta_history_contract import CHECKER_VERSION as PS_Q17H_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter import ADAPTER_VERSION, CHECKER_VERSION, adapt_snapshots, build_report, main


def _q17h_report() -> dict:
    return {
        "ok": True,
        "checker_version": PS_Q17H_CHECKER_VERSION,
        "contract_only": True,
        "delta_widget_rendering_allowed": False,
        "history_actual_read_allowed": False,
        "d_hot_actual_read_allowed": False,
        "warroom_widget_implementation_allowed": False,
        "contract_rows": [
            {"contract_id": "previous_latest_snapshot_reference_contract", "priority": "P0", "blocks_realtime_delta_widget": True},
            {"contract_id": "latest_snapshot_lineage_contract", "priority": "P0", "blocks_realtime_delta_widget": True},
            {"contract_id": "delta_computation_key_contract", "priority": "P0", "blocks_realtime_delta_widget": True},
            {"contract_id": "warroom_delta_widget_release_contract", "priority": "P0", "blocks_realtime_delta_widget": True},
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


def _snapshots() -> dict:
    return {
        "previous_snapshot": {"run_id": "prev", "generated_at": "2026-06-22T00:00:00Z", "source_artifact_ref": "fixture://prev", "records": [{"record_id": "r1", "market_uid": "BTC_JPY:bitFlyer", "family": "trend", "horizon_key": "short", "estimated_signal_strength_percent": 35, "source_quality_gate_state": "fail", "scenario_trace_state": "watch"}]},
        "latest_snapshot": {"run_id": "latest", "generated_at": "2026-06-22T00:05:00Z", "source_artifact_ref": "fixture://latest", "records": [{"record_id": "r1", "market_uid": "BTC_JPY:bitFlyer", "family": "trend", "horizon_key": "short", "estimated_signal_strength_percent": 40, "source_quality_gate_state": "fail", "scenario_trace_state": "watch"}]},
        "history_source_kind": "unit_supplied",
    }


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "adapter_only", "contract_only", "diagnostic_only", "warroom_widget_design_premise"):
        assert report[key] is True, key
    for key in (
        "warroom_widget_implementation_allowed",
        "delta_widget_rendering_allowed",
        "history_actual_read_allowed",
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


def test_ps_q17i_adapts_supplied_snapshots_to_delta_packet() -> None:
    report = build_report(supplied_q17h_report=_q17h_report(), supplied_snapshots=_snapshots())
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["adapter_version"] == ADAPTER_VERSION
    packet = report["adapted_packet"]
    history = packet["prediction_delta_history"]
    assert history["previous_snapshot"]["run_id"] == "prev"
    assert history["latest_snapshot"]["run_id"] == "latest"
    assert history["changed_row_count"] == 1
    assert history["changed_fields"] == ["estimated_signal_strength_percent"]
    assert packet["prediction_delta_release_gate"]["history_available"] is True
    assert packet["prediction_delta_release_gate"]["widget_reliability_claim_allowed"] is False
    assert packet["warroom_delta_review_packet"]["render_allowed"] is False
    _assert_safe(report)


def test_ps_q17i_blocks_invalid_source_contract_or_missing_snapshots() -> None:
    invalid = build_report()
    assert invalid["ok"] is False
    assert "q17h_checker_version_mismatch" in invalid["source_q17h_validation_failures"]
    _assert_safe(invalid)
    unsafe = _q17h_report()
    unsafe["would_send_to_broker"] = True
    report = build_report(supplied_q17h_report=unsafe, supplied_snapshots=_snapshots())
    assert report["ok"] is False
    assert "q17h_boundary_not_false:would_send_to_broker" in report["source_q17h_validation_failures"]
    _assert_safe(report)
    missing = build_report(supplied_q17h_report=_q17h_report())
    assert missing["ok"] is False
    assert "snapshots_missing_or_q17h_invalid" in missing["adapter_validation_failures"]


def test_ps_q17i_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["adapter_valid"] is True
    assert printed["adapted_packet"]["delta_packet_version"] == "prediction_delta_review_packet.v1"
    assert printed["adapted_packet"]["prediction_delta_release_gate"]["widget_reliability_claim_allowed"] is False
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)


def test_ps_q17i_adapter_function_is_pure_and_keeps_widget_release_false() -> None:
    packet = adapt_snapshots(_snapshots())
    assert packet["read_only"] is True
    assert packet["write_or_apply_allowed"] is False
    assert packet["history_actual_read_allowed"] is False
    assert packet["delta_widget_rendering_allowed"] is False
    assert packet["prediction_delta_release_gate"]["widget_reliability_claim_allowed"] is False
    assert packet["warroom_delta_review_packet"]["render_allowed"] is False
