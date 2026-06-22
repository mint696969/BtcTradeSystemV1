# path: ./tools/test_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit.py
# desc: Unit tests for PS-Q17A Prediction Engine real-output readiness audit.

from __future__ import annotations

import json
from pathlib import Path
import tempfile

from check_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit import CHECKER_VERSION, LATEST_RELATIVE_PATH, PRODUCER_STATUS_RELATIVE_PATH, build_report, main


def _payload() -> dict:
    records = []
    for family in ("market_regime", "trend_bias", "source_quality"):
        for horizon in ("15s", "300s"):
            records.append(
                {
                    "family": family,
                    "horizon_key": horizon,
                    "primary_label": "range_candidate" if family == "market_regime" else "neutral_bias",
                    "score": 0.49,
                    "confidence": "medium",
                    "usable": True,
                    "read_only": True,
                    "non_executing": True,
                    "parameter_set_id": f"{family}_prediction_v0_1_0",
                    "logic_version": "prediction_forecast_ledger.s130.v1",
                    "warnings": ["tier0_source_quality_missing_or_degraded"],
                    "blockers": [],
                    "values_snapshot": {
                        "estimated_signal_strength_percent": 49,
                        "estimated_reference_hit_rate_percent": 49,
                        "source_quality_gate_state": "warning_context_only",
                        "source_contribution_ledger": "list",
                    },
                    "would_append_ledger": False,
                    "would_send_to_broker": False,
                    "would_write_runtime_artifact": False,
                    "broker_execution_requested": False,
                    "mode_apply_requested": False,
                    "command_ledger_append_requested": False,
                }
            )
    return {
        "prediction_run_id": "prediction_system.ps_q17a:BTC_JPY:bitFlyer:unit",
        "generated_at": "2026-06-22T14:00:00Z",
        "market_uid": "BTC_JPY:bitFlyer",
        "read_only": True,
        "non_executing": True,
        "calibration_refs": [],
        "scenario_core": {
            "scenario_trace": {
                "prediction_evidence_weighting_trace": {"state": "available"},
                "prediction_invalidation_rewrite_trace": {"state": "available"},
                "prediction_scenario_switch_trace": {"state": "available"},
            },
            "gpt_review_digest": {"operator_next_action": "review_only"},
        },
        "forecast_batch": {
            "generated_at": "2026-06-22T14:00:00Z",
            "family_count": 3,
            "horizon_count": 2,
            "record_count": len(records),
            "records": records,
        },
        "approval_append_requested": False,
        "broker_execution_requested": False,
        "command_ledger_append_requested": False,
        "mode_apply_requested": False,
        "would_append_ledger": False,
        "would_send_to_broker": False,
        "would_write_runtime_artifact": False,
    }


def _producer_status() -> dict:
    return {
        "producer_state": "manual_refresh_exported_status_written",
        "producer_enabled": False,
        "scheduler_enabled": False,
        "last_success_generated_at": "2026-06-22T14:00:00Z",
        "freshness_max_age_sec": 3600,
        "recommended_cadence_sec": 300,
        "safe_flags": {
            "approval_or_authorization_allowed_false": True,
            "autotrade_trigger_allowed_false": True,
            "broker_private_api_allowed_false": True,
            "ledger_append_allowed_false": True,
            "parameter_apply_allowed_false": True,
            "parameter_staging_write_allowed_false": True,
        },
    }


def _assert_safe(report: dict) -> None:
    assert report["read_only"] is True
    assert report["non_executing"] is True
    assert report["actual_read_audit_only"] is True
    assert report["warroom_widget_design_premise"] is True
    for key in (
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


def test_ps_q17a_audits_supplied_real_output_widget_readiness() -> None:
    report = build_report(supplied_payload=_payload(), supplied_producer_status=_producer_status())
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["prediction_run_id"] == "prediction_system.ps_q17a:BTC_JPY:bitFlyer:unit"
    assert report["record_summary"]["record_count"] == 6
    assert report["record_summary"]["family_count"] == 3
    assert report["scenario_trace_summary"]["scenario_trace_present"] is True
    assert report["scenario_trace_summary"]["evidence_weighting_trace_present"] is True
    assert report["producer_status_summary"]["status_present"] is True
    assert report["widget_ready_count"] >= 6
    assert any(row["widget_id"] == "parameter_candidate_comparison_widget" and row["state"] == "partial" for row in report["widget_readiness_rows"])
    assert "calibration_refs_missing" in report["warning_reasons"]
    _assert_safe(report)


def test_ps_q17a_requires_operator_ack_for_actual_read_when_payload_not_supplied() -> None:
    report = build_report()
    assert report["ok"] is False
    assert "operator_acknowledgement_required_before_d_hot_actual_read" in report["blocked_reasons"]
    assert "allow_actual_read_required_before_d_hot_actual_read" in report["blocked_reasons"]
    _assert_safe(report)


def test_ps_q17a_can_read_temp_latest_payload_read_only() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        latest = root / LATEST_RELATIVE_PATH
        status = root / PRODUCER_STATUS_RELATIVE_PATH
        latest.parent.mkdir(parents=True, exist_ok=True)
        status.parent.mkdir(parents=True, exist_ok=True)
        latest.write_text(json.dumps(_payload(), ensure_ascii=False), encoding="utf-8")
        status.write_text(json.dumps(_producer_status(), ensure_ascii=False), encoding="utf-8")
        report = build_report(hot_root=str(root), operator_acknowledged=True, allow_actual_read=True)
    assert report["ok"] is True
    assert report["latest_read_meta"]["actual_file_read_attempted"] is True
    assert report["latest_read_meta"]["payload_decode_succeeded"] is True
    assert report["producer_status_summary"]["status_present"] is True
    _assert_safe(report)


def test_ps_q17a_blocks_unsafe_payload_and_main_without_flags(capsys) -> None:
    payload = _payload()
    payload["would_send_to_broker"] = True
    report = build_report(supplied_payload=payload)
    assert report["ok"] is False
    assert report["safe_boundary_summary"]["unsafe_boundary_count"] == 1
    assert report["readiness_state"] == "blocked_unsafe_boundary"
    _assert_safe(report)
    assert main([]) == 1
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is False
    assert "allow_actual_read_required_before_d_hot_actual_read" in printed["blocked_reasons"]
