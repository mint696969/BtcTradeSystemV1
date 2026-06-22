# path: ./tools/test_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan_guard.py
# desc: Focused guard for PS-Q17B inference quality gap plan.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import CHECKER_VERSION, TARGET_GAP_ORDER, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17B_INFERENCE_QUALITY_GAP_PLAN_2026-06-22.md"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.py",
    "tools/test_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17B_INFERENCE_QUALITY_GAP_PLAN_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17b_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in ("read_only", "non_executing", "plan_only", "warroom_widget_design_premise"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "warroom_widget_implementation_allowed",
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
        "CHECKER = \"ps_q17b_inference_quality_gap_plan\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.v1\"",
        "PS_Q17A_SOURCE_CHECKER_VERSION",
        "TARGET_GAP_ORDER",
        "source_quality_cap_and_coverage",
        "calibration_refs_and_signal_strength_validation",
        "prediction_delta_history",
        "scenario_trace_confirmation",
        "parameter_candidate_evidence",
        "replay_outcome_calibration",
        "warroom_widget_implementation_allowed",
        "--use-observed-fixture",
        "PS-Q17C source-quality coverage diagnostic",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    for forbidden in (
        "Path(",
        "read_text(",
        "write_text(",
        "write_bytes(",
        "open(",
        "mkdir(",
        "unlink(",
        "replace(",
        "build_report(hot_root=",
        "allow_actual_read=True",
        "append_decision(",
        "append_command(",
        "send_order(",
        "create_order(",
        "build_prediction_warroom_bounded_manual_refresh_runner(",
        "build_prediction_warroom_latest_payload_actual_export_runner(",
    ):
        if forbidden in tool_text:
            failures.append(f"forbidden tool token: {forbidden}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.v1":
        failures.append("checker version mismatch")
    if tuple(TARGET_GAP_ORDER) != (
        "source_quality_cap_and_coverage",
        "calibration_refs_and_signal_strength_validation",
        "prediction_delta_history",
        "scenario_trace_confirmation",
        "parameter_candidate_evidence",
        "replay_outcome_calibration",
    ):
        failures.append("target gap order mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture should produce ok plan: {report}")
    if report.get("recommended_first_slice") != "source_quality_cap_and_coverage":
        failures.append("recommended first slice should be source_quality_cap_and_coverage")
    if report.get("p0_gap_count", 0) < 4:
        failures.append("expected at least four P0 gaps")
    for gap_id in TARGET_GAP_ORDER:
        if gap_id not in [row.get("gap_id") for row in report.get("plan_rows", [])]:
            failures.append(f"missing plan gap: {gap_id}")
    for expected_blocker in (
        "source_quality_cap_and_coverage",
        "calibration_refs_and_signal_strength_validation",
        "prediction_delta_history",
        "replay_outcome_calibration",
    ):
        if expected_blocker not in report.get("blocks_before_warroom_widget_implementation", []):
            failures.append(f"missing widget blocker: {expected_blocker}")
    _assert_false_boundaries(report, failures)
    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing Q17A input should block")
    if "q17a_checker_version_mismatch" not in blocked.get("source_q17a_validation_failures", []):
        failures.append("missing source checker version failure for empty input")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without input should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit.v1",
        "plan_only=true",
        "warroom_widget_implementation_allowed=false",
        "parameter_apply_allowed=false",
        "parameter_staging_write_allowed=false",
        "ledger_append_allowed=false",
        "broker_private_api_allowed=false",
        "P0 source_quality_cap_and_coverage",
        "P0 calibration_refs_and_signal_strength_validation",
        "P0 prediction_delta_history",
        "P0 replay_outcome_calibration",
        "P1 scenario_trace_confirmation",
        "P1 parameter_candidate_evidence",
        "PS-Q17C: source-quality coverage diagnostic",
        "no_d_hot_actual_read",
        "no_widget_rendering_patch",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "warroom_widget_implementation_allowed=true",
        "parameter_apply_allowed=true",
        "parameter_staging_write_allowed=true",
        "ledger_append_allowed=true",
        "autotrade_trigger_allowed=true",
        "broker_private_api_allowed=true",
        "warroom_ui_trigger_enabled=true",
        "refresh_invocation_allowed=true",
        "scheduler_enabled=true",
    ):
        if forbidden in doc_text:
            failures.append(f"forbidden doc marker present: {forbidden}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {
        "ok": not failures,
        "guard": "ps_q17b_inference_quality_gap_plan_guard",
        "phase": "phase3_inference_quality_gap_plan_before_warroom_widgets",
        "contract": {
            "plan_only": True,
            "source_q17a_required": True,
            "warroom_widget_implementation_allowed": False,
            "no_d_hot_actual_read": True,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_parameter_apply": True,
            "no_parameter_staging_write": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17b_inference_quality_gap_plan_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
