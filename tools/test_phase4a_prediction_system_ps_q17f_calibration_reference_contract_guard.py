# path: ./tools/test_phase4a_prediction_system_ps_q17f_calibration_reference_contract_guard.py
# desc: Focused guard for PS-Q17F calibration reference contract.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17f_calibration_reference_contract import CHECKER_VERSION, CONTRACT_ORDER, REQUIRED_CALIBRATION_FIELDS, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17f_calibration_reference_contract.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17f_calibration_reference_contract.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17F_CALIBRATION_REFERENCE_CONTRACT_2026-06-22.md"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17f_calibration_reference_contract.py",
    "tools/test_phase4a_prediction_system_ps_q17f_calibration_reference_contract.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17F_CALIBRATION_REFERENCE_CONTRACT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17f_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17f_calibration_reference_contract_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in ("read_only", "non_executing", "contract_only", "diagnostic_only", "plan_only", "warroom_widget_design_premise"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
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
        "CHECKER = \"ps_q17f_calibration_reference_contract\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17f_calibration_reference_contract.v1\"",
        "PS_Q17B_SOURCE_CHECKER_VERSION",
        "SOURCE_GAP_ID = \"calibration_refs_and_signal_strength_validation\"",
        "CONTRACT_ORDER",
        "REQUIRED_CALIBRATION_FIELDS",
        "SIGNAL_BANDS",
        "REFERENCE_HIT_RATE_BANDS",
        "signal_strength_calibration_reference_contract",
        "reference_hit_rate_calibration_reference_contract",
        "calibration_sample_window_contract",
        "confidence_band_release_contract",
        "parameter_candidate_calibration_dependency_contract",
        "warroom_calibration_explanation_contract",
        "signal_reliability_claim_allowed",
        "parameter_tuning_allowed",
        "PS-Q17G calibration reference adapter",
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
        "append_decision(",
        "append_command(",
        "send_order(",
        "create_order(",
    ):
        if forbidden in tool_text:
            failures.append(f"forbidden tool token: {forbidden}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17f_calibration_reference_contract.v1":
        failures.append("checker version mismatch")
    if tuple(CONTRACT_ORDER) != (
        "signal_strength_calibration_reference_contract",
        "reference_hit_rate_calibration_reference_contract",
        "calibration_sample_window_contract",
        "confidence_band_release_contract",
        "parameter_candidate_calibration_dependency_contract",
        "warroom_calibration_explanation_contract",
    ):
        failures.append("contract order mismatch")
    for field in (
        "calibration_refs.signal_strength.model_version",
        "calibration_refs.signal_strength.sample_count",
        "calibration_refs.reference_hit_rate.model_version",
        "calibration_refs.reference_hit_rate.sample_count",
        "calibration_release_gate.confidence_band_claim_allowed",
        "calibration_release_gate.parameter_tuning_allowed",
    ):
        if field not in REQUIRED_CALIBRATION_FIELDS:
            failures.append(f"required calibration field missing: {field}")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture should produce ok contract: {report}")
    if report.get("contract_count") != 6:
        failures.append("expected six contract rows")
    if report.get("p0_contract_count") != 4:
        failures.append("expected four P0 contracts")
    if report.get("p1_contract_count") != 2:
        failures.append("expected two P1 contracts")
    if report.get("recommended_first_validation") != "signal_strength_calibration_reference_contract":
        failures.append("recommended first validation mismatch")
    if report.get("calibration_refs_required_before_confidence_claim") is not True:
        failures.append("calibration refs must be required before confidence claim")
    for contract_id in CONTRACT_ORDER:
        if contract_id not in [row.get("contract_id") for row in report.get("contract_rows", [])]:
            failures.append(f"missing contract row: {contract_id}")
    for contract_id in (
        "signal_strength_calibration_reference_contract",
        "reference_hit_rate_calibration_reference_contract",
        "calibration_sample_window_contract",
        "confidence_band_release_contract",
    ):
        if contract_id not in report.get("blocks_confidence_increase", []):
            failures.append(f"missing confidence blocker: {contract_id}")
    for row in report.get("contract_rows", []):
        if row.get("state") != "required":
            failures.append(f"contract row should stay required: {row}")
        if row.get("read_only") is not True or row.get("write_or_apply_allowed") is not False:
            failures.append(f"contract row boundary mismatch: {row}")
        if not str(row.get("next_validation", "")).endswith("_guard"):
            failures.append(f"next validation should be guard: {row}")
    _assert_false_boundaries(report, failures)
    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing Q17B source should block")
    if blocked.get("contract_rows"):
        failures.append("blocked report must not emit contract rows")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17f_calibration_reference_contract.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.v1",
        "source_gap_id=calibration_refs_and_signal_strength_validation",
        "contract_only=true",
        "diagnostic_only=true",
        "plan_only=true",
        "warroom_widget_implementation_allowed=false",
        "confidence_increase_allowed=false",
        "signal_reliability_claim_allowed=false",
        "parameter_tuning_allowed=false",
        "P0 signal_strength_calibration_reference_contract",
        "P0 reference_hit_rate_calibration_reference_contract",
        "P0 calibration_sample_window_contract",
        "P0 confidence_band_release_contract",
        "P1 parameter_candidate_calibration_dependency_contract",
        "P1 warroom_calibration_explanation_contract",
        "calibration_refs.signal_strength.model_version",
        "calibration_refs.reference_hit_rate.sample_count",
        "calibration_release_gate.confidence_band_claim_allowed",
        "calibration_release_gate.parameter_tuning_allowed",
        "no_parameter_tuning",
        "no_signal_reliability_claim",
        "PS-Q17G: calibration reference adapter",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "warroom_widget_implementation_allowed=true",
        "confidence_increase_allowed=true",
        "signal_reliability_claim_allowed=true",
        "parameter_tuning_allowed=true",
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
        "guard": "ps_q17f_calibration_reference_contract_guard",
        "phase": "phase3_calibration_reference_contract_before_confidence_and_parameter_tuning",
        "contract": {
            "contract_only": True,
            "source_q17b_required": True,
            "warroom_widget_implementation_allowed": False,
            "confidence_increase_allowed": False,
            "signal_reliability_claim_allowed": False,
            "parameter_tuning_allowed": False,
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


def test_ps_q17f_calibration_reference_contract_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
