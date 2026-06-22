# path: ./tools/test_phase4a_prediction_system_ps_q17a_engine_readiness_audit_guard.py
# desc: Focused guard for PS-Q17A Prediction Engine real-output readiness audit.

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
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit.py",
    "tools/test_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17A_ENGINE_REAL_OUTPUT_READINESS_AUDIT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17a_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17a_engine_readiness_audit_guard.py",
}
FORBIDDEN_TOOL_TOKENS = (
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
)
REQUIRED_DOC_MARKERS = (
    "checker=check_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit.v1",
    "actual_read_audit_only=true",
    "warroom_widget_design_premise=true",
    "read_only=true",
    "non_executing=true",
    "parameter_apply_allowed=false",
    "parameter_staging_write_allowed=false",
    "ledger_append_allowed=false",
    "warroom_ui_trigger_enabled=false",
    "latest_prediction_summary_widget",
    "prediction_delta_widget",
    "scenario_trace_widget",
    "parameter_candidate_comparison_widget",
    "replay_outcome_calibration_widget",
    "PS-Q17B: Inference Quality Gap Plan",
)
FORBIDDEN_DOC_MARKERS = (
    "parameter_apply_allowed=true",
    "parameter_staging_write_allowed=true",
    "ledger_append_allowed=true",
    "autotrade_trigger_allowed=true",
    "broker_private_api_allowed=true",
    "warroom_ui_trigger_enabled=true",
    "refresh_invocation_allowed=true",
    "scheduler_enabled=true",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _payload() -> dict:
    return {
        "prediction_run_id": "prediction_system.ps_q17a.guard",
        "generated_at": "2026-06-22T14:10:00Z",
        "market_uid": "BTC_JPY:bitFlyer",
        "read_only": True,
        "non_executing": True,
        "calibration_refs": [],
        "scenario_core": {
            "scenario_trace": {
                "prediction_evidence_weighting_trace": {"state": "available"},
                "prediction_invalidation_rewrite_trace": {"state": "available"},
                "prediction_scenario_switch_trace": {"state": "available"},
            }
        },
        "forecast_batch": {
            "records": [
                {
                    "family": "market_regime",
                    "horizon_key": "15s",
                    "primary_label": "range_candidate",
                    "score": 0.49,
                    "confidence": "medium",
                    "usable": True,
                    "read_only": True,
                    "non_executing": True,
                    "parameter_set_id": "market_regime_prediction_v0_1_0",
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
            ]
        },
        "approval_append_requested": False,
        "broker_execution_requested": False,
        "command_ledger_append_requested": False,
        "mode_apply_requested": False,
        "would_append_ledger": False,
        "would_send_to_broker": False,
        "would_write_runtime_artifact": False,
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
    for marker in (
        "CHECKER = \"ps_q17a_prediction_engine_real_output_readiness_audit\"",
        "DEFAULT_HOT_ROOT = r\"D:\\btc_ts_hot\"",
        "LATEST_RELATIVE_PATH = \"prediction/latest_prediction_system_result.json\"",
        "PRODUCER_STATUS_RELATIVE_PATH = \"prediction/status/non_ui_scheduled_producer_status.json\"",
        "WIDGET_FAMILIES",
        "operator_acknowledged",
        "allow_actual_read",
        "prediction_delta_widget",
        "parameter_candidate_comparison_widget",
        "replay_outcome_calibration_widget",
        "PS-Q17B inference quality gap plan",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    for token in FORBIDDEN_TOOL_TOKENS:
        if token in tool_text:
            failures.append(f"forbidden tool token: {token}")
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
    ready = build_report(supplied_payload=_payload())
    if ready.get("ok") is not True:
        failures.append(f"supplied payload audit should be ok: {ready}")
    if ready.get("widget_ready_count", 0) < 5:
        failures.append("expected at least five ready widget rows")
    if "calibration_refs_missing" not in ready.get("warning_reasons", []):
        failures.append("calibration refs missing should be explicit")
    _assert_safe(ready, failures)
    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("actual read without ack/allow should fail")
    for expected in (
        "operator_acknowledgement_required_before_d_hot_actual_read",
        "allow_actual_read_required_before_d_hot_actual_read",
    ):
        if expected not in blocked.get("blocked_reasons", []):
            failures.append(f"missing blocker: {expected}")
    unsafe_payload = _payload()
    unsafe_payload["would_write_runtime_artifact"] = True
    unsafe = build_report(supplied_payload=unsafe_payload)
    if unsafe.get("readiness_state") != "blocked_unsafe_boundary":
        failures.append("unsafe runtime boundary should block")
    _assert_safe(unsafe, failures)
    if main([]) != 1:
        failures.append("main without flags should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for marker in FORBIDDEN_DOC_MARKERS:
        if marker in doc_text:
            failures.append(f"forbidden doc marker present: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q17a_engine_readiness_audit",
        "phase": "phase3_prediction_engine_real_output_readiness_audit",
        "contract": {
            "actual_read_audit_only": True,
            "warroom_widget_design_premise": True,
            "widget_family_count": len(WIDGET_FAMILIES),
            "no_parameter_apply": True,
            "no_parameter_staging_write": True,
            "no_runtime_write": True,
            "no_refresh_invocation": True,
            "no_warroom_ui_trigger": True,
            "expected_dirty_only": not unexpected,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17a_engine_readiness_audit_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
