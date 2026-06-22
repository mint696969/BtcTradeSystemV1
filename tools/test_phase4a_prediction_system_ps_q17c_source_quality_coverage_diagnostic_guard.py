# path: ./tools/test_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic_guard.py
# desc: Focused guard for PS-Q17C source-quality coverage diagnostic.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic import CHECKER_VERSION, DIAGNOSTIC_ORDER, REQUIRED_SOURCE_QUALITY_FIELDS, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17C_SOURCE_QUALITY_COVERAGE_DIAGNOSTIC_2026-06-22.md"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic.py",
    "tools/test_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17C_SOURCE_QUALITY_COVERAGE_DIAGNOSTIC_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17c_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in ("read_only", "non_executing", "diagnostic_only", "plan_only", "warroom_widget_design_premise"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
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
        "CHECKER = \"ps_q17c_source_quality_coverage_diagnostic\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic.v1\"",
        "PS_Q17B_SOURCE_CHECKER_VERSION",
        "SOURCE_QUALITY_GAP_ID = \"source_quality_cap_and_coverage\"",
        "DIAGNOSTIC_ORDER",
        "OBSERVED_WARNING_TAXONOMY",
        "REQUIRED_SOURCE_QUALITY_FIELDS",
        "tier0_source_quality_gate_coverage",
        "source_quality_warning_taxonomy",
        "source_artifact_coverage_mapping",
        "signal_strength_cap_reason_accounting",
        "basis_and_cross_venue_reference_requirements",
        "context_profile_minimum_source_requirements",
        "confidence_increase_allowed",
        "d_hot_actual_read_allowed",
        "PS-Q17D tier0 source-quality gate coverage contract",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    for forbidden in (
        "from pathlib import Path",
        "read_text(",
        "write_text(",
        "write_bytes(",
        "open(",
        "mkdir(",
        "unlink(",
        "replace(",
        "data_read",
        "data_slice",
        "allow_actual_read=True",
        "build_report(hot_root=",
        "build_prediction_warroom_bounded_manual_refresh_runner(",
        "build_prediction_warroom_latest_payload_actual_export_runner(",
        "append_decision(",
        "append_command(",
        "send_order(",
        "create_order(",
    ):
        if forbidden in tool_text:
            failures.append(f"forbidden tool token: {forbidden}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic.v1":
        failures.append("checker version mismatch")
    if tuple(DIAGNOSTIC_ORDER) != (
        "tier0_source_quality_gate_coverage",
        "source_quality_warning_taxonomy",
        "source_artifact_coverage_mapping",
        "signal_strength_cap_reason_accounting",
        "basis_and_cross_venue_reference_requirements",
        "context_profile_minimum_source_requirements",
    ):
        failures.append("diagnostic order mismatch")
    if "tier0_source_quality_gate.state" not in REQUIRED_SOURCE_QUALITY_FIELDS:
        failures.append("required source-quality gate state field missing")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture should produce ok diagnostic: {report}")
    if report.get("diagnostic_count") != 6:
        failures.append("expected six diagnostic rows")
    if report.get("p0_diagnostic_count", 0) < 4:
        failures.append("expected at least four P0 diagnostics")
    if report.get("recommended_first_validation") != "tier0_source_quality_gate_coverage":
        failures.append("recommended first validation should be tier0_source_quality_gate_coverage")
    for diagnostic_id in DIAGNOSTIC_ORDER:
        if diagnostic_id not in [row.get("diagnostic_id") for row in report.get("diagnostic_rows", [])]:
            failures.append(f"missing diagnostic row: {diagnostic_id}")
    for expected_blocker in (
        "tier0_source_quality_gate_coverage",
        "source_quality_warning_taxonomy",
        "source_artifact_coverage_mapping",
        "signal_strength_cap_reason_accounting",
    ):
        if expected_blocker not in report.get("blocks_confidence_increase", []):
            failures.append(f"missing confidence blocker: {expected_blocker}")
    for row in report.get("diagnostic_rows", []):
        if row.get("state") != "open":
            failures.append(f"diagnostic row should stay open: {row}")
        if row.get("read_only") is not True or row.get("write_or_apply_allowed") is not False:
            failures.append(f"diagnostic row boundary mismatch: {row}")
        if not str(row.get("next_validation", "")).endswith("_guard"):
            failures.append(f"next validation should be guard: {row}")
    _assert_false_boundaries(report, failures)
    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing Q17B source should block")
    if blocked.get("diagnostic_rows"):
        failures.append("blocked report must not emit diagnostics")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.v1",
        "source_quality_gap_id=source_quality_cap_and_coverage",
        "diagnostic_only=true",
        "plan_only=true",
        "warroom_widget_implementation_allowed=false",
        "confidence_increase_allowed=false",
        "d_hot_actual_read_allowed=false",
        "P0 tier0_source_quality_gate_coverage",
        "P0 source_quality_warning_taxonomy",
        "P0 source_artifact_coverage_mapping",
        "P0 signal_strength_cap_reason_accounting",
        "P1 basis_and_cross_venue_reference_requirements",
        "P1 context_profile_minimum_source_requirements",
        "tier0_source_quality_gate_not_passed",
        "basis_blocker:bitflyer_spot_reference_missing",
        "tier0_source_quality_gate.state",
        "source_artifact_coverage.by_family",
        "signal_strength_cap_reason.by_record",
        "no_d_hot_actual_read",
        "no_confidence_increase",
        "PS-Q17D: tier0 source-quality gate coverage contract",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "warroom_widget_implementation_allowed=true",
        "confidence_increase_allowed=true",
        "d_hot_actual_read_allowed=true",
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
        "guard": "ps_q17c_source_quality_coverage_diagnostic_guard",
        "phase": "phase3_source_quality_coverage_diagnostic_before_confidence_increase",
        "contract": {
            "diagnostic_only": True,
            "source_q17b_required": True,
            "warroom_widget_implementation_allowed": False,
            "confidence_increase_allowed": False,
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


def test_ps_q17c_source_quality_coverage_diagnostic_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
