# path: ./tools/test_phase4a_prediction_system_ps_q17a_close_guard.py
# desc: Close guard for PS-Q17A Prediction Engine real-output readiness audit.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit import CHECKER_VERSION, WIDGET_FAMILIES, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17A_ENGINE_REAL_OUTPUT_READINESS_AUDIT_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17a_engine_readiness_audit_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit.py",
    "tools/test_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17A_ENGINE_REAL_OUTPUT_READINESS_AUDIT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17a_engine_readiness_audit_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17a_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _payload() -> dict:
    records = []
    for family in ("market_regime", "trend_bias", "reversal_zone", "source_quality"):
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
                    "warnings": ["tier0_source_quality_missing_or_degraded", "tier0_source_quality_signal_strength_capped"],
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
        "prediction_run_id": "prediction_system.ps_q17a.close",
        "generated_at": "2026-06-22T14:20:00Z",
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
            "generated_at": "2026-06-22T14:20:00Z",
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
        "last_success_generated_at": "2026-06-22T14:20:00Z",
        "freshness_max_age_sec": 3600,
        "recommended_cadence_sec": 300,
        "last_warning_count": 1,
        "safe_flags": {
            "approval_or_authorization_allowed_false": True,
            "autotrade_trigger_allowed_false": True,
            "broker_private_api_allowed_false": True,
            "ledger_append_allowed_false": True,
            "parameter_apply_allowed_false": True,
            "parameter_staging_write_allowed_false": True,
            "scheduler_enabled_false": True,
            "warroom_ui_trigger_false": True,
        },
    }


def _assert_safe(report: dict, failures: list[str]) -> None:
    for key in (
        "read_only",
        "non_executing",
        "actual_read_audit_only",
        "warroom_widget_design_premise",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
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
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")


def main_guard() -> int:
    failures: list[str] = []
    for path in (TOOL, UNIT, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    unit_text = _read(UNIT) if UNIT.exists() else ""
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "CHECKER = \"ps_q17a_prediction_engine_real_output_readiness_audit\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit.v1\"",
        "DEFAULT_HOT_ROOT = r\"D:\\btc_ts_hot\"",
        "LATEST_RELATIVE_PATH = \"prediction/latest_prediction_system_result.json\"",
        "PRODUCER_STATUS_RELATIVE_PATH = \"prediction/status/non_ui_scheduled_producer_status.json\"",
        "MAX_LATEST_BYTES = 8_000_000",
        "WIDGET_FAMILIES",
        "operator_acknowledged",
        "allow_actual_read",
        "source_quality_warnings_present_in_records",
        "previous_payload_missing_delta_widget_gap",
        "PS-Q17B inference quality gap plan",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    for forbidden in (
        "write_text(",
        "write_bytes(",
        "open(",
        "mkdir(",
        "unlink(",
        "replace(",
        "append_decision(",
        "append_command(",
        "send_order(",
        "create_order(",
        "submit_mode_change_command_request(",
        "build_prediction_warroom_bounded_manual_refresh_runner(",
        "build_prediction_warroom_latest_payload_actual_export_runner(",
    ):
        if forbidden in tool_text:
            failures.append(f"forbidden tool token: {forbidden}")
    if "test_ps_q17a_audits_supplied_real_output_widget_readiness" not in unit_text:
        failures.append("unit test must cover supplied real-output widget readiness")
    if "test_ps_q17a_requires_operator_ack_for_actual_read_when_payload_not_supplied" not in unit_text:
        failures.append("unit test must cover explicit actual-read gates")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit.v1":
        failures.append("checker version mismatch")
    if tuple(WIDGET_FAMILIES) != (
        "latest_prediction_summary_widget",
        "prediction_delta_widget",
        "scenario_trace_widget",
        "evidence_weighting_widget",
        "invalidation_rewrite_widget",
        "source_quality_freshness_widget",
        "warning_blocker_widget",
        "signal_strength_calibration_widget",
        "parameter_candidate_comparison_widget",
        "replay_outcome_calibration_widget",
        "producer_freshness_status_widget",
        "runtime_boundary_safety_widget",
    ):
        failures.append("widget family contract mismatch")
    ready = build_report(supplied_payload=_payload(), supplied_producer_status=_producer_status())
    if ready.get("ok") is not True:
        failures.append(f"supplied payload audit should be ok: {ready}")
    if ready.get("readiness_state") not in {"real_output_audit_ready_with_inference_quality_gaps", "real_output_present_but_widget_input_gaps"}:
        failures.append(f"unexpected readiness state: {ready.get('readiness_state')}")
    if ready.get("widget_ready_count", 0) < 6:
        failures.append("expected at least six ready widget rows")
    if ready.get("widget_partial_count", 0) < 2:
        failures.append("expected partial widget rows for quality gaps")
    partial_widget_ids = {
        row.get("widget_id")
        for row in ready.get("widget_readiness_rows", [])
        if row.get("state") == "partial"
    }
    for expected_partial in ("signal_strength_calibration_widget", "parameter_candidate_comparison_widget"):
        if expected_partial not in partial_widget_ids:
            failures.append(f"expected partial widget row: {expected_partial}")
    if "calibration_refs_missing" not in ready.get("warning_reasons", []):
        failures.append("calibration refs missing should remain explicit")
    if "previous_payload_missing_delta_widget_gap" not in ready.get("warning_reasons", []):
        failures.append("previous payload delta gap should remain explicit")
    _assert_safe(ready, failures)
    blocked = build_report()
    for expected in (
        "operator_acknowledgement_required_before_d_hot_actual_read",
        "allow_actual_read_required_before_d_hot_actual_read",
    ):
        if expected not in blocked.get("blocked_reasons", []):
            failures.append(f"missing blocker: {expected}")
    _assert_safe(blocked, failures)
    unsafe_payload = _payload()
    unsafe_payload["would_send_to_broker"] = True
    unsafe = build_report(supplied_payload=unsafe_payload, supplied_producer_status=_producer_status())
    if unsafe.get("ok") is not False:
        failures.append("unsafe broker boundary should fail ok")
    if unsafe.get("readiness_state") != "blocked_unsafe_boundary":
        failures.append("unsafe broker boundary should block")
    _assert_safe(unsafe, failures)
    if main([]) != 1:
        failures.append("main without actual-read flags should return 1")
    for marker in (
        "actual_read_audit_only=true",
        "warroom_widget_design_premise=true",
        "read_only=true",
        "non_executing=true",
        "runtime_artifact_write_allowed=false",
        "status_artifact_write_allowed=false",
        "parameter_apply_allowed=false",
        "parameter_staging_write_allowed=false",
        "approval_or_authorization_allowed=false",
        "ledger_append_allowed=false",
        "autotrade_trigger_allowed=false",
        "broker_private_api_allowed=false",
        "warroom_ui_trigger_enabled=false",
        "refresh_invocation_allowed=false",
        "scheduler_enabled=false",
        "latest_prediction_summary_widget",
        "prediction_delta_widget",
        "scenario_trace_widget",
        "parameter_candidate_comparison_widget",
        "replay_outcome_calibration_widget",
        "source quality warnings are present",
        "calibration_refs may be missing",
        "previous payload/history for delta widget may be missing",
        "PS-Q17B: Inference Quality Gap Plan",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "parameter_apply_allowed=true",
        "parameter_staging_write_allowed=true",
        "ledger_append_allowed=true",
        "autotrade_trigger_allowed=true",
        "broker_private_api_allowed=true",
        "warroom_ui_trigger_enabled=true",
        "refresh_invocation_allowed=true",
        "scheduler_enabled=true",
        "no_freshness_bypass=false",
    ):
        if forbidden in doc_text:
            failures.append(f"forbidden doc marker present: {forbidden}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q17a_close_guard",
        "phase": "phase3_prediction_engine_real_output_readiness_audit_closed",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17a_closed": not failures,
            "actual_read_audit_only": True,
            "warroom_widget_design_premise": True,
            "widget_family_count": len(WIDGET_FAMILIES),
            "real_output_readiness_audit": True,
            "no_parameter_apply": True,
            "no_parameter_staging_write": True,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_refresh_invocation": True,
            "no_warroom_ui_trigger": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
            "next_slice": "PS-Q17B inference quality gap plan before WarRoom widget implementation",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17a_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
