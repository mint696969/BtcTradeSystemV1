# path: ./tools/test_phase4a_prediction_system_ps_q17d_close_guard.py
# desc: Close guard for PS-Q17D tier0 source-quality gate coverage contract.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract import CHECKER_VERSION, CONTRACT_ORDER, GATE_STATE_ENUM, REASON_SEVERITY_ENUM, REQUIRED_TIER0_FIELDS, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17D_TIER0_SOURCE_QUALITY_GATE_COVERAGE_CONTRACT_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract.py",
    "tools/test_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17D_TIER0_SOURCE_QUALITY_GATE_COVERAGE_CONTRACT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17d_close_guard.py",
}
EXPECTED_CONTRACTS = (
    "tier0_gate_state_reason_contract",
    "required_usable_source_count_contract",
    "record_cap_provenance_contract",
    "confidence_release_gate_contract",
    "family_horizon_coverage_contract",
    "operator_action_reason_contract",
)
EXPECTED_CONFIDENCE_BLOCKERS = (
    "tier0_gate_state_reason_contract",
    "required_usable_source_count_contract",
    "record_cap_provenance_contract",
    "confidence_release_gate_contract",
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
        "contract_only",
        "diagnostic_only",
        "plan_only",
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
        "CHECKER = \"ps_q17d_tier0_source_quality_gate_coverage_contract\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract.v1\"",
        "PS_Q17C_SOURCE_CHECKER_VERSION",
        "SOURCE_DIAGNOSTIC_ID = \"tier0_source_quality_gate_coverage\"",
        "CONTRACT_ORDER",
        "GATE_STATE_ENUM",
        "REASON_SEVERITY_ENUM",
        "REQUIRED_TIER0_FIELDS",
        "tier0_gate_state_reason_contract",
        "required_usable_source_count_contract",
        "record_cap_provenance_contract",
        "confidence_release_gate_contract",
        "family_horizon_coverage_contract",
        "operator_action_reason_contract",
        "confidence_release_gate.source_quality_gate_passed",
        "confidence_increase_allowed",
        "d_hot_actual_read_allowed",
        "PS-Q17E tier0 gate contract implementation adapter",
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
    if "test_ps_q17d_builds_tier0_gate_contract_from_q17c_diagnostic" not in unit_text:
        failures.append("unit test must cover Q17C diagnostic to tier0 contract")
    if "test_ps_q17d_blocks_invalid_or_nonblocking_q17c_report" not in unit_text:
        failures.append("unit test must cover invalid/nonblocking Q17C blocking")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract.v1":
        failures.append("checker version mismatch")
    if tuple(CONTRACT_ORDER) != EXPECTED_CONTRACTS:
        failures.append("contract order mismatch")
    if tuple(GATE_STATE_ENUM) != ("pass", "warn", "fail", "unknown"):
        failures.append("gate state enum mismatch")
    if tuple(REASON_SEVERITY_ENUM) != ("blocking", "warning", "context_only"):
        failures.append("reason severity enum mismatch")
    for field in (
        "tier0_source_quality_gate.state",
        "tier0_source_quality_gate.reason_codes",
        "tier0_source_quality_gate.reason_severity_by_code",
        "source_artifact_coverage.required_source_count",
        "source_artifact_coverage.usable_source_count",
        "source_artifact_coverage.missing_source_count",
        "signal_strength_cap_reason.by_record",
        "estimated_signal_strength_percent.pre_cap",
        "estimated_signal_strength_percent.post_cap",
        "confidence_release_gate.source_quality_gate_passed",
    ):
        if field not in REQUIRED_TIER0_FIELDS:
            failures.append(f"required tier0 field missing: {field}")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture contract should be ok: {report}")
    if report.get("stage") != "tier0_source_quality_gate_coverage_contract_before_confidence_increase":
        failures.append("stage mismatch")
    if report.get("source_q17c_report_valid") is not True:
        failures.append("observed fixture source Q17C should validate")
    if report.get("source_diagnostic_id") != "tier0_source_quality_gate_coverage":
        failures.append("source diagnostic id mismatch")
    if report.get("contract_count") != 6:
        failures.append("expected six contracts")
    if report.get("p0_contract_count") != 4:
        failures.append("expected four P0 contracts")
    if report.get("p1_contract_count") != 2:
        failures.append("expected two P1 contracts")
    if report.get("recommended_first_validation") != "tier0_gate_state_reason_contract":
        failures.append("recommended first validation mismatch")
    contract_ids = [row.get("contract_id") for row in report.get("contract_rows", [])]
    priorities = {row.get("contract_id"): row.get("priority") for row in report.get("contract_rows", [])}
    for contract_id in EXPECTED_CONTRACTS:
        if contract_id not in contract_ids:
            failures.append(f"missing contract row: {contract_id}")
    for contract_id in EXPECTED_CONFIDENCE_BLOCKERS:
        if priorities.get(contract_id) != "P0":
            failures.append(f"expected P0 contract: {contract_id}")
        if contract_id not in report.get("blocks_confidence_increase", []):
            failures.append(f"expected confidence blocker: {contract_id}")
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
        failures.append("missing Q17C source should block")
    if blocked.get("contract_rows"):
        failures.append("blocked report must not emit contract rows")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic.v1",
        "source_diagnostic_id=tier0_source_quality_gate_coverage",
        "contract_only=true",
        "diagnostic_only=true",
        "plan_only=true",
        "warroom_widget_implementation_allowed=false",
        "confidence_increase_allowed=false",
        "d_hot_actual_read_allowed=false",
        "P0 tier0_gate_state_reason_contract",
        "P0 required_usable_source_count_contract",
        "P0 record_cap_provenance_contract",
        "P0 confidence_release_gate_contract",
        "P1 family_horizon_coverage_contract",
        "P1 operator_action_reason_contract",
        "tier0_source_quality_gate.state",
        "tier0_source_quality_gate.reason_severity_by_code",
        "source_artifact_coverage.missing_source_count",
        "signal_strength_cap_reason.by_record",
        "confidence_release_gate.source_quality_gate_passed",
        "confidence_release_gate.confidence_increase_allowed remains false unless no blocking reason codes remain",
        "gate_state_enum=pass,warn,fail,unknown",
        "reason_severity_enum=blocking,warning,context_only",
        "no_confidence_increase",
        "PS-Q17E: tier0 gate contract implementation adapter",
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
        "guard": "ps_q17d_close_guard",
        "phase": "phase3_tier0_source_quality_gate_contract_closed_before_confidence_increase",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17d_closed": not failures,
            "contract_only": True,
            "source_q17c_required": True,
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
            "next_slice": "PS-Q17E tier0 gate contract implementation adapter or calibration reference contract",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17d_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
