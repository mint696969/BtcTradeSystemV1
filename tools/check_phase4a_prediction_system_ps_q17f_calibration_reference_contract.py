# path: ./tools/check_phase4a_prediction_system_ps_q17f_calibration_reference_contract.py
# desc: PS-Q17F non-executing calibration reference contract. It consumes a PS-Q17B gap plan report or its observed fixture and emits required calibration refs for signal strength and reference hit-rate before confidence/reliability claims. It never reads D-hot, writes artifacts, invokes refresh, renders WarRoom widgets, increases confidence, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import CHECKER_VERSION as PS_Q17B_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import build_report as build_ps_q17b_report

CHECKER = "ps_q17f_calibration_reference_contract"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17f_calibration_reference_contract.v1"
PS_Q17B_SOURCE_CHECKER_VERSION = PS_Q17B_CHECKER_VERSION
SOURCE_GAP_ID = "calibration_refs_and_signal_strength_validation"

CONTRACT_ORDER = (
    "signal_strength_calibration_reference_contract",
    "reference_hit_rate_calibration_reference_contract",
    "calibration_sample_window_contract",
    "confidence_band_release_contract",
    "parameter_candidate_calibration_dependency_contract",
    "warroom_calibration_explanation_contract",
)

REQUIRED_CALIBRATION_FIELDS = (
    "calibration_refs.signal_strength.model_version",
    "calibration_refs.signal_strength.sample_window.start_at",
    "calibration_refs.signal_strength.sample_window.end_at",
    "calibration_refs.signal_strength.sample_count",
    "calibration_refs.signal_strength.bucket_metrics",
    "calibration_refs.reference_hit_rate.model_version",
    "calibration_refs.reference_hit_rate.sample_window.start_at",
    "calibration_refs.reference_hit_rate.sample_count",
    "calibration_refs.reference_hit_rate.bucket_metrics",
    "calibration_release_gate.calibration_refs_present",
    "calibration_release_gate.confidence_band_claim_allowed",
    "calibration_release_gate.parameter_tuning_allowed",
)

SIGNAL_BANDS = ("very_low", "low", "medium", "high", "unknown")
REFERENCE_HIT_RATE_BANDS = ("very_low", "low", "medium", "high", "unknown")


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
        failures.append("calibration_gap_missing")
    elif gap.get("priority") != "P0":
        failures.append("calibration_gap_not_p0")
    elif gap.get("blocks_before_warroom_widget_implementation") is not True:
        failures.append("calibration_gap_not_blocking_widgets")
    return not failures, failures


def _contract_row(contract_id: str, priority: str, required_fields: list[str], validation_rule: str, blocks_reliability_claim: bool = True) -> dict[str, Any]:
    return {
        "contract_id": contract_id,
        "priority": priority,
        "state": "required",
        "required_fields": required_fields,
        "validation_rule": validation_rule,
        "blocks_confidence_increase": priority == "P0",
        "blocks_signal_reliability_claim": blocks_reliability_claim,
        "blocks_parameter_tuning": contract_id in {"signal_strength_calibration_reference_contract", "reference_hit_rate_calibration_reference_contract", "confidence_band_release_contract", "parameter_candidate_calibration_dependency_contract"},
        "next_validation": f"{contract_id}_guard",
        "read_only": True,
        "write_or_apply_allowed": False,
    }


def _build_contract_rows(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    gap = _gap_map(report).get(SOURCE_GAP_ID, {})
    reasons = [str(item) for item in _as_list(gap.get("reasons"))]
    rows = [
        _contract_row(
            "signal_strength_calibration_reference_contract",
            "P0",
            [
                "calibration_refs.signal_strength.model_version",
                "calibration_refs.signal_strength.sample_window.start_at",
                "calibration_refs.signal_strength.sample_window.end_at",
                "calibration_refs.signal_strength.sample_count",
                "calibration_refs.signal_strength.bucket_metrics",
            ],
            "estimated_signal_strength_percent must not support confidence claims until model_version, sample_window, sample_count, and bucket metrics exist",
        ),
        _contract_row(
            "reference_hit_rate_calibration_reference_contract",
            "P0",
            [
                "calibration_refs.reference_hit_rate.model_version",
                "calibration_refs.reference_hit_rate.sample_window.start_at",
                "calibration_refs.reference_hit_rate.sample_count",
                "calibration_refs.reference_hit_rate.bucket_metrics",
            ],
            "estimated_reference_hit_rate_percent must not support reliability claims until reference hit-rate refs exist",
        ),
        _contract_row(
            "calibration_sample_window_contract",
            "P0",
            [
                "calibration_refs.sample_window.start_at",
                "calibration_refs.sample_window.end_at",
                "calibration_refs.sample_window.market_uid",
                "calibration_refs.sample_window.horizon_keys",
            ],
            "calibration refs must declare market, horizon, start/end window, and avoid cross-market ambiguity",
        ),
        _contract_row(
            "confidence_band_release_contract",
            "P0",
            [
                "calibration_release_gate.calibration_refs_present",
                "calibration_release_gate.confidence_band_claim_allowed",
                "calibration_release_gate.blocking_reason_codes",
            ],
            "confidence band claims remain false while calibration refs are missing or stale",
        ),
        _contract_row(
            "parameter_candidate_calibration_dependency_contract",
            "P1",
            [
                "parameter_candidate_review.calibration_ref_id",
                "parameter_candidate_review.baseline_signal_band",
                "parameter_candidate_review.candidate_signal_band",
                "parameter_candidate_review.rollback_threshold_ref",
            ],
            "parameter candidate tuning must remain review-only until calibration refs tie baseline/candidate/rollback evidence together",
        ),
        _contract_row(
            "warroom_calibration_explanation_contract",
            "P1",
            [
                "warroom_signal_strength_calibration_widget.calibration_ref_id",
                "warroom_signal_strength_calibration_widget.sample_count",
                "warroom_signal_strength_calibration_widget.staleness_state",
                "warroom_signal_strength_calibration_widget.operator_explanation",
            ],
            "WarRoom may display calibration explanation later, but rendering and reliability claims remain deferred until refs exist",
            blocks_reliability_claim=True,
        ),
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
    confidence_blockers = [row["contract_id"] for row in contract_rows if row.get("blocks_confidence_increase")]
    tuning_blockers = [row["contract_id"] for row in contract_rows if row.get("blocks_parameter_tuning")]
    ok = bool(safe_q17b and contract_rows and p0_count == 4 and confidence_blockers)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "stage": "calibration_reference_contract_before_confidence_and_parameter_tuning",
        "source_checker_version": PS_Q17B_SOURCE_CHECKER_VERSION,
        "source_q17b_report_valid": safe_q17b,
        "source_q17b_validation_failures": validation_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "source_gap_id": SOURCE_GAP_ID,
        "contract_rows": contract_rows,
        "contract_count": len(contract_rows),
        "p0_contract_count": p0_count,
        "p1_contract_count": p1_count,
        "required_calibration_fields": list(REQUIRED_CALIBRATION_FIELDS),
        "signal_bands": list(SIGNAL_BANDS),
        "reference_hit_rate_bands": list(REFERENCE_HIT_RATE_BANDS),
        "blocks_confidence_increase": confidence_blockers,
        "blocks_parameter_tuning": tuning_blockers,
        "calibration_refs_required_before_confidence_claim": True,
        "recommended_first_validation": confidence_blockers[0] if confidence_blockers else "",
        "recommended_next_slice": "PS-Q17G calibration reference adapter or prediction-delta history contract; confidence increase, parameter apply, and WarRoom widget rendering remain deferred.",
        "human_interpretation": "PS-Q17F turns the calibration_refs_missing P0 gap into explicit signal-strength and reference-hit-rate calibration contracts. It does not read D-hot, generate predictions, raise confidence, tune parameters, render WarRoom widgets, or call broker APIs.",
        "read_only": True,
        "non_executing": True,
        "contract_only": True,
        "diagnostic_only": True,
        "plan_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17F calibration reference contract")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use the static PS-Q17B observed fixture path; no D-hot read is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
