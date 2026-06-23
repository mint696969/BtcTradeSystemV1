# path: ./tools/check_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight.py
# desc: PS-Q18A WarRoom prediction widget source artifact resolution preflight checker. It validates artifact-ref resolution readiness only; it never resolves source artifacts, reads D-hot, renders real Prediction widgets, invokes refresh, writes artifacts, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Mapping

BTCTS_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "btcts_next", "src")
if BTCTS_SRC not in sys.path:
    sys.path.insert(0, BTCTS_SRC)

from check_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount import CHECKER_VERSION as PS_Q17Z_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount import build_report as build_ps_q17z_report
from btcts.apps.operator_ui.components.prediction_warroom_prediction_widget_source_artifact_resolution_preflight_panel import PREDICTION_WARROOM_SOURCE_ARTIFACT_RESOLUTION_PREFLIGHT_PANEL_VERSION, build_prediction_warroom_prediction_widget_source_artifact_resolution_preflight_packet

CHECKER = "ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight.v1"
SOURCE_ARTIFACT_RESOLUTION_PREFLIGHT_VERSION = "warroom_prediction_widget_source_artifact_resolution_preflight.v1"
PS_Q17Z_SOURCE_CHECKER_VERSION = PS_Q17Z_CHECKER_VERSION


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _safe_q17z_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17Z_SOURCE_CHECKER_VERSION:
        failures.append("q17z_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17z_report_not_ok")
    if report.get("readiness_row_count") != 12:
        failures.append("q17z_readiness_row_count_mismatch")
    if report.get("unique_source_packet_count") != 9:
        failures.append("q17z_unique_source_packet_count_mismatch")
    if report.get("source_binding_contract_ready") is not True:
        failures.append("q17z_source_binding_contract_not_ready")
    if report.get("readiness_row_visible_in_warroom") is not True:
        failures.append("q17z_readiness_row_not_visible")
    for key in (
        "source_artifact_resolution_allowed",
        "actual_source_bound",
        "source_artifact_resolved",
        "freshness_checked_against_d_hot",
        "real_prediction_widget_rendering_allowed",
        "warroom_widget_rendering_allowed",
        "actual_source_read_allowed",
        "d_hot_actual_read_allowed",
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
            failures.append(f"q17z_boundary_not_false:{key}")
    return not failures, failures


def _safe_panel_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("panel_version") != PREDICTION_WARROOM_SOURCE_ARTIFACT_RESOLUTION_PREFLIGHT_PANEL_VERSION:
        failures.append("panel_version_mismatch")
    if packet.get("ok") is not True:
        failures.append("panel_packet_not_ok")
    if packet.get("artifact_resolution_row_count") != 12:
        failures.append("artifact_resolution_row_count_mismatch")
    if packet.get("unique_artifact_resolution_key_count") != 9:
        failures.append("unique_artifact_resolution_key_count_mismatch")
    if packet.get("unique_source_packet_count") != 9:
        failures.append("unique_source_packet_count_mismatch")
    if packet.get("source_artifact_resolution_preflight_ready") is not True:
        failures.append("source_artifact_resolution_preflight_not_ready")
    rows = list(packet.get("artifact_resolution_rows") or [])
    for row_value in rows:
        row = _as_mapping(row_value)
        widget_id = str(row.get("widget_family_id") or "")
        for field in ("source_packet_id", "source_artifact_ref_field", "freshness_field", "release_gate_field", "artifact_resolution_key"):
            if not str(row.get(field) or ""):
                failures.append(f"row_missing_field:{widget_id}:{field}")
        if row.get("source_artifact_resolution_preflight_ready") is not True:
            failures.append(f"row_preflight_not_ready:{widget_id}")
        for key in (
            "source_artifact_resolution_allowed",
            "source_artifact_resolved",
            "source_artifact_path_materialized",
            "source_artifact_exists_checked",
            "source_artifact_schema_checked",
            "actual_source_bound",
            "actual_source_read_allowed",
            "d_hot_actual_read_allowed",
            "freshness_checked_against_d_hot",
            "real_widget_render_ready",
            "render_allowed",
            "refresh_invocation_allowed",
            "runtime_artifact_write_allowed",
            "status_artifact_write_allowed",
            "confidence_increase_allowed",
            "parameter_apply_allowed",
            "parameter_staging_write_allowed",
            "ledger_append_allowed",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
        ):
            if row.get(key) is not False:
                failures.append(f"row_boundary_not_false:{widget_id}:{key}")
    return not failures, failures


def build_report(*, supplied_q17z_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17z_report = _as_mapping(supplied_q17z_report)
    if not q17z_report and use_observed_fixture:
        q17z_report = build_ps_q17z_report(use_observed_fixture=True)
    safe_q17z, q17z_failures = _safe_q17z_boundary(q17z_report)
    panel_packet = build_prediction_warroom_prediction_widget_source_artifact_resolution_preflight_packet() if safe_q17z else {}
    safe_panel, panel_failures = _safe_panel_packet(panel_packet) if panel_packet else (False, [])
    ok = bool(safe_q17z and safe_panel)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "source_artifact_resolution_preflight_version": SOURCE_ARTIFACT_RESOLUTION_PREFLIGHT_VERSION,
        "stage": "warroom_prediction_widget_source_artifact_resolution_preflight_before_source_materialization_d_hot_read_and_real_widget_rendering",
        "source_q17z_checker_version": PS_Q17Z_SOURCE_CHECKER_VERSION,
        "source_q17z_report_valid": safe_q17z,
        "source_q17z_validation_failures": q17z_failures,
        "panel_packet_valid": safe_panel,
        "panel_validation_failures": panel_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "panel_version": PREDICTION_WARROOM_SOURCE_ARTIFACT_RESOLUTION_PREFLIGHT_PANEL_VERSION,
        "artifact_resolution_row_count": int(panel_packet.get("artifact_resolution_row_count") or 0) if panel_packet else 0,
        "unique_artifact_resolution_key_count": int(panel_packet.get("unique_artifact_resolution_key_count") or 0) if panel_packet else 0,
        "unique_source_packet_count": int(panel_packet.get("unique_source_packet_count") or 0) if panel_packet else 0,
        "unique_artifact_resolution_keys": list(panel_packet.get("unique_artifact_resolution_keys") or []) if panel_packet else [],
        "recommended_first_validation": "latest_prediction_summary_widget_source_artifact_resolution_preflight_guard" if ok else "",
        "recommended_next_slice": "PS-Q18B first bounded actual-source read probe or WarRoom source artifact resolution row mount; real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18A validates that each visible Prediction widget source readiness row has enough artifact-ref metadata for a future resolver. It does not materialize paths, check file existence/schema, read D-hot, refresh, write artifacts, render real widgets, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.",
        "read_only": True,
        "non_executing": True,
        "source_artifact_resolution_preflight_only": True,
        "source_artifact_resolution_preflight_ready": ok,
        "source_artifact_resolution_allowed": False,
        "source_artifact_resolved": False,
        "source_artifact_path_materialized": False,
        "source_artifact_exists_checked": False,
        "source_artifact_schema_checked": False,
        "actual_source_bound": False,
        "actual_source_read_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
        "real_prediction_widget_rendering_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "warroom_page_mutation_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q18A WarRoom prediction widget source artifact resolution preflight")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use PS-Q17Z observed fixture; validates artifact-ref resolution readiness without path materialization, D-hot read, real widget render, refresh, or artifact write.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
