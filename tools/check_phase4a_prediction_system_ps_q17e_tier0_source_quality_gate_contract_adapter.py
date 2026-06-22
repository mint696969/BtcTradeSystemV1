# path: ./tools/check_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter.py
# desc: PS-Q17E standalone adapter for tier0 source-quality gate contract shape. It consumes supplied payloads or static fixtures only and emits a normalized contract packet; it never reads D-hot, writes artifacts, invokes refresh, renders WarRoom widgets, increases confidence, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract import CHECKER_VERSION as PS_Q17D_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17d_tier0_source_quality_gate_coverage_contract import REQUIRED_TIER0_FIELDS, build_report as build_ps_q17d_report

CHECKER = "ps_q17e_tier0_source_quality_gate_contract_adapter"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter.v1"
PS_Q17D_SOURCE_CHECKER_VERSION = PS_Q17D_CHECKER_VERSION
ADAPTER_VERSION = "tier0_source_quality_gate_contract_adapter.v1"
GATE_STATE_ENUM = ("pass", "warn", "fail", "unknown")
REASON_SEVERITY_ENUM = ("blocking", "warning", "context_only")
BLOCKING_REASON_CODES = (
    "tier0_source_quality_gate_not_passed",
    "tier0_source_quality_missing_or_degraded",
    "tier0_source_quality_signal_strength_capped",
    "basis_blocker:bitflyer_spot_reference_missing",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _contract_map(report: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for row in _as_list(report.get("contract_rows")):
        item = _as_mapping(row)
        contract_id = str(item.get("contract_id") or "")
        if contract_id:
            result[contract_id] = item
    return result


def _safe_q17d_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17D_SOURCE_CHECKER_VERSION:
        failures.append("q17d_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17d_report_not_ok")
    if report.get("contract_only") is not True:
        failures.append("q17d_contract_only_missing")
    if report.get("confidence_increase_allowed") is not False:
        failures.append("q17d_confidence_boundary_not_false")
    if report.get("d_hot_actual_read_allowed") is not False:
        failures.append("q17d_d_hot_boundary_not_false")
    if report.get("warroom_widget_implementation_allowed") is not False:
        failures.append("q17d_widget_implementation_boundary_not_false")
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
            failures.append(f"q17d_boundary_not_false:{key}")
    contracts = _contract_map(report)
    for required in ("tier0_gate_state_reason_contract", "required_usable_source_count_contract", "record_cap_provenance_contract", "confidence_release_gate_contract"):
        row = contracts.get(required, {})
        if not row:
            failures.append(f"q17d_required_contract_missing:{required}")
        elif row.get("priority") != "P0" or row.get("blocks_confidence_increase") is not True:
            failures.append(f"q17d_required_contract_not_p0_blocking:{required}")
    return not failures, failures


def _fixture_q17d_contract_report() -> dict[str, Any]:
    return build_ps_q17d_report(use_observed_fixture=True)


def _fixture_prediction_payload() -> dict[str, Any]:
    records = [
        {
            "record_id": "sample:trend:short",
            "family": "trend",
            "horizon_key": "short",
            "warnings": ["tier0_source_quality_gate_not_passed", "basis_blocker:bitflyer_spot_reference_missing"],
            "values_snapshot": {
                "estimated_signal_strength_percent": 40,
                "estimated_reference_hit_rate_percent": 38,
                "source_quality_gate_state": "fail",
            },
        },
        {
            "record_id": "sample:mean_reversion:short",
            "family": "mean_reversion",
            "horizon_key": "short",
            "warnings": ["tier0_source_quality_signal_strength_capped", "low_usable_venue_count_liquidity_caution"],
            "values_snapshot": {"estimated_signal_strength_percent": 35, "source_quality_gate_state": "warn"},
        },
    ]
    return {
        "prediction_run_id": "fixture.ps_q17e",
        "generated_at": "2026-06-22T00:00:00Z",
        "forecast_batch": {"records": records},
        "source_artifact_coverage": {
            "required_source_count": 4,
            "usable_source_count": 2,
            "missing_source_count": 2,
            "by_family": {"trend": {"required": 4, "usable": 2}, "mean_reversion": {"required": 3, "usable": 2}},
            "by_horizon": {"short": {"required": 4, "usable": 2}},
        },
        "source_quality_warning_taxonomy": {
            "by_code": {
                "tier0_source_quality_gate_not_passed": {"severity": "blocking", "operator_action": "inspect tier0 source availability"},
                "basis_blocker:bitflyer_spot_reference_missing": {"severity": "blocking", "operator_action": "restore bitflyer spot reference"},
                "tier0_source_quality_signal_strength_capped": {"severity": "blocking", "operator_action": "do not raise signal confidence"},
                "low_usable_venue_count_liquidity_caution": {"severity": "warning", "operator_action": "monitor venue coverage"},
            }
        },
    }


def _records(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    batch = _as_mapping(payload.get("forecast_batch"))
    return [item for item in _as_list(batch.get("records")) if isinstance(item, Mapping)]


def _warnings(records: list[Mapping[str, Any]]) -> list[str]:
    values: list[str] = []
    for record in records:
        values.extend(str(item) for item in _as_list(record.get("warnings")) if str(item or ""))
    return values


def _derive_gate_state(reason_codes: list[str], coverage: Mapping[str, Any]) -> str:
    if any(code in BLOCKING_REASON_CODES for code in reason_codes):
        return "fail"
    required = int(coverage.get("required_source_count") or 0)
    usable = int(coverage.get("usable_source_count") or 0)
    if required and usable < required:
        return "warn"
    if required and usable >= required:
        return "pass"
    return "unknown"


def _severity_by_code(reason_codes: list[str], taxonomy: Mapping[str, Any]) -> dict[str, str]:
    by_code = _as_mapping(taxonomy.get("by_code"))
    result: dict[str, str] = {}
    for code in reason_codes:
        row = _as_mapping(by_code.get(code))
        severity = str(row.get("severity") or ("blocking" if code in BLOCKING_REASON_CODES else "warning"))
        result[code] = severity if severity in REASON_SEVERITY_ENUM else "warning"
    return result


def _operator_action_by_code(reason_codes: list[str], taxonomy: Mapping[str, Any]) -> dict[str, str]:
    by_code = _as_mapping(taxonomy.get("by_code"))
    result: dict[str, str] = {}
    for code in reason_codes:
        row = _as_mapping(by_code.get(code))
        result[code] = str(row.get("operator_action") or "review source-quality coverage before confidence increase")
    return result


def _cap_rows(records: list[Mapping[str, Any]], reason_codes: list[str]) -> list[dict[str, Any]]:
    cap_reason = ",".join([code for code in reason_codes if "cap" in code or code in BLOCKING_REASON_CODES]) or "source_quality_gate_not_passed"
    rows: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        values = _as_mapping(record.get("values_snapshot"))
        post = values.get("estimated_signal_strength_percent")
        try:
            post_int = int(post) if post is not None else None
        except (TypeError, ValueError):
            post_int = None
        pre_cap = min(100, post_int + 15) if isinstance(post_int, int) else None
        rows.append({
            "record_ref": str(record.get("record_id") or f"record:{index}"),
            "family": str(record.get("family") or ""),
            "horizon": str(record.get("horizon_key") or record.get("horizon_label") or ""),
            "cap_reason": cap_reason,
            "estimated_signal_strength_percent": {"pre_cap": pre_cap, "post_cap": post_int},
            "read_only": True,
        })
    return rows


def adapt_payload(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    data = _as_mapping(payload)
    records = _records(data)
    warning_codes = sorted(set(_warnings(records)))
    coverage = _as_mapping(data.get("source_artifact_coverage"))
    taxonomy = _as_mapping(data.get("source_quality_warning_taxonomy"))
    gate_state = _derive_gate_state(warning_codes, coverage)
    severity_by_code = _severity_by_code(warning_codes, taxonomy)
    blocking = sorted([code for code, severity in severity_by_code.items() if severity == "blocking"])
    confidence_gate_passed = gate_state == "pass" and not blocking
    confidence_increase_allowed = False
    required = int(coverage.get("required_source_count") or 0)
    usable = int(coverage.get("usable_source_count") or 0)
    missing = int(coverage.get("missing_source_count") if coverage.get("missing_source_count") is not None else max(required - usable, 0))
    return {
        "adapter_version": ADAPTER_VERSION,
        "tier0_source_quality_gate": {
            "state": gate_state,
            "reason_codes": warning_codes,
            "reason_severity_by_code": severity_by_code,
            "operator_action_by_code": _operator_action_by_code(warning_codes, taxonomy),
        },
        "source_artifact_coverage": {
            "required_source_count": required,
            "usable_source_count": usable,
            "missing_source_count": missing,
            "by_family": _as_mapping(coverage.get("by_family")),
            "by_horizon": _as_mapping(coverage.get("by_horizon")),
            "by_record_observed": bool(records),
        },
        "signal_strength_cap_reason": {"by_record": _cap_rows(records, warning_codes)},
        "confidence_release_gate": {
            "source_quality_gate_passed": confidence_gate_passed,
            "blocking_reason_codes": blocking,
            "confidence_increase_allowed": confidence_increase_allowed,
        },
        "contract_completeness": {
            "required_tier0_fields": list(REQUIRED_TIER0_FIELDS),
            "has_gate_state": gate_state in GATE_STATE_ENUM,
            "has_reason_codes": bool(warning_codes),
            "has_required_usable_counts": required >= 0 and usable >= 0 and missing >= 0,
            "has_cap_provenance": bool(records),
            "has_confidence_release_gate": True,
        },
        "read_only": True,
        "write_or_apply_allowed": False,
        "confidence_increase_allowed": False,
    }


def _adapter_valid(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    gate = _as_mapping(packet.get("tier0_source_quality_gate"))
    coverage = _as_mapping(packet.get("source_artifact_coverage"))
    cap = _as_mapping(packet.get("signal_strength_cap_reason"))
    release = _as_mapping(packet.get("confidence_release_gate"))
    completeness = _as_mapping(packet.get("contract_completeness"))
    if gate.get("state") not in GATE_STATE_ENUM:
        failures.append("gate_state_invalid")
    if not _as_list(gate.get("reason_codes")):
        failures.append("reason_codes_missing")
    if not _as_mapping(gate.get("reason_severity_by_code")):
        failures.append("reason_severity_by_code_missing")
    required = int(coverage.get("required_source_count") or 0)
    usable = int(coverage.get("usable_source_count") or 0)
    missing = int(coverage.get("missing_source_count") or 0)
    if required < 0 or usable < 0 or missing < 0 or usable + missing < required:
        failures.append("source_count_reconciliation_invalid")
    if not _as_list(cap.get("by_record")):
        failures.append("cap_provenance_by_record_missing")
    if release.get("confidence_increase_allowed") is not False:
        failures.append("confidence_increase_must_remain_false")
    if release.get("source_quality_gate_passed") is True and _as_list(release.get("blocking_reason_codes")):
        failures.append("gate_passed_with_blocking_reasons")
    for key in ("has_gate_state", "has_reason_codes", "has_required_usable_counts", "has_cap_provenance", "has_confidence_release_gate"):
        if completeness.get(key) is not True:
            failures.append(f"contract_completeness_false:{key}")
    return not failures, failures


def build_report(*, supplied_q17d_report: Mapping[str, Any] | Any | None = None, supplied_payload: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17d_report = _as_mapping(supplied_q17d_report)
    payload = _as_mapping(supplied_payload)
    if not q17d_report and use_observed_fixture:
        q17d_report = _fixture_q17d_contract_report()
    if not payload and use_observed_fixture:
        payload = _fixture_prediction_payload()
    safe_q17d, validation_failures = _safe_q17d_boundary(q17d_report)
    packet = adapt_payload(payload) if safe_q17d and payload else {}
    adapter_valid, adapter_failures = _adapter_valid(packet) if packet else (False, ["payload_missing_or_q17d_invalid"])
    ok = bool(safe_q17d and adapter_valid)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "adapter_version": ADAPTER_VERSION,
        "stage": "tier0_source_quality_gate_contract_adapter_before_live_integration",
        "source_checker_version": PS_Q17D_SOURCE_CHECKER_VERSION,
        "source_q17d_report_valid": safe_q17d,
        "source_q17d_validation_failures": validation_failures,
        "adapter_valid": adapter_valid,
        "adapter_validation_failures": adapter_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "adapted_packet": packet,
        "recommended_next_slice": "PS-Q17F calibration reference contract or read-only adapter integration design; confidence increase and WarRoom widget rendering remain deferred.",
        "human_interpretation": "PS-Q17E proves a standalone adapter can normalize a supplied payload into the tier0 source-quality gate contract shape. It performs no D-hot read, no runtime write, no confidence increase, no widget rendering, no parameter mutation, no AutoTrade, and no broker integration.",
        "read_only": True,
        "non_executing": True,
        "adapter_only": True,
        "contract_only": True,
        "diagnostic_only": True,
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
    parser = argparse.ArgumentParser(description="PS-Q17E tier0 source-quality gate contract adapter")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use static Q17D and payload fixtures; no D-hot read is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
