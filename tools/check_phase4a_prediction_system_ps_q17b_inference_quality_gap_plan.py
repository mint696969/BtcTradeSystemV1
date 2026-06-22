# path: ./tools/check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.py
# desc: PS-Q17B non-executing inference quality gap plan. It consumes a PS-Q17A audit report or a static observed fixture and emits prioritized engine-quality gaps before WarRoom widget implementation. It never reads D-hot, writes artifacts, stages/applies parameters, invokes refresh, registers schedulers, triggers WarRoom UI, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17a_prediction_engine_real_output_readiness_audit import CHECKER_VERSION as PS_Q17A_CHECKER_VERSION

CHECKER = "ps_q17b_inference_quality_gap_plan"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan.v1"
PS_Q17A_SOURCE_CHECKER_VERSION = PS_Q17A_CHECKER_VERSION

TARGET_GAP_ORDER = (
    "source_quality_cap_and_coverage",
    "calibration_refs_and_signal_strength_validation",
    "prediction_delta_history",
    "scenario_trace_confirmation",
    "parameter_candidate_evidence",
    "replay_outcome_calibration",
)

WIDGET_TO_GAP = {
    "source_quality_freshness_widget": "source_quality_cap_and_coverage",
    "signal_strength_calibration_widget": "calibration_refs_and_signal_strength_validation",
    "prediction_delta_widget": "prediction_delta_history",
    "evidence_weighting_widget": "scenario_trace_confirmation",
    "invalidation_rewrite_widget": "scenario_trace_confirmation",
    "scenario_trace_widget": "scenario_trace_confirmation",
    "parameter_candidate_comparison_widget": "parameter_candidate_evidence",
    "replay_outcome_calibration_widget": "replay_outcome_calibration",
}


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _widget_map(report: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = _as_list(report.get("widget_readiness_rows"))
    result: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        item = _as_mapping(row)
        widget_id = str(item.get("widget_id") or "")
        if widget_id:
            result[widget_id] = item
    return result


def _safe_q17a_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17A_SOURCE_CHECKER_VERSION:
        failures.append("q17a_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17a_report_not_ok")
    if report.get("actual_read_audit_only") is not True:
        failures.append("q17a_actual_read_audit_only_missing")
    if report.get("warroom_widget_design_premise") is not True:
        failures.append("q17a_warroom_widget_design_premise_missing")
    safe_boundary = _as_mapping(report.get("safe_boundary_summary"))
    if safe_boundary.get("unsafe_boundary_count", 0) not in (0, None):
        failures.append("q17a_unsafe_boundary_count_nonzero")
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
            failures.append(f"q17a_boundary_not_false:{key}")
    return not failures, failures


def _severity(gap_id: str, report: Mapping[str, Any], widgets: Mapping[str, Mapping[str, Any]]) -> str:
    record_summary = _as_mapping(report.get("record_summary"))
    calibration = _as_mapping(report.get("calibration_summary"))
    scenario = _as_mapping(report.get("scenario_trace_summary"))
    warnings = set(str(item) for item in _as_list(report.get("warning_reasons")))
    if gap_id == "source_quality_cap_and_coverage":
        if int(record_summary.get("source_quality_warning_record_count") or 0) > 0:
            return "P0"
        return "P1"
    if gap_id == "calibration_refs_and_signal_strength_validation":
        if calibration.get("calibration_refs_present") is False:
            return "P0"
        return "P1"
    if gap_id == "prediction_delta_history":
        if "previous_payload_missing_delta_widget_gap" in warnings or widgets.get("prediction_delta_widget", {}).get("state") == "gap":
            return "P0"
        return "P1"
    if gap_id == "scenario_trace_confirmation":
        if scenario.get("evidence_weighting_trace_present") is False or scenario.get("invalidation_rewrite_trace_present") is False or scenario.get("scenario_switch_trace_present") is False:
            return "P1"
        return "P2"
    if gap_id == "parameter_candidate_evidence":
        if widgets.get("parameter_candidate_comparison_widget", {}).get("state") in {"partial", "gap"}:
            return "P1"
        return "P2"
    if gap_id == "replay_outcome_calibration":
        if calibration.get("replay_feedback_present") is False or widgets.get("replay_outcome_calibration_widget", {}).get("state") == "gap":
            return "P0"
        return "P2"
    return "P2"


def _gap_reason(gap_id: str, report: Mapping[str, Any], widgets: Mapping[str, Mapping[str, Any]]) -> list[str]:
    record_summary = _as_mapping(report.get("record_summary"))
    calibration = _as_mapping(report.get("calibration_summary"))
    scenario = _as_mapping(report.get("scenario_trace_summary"))
    warning_reasons = set(str(item) for item in _as_list(report.get("warning_reasons")))
    reasons: list[str] = []
    if gap_id == "source_quality_cap_and_coverage":
        count = int(record_summary.get("source_quality_warning_record_count") or 0)
        if count:
            reasons.append(f"source_quality_warning_record_count={count}")
        reasons.extend([item for item in warning_reasons if "source_quality" in item])
    elif gap_id == "calibration_refs_and_signal_strength_validation":
        if calibration.get("calibration_refs_present") is False:
            reasons.append("calibration_refs_present=false")
        reasons.append(f"signal_strength_range={record_summary.get('signal_strength_min')}..{record_summary.get('signal_strength_max')}")
        reasons.append(f"reference_hit_rate_range={record_summary.get('reference_hit_rate_min')}..{record_summary.get('reference_hit_rate_max')}")
    elif gap_id == "prediction_delta_history":
        if "previous_payload_missing_delta_widget_gap" in warning_reasons:
            reasons.append("previous_payload_missing_delta_widget_gap")
        row = widgets.get("prediction_delta_widget", {})
        if row.get("state"):
            reasons.append(f"prediction_delta_widget={row.get('state')}")
    elif gap_id == "scenario_trace_confirmation":
        for key in ("evidence_weighting_trace_present", "invalidation_rewrite_trace_present", "scenario_switch_trace_present"):
            if scenario.get(key) is False:
                reasons.append(f"{key}=false")
        keys = _as_list(scenario.get("scenario_trace_keys"))
        if keys:
            reasons.append("scenario_trace_keys_present_but_ps_q11_trace_names_not_confirmed")
    elif gap_id == "parameter_candidate_evidence":
        row = widgets.get("parameter_candidate_comparison_widget", {})
        if row.get("state"):
            reasons.append(f"parameter_candidate_comparison_widget={row.get('state')}")
        if row.get("warnings"):
            reasons.extend(str(item) for item in _as_list(row.get("warnings")))
    elif gap_id == "replay_outcome_calibration":
        if calibration.get("replay_feedback_present") is False:
            reasons.append("replay_feedback_present=false")
        row = widgets.get("replay_outcome_calibration_widget", {})
        if row.get("state"):
            reasons.append(f"replay_outcome_calibration_widget={row.get('state')}")
    return list(dict.fromkeys([item for item in reasons if item]))


def _recommended_action(gap_id: str) -> str:
    return {
        "source_quality_cap_and_coverage": "Audit tier0 source-quality gate coverage and make missing/degraded source reasons actionable before increasing signal confidence.",
        "calibration_refs_and_signal_strength_validation": "Create calibration reference contract for estimated_signal_strength_percent and estimated_reference_hit_rate_percent before tuning parameter candidates.",
        "prediction_delta_history": "Design a read-only previous-latest snapshot/delta source so realtime widgets can explain what changed without WarRoom-triggered generation.",
        "scenario_trace_confirmation": "Map current scenario_core.scenario_trace keys to PS-Q11 evidence/invalidation/switch semantics or add adapter/contract gaps for missing trace names.",
        "parameter_candidate_evidence": "Define baseline/candidate/rollback evidence requirements for parameter candidates before staging or apply is allowed.",
        "replay_outcome_calibration": "Connect replay/outcome evaluation refs to the audit plan before treating signal bands or parameter candidates as reliable.",
    }[gap_id]


def _next_validation(gap_id: str) -> str:
    return {
        "source_quality_cap_and_coverage": "source_quality_gap_diagnostic_guard",
        "calibration_refs_and_signal_strength_validation": "signal_strength_calibration_ref_contract_guard",
        "prediction_delta_history": "prediction_delta_history_contract_guard",
        "scenario_trace_confirmation": "scenario_trace_semantic_mapping_guard",
        "parameter_candidate_evidence": "parameter_candidate_evidence_contract_guard",
        "replay_outcome_calibration": "replay_outcome_calibration_ref_contract_guard",
    }[gap_id]


def _plan_rows(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    widgets = _widget_map(report)
    rows: list[dict[str, Any]] = []
    for gap_id in TARGET_GAP_ORDER:
        reasons = _gap_reason(gap_id, report, widgets)
        if not reasons and gap_id not in {"source_quality_cap_and_coverage", "scenario_trace_confirmation"}:
            continue
        rows.append(
            {
                "gap_id": gap_id,
                "priority": _severity(gap_id, report, widgets),
                "state": "open",
                "reasons": reasons or ["keep_under_observation"],
                "recommended_action": _recommended_action(gap_id),
                "next_validation": _next_validation(gap_id),
                "blocks_before_warroom_widget_implementation": gap_id in {
                    "source_quality_cap_and_coverage",
                    "calibration_refs_and_signal_strength_validation",
                    "prediction_delta_history",
                    "replay_outcome_calibration",
                },
                "read_only": True,
                "write_or_apply_allowed": False,
            }
        )
    return sorted(rows, key=lambda row: ({"P0": 0, "P1": 1, "P2": 2}.get(str(row["priority"]), 9), TARGET_GAP_ORDER.index(str(row["gap_id"]))))


def _fixture_q17a_observed_report() -> dict[str, Any]:
    return {
        "ok": True,
        "checker_version": PS_Q17A_SOURCE_CHECKER_VERSION,
        "actual_read_audit_only": True,
        "warroom_widget_design_premise": True,
        "readiness_state": "real_output_audit_ready_with_inference_quality_gaps",
        "record_summary": {
            "record_count": 110,
            "usable_record_count": 110,
            "family_count": 11,
            "horizon_count": 10,
            "source_quality_warning_record_count": 110,
            "warning_count": 418,
            "unique_warning_count": 13,
            "signal_strength_min": 24,
            "signal_strength_max": 49,
            "reference_hit_rate_min": 24,
            "reference_hit_rate_max": 49,
        },
        "scenario_trace_summary": {
            "scenario_trace_present": True,
            "scenario_core_present": True,
            "gpt_review_digest_present": True,
            "evidence_weighting_trace_present": False,
            "invalidation_rewrite_trace_present": False,
            "scenario_switch_trace_present": False,
            "scenario_trace_keys": ["context_evidence_profiles", "tier0_source_quality_gate", "what_to_watch_next"],
        },
        "calibration_summary": {
            "calibration_refs_present": False,
            "replay_feedback_present": False,
            "forecast_batch_present": True,
        },
        "safe_boundary_summary": {"unsafe_boundary_count": 0},
        "warning_reasons": [
            "source_quality_warnings_present_in_records",
            "calibration_refs_missing",
            "previous_payload_missing_delta_widget_gap",
        ],
        "widget_readiness_rows": [
            {"widget_id": "latest_prediction_summary_widget", "state": "ready", "warnings": []},
            {"widget_id": "prediction_delta_widget", "state": "gap", "warnings": ["delta_widget_requires_previous_latest_snapshot_or_history"]},
            {"widget_id": "scenario_trace_widget", "state": "ready", "warnings": []},
            {"widget_id": "evidence_weighting_widget", "state": "partial", "warnings": ["evidence_weighting_trace_not_confirmed_in_payload"]},
            {"widget_id": "invalidation_rewrite_widget", "state": "partial", "warnings": ["invalidation_rewrite_trace_not_confirmed_in_payload"]},
            {"widget_id": "source_quality_freshness_widget", "state": "ready", "warnings": ["source_quality_warning_records_present"]},
            {"widget_id": "warning_blocker_widget", "state": "ready", "warnings": []},
            {"widget_id": "signal_strength_calibration_widget", "state": "partial", "warnings": ["calibration_refs_missing"]},
            {"widget_id": "parameter_candidate_comparison_widget", "state": "partial", "warnings": ["baseline_candidate_rollback_comparison_not_confirmed"]},
            {"widget_id": "replay_outcome_calibration_widget", "state": "gap", "warnings": []},
            {"widget_id": "producer_freshness_status_widget", "state": "ready", "warnings": []},
            {"widget_id": "runtime_boundary_safety_widget", "state": "ready", "warnings": []},
        ],
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


def build_report(*, supplied_q17a_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17a_report = _as_mapping(supplied_q17a_report)
    if not q17a_report and use_observed_fixture:
        q17a_report = _fixture_q17a_observed_report()
    safe_q17a, validation_failures = _safe_q17a_boundary(q17a_report)
    plan_rows = _plan_rows(q17a_report) if safe_q17a else []
    p0_count = sum(1 for row in plan_rows if row.get("priority") == "P0")
    p1_count = sum(1 for row in plan_rows if row.get("priority") == "P1")
    blockers_before_widgets = [row["gap_id"] for row in plan_rows if row.get("blocks_before_warroom_widget_implementation")]
    ok = bool(safe_q17a and plan_rows and blockers_before_widgets)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "stage": "inference_quality_gap_plan_before_warroom_widget_implementation",
        "source_checker_version": PS_Q17A_SOURCE_CHECKER_VERSION,
        "source_q17a_report_valid": safe_q17a,
        "source_q17a_validation_failures": validation_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "plan_rows": plan_rows,
        "gap_count": len(plan_rows),
        "p0_gap_count": p0_count,
        "p1_gap_count": p1_count,
        "blocks_before_warroom_widget_implementation": blockers_before_widgets,
        "recommended_first_slice": blockers_before_widgets[0] if blockers_before_widgets else "",
        "recommended_next_slice": "PS-Q17C source-quality coverage diagnostic or calibration/delta contract, before WarRoom widget rendering.",
        "human_interpretation": "PS-Q17B converts the PS-Q17A real-output audit into a prioritized engine-quality plan. It does not render widgets, generate predictions, write artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker APIs.",
        "read_only": True,
        "non_executing": True,
        "plan_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17B inference quality gap plan")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use the static PS-Q17A observed summary embedded in this checker; no D-hot read is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
