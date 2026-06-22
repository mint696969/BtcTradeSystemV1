# path: ./tools/test_phase4a_prediction_system_ps_q17e_close_guard.py
# desc: Close guard for PS-Q17E tier0 source-quality gate contract adapter.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter import ADAPTER_VERSION, BLOCKING_REASON_CODES, CHECKER_VERSION, GATE_STATE_ENUM, REASON_SEVERITY_ENUM, adapt_payload, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17E_TIER0_SOURCE_QUALITY_GATE_CONTRACT_ADAPTER_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter.py",
    "tools/test_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17E_TIER0_SOURCE_QUALITY_GATE_CONTRACT_ADAPTER_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17e_close_guard.py",
}
REQUIRED_PACKET_KEYS = (
    "tier0_source_quality_gate",
    "source_artifact_coverage",
    "signal_strength_cap_reason",
    "confidence_release_gate",
    "contract_completeness",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in (
        "read_only",
        "non_executing",
        "adapter_only",
        "contract_only",
        "diagnostic_only",
        "warroom_widget_design_premise",
    ):
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
    unit_text = _read(UNIT) if UNIT.exists() else ""
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "CHECKER = \"ps_q17e_tier0_source_quality_gate_contract_adapter\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter.v1\"",
        "ADAPTER_VERSION = \"tier0_source_quality_gate_contract_adapter.v1\"",
        "PS_Q17D_SOURCE_CHECKER_VERSION",
        "adapt_payload",
        "_safe_q17d_boundary",
        "_adapter_valid",
        "tier0_source_quality_gate",
        "reason_severity_by_code",
        "operator_action_by_code",
        "source_artifact_coverage",
        "signal_strength_cap_reason",
        "confidence_release_gate",
        "contract_completeness",
        "confidence_increase_allowed",
        "d_hot_actual_read_allowed",
        "PS-Q17F calibration reference contract",
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
    if "test_ps_q17e_adapts_supplied_payload_to_tier0_contract_packet" not in unit_text:
        failures.append("unit test must cover supplied payload adaptation")
    if "test_ps_q17e_blocks_invalid_source_contract_or_missing_payload" not in unit_text:
        failures.append("unit test must cover invalid source/missing payload blocking")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter.v1":
        failures.append("checker version mismatch")
    if ADAPTER_VERSION != "tier0_source_quality_gate_contract_adapter.v1":
        failures.append("adapter version mismatch")
    if tuple(GATE_STATE_ENUM) != ("pass", "warn", "fail", "unknown"):
        failures.append("gate state enum mismatch")
    if tuple(REASON_SEVERITY_ENUM) != ("blocking", "warning", "context_only"):
        failures.append("reason severity enum mismatch")
    if "tier0_source_quality_gate_not_passed" not in BLOCKING_REASON_CODES:
        failures.append("blocking reason codes must include tier0_source_quality_gate_not_passed")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture adapter should be ok: {report}")
    if report.get("stage") != "tier0_source_quality_gate_contract_adapter_before_live_integration":
        failures.append("stage mismatch")
    if report.get("source_q17d_report_valid") is not True:
        failures.append("observed fixture source Q17D should validate")
    if report.get("adapter_valid") is not True:
        failures.append("adapter should validate")
    if report.get("adapter_validation_failures"):
        failures.append(f"adapter validation failures should be empty: {report.get('adapter_validation_failures')}")
    packet = report.get("adapted_packet", {})
    for key in REQUIRED_PACKET_KEYS:
        if key not in packet:
            failures.append(f"adapted packet missing: {key}")
    gate = packet.get("tier0_source_quality_gate", {})
    release = packet.get("confidence_release_gate", {})
    coverage = packet.get("source_artifact_coverage", {})
    cap = packet.get("signal_strength_cap_reason", {})
    completeness = packet.get("contract_completeness", {})
    if gate.get("state") not in GATE_STATE_ENUM:
        failures.append("adapted gate state invalid")
    if not gate.get("reason_codes"):
        failures.append("adapted reason codes missing")
    if not gate.get("reason_severity_by_code"):
        failures.append("adapted reason severity missing")
    if not gate.get("operator_action_by_code"):
        failures.append("adapted operator action missing")
    if int(coverage.get("required_source_count", -1)) < 0 or int(coverage.get("usable_source_count", -1)) < 0 or int(coverage.get("missing_source_count", -1)) < 0:
        failures.append("adapted coverage counts invalid")
    if not cap.get("by_record"):
        failures.append("adapted cap provenance missing")
    if release.get("confidence_increase_allowed") is not False:
        failures.append("adapted confidence increase must remain false")
    if release.get("source_quality_gate_passed") is not False:
        failures.append("observed fixture gate should not pass")
    if not release.get("blocking_reason_codes"):
        failures.append("observed fixture must expose blocking reasons")
    for key in ("has_gate_state", "has_reason_codes", "has_required_usable_counts", "has_cap_provenance", "has_confidence_release_gate"):
        if completeness.get(key) is not True:
            failures.append(f"contract completeness should be true: {key}")
    _assert_false_boundaries(report, failures)
    direct_packet = adapt_payload({
        "forecast_batch": {"records": [{"record_id": "direct", "warnings": ["tier0_source_quality_gate_not_passed"], "values_snapshot": {"estimated_signal_strength_percent": 10}}]},
        "source_artifact_coverage": {"required_source_count": 2, "usable_source_count": 1, "missing_source_count": 1},
    })
    if direct_packet.get("confidence_release_gate", {}).get("confidence_increase_allowed") is not False:
        failures.append("direct adapter confidence increase should remain false")
    if not direct_packet.get("signal_strength_cap_reason", {}).get("by_record"):
        failures.append("direct adapter should emit cap provenance")
    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing Q17D source/payload should block")
    if blocked.get("adapted_packet"):
        failures.append("blocked report must not emit adapted packet")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter.v1",
        "adapter_version=tier0_source_quality_gate_contract_adapter.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract.v1",
        "adapter_only=true",
        "contract_only=true",
        "diagnostic_only=true",
        "warroom_widget_implementation_allowed=false",
        "confidence_increase_allowed=false",
        "d_hot_actual_read_allowed=false",
        "tier0_source_quality_gate.state",
        "tier0_source_quality_gate.reason_severity_by_code",
        "tier0_source_quality_gate.operator_action_by_code",
        "source_artifact_coverage.required_source_count",
        "source_artifact_coverage.usable_source_count",
        "source_artifact_coverage.missing_source_count",
        "signal_strength_cap_reason.by_record",
        "confidence_release_gate.source_quality_gate_passed",
        "confidence_release_gate.confidence_increase_allowed=false",
        "no_d_hot_actual_read",
        "no_confidence_increase",
        "PS-Q17F: calibration reference contract",
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
        "guard": "ps_q17e_close_guard",
        "phase": "phase3_tier0_gate_contract_adapter_closed_before_live_integration",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17e_closed": not failures,
            "adapter_only": True,
            "source_q17d_required": True,
            "warroom_widget_design_premise": True,
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
            "next_slice": "PS-Q17F calibration reference contract or read-only adapter integration design",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17e_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
