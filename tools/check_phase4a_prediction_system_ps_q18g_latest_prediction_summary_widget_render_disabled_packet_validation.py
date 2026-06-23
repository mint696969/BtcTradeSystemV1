# path: ./tools/check_phase4a_prediction_system_ps_q18g_latest_prediction_summary_widget_render_disabled_packet_validation.py
# desc: PS-Q18G checker for latest_prediction_summary_widget render-disabled component packet validation. It invokes only the pure-data skeleton packet builder using Q18E props candidate; no Streamlit render, source read, D-hot discovery, refresh, writes, AutoTrade, or broker calls.

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Mapping

BTCTS_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "btcts_next", "src")
if BTCTS_SRC not in sys.path:
    sys.path.insert(0, BTCTS_SRC)

from check_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight import CHECKER_VERSION as PS_Q18E_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight import _observed_schema_probe_packet as build_observed_schema_probe_packet
from check_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight import build_report as build_ps_q18e_report
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_props_binding_preflight import build_latest_prediction_summary_widget_props_binding_preflight_packet
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_render_disabled_packet_validation import LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_VALIDATION_VERSION, build_latest_prediction_summary_widget_render_disabled_packet_validation

CHECKER = "ps_q18g_latest_prediction_summary_widget_render_disabled_packet_validation"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18g_latest_prediction_summary_widget_render_disabled_packet_validation.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_VALIDATION_CHECK_VERSION = "latest_prediction_summary_widget_render_disabled_packet_validation.v1"
PS_Q18E_SOURCE_CHECKER_VERSION = PS_Q18E_CHECKER_VERSION


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _safe_q18e_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q18E_SOURCE_CHECKER_VERSION:
        failures.append("q18e_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q18e_report_not_ok")
    if report.get("props_packet_valid") is not True:
        failures.append("q18e_props_packet_not_valid")
    if report.get("missing_required_component_props") != []:
        failures.append("q18e_missing_required_component_props_present")
    for key in ("latest_prediction_summary_widget_props_binding_preflight_only", "props_candidate_ready", "props_contract_complete", "props_value_binding_deferred"):
        if report.get(key) is not True:
            failures.append(f"q18e_true_boundary_missing:{key}")
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
        "warroom_ui_trigger_enabled",
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
            failures.append(f"q18e_boundary_not_false:{key}")
    return not failures, failures


def _safe_validation_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("validation_version") != LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_VALIDATION_VERSION:
        failures.append("validation_version_mismatch")
    if packet.get("ok") is not True:
        failures.append("validation_packet_not_ok")
    if packet.get("component_packet_valid") is not True:
        failures.append("component_packet_not_valid")
    if packet.get("component_packet_state") != "read_only_component_skeleton_render_disabled":
        failures.append("component_packet_state_mismatch")
    if packet.get("component_missing_props") != []:
        failures.append("component_missing_props_present")
    if packet.get("component_source_generated_at") != "schema_verified_value_not_bound":
        failures.append("component_source_generated_at_not_placeholder")
    if packet.get("component_source_artifact_ref") != "schema_verified_value_not_bound":
        failures.append("component_source_artifact_ref_not_placeholder")
    for key in (
        "read_only",
        "non_executing",
        "latest_prediction_summary_widget_render_disabled_packet_validation_only",
        "render_disabled_component_packet_validation_only",
        "component_skeleton_packet_only",
        "props_candidate_supplied_to_packet_builder",
        "props_value_binding_deferred",
    ):
        if packet.get(key) is not True:
            failures.append(f"validation_true_boundary_missing:{key}")
    for key in (
        "real_payload_values_bound",
        "streamlit_render_allowed",
        "streamlit_render_invoked",
        "real_prediction_widget_rendering_allowed",
        "component_runtime_binding_allowed",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_ui_trigger_enabled",
        "actual_source_read_invoked_by_validation",
        "actual_source_read_allowed_by_validation",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
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
            failures.append(f"validation_false_boundary_not_false:{key}")
    return not failures, failures


def _observed_props_preflight_packet() -> dict[str, Any]:
    schema_packet = build_observed_schema_probe_packet()
    return build_latest_prediction_summary_widget_props_binding_preflight_packet(supplied_schema_probe_packet=schema_packet)


def build_report(*, supplied_q18e_report: Mapping[str, Any] | Any | None = None, supplied_props_preflight_packet: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18e_report = _as_mapping(supplied_q18e_report)
    props_preflight_packet = _as_mapping(supplied_props_preflight_packet)
    if use_observed_fixture:
        if not q18e_report:
            q18e_report = build_ps_q18e_report(use_observed_fixture=True)
        if not props_preflight_packet:
            props_preflight_packet = _observed_props_preflight_packet()
    safe_q18e, q18e_failures = _safe_q18e_boundary(q18e_report)
    validation_packet = build_latest_prediction_summary_widget_render_disabled_packet_validation(supplied_props_preflight_packet=props_preflight_packet) if safe_q18e and props_preflight_packet else {}
    safe_validation, validation_failures = _safe_validation_packet(validation_packet) if validation_packet else (False, [] if props_preflight_packet else ["props_preflight_packet_missing"])
    ok = bool(safe_q18e and safe_validation)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "latest_prediction_summary_widget_render_disabled_packet_validation_check_version": LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_VALIDATION_CHECK_VERSION,
        "stage": "latest_prediction_summary_widget_render_disabled_component_packet_validation_before_real_rendering_refresh_and_writes",
        "source_q18e_checker_version": PS_Q18E_SOURCE_CHECKER_VERSION,
        "source_q18e_report_valid": safe_q18e,
        "source_q18e_validation_failures": q18e_failures,
        "validation_packet_valid": safe_validation,
        "validation_failures": validation_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "validation_version": LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_VALIDATION_VERSION,
        "widget_family_id": validation_packet.get("widget_family_id") if validation_packet else "latest_prediction_summary_widget",
        "source_packet_id": validation_packet.get("source_packet_id") if validation_packet else "latest_prediction_source_review_packet",
        "component_packet_builder_invoked": bool(validation_packet.get("component_packet_builder_invoked")) if validation_packet else False,
        "component_packet_valid": bool(validation_packet.get("component_packet_valid")) if validation_packet else False,
        "component_packet_state": validation_packet.get("component_packet_state") if validation_packet else "",
        "component_missing_props": list(validation_packet.get("component_missing_props") or []) if validation_packet else [],
        "component_source_generated_at": validation_packet.get("component_source_generated_at") if validation_packet else "",
        "component_source_artifact_ref": validation_packet.get("component_source_artifact_ref") if validation_packet else "",
        "recommended_first_validation": "latest_prediction_summary_widget_render_disabled_component_packet_validation_guard" if ok else "",
        "recommended_next_slice": "PS-Q18H WarRoom render-disabled latest_prediction_summary_widget packet status row mount or first real payload value mapping preflight; real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18G validates that the latest_prediction_summary_widget pure-data component packet builder returns a render-disabled skeleton packet when supplied the Q18E props candidate. It does not invoke Streamlit rendering, perform new file reads, reparse payloads, discover D-hot, mutate WarRoom, refresh, write artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_render_disabled_packet_validation_only": True,
        "render_disabled_component_packet_validation_only": True,
        "component_skeleton_packet_only": True,
        "props_candidate_supplied_to_packet_builder": ok,
        "props_value_binding_deferred": True,
        "real_payload_values_bound": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
        "real_prediction_widget_rendering_allowed": False,
        "component_runtime_binding_allowed": False,
        "warroom_page_mutation_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "warroom_ui_trigger_enabled": False,
        "actual_source_read_invoked_by_validation": False,
        "actual_source_read_allowed_by_validation": False,
        "payload_reparse_allowed": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
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
    parser = argparse.ArgumentParser(description="PS-Q18G latest prediction summary widget render-disabled packet validation")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use Q18E observed props preflight packet; no Streamlit rendering, source read, refresh, or write is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
