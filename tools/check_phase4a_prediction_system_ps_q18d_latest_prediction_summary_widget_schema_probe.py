# path: ./tools/check_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe.py
# desc: PS-Q18D checker for latest_prediction_summary_widget schema-specific probe. It consumes Q18B fixture probe packet metadata; it does not perform new file reads, D-hot discovery, WarRoom mutation, real widget rendering, refresh, writes, AutoTrade, or broker calls.

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Mapping

BTCTS_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "btcts_next", "src")
if BTCTS_SRC not in sys.path:
    sys.path.insert(0, BTCTS_SRC)

from check_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe import CHECKER_VERSION as PS_Q18B_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe import build_report as build_ps_q18b_report
from check_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe import _fixture_probe_packet as build_q18b_fixture_probe_packet
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_schema_probe import LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_VERSION, REQUIRED_SUMMARY_SCHEMA_KEYS, build_latest_prediction_summary_widget_schema_probe_packet

CHECKER = "ps_q18d_latest_prediction_summary_widget_schema_probe"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe.v1"
LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_CHECK_VERSION = "latest_prediction_summary_widget_schema_probe.v1"
PS_Q18B_SOURCE_CHECKER_VERSION = PS_Q18B_CHECKER_VERSION


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _safe_q18b_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q18B_SOURCE_CHECKER_VERSION:
        failures.append("q18b_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q18b_report_not_ok")
    if report.get("probe_packet_valid") is not True:
        failures.append("q18b_probe_packet_not_valid")
    for key in ("bounded_actual_source_read_probe_only", "single_file_probe_only", "actual_file_read_attempted", "payload_decode_succeeded", "schema_probe_ok"):
        if report.get(key) is not True:
            failures.append(f"q18b_true_boundary_missing:{key}")
    for key in (
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
        "real_prediction_widget_rendering_allowed",
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
            failures.append(f"q18b_boundary_not_false:{key}")
    return not failures, failures


def _safe_schema_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("probe_version") != LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_VERSION:
        failures.append("schema_probe_version_mismatch")
    if packet.get("ok") is not True:
        failures.append("schema_probe_packet_not_ok")
    if packet.get("widget_family_id") != "latest_prediction_summary_widget":
        failures.append("widget_family_mismatch")
    if packet.get("source_packet_id") != "latest_prediction_source_review_packet":
        failures.append("source_packet_mismatch")
    if packet.get("schema_probe_row_count") != len(REQUIRED_SUMMARY_SCHEMA_KEYS):
        failures.append("schema_probe_row_count_mismatch")
    if packet.get("missing_required_schema_keys") != []:
        failures.append("missing_required_schema_keys_present")
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_schema_probe_only", "schema_specific_probe_ready", "preview_key_contract_only"):
        if packet.get(key) is not True:
            failures.append(f"schema_true_boundary_missing:{key}")
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
    ):
        if packet.get(key) is not False:
            failures.append(f"schema_false_boundary_not_false:{key}")
    return not failures, failures


def build_report(*, supplied_q18b_report: Mapping[str, Any] | Any | None = None, supplied_probe_packet: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18b_report = _as_mapping(supplied_q18b_report)
    probe_packet = _as_mapping(supplied_probe_packet)
    if use_observed_fixture:
        if not q18b_report:
            q18b_report = build_ps_q18b_report(use_observed_fixture=True)
        if not probe_packet:
            probe_packet = build_q18b_fixture_probe_packet()
    safe_q18b, q18b_failures = _safe_q18b_boundary(q18b_report)
    schema_packet = build_latest_prediction_summary_widget_schema_probe_packet(supplied_probe_packet=probe_packet) if safe_q18b and probe_packet else {}
    safe_schema, schema_failures = _safe_schema_packet(schema_packet) if schema_packet else (False, [] if probe_packet else ["probe_packet_missing"])
    ok = bool(safe_q18b and safe_schema)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "latest_prediction_summary_widget_schema_probe_check_version": LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_CHECK_VERSION,
        "stage": "latest_prediction_summary_widget_schema_probe_before_widget_props_binding_real_rendering_refresh_and_writes",
        "source_q18b_checker_version": PS_Q18B_SOURCE_CHECKER_VERSION,
        "source_q18b_report_valid": safe_q18b,
        "source_q18b_validation_failures": q18b_failures,
        "schema_packet_valid": safe_schema,
        "schema_validation_failures": schema_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "schema_probe_version": LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_VERSION,
        "widget_family_id": schema_packet.get("widget_family_id") if schema_packet else "latest_prediction_summary_widget",
        "source_packet_id": schema_packet.get("source_packet_id") if schema_packet else "latest_prediction_source_review_packet",
        "required_schema_keys": list(REQUIRED_SUMMARY_SCHEMA_KEYS),
        "schema_probe_row_count": int(schema_packet.get("schema_probe_row_count") or 0) if schema_packet else 0,
        "missing_required_schema_keys": list(schema_packet.get("missing_required_schema_keys") or []) if schema_packet else [],
        "recommended_first_validation": "latest_prediction_summary_widget_minimum_schema_probe_guard" if ok else "",
        "recommended_next_slice": "PS-Q18E first latest_prediction_summary_widget props binding preflight or schema-specific probe status row mount; real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18D checks the latest_prediction_summary_widget minimum schema keys against Q18B probe metadata. It does not perform new file reads, reparse payloads, discover D-hot, mutate WarRoom, bind widget props, render real widgets, refresh, write artifacts, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_schema_probe_only": True,
        "schema_specific_probe_ready": ok,
        "preview_key_contract_only": True,
        "payload_reparse_allowed": False,
        "actual_source_read_invoked_by_schema_probe": False,
        "actual_source_read_allowed_by_schema_probe": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
        "warroom_page_mutation_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "real_prediction_widget_rendering_allowed": False,
        "widget_props_binding_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q18D latest prediction summary widget schema-specific probe")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use Q18B temporary JSON fixture/probe metadata; no new actual-source read is performed by this schema probe.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
