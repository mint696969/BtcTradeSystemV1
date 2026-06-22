# path: ./tools/check_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract.py
# desc: PS-Q17D non-executing tier0 source-quality gate coverage contract. It consumes a PS-Q17C diagnostic report or its observed fixture and emits the required contract for gate state/reasons/counts/cap provenance before confidence increase. It never reads D-hot, writes artifacts, invokes refresh, renders WarRoom widgets, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic import CHECKER_VERSION as PS_Q17C_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17c_source_quality_coverage_diagnostic import build_report as build_ps_q17c_report

CHECKER = "ps_q17d_tier0_source_quality_gate_coverage_contract"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract.v1"
PS_Q17C_SOURCE_CHECKER_VERSION = PS_Q17C_CHECKER_VERSION
SOURCE_DIAGNOSTIC_ID = "tier0_source_quality_gate_coverage"

CONTRACT_ORDER = (
    "tier0_gate_state_reason_contract",
    "required_usable_source_count_contract",
    "record_cap_provenance_contract",
    "confidence_release_gate_contract",
    "family_horizon_coverage_contract",
    "operator_action_reason_contract",
)

GATE_STATE_ENUM = ("pass", "warn", "fail", "unknown")
REASON_SEVERITY_ENUM = ("blocking", "warning", "context_only")
REQUIRED_TIER0_FIELDS = (
    "tier0_source_quality_gate.state",
    "tier0_source_quality_gate.reason_codes",
    "tier0_source_quality_gate.reason_severity_by_code",
    "source_artifact_coverage.required_source_count",
    "source_artifact_coverage.usable_source_count",
    "source_artifact_coverage.missing_source_count",
    "source_artifact_coverage.by_family",
    "source_artifact_coverage.by_horizon",
    "signal_strength_cap_reason.by_record",
    "estimated_signal_strength_percent.pre_cap",
    "estimated_signal_strength_percent.post_cap",
    "confidence_release_gate.source_quality_gate_passed",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _diagnostic_map(report: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for row in _as_list(report.get("diagnostic_rows")):
        item = _as_mapping(row)
        diagnostic_id = str(item.get("diagnostic_id") or "")
        if diagnostic_id:
            result[diagnostic_id] = item
    return result


def _safe_q17c_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17C_SOURCE_CHECKER_VERSION:
        failures.append("q17c_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17c_report_not_ok")
    if report.get("diagnostic_only") is not True:
        failures.append("q17c_diagnostic_only_missing")
    if report.get("plan_only") is not True:
        failures.append("q17c_plan_only_missing")
    if report.get("warroom_widget_design_premise") is not True:
        failures.append("q17c_warroom_widget_design_premise_missing")
    if report.get("confidence_increase_allowed") is not False:
        failures.append("q17c_confidence_boundary_not_false")
    if report.get("d_hot_actual_read_allowed") is not False:
        failures.append("q17c_d_hot_boundary_not_false")
    if report.get("warroom_widget_implementation_allowed") is not False:
        failures.append("q17c_widget_implementation_boundary_not_false")
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
            failures.append(f"q17c_boundary_not_false:{key}")
    diagnostic = _diagnostic_map(report).get(SOURCE_DIAGNOSTIC_ID, {})
    if not diagnostic:
        failures.append("tier0_source_quality_gate_coverage_missing")
    elif diagnostic.get("priority") != "P0":
        failures.append("tier0_source_quality_gate_coverage_not_p0")
    elif diagnostic.get("blocks_confidence_increase") is not True:
        failures.append("tier0_source_quality_gate_coverage_not_confidence_blocking")
    return not failures, failures


def _contract_row(contract_id: str, priority: str, required_fields: list[str], validation_rule: str, release_blocker: bool) -> dict[str, Any]:
    return {
        "contract_id": contract_id,
        "priority": priority,
        "state": "required",
        "required_fields": required_fields,
        "validation_rule": validation_rule,
        "blocks_confidence_increase": release_blocker,
        "blocks_warroom_widget_reliability_claim": priority in {"P0", "P1"},
        "next_validation": f"{contract_id}_guard",
        "read_only": True,
        "write_or_apply_allowed": False,
    }


def _build_contract_rows(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    diagnostic = _diagnostic_map(report).get(SOURCE_DIAGNOSTIC_ID, {})
    missing = [str(item) for item in _as_list(diagnostic.get("missing_contracts"))]
    rows = [
        _contract_row(
            "tier0_gate_state_reason_contract",
            "P0",
            [
                "tier0_source_quality_gate.state",
                "tier0_source_quality_gate.reason_codes",
                "tier0_source_quality_gate.reason_severity_by_code",
            ],
            "state must be one of pass/warn/fail/unknown; non-pass must carry reason_codes and severity mapping",
            True,
        ),
        _contract_row(
            "required_usable_source_count_contract",
            "P0",
            [
                "source_artifact_coverage.required_source_count",
                "source_artifact_coverage.usable_source_count",
                "source_artifact_coverage.missing_source_count",
            ],
            "usable_source_count and missing_source_count must reconcile against required_source_count",
            True,
        ),
        _contract_row(
            "record_cap_provenance_contract",
            "P0",
            [
                "signal_strength_cap_reason.by_record",
                "estimated_signal_strength_percent.pre_cap",
                "estimated_signal_strength_percent.post_cap",
            ],
            "each capped record must expose cap reason and pre/post cap signal strength",
            True,
        ),
        _contract_row(
            "confidence_release_gate_contract",
            "P0",
            [
                "confidence_release_gate.source_quality_gate_passed",
                "confidence_release_gate.blocking_reason_codes",
                "confidence_release_gate.confidence_increase_allowed",
            ],
            "confidence increase remains false unless source-quality gate passes and no blocking reason codes remain",
            True,
        ),
        _contract_row(
            "family_horizon_coverage_contract",
            "P1",
            [
                "source_artifact_coverage.by_family",
                "source_artifact_coverage.by_horizon",
                "source_artifact_coverage.by_record",
            ],
            "coverage must be visible by family, horizon, and record before widget reliability claims",
            False,
        ),
        _contract_row(
            "operator_action_reason_contract",
            "P1",
            [
                "source_quality_warning_taxonomy.by_code",
                "source_quality_warning_taxonomy.severity",
                "source_quality_warning_taxonomy.operator_action",
            ],
            "each reason code should map to severity and operator action before WarRoom presentation",
            False,
        ),
    ]
    if missing:
        rows[0]["source_diagnostic_missing_contracts"] = missing
    return sorted(rows, key=lambda row: ({"P0": 0, "P1": 1, "P2": 2}.get(str(row["priority"]), 9), CONTRACT_ORDER.index(str(row["contract_id"]))))


def build_report(*, supplied_q17c_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17c_report = _as_mapping(supplied_q17c_report)
    if not q17c_report and use_observed_fixture:
        q17c_report = build_ps_q17c_report(use_observed_fixture=True)
    safe_q17c, validation_failures = _safe_q17c_boundary(q17c_report)
    contract_rows = _build_contract_rows(q17c_report) if safe_q17c else []
    p0_count = sum(1 for row in contract_rows if row.get("priority") == "P0")
    p1_count = sum(1 for row in contract_rows if row.get("priority") == "P1")
    confidence_blockers = [row["contract_id"] for row in contract_rows if row.get("blocks_confidence_increase")]
    ok = bool(safe_q17c and contract_rows and p0_count == 4 and confidence_blockers)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "stage": "tier0_source_quality_gate_coverage_contract_before_confidence_increase",
        "source_checker_version": PS_Q17C_SOURCE_CHECKER_VERSION,
        "source_q17c_report_valid": safe_q17c,
        "source_q17c_validation_failures": validation_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "source_diagnostic_id": SOURCE_DIAGNOSTIC_ID,
        "contract_rows": contract_rows,
        "contract_count": len(contract_rows),
        "p0_contract_count": p0_count,
        "p1_contract_count": p1_count,
        "gate_state_enum": list(GATE_STATE_ENUM),
        "reason_severity_enum": list(REASON_SEVERITY_ENUM),
        "required_tier0_fields": list(REQUIRED_TIER0_FIELDS),
        "blocks_confidence_increase": confidence_blockers,
        "recommended_first_validation": confidence_blockers[0] if confidence_blockers else "",
        "recommended_next_slice": "PS-Q17E tier0 gate contract implementation adapter or calibration reference contract; confidence increase and WarRoom widget rendering remain deferred.",
        "human_interpretation": "PS-Q17D turns the tier0 source-quality gate coverage diagnostic into an explicit field contract. It is not a live data reader, prediction generator, confidence increase, widget renderer, parameter writer, AutoTrade trigger, or broker integration.",
        "read_only": True,
        "non_executing": True,
        "contract_only": True,
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
    parser = argparse.ArgumentParser(description="PS-Q17D tier0 source-quality gate coverage contract")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use the static PS-Q17C observed fixture path; no D-hot read is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
