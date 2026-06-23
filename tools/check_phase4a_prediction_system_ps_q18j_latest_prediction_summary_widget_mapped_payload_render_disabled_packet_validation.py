# path: ./tools/check_phase4a_prediction_system_ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.py
# desc: PS-Q18J checker for latest_prediction_summary_widget render-disabled packet validation with mapped real payload values. It invokes only the pure-data skeleton packet builder; no Streamlit render, source read, D-hot discovery, refresh, writes, AutoTrade, or broker calls.

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Mapping

BTCTS_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "btcts_next", "src")
if BTCTS_SRC not in sys.path:
    sys.path.insert(0, BTCTS_SRC)

from check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight import CHECKER_VERSION as PS_Q18I_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight import _observed_props_preflight_packet, build_report as build_ps_q18i_report, observed_decoded_payload_fixture
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_real_payload_value_mapping_preflight import build_latest_prediction_summary_widget_real_payload_value_mapping_preflight_packet
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation import LATEST_PREDICTION_SUMMARY_WIDGET_MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_VALIDATION_VERSION, build_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation

CHECKER = "ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.v1"
MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_VALIDATION_CHECK_VERSION = "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.v1"
PS_Q18I_SOURCE_CHECKER_VERSION = PS_Q18I_CHECKER_VERSION


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _observed_mapping_preflight_packet() -> dict[str, Any]:
    return build_latest_prediction_summary_widget_real_payload_value_mapping_preflight_packet(
        supplied_props_preflight_packet=_observed_props_preflight_packet(),
        supplied_decoded_payload=observed_decoded_payload_fixture(),
    )


def _safe_q18i_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q18I_SOURCE_CHECKER_VERSION:
        failures.append("q18i_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q18i_report_not_ok")
    if report.get("mapping_packet_valid") is not True:
        failures.append("q18i_mapping_packet_not_valid")
    if report.get("missing_required_payload_value_keys") != []:
        failures.append("q18i_missing_required_payload_value_keys_present")
    if report.get("missing_required_component_props") != []:
        failures.append("q18i_missing_required_component_props_present")
    for key in ("latest_prediction_summary_widget_real_payload_value_mapping_preflight_only", "decoded_payload_supplied", "decoded_payload_values_mapped_to_props_candidate", "real_payload_values_bound_to_props_candidate"):
        if report.get(key) is not True:
            failures.append(f"q18i_true_boundary_missing:{key}")
    if report.get("props_value_binding_deferred") is not False:
        failures.append("q18i_props_value_binding_deferred_not_false")
    for key in (
        "real_payload_values_bound_to_component",
        "component_props_binding_allowed",
        "component_props_bound_to_component",
        "component_runtime_binding_allowed",
        "streamlit_render_allowed",
        "streamlit_render_invoked",
        "render_invocation_allowed",
        "real_prediction_widget_rendering_allowed",
        "actual_source_read_invoked_by_mapping",
        "actual_source_read_allowed_by_mapping",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
        "refresh_invocation_allowed",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "confidence_increase_allowed",
        "parameter_apply_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
    ):
        if report.get(key) is not False:
            failures.append(f"q18i_boundary_not_false:{key}")
    return not failures, failures


def _safe_validation_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("validation_version") != LATEST_PREDICTION_SUMMARY_WIDGET_MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_VALIDATION_VERSION:
        failures.append("validation_version_mismatch")
    if packet.get("ok") is not True:
        failures.append("validation_packet_not_ok")
    if packet.get("component_packet_valid") is not True:
        failures.append("component_packet_not_valid")
    if packet.get("component_packet_state") != "read_only_component_skeleton_render_disabled":
        failures.append("component_packet_state_mismatch")
    if packet.get("component_missing_props") != []:
        failures.append("component_missing_props_present")
    expected_values = {
        "mapped_prediction_run_id": "ps_q18i_fixture_run",
        "mapped_market_uid": "BTC-USD",
        "mapped_source_generated_at": "2026-06-22T00:00:00Z",
        "mapped_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
        "component_source_generated_at": "2026-06-22T00:00:00Z",
        "component_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
    }
    for key, value in expected_values.items():
        if packet.get(key) != value:
            failures.append(f"mapped_or_component_value_mismatch:{key}")
    for key in (
        "read_only",
        "non_executing",
        "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation_only",
        "render_disabled_component_packet_validation_only",
        "component_skeleton_packet_only",
        "mapped_payload_values_supplied_to_packet_builder",
        "real_payload_values_bound_to_props_candidate",
        "real_payload_values_visible_in_component_packet",
    ):
        if packet.get(key) is not True:
            failures.append(f"validation_true_boundary_missing:{key}")
    for key in (
        "real_payload_values_bound_to_component",
        "component_props_binding_allowed",
        "component_props_bound_to_component",
        "component_runtime_binding_allowed",
        "streamlit_render_allowed",
        "streamlit_render_invoked",
        "render_invocation_allowed",
        "real_prediction_widget_rendering_allowed",
        "actual_source_read_invoked_by_validation",
        "actual_source_read_allowed_by_validation",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
        "refresh_invocation_allowed",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "confidence_increase_allowed",
        "parameter_apply_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
    ):
        if packet.get(key) is not False:
            failures.append(f"validation_false_boundary_not_false:{key}")
    return not failures, failures


def build_report(*, supplied_q18i_report: Mapping[str, Any] | Any | None = None, supplied_mapping_preflight_packet: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18i_report = _as_mapping(supplied_q18i_report)
    mapping_packet = _as_mapping(supplied_mapping_preflight_packet)
    if use_observed_fixture:
        if not q18i_report:
            q18i_report = build_ps_q18i_report(use_observed_fixture=True)
        if not mapping_packet:
            mapping_packet = _observed_mapping_preflight_packet()
    safe_q18i, q18i_failures = _safe_q18i_boundary(q18i_report)
    validation_packet = build_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation(supplied_mapping_preflight_packet=mapping_packet) if safe_q18i and mapping_packet else {}
    safe_validation, validation_failures = _safe_validation_packet(validation_packet) if validation_packet else (False, [] if mapping_packet else ["mapping_preflight_packet_missing"])
    ok = bool(safe_q18i and safe_validation)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "mapped_payload_render_disabled_packet_validation_check_version": MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_VALIDATION_CHECK_VERSION,
        "stage": "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation_before_real_rendering_refresh_and_writes",
        "source_q18i_checker_version": PS_Q18I_SOURCE_CHECKER_VERSION,
        "source_q18i_report_valid": safe_q18i,
        "source_q18i_validation_failures": q18i_failures,
        "validation_packet_valid": safe_validation,
        "validation_failures": validation_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "validation_version": LATEST_PREDICTION_SUMMARY_WIDGET_MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_VALIDATION_VERSION,
        "widget_family_id": validation_packet.get("widget_family_id") if validation_packet else "latest_prediction_summary_widget",
        "source_packet_id": validation_packet.get("source_packet_id") if validation_packet else "latest_prediction_source_review_packet",
        "component_packet_builder_invoked": bool(validation_packet.get("component_packet_builder_invoked")) if validation_packet else False,
        "component_packet_valid": bool(validation_packet.get("component_packet_valid")) if validation_packet else False,
        "component_packet_state": validation_packet.get("component_packet_state") if validation_packet else "",
        "component_missing_props": list(validation_packet.get("component_missing_props") or []) if validation_packet else [],
        "mapped_prediction_run_id": validation_packet.get("mapped_prediction_run_id") if validation_packet else "",
        "mapped_market_uid": validation_packet.get("mapped_market_uid") if validation_packet else "",
        "mapped_source_generated_at": validation_packet.get("mapped_source_generated_at") if validation_packet else "",
        "mapped_source_artifact_ref": validation_packet.get("mapped_source_artifact_ref") if validation_packet else "",
        "component_source_generated_at": validation_packet.get("component_source_generated_at") if validation_packet else "",
        "component_source_artifact_ref": validation_packet.get("component_source_artifact_ref") if validation_packet else "",
        "recommended_first_validation": "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation_guard" if ok else "",
        "recommended_next_slice": "PS-Q18K WarRoom mapped real payload render-disabled packet status row mount or first operator-visible latest summary value panel; real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18J validates that the latest_prediction_summary_widget pure-data component packet builder returns a render-disabled skeleton packet when supplied PS-Q18I mapped real payload values. It does not invoke Streamlit rendering, perform file reads, reparse payloads, discover D-hot, mutate WarRoom, refresh, write artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation_only": True,
        "render_disabled_component_packet_validation_only": True,
        "component_skeleton_packet_only": True,
        "mapped_payload_values_supplied_to_packet_builder": ok,
        "real_payload_values_bound_to_props_candidate": ok,
        "real_payload_values_bound_to_component": False,
        "real_payload_values_visible_in_component_packet": ok,
        "component_props_binding_allowed": False,
        "component_props_bound_to_component": False,
        "component_runtime_binding_allowed": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
        "render_invocation_allowed": False,
        "real_prediction_widget_rendering_allowed": False,
        "actual_source_read_invoked_by_validation": False,
        "actual_source_read_allowed_by_validation": False,
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
    parser = argparse.ArgumentParser(description="PS-Q18J latest prediction summary widget mapped payload render-disabled packet validation")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use Q18I in-memory mapped payload fixture; no Streamlit rendering, source read, refresh, or write is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
