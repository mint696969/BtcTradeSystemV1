# path: ./tools/test_phase4a_prediction_system_ps_q17g_calibration_reference_adapter_guard.py
# desc: Focused guard for PS-Q17G calibration reference adapter.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17g_calibration_reference_adapter import ADAPTER_VERSION, CHECKER_VERSION, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17g_calibration_reference_adapter.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17g_calibration_reference_adapter.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17G_CALIBRATION_REFERENCE_ADAPTER_2026-06-22.md"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17g_calibration_reference_adapter.py",
    "tools/test_phase4a_prediction_system_ps_q17g_calibration_reference_adapter.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17G_CALIBRATION_REFERENCE_ADAPTER_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17g_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17g_calibration_reference_adapter_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in ("read_only", "non_executing", "adapter_only", "contract_only", "diagnostic_only", "warroom_widget_design_premise"):
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
        "CHECKER = \"ps_q17g_calibration_reference_adapter\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17g_calibration_reference_adapter.v1\"",
        "ADAPTER_VERSION = \"calibration_reference_adapter.v1\"",
        "PS_Q17F_SOURCE_CHECKER_VERSION",
        "adapt_calibration_refs",
        "calibration_release_gate",
        "warroom_calibration_explanation_packet",
        "confidence_band_claim_allowed",
        "signal_reliability_claim_allowed",
        "parameter_tuning_allowed",
        "d_hot_actual_read_allowed",
        "PS-Q17H prediction-delta history contract",
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
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17g_calibration_reference_adapter.v1":
        failures.append("checker version mismatch")
    if ADAPTER_VERSION != "calibration_reference_adapter.v1":
        failures.append("adapter version mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture adapter should be ok: {report}")
    if report.get("adapter_valid") is not True:
        failures.append("adapter must validate")
    packet = report.get("adapted_packet", {})
    for key in ("calibration_ref_id", "sample_window", "calibration_refs", "calibration_release_gate", "warroom_calibration_explanation_packet", "contract_completeness"):
        if key not in packet:
            failures.append(f"adapted packet missing: {key}")
    release = packet.get("calibration_release_gate", {})
    if release.get("calibration_refs_present") is not True:
        failures.append("fixture refs should normalize as present")
    for key in ("confidence_band_claim_allowed", "signal_reliability_claim_allowed", "parameter_tuning_allowed"):
        if release.get(key) is not False:
            failures.append(f"release gate must keep false: {key}")
    if packet.get("warroom_calibration_explanation_packet", {}).get("render_allowed") is not False:
        failures.append("warroom calibration explanation render must remain false")
    _assert_false_boundaries(report, failures)
    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing Q17F source/refs should block")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17g_calibration_reference_adapter.v1",
        "adapter_version=calibration_reference_adapter.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17f_calibration_reference_contract.v1",
        "adapter_only=true",
        "contract_only=true",
        "warroom_widget_implementation_allowed=false",
        "confidence_increase_allowed=false",
        "signal_reliability_claim_allowed=false",
        "parameter_tuning_allowed=false",
        "d_hot_actual_read_allowed=false",
        "calibration_refs.signal_strength.model_version",
        "calibration_refs.reference_hit_rate.sample_count",
        "calibration_release_gate.confidence_band_claim_allowed=false",
        "calibration_release_gate.parameter_tuning_allowed=false",
        "warroom_calibration_explanation_packet.render_allowed=false",
        "no_d_hot_actual_read",
        "no_signal_reliability_claim",
        "PS-Q17H: prediction-delta history contract",
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
        "guard": "ps_q17g_calibration_reference_adapter_guard",
        "phase": "phase3_calibration_reference_adapter_before_release_and_widget_rendering",
        "contract": {
            "adapter_only": True,
            "source_q17f_required": True,
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


def test_ps_q17g_calibration_reference_adapter_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
