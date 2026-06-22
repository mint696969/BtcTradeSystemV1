# path: ./tools/check_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic.py
# desc: PS-Q17C non-executing source-quality coverage diagnostic. It consumes a PS-Q17B plan report or its static observed fixture and emits diagnostic rows for the source_quality_cap_and_coverage P0 gap. It never reads D-hot, writes artifacts, invokes refresh, renders WarRoom widgets, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import CHECKER_VERSION as PS_Q17B_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17b_inference_quality_gap_plan import build_report as build_ps_q17b_report

CHECKER = "ps_q17c_source_quality_coverage_diagnostic"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic.v1"
PS_Q17B_SOURCE_CHECKER_VERSION = PS_Q17B_CHECKER_VERSION
SOURCE_QUALITY_GAP_ID = "source_quality_cap_and_coverage"

DIAGNOSTIC_ORDER = (
    "tier0_source_quality_gate_coverage",
    "source_quality_warning_taxonomy",
    "source_artifact_coverage_mapping",
    "signal_strength_cap_reason_accounting",
    "basis_and_cross_venue_reference_requirements",
    "context_profile_minimum_source_requirements",
)

OBSERVED_WARNING_TAXONOMY = (
    "tier0_source_quality_gate_not_passed",
    "tier0_source_quality_missing_or_degraded",
    "tier0_source_quality_signal_strength_capped",
    "basis_blocker:bitflyer_spot_reference_missing",
    "low_usable_venue_count_liquidity_caution",
    "context_profile_family_minimum_sources_missing",
    "technical_warning:insufficient_candles_for_long_ma",
)

REQUIRED_SOURCE_QUALITY_FIELDS = (
    "tier0_source_quality_gate.state",
    "tier0_source_quality_gate.reason_codes",
    "source_artifact_coverage.by_family",
    "source_artifact_coverage.required_source_count",
    "source_artifact_coverage.usable_source_count",
    "source_contribution_ledger.by_record",
    "signal_strength_cap_reason.by_record",
    "basis_reference_status.bitflyer_spot",
    "cross_venue_reference_status.usable_venue_count",
    "context_profile_source_caps.by_family",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _gap_map(plan_report: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = _as_list(plan_report.get("plan_rows"))
    result: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        item = _as_mapping(row)
        gap_id = str(item.get("gap_id") or "")
        if gap_id:
            result[gap_id] = item
    return result


def _safe_q17b_boundary(plan_report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if plan_report.get("checker_version") != PS_Q17B_SOURCE_CHECKER_VERSION:
        failures.append("q17b_checker_version_mismatch")
    if plan_report.get("ok") is not True:
        failures.append("q17b_report_not_ok")
    if plan_report.get("plan_only") is not True:
        failures.append("q17b_plan_only_missing")
    if plan_report.get("warroom_widget_design_premise") is not True:
        failures.append("q17b_warroom_widget_design_premise_missing")
    if plan_report.get("warroom_widget_implementation_allowed") is not False:
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
        if plan_report.get(key) is not False:
            failures.append(f"q17b_boundary_not_false:{key}")
    gaps = _gap_map(plan_report)
    source_quality = gaps.get(SOURCE_QUALITY_GAP_ID, {})
    if not source_quality:
        failures.append("source_quality_gap_missing")
    elif source_quality.get("priority") != "P0":
        failures.append("source_quality_gap_not_p0")
    elif source_quality.get("blocks_before_warroom_widget_implementation") is not True:
        failures.append("source_quality_gap_not_blocking_widgets")
    return not failures, failures


def _diagnostic_row(diagnostic_id: str, priority: str, evidence: list[str], missing_contracts: list[str], next_validation: str) -> dict[str, Any]:
    return {
        "diagnostic_id": diagnostic_id,
        "priority": priority,
        "state": "open",
        "evidence": evidence,
        "missing_contracts": missing_contracts,
        "next_validation": next_validation,
        "blocks_confidence_increase": priority == "P0",
        "blocks_warroom_widget_reliability_claim": priority in {"P0", "P1"},
        "read_only": True,
        "write_or_apply_allowed": False,
    }


def _build_diagnostic_rows(plan_report: Mapping[str, Any]) -> list[dict[str, Any]]:
    source_gap = _gap_map(plan_report).get(SOURCE_QUALITY_GAP_ID, {})
    reasons = [str(item) for item in _as_list(source_gap.get("reasons"))]
    has_110 = any("source_quality_warning_record_count=110" in item for item in reasons)
    has_warning_reason = any("source_quality_warnings_present_in_records" in item for item in reasons)
    rows = [
        _diagnostic_row(
            "tier0_source_quality_gate_coverage",
            "P0" if has_110 else "P1",
            [item for item in reasons if "source_quality_warning_record_count" in item] or ["source_quality_warning_record_count_unknown"],
            [
                "tier0_source_quality_gate.state",
                "tier0_source_quality_gate.reason_codes",
                "source_artifact_coverage.required_source_count",
                "source_artifact_coverage.usable_source_count",
            ],
            "tier0_source_quality_gate_coverage_contract_guard",
        ),
        _diagnostic_row(
            "source_quality_warning_taxonomy",
            "P0" if has_warning_reason else "P1",
            list(OBSERVED_WARNING_TAXONOMY),
            ["source_quality_warning_taxonomy.by_code", "source_quality_warning_taxonomy.severity", "source_quality_warning_taxonomy.operator_action"],
            "source_quality_warning_taxonomy_guard",
        ),
        _diagnostic_row(
            "source_artifact_coverage_mapping",
            "P0",
            ["source_artifact_coverage exists in scenario_trace_keys but family/source mapping is not audited yet"],
            ["source_artifact_coverage.by_family", "source_artifact_coverage.by_horizon", "source_artifact_coverage.by_record"],
            "source_artifact_coverage_mapping_guard",
        ),
        _diagnostic_row(
            "signal_strength_cap_reason_accounting",
            "P0",
            ["tier0 source-quality cap is present before signal-confidence increase", "signal_strength_range=24..49 from PS-Q17B observed fixture"],
            ["signal_strength_cap_reason.by_record", "estimated_signal_strength_percent.pre_cap", "estimated_signal_strength_percent.post_cap"],
            "signal_strength_cap_reason_accounting_guard",
        ),
        _diagnostic_row(
            "basis_and_cross_venue_reference_requirements",
            "P1",
            ["basis_blocker:bitflyer_spot_reference_missing", "low_usable_venue_count_liquidity_caution"],
            ["basis_reference_status.bitflyer_spot", "cross_venue_reference_status.usable_venue_count", "cross_venue_reference_status.minimum_required_count"],
            "basis_cross_venue_reference_requirements_guard",
        ),
        _diagnostic_row(
            "context_profile_minimum_source_requirements",
            "P1",
            ["context_profile_family_minimum_sources_missing"],
            ["context_profile_source_caps.by_family", "context_profile_minimum_sources.by_family", "context_profile_source_gap_reason.by_family"],
            "context_profile_minimum_source_requirements_guard",
        ),
    ]
    return sorted(rows, key=lambda row: ({"P0": 0, "P1": 1, "P2": 2}.get(str(row["priority"]), 9), DIAGNOSTIC_ORDER.index(str(row["diagnostic_id"]))))


def build_report(*, supplied_q17b_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17b_report = _as_mapping(supplied_q17b_report)
    if not q17b_report and use_observed_fixture:
        q17b_report = build_ps_q17b_report(use_observed_fixture=True)
    safe_q17b, validation_failures = _safe_q17b_boundary(q17b_report)
    diagnostic_rows = _build_diagnostic_rows(q17b_report) if safe_q17b else []
    p0_count = sum(1 for row in diagnostic_rows if row.get("priority") == "P0")
    p1_count = sum(1 for row in diagnostic_rows if row.get("priority") == "P1")
    blocking_confidence = [row["diagnostic_id"] for row in diagnostic_rows if row.get("blocks_confidence_increase")]
    ok = bool(safe_q17b and diagnostic_rows and p0_count >= 4)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "stage": "source_quality_coverage_diagnostic_before_confidence_increase_and_warroom_widgets",
        "source_checker_version": PS_Q17B_SOURCE_CHECKER_VERSION,
        "source_q17b_report_valid": safe_q17b,
        "source_q17b_validation_failures": validation_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "source_quality_gap_id": SOURCE_QUALITY_GAP_ID,
        "diagnostic_rows": diagnostic_rows,
        "diagnostic_count": len(diagnostic_rows),
        "p0_diagnostic_count": p0_count,
        "p1_diagnostic_count": p1_count,
        "required_source_quality_fields": list(REQUIRED_SOURCE_QUALITY_FIELDS),
        "observed_warning_taxonomy": list(OBSERVED_WARNING_TAXONOMY),
        "blocks_confidence_increase": blocking_confidence,
        "recommended_first_validation": blocking_confidence[0] if blocking_confidence else "",
        "recommended_next_slice": "PS-Q17D tier0 source-quality gate coverage contract or calibration reference contract; WarRoom widget rendering remains deferred.",
        "human_interpretation": "PS-Q17C decomposes the source-quality P0 gap into diagnostic contracts. It is a diagnostic plan, not a prediction generator, UI widget renderer, parameter writer, ledger writer, AutoTrade trigger, or broker integration.",
        "read_only": True,
        "non_executing": True,
        "diagnostic_only": True,
        "plan_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "confidence_increase_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17C source-quality coverage diagnostic")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use the static PS-Q17B observed fixture path; no D-hot read is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
