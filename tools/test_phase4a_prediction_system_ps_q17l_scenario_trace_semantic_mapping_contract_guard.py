# path: ./tools/test_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract_guard.py
# desc: Focused guard for PS-Q17L scenario-trace semantic mapping contract.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract import CHECKER_VERSION, CONTRACT_ORDER, REQUIRED_TRACE_FIELDS, TRACE_REASON_CODES, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17L_SCENARIO_TRACE_SEMANTIC_MAPPING_CONTRACT_2026-06-22.md"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract.py",
    "tools/test_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17L_SCENARIO_TRACE_SEMANTIC_MAPPING_CONTRACT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17l_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract_guard.py",
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
        "scenario_trace_actual_read_allowed",
        "scenario_trace_widget_rendering_allowed",
        "scenario_trace_reliability_claim_allowed",
        "evidence_weighting_reliability_claim_allowed",
        "invalidation_rewrite_reliability_claim_allowed",
        "scenario_switch_reliability_claim_allowed",
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
        "CHECKER = \"ps_q17l_scenario_trace_semantic_mapping_contract\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract.v1\"",
        "SOURCE_GAP_ID = \"scenario_trace_confirmation\"",
        "CONTRACT_ORDER",
        "REQUIRED_TRACE_FIELDS",
        "TRACE_REASON_CODES",
        "scenario_trace_source_key_contract",
        "evidence_weighting_trace_semantic_contract",
        "invalidation_rewrite_trace_semantic_contract",
        "scenario_switch_trace_semantic_contract",
        "warroom_scenario_trace_release_gate_contract",
        "operator_explanation_trace_taxonomy_contract",
        "semantic_mapping_required_before_reliability_claim",
        "scenario_trace_actual_read_allowed",
        "scenario_trace_widget_rendering_allowed",
        "scenario_trace_reliability_claim_allowed",
        "evidence_weighting_reliability_claim_allowed",
        "invalidation_rewrite_reliability_claim_allowed",
        "scenario_switch_reliability_claim_allowed",
        "PS-Q17M scenario-trace semantic mapping adapter",
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
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract.v1":
        failures.append("checker version mismatch")
    if tuple(CONTRACT_ORDER) != (
        "scenario_trace_source_key_contract",
        "evidence_weighting_trace_semantic_contract",
        "invalidation_rewrite_trace_semantic_contract",
        "scenario_switch_trace_semantic_contract",
        "warroom_scenario_trace_release_gate_contract",
        "operator_explanation_trace_taxonomy_contract",
    ):
        failures.append("contract order mismatch")
    for reason in (
        "evidence_weighting_trace_present=false",
        "invalidation_rewrite_trace_present=false",
        "scenario_switch_trace_present=false",
        "scenario_trace_keys_present_but_ps_q11_trace_names_not_confirmed",
        "semantic_mapping_missing_or_unverified",
    ):
        if reason not in TRACE_REASON_CODES:
            failures.append(f"trace reason code missing: {reason}")
    for field in (
        "scenario_trace.source_artifact_ref",
        "scenario_trace.scenario_core.scenario_trace_keys",
        "scenario_trace.semantic_mapping.evidence_weighting_trace_key",
        "scenario_trace.semantic_mapping.invalidation_rewrite_trace_key",
        "scenario_trace.semantic_mapping.scenario_switch_trace_key",
        "warroom_scenario_trace_release_gate.render_allowed",
    ):
        if field not in REQUIRED_TRACE_FIELDS:
            failures.append(f"required trace field missing: {field}")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture should produce ok contract: {report}")
    if report.get("contract_count") != 6:
        failures.append("expected six contract rows")
    if report.get("p0_contract_count") != 5:
        failures.append("expected five P0 contracts")
    if report.get("p1_contract_count") != 1:
        failures.append("expected one P1 contract")
    if report.get("recommended_first_validation") != "scenario_trace_source_key_contract":
        failures.append("recommended first validation mismatch")
    if report.get("semantic_mapping_required_before_reliability_claim") is not True:
        failures.append("semantic mapping required flag must be true")
    for contract_id in CONTRACT_ORDER:
        if contract_id not in [row.get("contract_id") for row in report.get("contract_rows", [])]:
            failures.append(f"missing contract row: {contract_id}")
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
        "checker=check_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.v1",
        "source_gap_id=scenario_trace_confirmation",
        "contract_only=true",
        "diagnostic_only=true",
        "plan_only=true",
        "warroom_widget_implementation_allowed=false",
        "scenario_trace_actual_read_allowed=false",
        "scenario_trace_widget_rendering_allowed=false",
        "scenario_trace_reliability_claim_allowed=false",
        "evidence_weighting_reliability_claim_allowed=false",
        "invalidation_rewrite_reliability_claim_allowed=false",
        "scenario_switch_reliability_claim_allowed=false",
        "P0 scenario_trace_source_key_contract",
        "P0 evidence_weighting_trace_semantic_contract",
        "P0 invalidation_rewrite_trace_semantic_contract",
        "P0 scenario_switch_trace_semantic_contract",
        "P0 warroom_scenario_trace_release_gate_contract",
        "P1 operator_explanation_trace_taxonomy_contract",
        "scenario_trace.semantic_mapping.evidence_weighting_trace_key",
        "warroom_scenario_trace_release_gate.render_allowed",
        "no_scenario_trace_actual_read",
        "PS-Q17M: scenario-trace semantic mapping adapter",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "warroom_widget_implementation_allowed=true",
        "scenario_trace_actual_read_allowed=true",
        "scenario_trace_widget_rendering_allowed=true",
        "scenario_trace_reliability_claim_allowed=true",
        "evidence_weighting_reliability_claim_allowed=true",
        "invalidation_rewrite_reliability_claim_allowed=true",
        "scenario_switch_reliability_claim_allowed=true",
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
    result = {"ok": not failures, "guard": "ps_q17l_scenario_trace_semantic_mapping_contract_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17l_scenario_trace_semantic_mapping_contract_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
