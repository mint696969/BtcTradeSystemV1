# path: ./tools/check_phase4a_prediction_system_ps_q17j_replay_outcome_calibration_contract.py
# desc: PS-Q17J non-executing replay-outcome calibration contract. It consumes a PS-Q17B gap plan report or its observed fixture and emits required replay feedback/outcome contracts before confidence, reliability, parameter tuning, or WarRoom replay widget claims. It never reads D-hot or replay history, writes artifacts, invokes refresh, renders WarRoom widgets, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import CHECKER_VERSION as PS_Q17B_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import build_report as build_ps_q17b_report

CHECKER = "ps_q17j_replay_outcome_calibration_contract"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17j_replay_outcome_calibration_contract.v1"
PS_Q17B_SOURCE_CHECKER_VERSION = PS_Q17B_CHECKER_VERSION
SOURCE_GAP_ID = "replay_outcome_calibration"

CONTRACT_ORDER = (
    "replay_feedback_reference_contract",
    "outcome_window_contract",
    "forecast_to_outcome_join_key_contract",
    "replay_calibration_release_gate_contract",
    "outcome_metric_taxonomy_contract",
    "warroom_replay_outcome_explanation_contract",
)

REQUIRED_REPLAY_FIELDS = (
    "replay_outcome_calibration.replay_feedback.run_id",
    "replay_outcome_calibration.replay_feedback.generated_at",
    "replay_outcome_calibration.replay_feedback.source_artifact_ref",
    "replay_outcome_calibration.outcome_window.start_at",
    "replay_outcome_calibration.outcome_window.end_at",
    "replay_outcome_calibration.outcome_window.market_uid",
    "replay_outcome_calibration.outcome_window.horizon_keys",
    "replay_outcome_calibration.forecast_to_outcome_key.market_uid",
    "replay_outcome_calibration.forecast_to_outcome_key.family",
    "replay_outcome_calibration.forecast_to_outcome_key.horizon_key",
    "replay_outcome_calibration.forecast_to_outcome_key.record_id",
    "replay_outcome_calibration.outcome_metrics.predicted_direction_hit",
    "replay_outcome_calibration.outcome_metrics.actual_return_bps",
    "replay_outcome_calibration.outcome_metrics.magnitude_error_bps",
    "replay_calibration_release_gate.replay_feedback_present",
    "replay_calibration_release_gate.confidence_reliability_claim_allowed",
)

REPLAY_REASON_CODES = (
    "replay_feedback_present=false",
    "replay_outcome_calibration_widget=gap",
    "outcome_window_missing_or_unverified",
    "forecast_to_outcome_join_key_missing",
    "outcome_metric_taxonomy_missing",
    "adapter_stage_no_confidence_or_parameter_release",
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
        failures.append("replay_outcome_calibration_gap_missing")
    elif gap.get("priority") != "P0":
        failures.append("replay_outcome_calibration_gap_not_p0")
    elif gap.get("blocks_before_warroom_widget_implementation") is not True:
        failures.append("replay_outcome_calibration_gap_not_blocking_widgets")
    return not failures, failures


def _contract_row(contract_id: str, priority: str, required_fields: list[str], validation_rule: str) -> dict[str, Any]:
    return {
        "contract_id": contract_id,
        "priority": priority,
        "state": "required",
        "required_fields": required_fields,
        "validation_rule": validation_rule,
        "blocks_confidence_reliability_claim": True,
        "blocks_parameter_tuning": contract_id in {"replay_feedback_reference_contract", "forecast_to_outcome_join_key_contract", "replay_calibration_release_gate_contract"},
        "blocks_warroom_replay_widget": True,
        "next_validation": f"{contract_id}_guard",
        "read_only": True,
        "write_or_apply_allowed": False,
    }


def _build_contract_rows(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    gap = _gap_map(report).get(SOURCE_GAP_ID, {})
    reasons = [str(item) for item in _as_list(gap.get("reasons"))]
    rows = [
        _contract_row("replay_feedback_reference_contract", "P0", [
            "replay_outcome_calibration.replay_feedback.run_id",
            "replay_outcome_calibration.replay_feedback.generated_at",
            "replay_outcome_calibration.replay_feedback.source_artifact_ref",
        ], "replay feedback reference must exist before outcome calibration or reliability claims"),
        _contract_row("outcome_window_contract", "P0", [
            "replay_outcome_calibration.outcome_window.start_at",
            "replay_outcome_calibration.outcome_window.end_at",
            "replay_outcome_calibration.outcome_window.market_uid",
            "replay_outcome_calibration.outcome_window.horizon_keys",
        ], "outcome window must declare market, horizons, and start/end before joining forecast outcomes"),
        _contract_row("forecast_to_outcome_join_key_contract", "P0", [
            "replay_outcome_calibration.forecast_to_outcome_key.market_uid",
            "replay_outcome_calibration.forecast_to_outcome_key.family",
            "replay_outcome_calibration.forecast_to_outcome_key.horizon_key",
            "replay_outcome_calibration.forecast_to_outcome_key.record_id",
        ], "forecast records and outcomes must be joined by stable market/family/horizon/record identity"),
        _contract_row("replay_calibration_release_gate_contract", "P0", [
            "replay_calibration_release_gate.replay_feedback_present",
            "replay_calibration_release_gate.confidence_reliability_claim_allowed",
            "replay_calibration_release_gate.parameter_tuning_allowed",
            "replay_calibration_release_gate.blocking_reason_codes",
        ], "confidence, reliability, and parameter tuning remain false until replay feedback is present and verified"),
        _contract_row("outcome_metric_taxonomy_contract", "P1", [
            "replay_outcome_calibration.outcome_metrics.predicted_direction_hit",
            "replay_outcome_calibration.outcome_metrics.actual_return_bps",
            "replay_outcome_calibration.outcome_metrics.magnitude_error_bps",
        ], "outcome metrics must be named and typed before WarRoom explanation or parameter review"),
        _contract_row("warroom_replay_outcome_explanation_contract", "P1", [
            "warroom_replay_outcome_widget.replay_feedback_ref_id",
            "warroom_replay_outcome_widget.sample_count",
            "warroom_replay_outcome_widget.operator_explanation",
            "warroom_replay_outcome_widget.render_allowed",
        ], "WarRoom may explain replay outcomes later, but rendering and reliability claims remain deferred"),
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
    confidence_blockers = [row["contract_id"] for row in contract_rows if row.get("blocks_confidence_reliability_claim")]
    tuning_blockers = [row["contract_id"] for row in contract_rows if row.get("blocks_parameter_tuning")]
    widget_blockers = [row["contract_id"] for row in contract_rows if row.get("blocks_warroom_replay_widget")]
    ok = bool(safe_q17b and contract_rows and p0_count == 4 and confidence_blockers and widget_blockers)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "stage": "replay_outcome_calibration_contract_before_confidence_parameter_and_widget_release",
        "source_checker_version": PS_Q17B_SOURCE_CHECKER_VERSION,
        "source_q17b_report_valid": safe_q17b,
        "source_q17b_validation_failures": validation_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "source_gap_id": SOURCE_GAP_ID,
        "contract_rows": contract_rows,
        "contract_count": len(contract_rows),
        "p0_contract_count": p0_count,
        "p1_contract_count": p1_count,
        "required_replay_fields": list(REQUIRED_REPLAY_FIELDS),
        "replay_reason_codes": list(REPLAY_REASON_CODES),
        "blocks_confidence_reliability_claim": confidence_blockers,
        "blocks_parameter_tuning": tuning_blockers,
        "blocks_warroom_replay_widget": widget_blockers,
        "replay_feedback_required_before_confidence_claim": True,
        "recommended_first_validation": confidence_blockers[0] if confidence_blockers else "",
        "recommended_next_slice": "PS-Q17K replay-outcome calibration adapter or scenario-trace semantic mapping contract; confidence increase, parameter apply, and WarRoom widget rendering remain deferred.",
        "human_interpretation": "PS-Q17J turns the replay_feedback_missing P0 gap into explicit replay feedback, outcome window, join-key, release-gate, and WarRoom explanation contracts. It does not read replay history, compute outcomes, render widgets, write artifacts, or trigger generation.",
        "read_only": True,
        "non_executing": True,
        "contract_only": True,
        "diagnostic_only": True,
        "plan_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "replay_history_actual_read_allowed": False,
        "replay_outcome_widget_rendering_allowed": False,
        "confidence_increase_allowed": False,
        "signal_reliability_claim_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17J replay-outcome calibration contract")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use the static PS-Q17B observed fixture path; no D-hot or replay-history read is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
