# path: ./tools/check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.py
# desc: PS-Q18I checker for latest_prediction_summary_widget real decoded-payload value mapping preflight. It uses supplied decoded payload only; no file read, D-hot discovery, component binding, Streamlit render, refresh, writes, AutoTrade, or broker calls.

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
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_real_payload_value_mapping_preflight import LATEST_PREDICTION_SUMMARY_WIDGET_REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_VERSION, build_latest_prediction_summary_widget_real_payload_value_mapping_preflight_packet

CHECKER = "ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.v1"
REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_CHECK_VERSION = "latest_prediction_summary_widget_real_payload_value_mapping_preflight.v1"
PS_Q18E_SOURCE_CHECKER_VERSION = PS_Q18E_CHECKER_VERSION


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def observed_decoded_payload_fixture() -> dict[str, Any]:
    return {
        "prediction_run_id": "ps_q18i_fixture_run",
        "generated_at": "2026-06-22T00:00:00Z",
        "market_uid": "BTC-USD",
        "source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
        "read_only_fixture": True,
    }


def _observed_props_preflight_packet() -> dict[str, Any]:
    schema_packet = build_observed_schema_probe_packet()
    return build_latest_prediction_summary_widget_props_binding_preflight_packet(supplied_schema_probe_packet=schema_packet)


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
    for key in ("latest_prediction_summary_widget_props_binding_preflight_only", "props_candidate_ready", "props_contract_complete"):
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
            failures.append(f"q18e_boundary_not_false:{key}")
    return not failures, failures


def _safe_mapping_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("mapping_preflight_version") != LATEST_PREDICTION_SUMMARY_WIDGET_REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_VERSION:
        failures.append("mapping_preflight_version_mismatch")
    if packet.get("ok") is not True:
        failures.append("mapping_packet_not_ok")
    if packet.get("missing_required_payload_value_keys") != []:
        failures.append("missing_required_payload_values_present")
    if packet.get("missing_required_component_props") != []:
        failures.append("missing_required_component_props_present")
    expected_values = {
        "mapped_prediction_run_id": "ps_q18i_fixture_run",
        "mapped_market_uid": "BTC-USD",
        "mapped_source_generated_at": "2026-06-22T00:00:00Z",
        "mapped_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
    }
    for key, value in expected_values.items():
        if packet.get(key) != value:
            failures.append(f"mapped_value_mismatch:{key}")
    for key in (
        "read_only",
        "non_executing",
        "latest_prediction_summary_widget_real_payload_value_mapping_preflight_only",
        "decoded_payload_supplied",
        "decoded_payload_values_mapped_to_props_candidate",
        "props_contract_complete",
        "real_payload_values_bound_to_props_candidate",
    ):
        if packet.get(key) is not True:
            failures.append(f"mapping_true_boundary_missing:{key}")
    if packet.get("props_value_binding_deferred") is not False:
        failures.append("props_value_binding_should_not_be_deferred_after_props_candidate_mapping")
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
            failures.append(f"mapping_false_boundary_not_false:{key}")
    return not failures, failures


def build_report(*, supplied_q18e_report: Mapping[str, Any] | Any | None = None, supplied_props_preflight_packet: Mapping[str, Any] | Any | None = None, supplied_decoded_payload: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18e_report = _as_mapping(supplied_q18e_report)
    props_packet = _as_mapping(supplied_props_preflight_packet)
    decoded_payload = _as_mapping(supplied_decoded_payload)
    if use_observed_fixture:
        if not q18e_report:
            q18e_report = build_ps_q18e_report(use_observed_fixture=True)
        if not props_packet:
            props_packet = _observed_props_preflight_packet()
        if not decoded_payload:
            decoded_payload = observed_decoded_payload_fixture()
    safe_q18e, q18e_failures = _safe_q18e_boundary(q18e_report)
    mapping_packet = build_latest_prediction_summary_widget_real_payload_value_mapping_preflight_packet(
        supplied_props_preflight_packet=props_packet,
        supplied_decoded_payload=decoded_payload,
    ) if safe_q18e and props_packet and decoded_payload else {}
    safe_mapping, mapping_failures = _safe_mapping_packet(mapping_packet) if mapping_packet else (False, [] if decoded_payload else ["decoded_payload_missing"])
    ok = bool(safe_q18e and safe_mapping)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "real_payload_value_mapping_preflight_check_version": REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_CHECK_VERSION,
        "stage": "latest_prediction_summary_widget_real_payload_value_mapping_preflight_before_component_binding_real_rendering_refresh_and_writes",
        "source_q18e_checker_version": PS_Q18E_SOURCE_CHECKER_VERSION,
        "source_q18e_report_valid": safe_q18e,
        "source_q18e_validation_failures": q18e_failures,
        "mapping_packet_valid": safe_mapping,
        "mapping_validation_failures": mapping_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "mapping_preflight_version": LATEST_PREDICTION_SUMMARY_WIDGET_REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_VERSION,
        "widget_family_id": mapping_packet.get("widget_family_id") if mapping_packet else "latest_prediction_summary_widget",
        "source_packet_id": mapping_packet.get("source_packet_id") if mapping_packet else "latest_prediction_source_review_packet",
        "mapped_props_candidate_key_count": int(mapping_packet.get("mapped_props_candidate_key_count") or 0) if mapping_packet else 0,
        "missing_required_payload_value_keys": list(mapping_packet.get("missing_required_payload_value_keys") or []) if mapping_packet else [],
        "missing_required_component_props": list(mapping_packet.get("missing_required_component_props") or []) if mapping_packet else [],
        "mapped_prediction_run_id": mapping_packet.get("mapped_prediction_run_id") if mapping_packet else "",
        "mapped_market_uid": mapping_packet.get("mapped_market_uid") if mapping_packet else "",
        "mapped_source_generated_at": mapping_packet.get("mapped_source_generated_at") if mapping_packet else "",
        "mapped_source_artifact_ref": mapping_packet.get("mapped_source_artifact_ref") if mapping_packet else "",
        "recommended_first_validation": "latest_prediction_summary_widget_real_payload_value_mapping_preflight_guard" if ok else "",
        "recommended_next_slice": "PS-Q18J render-disabled latest_prediction_summary_widget packet validation with mapped real payload values; real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18I maps already-supplied decoded latest-prediction payload values into a latest_prediction_summary_widget props candidate. It does not read files, reparse payloads, discover D-hot, bind props to a component, render a widget, mutate WarRoom, refresh, write artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_real_payload_value_mapping_preflight_only": True,
        "decoded_payload_supplied": ok,
        "decoded_payload_values_mapped_to_props_candidate": ok,
        "props_value_binding_deferred": False if ok else True,
        "real_payload_values_bound_to_props_candidate": ok,
        "real_payload_values_bound_to_component": False,
        "component_props_binding_allowed": False,
        "component_props_bound_to_component": False,
        "component_runtime_binding_allowed": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
        "render_invocation_allowed": False,
        "real_prediction_widget_rendering_allowed": False,
        "actual_source_read_invoked_by_mapping": False,
        "actual_source_read_allowed_by_mapping": False,
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
    parser = argparse.ArgumentParser(description="PS-Q18I latest prediction summary widget real payload value mapping preflight")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use an in-memory decoded payload fixture; no file read, D-hot discovery, render, refresh, or write is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
