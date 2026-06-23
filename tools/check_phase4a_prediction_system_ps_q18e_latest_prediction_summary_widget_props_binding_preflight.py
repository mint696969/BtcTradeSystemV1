# path: ./tools/check_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight.py
# desc: PS-Q18E checker for latest_prediction_summary_widget props binding preflight. It consumes Q18D schema probe packet and builds a contract-complete props candidate only; no widget render, actual-source read, payload reparse, D-hot discovery, refresh, writes, AutoTrade, or broker calls.

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Mapping

BTCTS_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "btcts_next", "src")
if BTCTS_SRC not in sys.path:
    sys.path.insert(0, BTCTS_SRC)

from check_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe import CHECKER_VERSION as PS_Q18D_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe import build_report as build_ps_q18d_report
from check_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe import build_q18b_fixture_probe_packet
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_schema_probe import build_latest_prediction_summary_widget_schema_probe_packet
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_props_binding_preflight import LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_VERSION, build_latest_prediction_summary_widget_props_binding_preflight_packet

CHECKER = "ps_q18e_latest_prediction_summary_widget_props_binding_preflight"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_CHECK_VERSION = "latest_prediction_summary_widget_props_binding_preflight.v1"
PS_Q18D_SOURCE_CHECKER_VERSION = PS_Q18D_CHECKER_VERSION


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _safe_q18d_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q18D_SOURCE_CHECKER_VERSION:
        failures.append("q18d_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q18d_report_not_ok")
    if report.get("schema_packet_valid") is not True:
        failures.append("q18d_schema_packet_not_valid")
    if report.get("schema_probe_row_count") != 4:
        failures.append("q18d_schema_row_count_mismatch")
    if report.get("missing_required_schema_keys") != []:
        failures.append("q18d_missing_required_schema_keys_present")
    for key in ("latest_prediction_summary_widget_schema_probe_only", "schema_specific_probe_ready", "preview_key_contract_only"):
        if report.get(key) is not True:
            failures.append(f"q18d_true_boundary_missing:{key}")
    for key in (
        "payload_reparse_allowed",
        "actual_source_read_invoked_by_schema_probe",
        "actual_source_read_allowed_by_schema_probe",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
        "real_prediction_widget_rendering_allowed",
        "widget_props_binding_allowed",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "confidence_increase_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
    ):
        if report.get(key) is not False:
            failures.append(f"q18d_boundary_not_false:{key}")
    return not failures, failures


def _safe_props_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("preflight_version") != LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_VERSION:
        failures.append("props_preflight_version_mismatch")
    if packet.get("ok") is not True:
        failures.append("props_preflight_packet_not_ok")
    if packet.get("props_contract_complete") is not True:
        failures.append("props_contract_not_complete")
    if packet.get("missing_required_component_props") != []:
        failures.append("missing_required_component_props_present")
    candidate = _as_mapping(packet.get("props_candidate"))
    for field in packet.get("required_component_props") or []:
        if field not in candidate:
            failures.append(f"candidate_missing_prop:{field}")
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_props_binding_preflight_only", "props_candidate_ready", "props_contract_complete", "props_value_binding_deferred"):
        if packet.get(key) is not True:
            failures.append(f"props_true_boundary_missing:{key}")
    for key in (
        "real_payload_values_bound",
        "widget_props_binding_allowed",
        "widget_props_bound_to_component",
        "render_invocation_allowed",
        "real_prediction_widget_rendering_allowed",
        "actual_source_read_invoked_by_props_preflight",
        "actual_source_read_allowed_by_props_preflight",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "confidence_increase_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
    ):
        if packet.get(key) is not False:
            failures.append(f"props_false_boundary_not_false:{key}")
    return not failures, failures


def _observed_schema_probe_packet() -> dict[str, Any]:
    probe_packet = build_q18b_fixture_probe_packet()
    return build_latest_prediction_summary_widget_schema_probe_packet(supplied_probe_packet=probe_packet)


def build_report(*, supplied_q18d_report: Mapping[str, Any] | Any | None = None, supplied_schema_probe_packet: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18d_report = _as_mapping(supplied_q18d_report)
    schema_probe_packet = _as_mapping(supplied_schema_probe_packet)
    if use_observed_fixture:
        if not q18d_report:
            q18d_report = build_ps_q18d_report(use_observed_fixture=True)
        if not schema_probe_packet:
            schema_probe_packet = _observed_schema_probe_packet()
    safe_q18d, q18d_failures = _safe_q18d_boundary(q18d_report)
    props_packet = build_latest_prediction_summary_widget_props_binding_preflight_packet(supplied_schema_probe_packet=schema_probe_packet) if safe_q18d and schema_probe_packet else {}
    safe_props, props_failures = _safe_props_packet(props_packet) if props_packet else (False, [] if schema_probe_packet else ["schema_probe_packet_missing"])
    ok = bool(safe_q18d and safe_props)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "latest_prediction_summary_widget_props_binding_preflight_check_version": LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_CHECK_VERSION,
        "stage": "latest_prediction_summary_widget_props_binding_preflight_before_component_binding_real_rendering_refresh_and_writes",
        "source_q18d_checker_version": PS_Q18D_SOURCE_CHECKER_VERSION,
        "source_q18d_report_valid": safe_q18d,
        "source_q18d_validation_failures": q18d_failures,
        "props_packet_valid": safe_props,
        "props_validation_failures": props_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "preflight_version": LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_VERSION,
        "widget_family_id": props_packet.get("widget_family_id") if props_packet else "latest_prediction_summary_widget",
        "source_packet_id": props_packet.get("source_packet_id") if props_packet else "latest_prediction_source_review_packet",
        "props_candidate_key_count": int(props_packet.get("props_candidate_key_count") or 0) if props_packet else 0,
        "missing_required_component_props": list(props_packet.get("missing_required_component_props") or []) if props_packet else [],
        "schema_probe_row_count": int(props_packet.get("schema_probe_row_count") or 0) if props_packet else 0,
        "missing_required_schema_keys": list(props_packet.get("missing_required_schema_keys") or []) if props_packet else [],
        "recommended_first_validation": "latest_prediction_summary_widget_props_binding_preflight_guard" if ok else "",
        "recommended_next_slice": "PS-Q18F latest_prediction_summary_widget props candidate status row mount or first render-disabled component packet validation; real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18E builds a contract-complete latest_prediction_summary_widget props candidate from Q18D schema-probe metadata only. It does not bind props to the component, render a real widget, perform new file reads, reparse payloads, discover D-hot, mutate WarRoom, refresh, write artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_props_binding_preflight_only": True,
        "props_candidate_ready": ok,
        "props_contract_complete": ok,
        "props_value_binding_deferred": True,
        "real_payload_values_bound": False,
        "widget_props_binding_allowed": False,
        "widget_props_bound_to_component": False,
        "render_invocation_allowed": False,
        "real_prediction_widget_rendering_allowed": False,
        "actual_source_read_invoked_by_props_preflight": False,
        "actual_source_read_allowed_by_props_preflight": False,
        "payload_reparse_allowed": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
        "warroom_page_mutation_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "warroom_ui_trigger_enabled": False,
        "refresh_invocation_allowed": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "confidence_increase_allowed": False,
        "signal_reliability_claim_allowed": False,
        "parameter_candidate_reliability_claim_allowed": False,
        "parameter_tuning_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q18E latest prediction summary widget props binding preflight")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use Q18D observed schema probe packet; no props are bound to the real component and no render is invoked.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
