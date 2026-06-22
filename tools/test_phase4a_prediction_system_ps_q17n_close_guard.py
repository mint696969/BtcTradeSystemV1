# path: ./tools/test_phase4a_prediction_system_ps_q17n_close_guard.py
# desc: Close guard for PS-Q17N parameter-candidate evidence contract.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract import CHECKER_VERSION, CONTRACT_ORDER, PARAMETER_REASON_CODES, REQUIRED_PARAMETER_FIELDS, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17N_PARAMETER_CANDIDATE_EVIDENCE_CONTRACT_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract.py",
    "tools/test_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17N_PARAMETER_CANDIDATE_EVIDENCE_CONTRACT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17n_close_guard.py",
}
EXPECTED_CONTRACTS = (
    "parameter_candidate_source_contract",
    "baseline_parameter_reference_contract",
    "candidate_parameter_diff_contract",
    "rollback_threshold_contract",
    "parameter_evidence_completeness_release_gate_contract",
    "warroom_parameter_candidate_explanation_contract",
)
EXPECTED_P0 = (
    "parameter_candidate_source_contract",
    "baseline_parameter_reference_contract",
    "candidate_parameter_diff_contract",
    "rollback_threshold_contract",
    "parameter_evidence_completeness_release_gate_contract",
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
        "parameter_candidate_actual_read_allowed",
        "parameter_candidate_widget_rendering_allowed",
        "parameter_candidate_reliability_claim_allowed",
        "confidence_increase_allowed",
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
    unit_text = _read(UNIT) if UNIT.exists() else ""
    doc_text = _read(DOC) if DOC.exists() else ""

    for marker in (
        "CHECKER = \"ps_q17n_parameter_candidate_evidence_contract\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract.v1\"",
        "PS_Q17B_SOURCE_CHECKER_VERSION",
        "SOURCE_GAP_ID = \"parameter_candidate_evidence\"",
        "CONTRACT_ORDER",
        "REQUIRED_PARAMETER_FIELDS",
        "PARAMETER_REASON_CODES",
        "parameter_candidate_source_contract",
        "baseline_parameter_reference_contract",
        "candidate_parameter_diff_contract",
        "rollback_threshold_contract",
        "parameter_evidence_completeness_release_gate_contract",
        "warroom_parameter_candidate_explanation_contract",
        "blocks_parameter_staging",
        "blocks_parameter_apply",
        "blocks_confidence_increase",
        "blocks_warroom_parameter_candidate_widget_reliability",
        "baseline_candidate_rollback_evidence_required_before_staging",
        "parameter_candidate_actual_read_allowed",
        "parameter_candidate_widget_rendering_allowed",
        "parameter_candidate_reliability_claim_allowed",
        "confidence_increase_allowed",
        "parameter_tuning_allowed",
        "PS-Q17O parameter-candidate evidence adapter",
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
    if "test_ps_q17n_builds_parameter_candidate_contract_from_q17b_gap" not in unit_text:
        failures.append("unit test must cover Q17B parameter gap to contract")
    if "test_ps_q17n_blocks_invalid_or_wrong_priority_q17b_report" not in unit_text:
        failures.append("unit test must cover invalid/wrong priority Q17B blocking")

    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract.v1":
        failures.append("checker version mismatch")
    if tuple(CONTRACT_ORDER) != EXPECTED_CONTRACTS:
        failures.append("contract order mismatch")
    for reason in (
        "parameter_candidate_comparison_widget=partial",
        "baseline_candidate_rollback_comparison_not_confirmed",
        "baseline_parameter_reference_missing_or_unverified",
        "candidate_parameter_diff_missing_or_unverified",
        "rollback_threshold_missing_or_unverified",
        "adapter_stage_no_parameter_staging_or_apply",
    ):
        if reason not in PARAMETER_REASON_CODES:
            failures.append(f"parameter reason code missing: {reason}")
    for field in (
        "parameter_candidate.source_artifact_ref",
        "parameter_candidate.generated_at",
        "parameter_candidate.baseline.ref_id",
        "parameter_candidate.baseline.parameter_set_id",
        "parameter_candidate.candidate.candidate_id",
        "parameter_candidate.candidate.changed_parameter_keys",
        "parameter_candidate.candidate.expected_effect_summary",
        "parameter_candidate.evidence.source_quality_ref_id",
        "parameter_candidate.evidence.calibration_ref_id",
        "parameter_candidate.evidence.replay_feedback_ref_id",
        "parameter_candidate.rollback.rollback_threshold_ref_id",
        "parameter_candidate.rollback.rollback_condition_summary",
        "parameter_candidate_release_gate.evidence_complete",
        "parameter_candidate_release_gate.parameter_staging_allowed",
        "parameter_candidate_release_gate.parameter_apply_allowed",
    ):
        if field not in REQUIRED_PARAMETER_FIELDS:
            failures.append(f"required parameter field missing: {field}")

    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture contract should be ok: {report}")
    if report.get("stage") != "parameter_candidate_evidence_contract_before_staging_apply_confidence_and_widget_release":
        failures.append("stage mismatch")
    if report.get("source_q17b_report_valid") is not True:
        failures.append("observed fixture source Q17B should validate")
    if report.get("source_gap_id") != "parameter_candidate_evidence":
        failures.append("source gap id mismatch")
    if report.get("contract_count") != 6:
        failures.append("expected six contracts")
    if report.get("p0_contract_count") != 5:
        failures.append("expected five P0 contracts")
    if report.get("p1_contract_count") != 1:
        failures.append("expected one P1 contract")
    if report.get("recommended_first_validation") != "parameter_candidate_source_contract":
        failures.append("recommended first validation mismatch")
    if report.get("baseline_candidate_rollback_evidence_required_before_staging") is not True:
        failures.append("baseline/candidate/rollback evidence flag must be true")

    contract_ids = [row.get("contract_id") for row in report.get("contract_rows", [])]
    priorities = {row.get("contract_id"): row.get("priority") for row in report.get("contract_rows", [])}
    for contract_id in EXPECTED_CONTRACTS:
        if contract_id not in contract_ids:
            failures.append(f"missing contract row: {contract_id}")
        if contract_id not in report.get("blocks_parameter_staging", []):
            failures.append(f"expected staging blocker: {contract_id}")
        if contract_id not in report.get("blocks_parameter_apply", []):
            failures.append(f"expected apply blocker: {contract_id}")
        if contract_id not in report.get("blocks_warroom_parameter_candidate_widget_reliability", []):
            failures.append(f"expected WarRoom candidate widget reliability blocker: {contract_id}")
    for contract_id in EXPECTED_P0:
        if priorities.get(contract_id) != "P0":
            failures.append(f"expected P0 contract: {contract_id}")
        if contract_id not in report.get("blocks_confidence_increase", []):
            failures.append(f"expected confidence blocker: {contract_id}")
    if priorities.get("warroom_parameter_candidate_explanation_contract") != "P1":
        failures.append("expected WarRoom parameter candidate explanation to be P1")
    if "warroom_parameter_candidate_explanation_contract" in report.get("blocks_confidence_increase", []):
        failures.append("WarRoom explanation contract should not be a confidence blocker")
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

    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.v1",
        "source_gap_id=parameter_candidate_evidence",
        "contract_only=true",
        "diagnostic_only=true",
        "plan_only=true",
        "warroom_widget_implementation_allowed=false",
        "parameter_candidate_actual_read_allowed=false",
        "parameter_candidate_widget_rendering_allowed=false",
        "parameter_candidate_reliability_claim_allowed=false",
        "confidence_increase_allowed=false",
        "parameter_tuning_allowed=false",
        "d_hot_actual_read_allowed=false",
        "parameter_apply_allowed=false",
        "parameter_staging_write_allowed=false",
        "P0 parameter_candidate_source_contract",
        "P0 baseline_parameter_reference_contract",
        "P0 candidate_parameter_diff_contract",
        "P0 rollback_threshold_contract",
        "P0 parameter_evidence_completeness_release_gate_contract",
        "P1 warroom_parameter_candidate_explanation_contract",
        "parameter_candidate.source_artifact_ref",
        "parameter_candidate.baseline.ref_id",
        "parameter_candidate.candidate.changed_parameter_keys",
        "parameter_candidate.rollback.rollback_threshold_ref_id",
        "parameter_candidate_release_gate.parameter_staging_allowed",
        "parameter_candidate_release_gate.parameter_apply_allowed",
        "baseline_candidate_rollback_evidence_required_before_staging=true",
        "parameter_staging_write_allowed=false until baseline, candidate diff, rollback, source-quality, calibration, and replay evidence are complete",
        "no_parameter_candidate_actual_read",
        "no_live_parameter_candidate_evaluation",
        "PS-Q17O: parameter-candidate evidence adapter",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "warroom_widget_implementation_allowed=true",
        "parameter_candidate_actual_read_allowed=true",
        "parameter_candidate_widget_rendering_allowed=true",
        "parameter_candidate_reliability_claim_allowed=true",
        "confidence_increase_allowed=true",
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
        "guard": "ps_q17n_close_guard",
        "phase": "phase3_parameter_candidate_evidence_contract_closed_before_staging_apply_confidence_and_widget_release",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17n_closed": not failures,
            "contract_only": True,
            "source_q17b_required": True,
            "warroom_widget_design_premise": True,
            "warroom_widget_implementation_allowed": False,
            "parameter_candidate_actual_read_allowed": False,
            "parameter_candidate_widget_rendering_allowed": False,
            "parameter_candidate_reliability_claim_allowed": False,
            "confidence_increase_allowed": False,
            "parameter_tuning_allowed": False,
            "parameter_staging_write_allowed": False,
            "parameter_apply_allowed": False,
            "no_d_hot_actual_read": True,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
            "next_slice": "PS-Q17O parameter-candidate evidence adapter or WarRoom prediction widget integration design checkpoint",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17n_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
