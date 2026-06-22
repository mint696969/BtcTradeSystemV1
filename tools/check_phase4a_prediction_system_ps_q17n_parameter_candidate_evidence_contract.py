# path: ./tools/check_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract.py
# desc: PS-Q17N non-executing parameter-candidate evidence contract. It consumes a PS-Q17B gap plan report or its observed fixture and emits required baseline/candidate/rollback/evidence contracts before parameter staging, parameter apply, confidence increase, or WarRoom parameter-candidate widget reliability. It never reads D-hot, writes artifacts, invokes refresh, renders WarRoom widgets, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import CHECKER_VERSION as PS_Q17B_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import build_report as build_ps_q17b_report

CHECKER = "ps_q17n_parameter_candidate_evidence_contract"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17n_parameter_candidate_evidence_contract.v1"
PS_Q17B_SOURCE_CHECKER_VERSION = PS_Q17B_CHECKER_VERSION
SOURCE_GAP_ID = "parameter_candidate_evidence"

CONTRACT_ORDER = (
    "parameter_candidate_source_contract",
    "baseline_parameter_reference_contract",
    "candidate_parameter_diff_contract",
    "rollback_threshold_contract",
    "parameter_evidence_completeness_release_gate_contract",
    "warroom_parameter_candidate_explanation_contract",
)

REQUIRED_PARAMETER_FIELDS = (
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
)

PARAMETER_REASON_CODES = (
    "parameter_candidate_comparison_widget=partial",
    "baseline_candidate_rollback_comparison_not_confirmed",
    "baseline_parameter_reference_missing_or_unverified",
    "candidate_parameter_diff_missing_or_unverified",
    "rollback_threshold_missing_or_unverified",
    "adapter_stage_no_parameter_staging_or_apply",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _gap_map(report: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for row in _as_list(report.get("plan_rows")):
        item = _as_mapping(row)
        gap_id = str(item.get("gap_id") or "")
        if gap_id:
            result[gap_id] = item
    return result


def _safe_q17b_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17B_SOURCE_CHECKER_VERSION:
        failures.append("q17b_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17b_report_not_ok")
    if report.get("plan_only") is not True:
        failures.append("q17b_plan_only_missing")
    if report.get("warroom_widget_design_premise") is not True:
        failures.append("q17b_warroom_widget_design_premise_missing")
    if report.get("warroom_widget_implementation_allowed") is not False:
        failures.append("q17b_widget_implementation_boundary_not_false")
    for key in (
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
            failures.append(f"q17b_boundary_not_false:{key}")
    gap = _gap_map(report).get(SOURCE_GAP_ID, {})
    if not gap:
        failures.append("parameter_candidate_evidence_gap_missing")
    elif gap.get("priority") != "P1":
        failures.append("parameter_candidate_evidence_gap_not_p1")
    return not failures, failures


def _contract_row(contract_id: str, priority: str, required_fields: list[str], validation_rule: str) -> dict[str, Any]:
    return {
        "contract_id": contract_id,
        "priority": priority,
        "state": "required",
        "required_fields": required_fields,
        "validation_rule": validation_rule,
        "blocks_parameter_staging": True,
        "blocks_parameter_apply": True,
        "blocks_confidence_increase": contract_id != "warroom_parameter_candidate_explanation_contract",
        "blocks_warroom_parameter_candidate_widget_reliability": True,
        "next_validation": f"{contract_id}_guard",
        "read_only": True,
        "write_or_apply_allowed": False,
    }


def _build_contract_rows(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    gap = _gap_map(report).get(SOURCE_GAP_ID, {})
    reasons = [str(item) for item in _as_list(gap.get("reasons"))]
    rows = [
        _contract_row("parameter_candidate_source_contract", "P0", [
            "parameter_candidate.source_artifact_ref",
            "parameter_candidate.generated_at",
            "parameter_candidate.candidate.candidate_id",
        ], "parameter candidate source identity must exist before comparison, staging, or WarRoom reliability"),
        _contract_row("baseline_parameter_reference_contract", "P0", [
            "parameter_candidate.baseline.ref_id",
            "parameter_candidate.baseline.parameter_set_id",
            "parameter_candidate.baseline.effective_at",
        ], "baseline parameter reference must be declared before candidate diffs or rollback thresholds are meaningful"),
        _contract_row("candidate_parameter_diff_contract", "P0", [
            "parameter_candidate.candidate.changed_parameter_keys",
            "parameter_candidate.candidate.diff_summary",
            "parameter_candidate.candidate.expected_effect_summary",
        ], "candidate parameter changes must be explicit before operator review or staging"),
        _contract_row("rollback_threshold_contract", "P0", [
            "parameter_candidate.rollback.rollback_threshold_ref_id",
            "parameter_candidate.rollback.rollback_condition_summary",
            "parameter_candidate.rollback.abort_condition_summary",
        ], "rollback and abort thresholds must be declared before staging or apply can be considered"),
        _contract_row("parameter_evidence_completeness_release_gate_contract", "P0", [
            "parameter_candidate_release_gate.evidence_complete",
            "parameter_candidate_release_gate.parameter_staging_allowed",
            "parameter_candidate_release_gate.parameter_apply_allowed",
            "parameter_candidate_release_gate.blocking_reason_codes",
        ], "parameter staging/apply and confidence increase remain false until baseline, candidate, rollback, calibration, source-quality, and replay evidence are complete"),
        _contract_row("warroom_parameter_candidate_explanation_contract", "P1", [
            "warroom_parameter_candidate_widget.candidate_id",
            "warroom_parameter_candidate_widget.baseline_ref_id",
            "warroom_parameter_candidate_widget.operator_explanation",
            "warroom_parameter_candidate_widget.render_allowed",
        ], "WarRoom may explain parameter candidates later, but rendering/reliability remain deferred"),
    ]
    if reasons:
        rows[0]["source_gap_reasons"] = reasons
    return sorted(rows, key=lambda row: ({"P0": 0, "P1": 1, "P2": 2}.get(str(row["priority"]), 9), CONTRACT_ORDER.index(str(row["contract_id"]))))


def build_report(*, supplied_q17b_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17b_report = _as_mapping(supplied_q17b_report)
    if not q17b_report and use_observed_fixture:
        q17b_report = build_ps_q17b_report(use_observed_fixture=True)
    safe_q17b, validation_failures = _safe_q17b_boundary(q17b_report)
    contract_rows = _build_contract_rows(q17b_report) if safe_q17b else []
    p0_count = sum(1 for row in contract_rows if row.get("priority") == "P0")
    p1_count = sum(1 for row in contract_rows if row.get("priority") == "P1")
    staging_blockers = [row["contract_id"] for row in contract_rows if row.get("blocks_parameter_staging")]
    apply_blockers = [row["contract_id"] for row in contract_rows if row.get("blocks_parameter_apply")]
    confidence_blockers = [row["contract_id"] for row in contract_rows if row.get("blocks_confidence_increase")]
    widget_blockers = [row["contract_id"] for row in contract_rows if row.get("blocks_warroom_parameter_candidate_widget_reliability")]
    ok = bool(safe_q17b and contract_rows and p0_count == 5 and p1_count == 1 and staging_blockers and apply_blockers)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "stage": "parameter_candidate_evidence_contract_before_staging_apply_confidence_and_widget_release",
        "source_checker_version": PS_Q17B_SOURCE_CHECKER_VERSION,
        "source_q17b_report_valid": safe_q17b,
        "source_q17b_validation_failures": validation_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "source_gap_id": SOURCE_GAP_ID,
        "contract_rows": contract_rows,
        "contract_count": len(contract_rows),
        "p0_contract_count": p0_count,
        "p1_contract_count": p1_count,
        "required_parameter_fields": list(REQUIRED_PARAMETER_FIELDS),
        "parameter_reason_codes": list(PARAMETER_REASON_CODES),
        "blocks_parameter_staging": staging_blockers,
        "blocks_parameter_apply": apply_blockers,
        "blocks_confidence_increase": confidence_blockers,
        "blocks_warroom_parameter_candidate_widget_reliability": widget_blockers,
        "baseline_candidate_rollback_evidence_required_before_staging": True,
        "recommended_first_validation": staging_blockers[0] if staging_blockers else "",
        "recommended_next_slice": "PS-Q17O parameter-candidate evidence adapter or WarRoom prediction widget integration design checkpoint; confidence increase, parameter staging/apply, and WarRoom widget rendering remain deferred.",
        "human_interpretation": "PS-Q17N turns the parameter_candidate_evidence P1 gap into explicit source, baseline, candidate diff, rollback threshold, release gate, and WarRoom explanation contracts. It does not stage/apply parameters, render widgets, write artifacts, or trigger generation.",
        "read_only": True,
        "non_executing": True,
        "contract_only": True,
        "diagnostic_only": True,
        "plan_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "parameter_candidate_actual_read_allowed": False,
        "parameter_candidate_widget_rendering_allowed": False,
        "parameter_candidate_reliability_claim_allowed": False,
        "confidence_increase_allowed": False,
        "parameter_tuning_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "d_hot_actual_read_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "warroom_ui_trigger_enabled": False,
        "refresh_invocation_allowed": False,
        "scheduler_enabled": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q17N parameter-candidate evidence contract")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use the static PS-Q17B observed fixture path; no D-hot or parameter-candidate read is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
