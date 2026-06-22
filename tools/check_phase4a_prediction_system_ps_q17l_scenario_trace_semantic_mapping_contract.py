# path: ./tools/check_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract.py
# desc: PS-Q17L non-executing scenario-trace semantic mapping contract. It consumes a PS-Q17B gap plan report or its observed fixture and emits required semantic contracts before evidence/invalidation/scenario-switch reliability claims. It never reads D-hot, writes artifacts, invokes refresh, renders WarRoom widgets, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import CHECKER_VERSION as PS_Q17B_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import build_report as build_ps_q17b_report

CHECKER = "ps_q17l_scenario_trace_semantic_mapping_contract"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract.v1"
PS_Q17B_SOURCE_CHECKER_VERSION = PS_Q17B_CHECKER_VERSION
SOURCE_GAP_ID = "scenario_trace_confirmation"

CONTRACT_ORDER = (
    "scenario_trace_source_key_contract",
    "evidence_weighting_trace_semantic_contract",
    "invalidation_rewrite_trace_semantic_contract",
    "scenario_switch_trace_semantic_contract",
    "warroom_scenario_trace_release_gate_contract",
    "operator_explanation_trace_taxonomy_contract",
)

REQUIRED_TRACE_FIELDS = (
    "scenario_trace.source_artifact_ref",
    "scenario_trace.scenario_core.scenario_trace_keys",
    "scenario_trace.semantic_mapping.evidence_weighting_trace_key",
    "scenario_trace.semantic_mapping.invalidation_rewrite_trace_key",
    "scenario_trace.semantic_mapping.scenario_switch_trace_key",
    "scenario_trace.semantic_mapping.semantic_confidence_state",
    "scenario_trace.semantic_mapping.unmapped_trace_keys",
    "warroom_scenario_trace_release_gate.evidence_reliability_claim_allowed",
    "warroom_scenario_trace_release_gate.invalidation_reliability_claim_allowed",
    "warroom_scenario_trace_release_gate.scenario_switch_reliability_claim_allowed",
    "warroom_scenario_trace_release_gate.render_allowed",
)

TRACE_REASON_CODES = (
    "evidence_weighting_trace_present=false",
    "invalidation_rewrite_trace_present=false",
    "scenario_switch_trace_present=false",
    "scenario_trace_keys_present_but_ps_q11_trace_names_not_confirmed",
    "semantic_mapping_missing_or_unverified",
    "adapter_stage_no_scenario_trace_reliability_release",
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
        failures.append("scenario_trace_confirmation_gap_missing")
    elif gap.get("priority") != "P1":
        failures.append("scenario_trace_confirmation_gap_not_p1")
    return not failures, failures


def _contract_row(contract_id: str, priority: str, required_fields: list[str], validation_rule: str) -> dict[str, Any]:
    return {
        "contract_id": contract_id,
        "priority": priority,
        "state": "required",
        "required_fields": required_fields,
        "validation_rule": validation_rule,
        "blocks_scenario_trace_reliability_claim": True,
        "blocks_warroom_scenario_trace_widget_reliability": True,
        "blocks_warroom_widget_rendering": contract_id == "warroom_scenario_trace_release_gate_contract",
        "next_validation": f"{contract_id}_guard",
        "read_only": True,
        "write_or_apply_allowed": False,
    }


def _build_contract_rows(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    gap = _gap_map(report).get(SOURCE_GAP_ID, {})
    reasons = [str(item) for item in _as_list(gap.get("reasons"))]
    rows = [
        _contract_row("scenario_trace_source_key_contract", "P0", [
            "scenario_trace.source_artifact_ref",
            "scenario_trace.scenario_core.scenario_trace_keys",
            "scenario_trace.scenario_core.generated_at",
        ], "scenario trace source keys must be declared before semantic mapping or WarRoom reliability claims"),
        _contract_row("evidence_weighting_trace_semantic_contract", "P0", [
            "scenario_trace.semantic_mapping.evidence_weighting_trace_key",
            "scenario_trace.semantic_mapping.evidence_weighting_trace_present",
            "scenario_trace.semantic_mapping.evidence_weighting_semantic_state",
        ], "evidence weighting trace must map to a named key and semantic state before evidence weighting widget reliability"),
        _contract_row("invalidation_rewrite_trace_semantic_contract", "P0", [
            "scenario_trace.semantic_mapping.invalidation_rewrite_trace_key",
            "scenario_trace.semantic_mapping.invalidation_rewrite_trace_present",
            "scenario_trace.semantic_mapping.invalidation_rewrite_semantic_state",
        ], "invalidation rewrite trace must map to a named key and semantic state before invalidation widget reliability"),
        _contract_row("scenario_switch_trace_semantic_contract", "P0", [
            "scenario_trace.semantic_mapping.scenario_switch_trace_key",
            "scenario_trace.semantic_mapping.scenario_switch_trace_present",
            "scenario_trace.semantic_mapping.scenario_switch_semantic_state",
        ], "scenario switch trace must map to a named key and semantic state before scenario trace reliability"),
        _contract_row("warroom_scenario_trace_release_gate_contract", "P0", [
            "warroom_scenario_trace_release_gate.evidence_reliability_claim_allowed",
            "warroom_scenario_trace_release_gate.invalidation_reliability_claim_allowed",
            "warroom_scenario_trace_release_gate.scenario_switch_reliability_claim_allowed",
            "warroom_scenario_trace_release_gate.render_allowed",
            "warroom_scenario_trace_release_gate.blocking_reason_codes",
        ], "WarRoom scenario trace reliability and render remain false until all semantic mappings are verified"),
        _contract_row("operator_explanation_trace_taxonomy_contract", "P1", [
            "scenario_trace.operator_explanation_trace_taxonomy.evidence_label",
            "scenario_trace.operator_explanation_trace_taxonomy.invalidation_label",
            "scenario_trace.operator_explanation_trace_taxonomy.scenario_switch_label",
            "scenario_trace.operator_explanation_trace_taxonomy.unmapped_trace_keys",
        ], "operator-facing explanation labels must exist before scenario trace semantics are displayed as reliable"),
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
    reliability_blockers = [row["contract_id"] for row in contract_rows if row.get("blocks_scenario_trace_reliability_claim")]
    widget_reliability_blockers = [row["contract_id"] for row in contract_rows if row.get("blocks_warroom_scenario_trace_widget_reliability")]
    render_blockers = [row["contract_id"] for row in contract_rows if row.get("blocks_warroom_widget_rendering")]
    ok = bool(safe_q17b and contract_rows and p0_count == 5 and p1_count == 1 and reliability_blockers)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "stage": "scenario_trace_semantic_mapping_contract_before_reliability_and_widget_rendering",
        "source_checker_version": PS_Q17B_SOURCE_CHECKER_VERSION,
        "source_q17b_report_valid": safe_q17b,
        "source_q17b_validation_failures": validation_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "source_gap_id": SOURCE_GAP_ID,
        "contract_rows": contract_rows,
        "contract_count": len(contract_rows),
        "p0_contract_count": p0_count,
        "p1_contract_count": p1_count,
        "required_trace_fields": list(REQUIRED_TRACE_FIELDS),
        "trace_reason_codes": list(TRACE_REASON_CODES),
        "blocks_scenario_trace_reliability_claim": reliability_blockers,
        "blocks_warroom_scenario_trace_widget_reliability": widget_reliability_blockers,
        "blocks_warroom_widget_rendering": render_blockers,
        "semantic_mapping_required_before_reliability_claim": True,
        "recommended_first_validation": reliability_blockers[0] if reliability_blockers else "",
        "recommended_next_slice": "PS-Q17M scenario-trace semantic mapping adapter or parameter-candidate evidence contract; confidence increase, parameter apply, and WarRoom widget rendering remain deferred.",
        "human_interpretation": "PS-Q17L turns the scenario_trace_confirmation P1 gap into explicit source-key, evidence, invalidation, scenario-switch, release-gate, and operator explanation contracts. It does not read D-hot, infer semantics live, render widgets, write artifacts, or trigger generation.",
        "read_only": True,
        "non_executing": True,
        "contract_only": True,
        "diagnostic_only": True,
        "plan_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "scenario_trace_actual_read_allowed": False,
        "scenario_trace_widget_rendering_allowed": False,
        "scenario_trace_reliability_claim_allowed": False,
        "evidence_weighting_reliability_claim_allowed": False,
        "invalidation_rewrite_reliability_claim_allowed": False,
        "scenario_switch_reliability_claim_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17L scenario-trace semantic mapping contract")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use the static PS-Q17B observed fixture path; no D-hot or scenario-trace read is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
