# path: ./tools/check_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight.py
# desc: PS-Q17Y WarRoom prediction widget actual-source preflight checker. It validates source-binding readiness from PS-Q17P integration rows and PS-Q17X page review mount, but never reads D-hot, renders real Prediction widgets, invokes refresh, writes artifacts, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint import CHECKER_VERSION as PS_Q17P_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint import REQUIRED_INTEGRATION_FIELDS, WIDGET_FAMILY_ORDER, build_report as build_ps_q17p_report
from check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount import CHECKER_VERSION as PS_Q17X_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount import build_report as build_ps_q17x_report

CHECKER = "ps_q17y_warroom_prediction_widget_actual_source_preflight"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight.v1"
ACTUAL_SOURCE_PREFLIGHT_VERSION = "warroom_prediction_widget_actual_source_preflight.v1"
PS_Q17P_SOURCE_CHECKER_VERSION = PS_Q17P_CHECKER_VERSION
PS_Q17X_SOURCE_CHECKER_VERSION = PS_Q17X_CHECKER_VERSION


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _fixture_q17p_report() -> dict[str, Any]:
    return build_ps_q17p_report(use_observed_fixture=True)


def _fixture_q17x_report() -> dict[str, Any]:
    return build_ps_q17x_report(use_observed_fixture=True)


def _safe_q17p_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17P_SOURCE_CHECKER_VERSION:
        failures.append("q17p_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17p_report_not_ok")
    if report.get("widget_family_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17p_widget_family_count_mismatch")
    rows = [_as_mapping(row) for row in _as_list(report.get("integration_rows"))]
    if [str(row.get("widget_family_id") or "") for row in rows] != list(WIDGET_FAMILY_ORDER):
        failures.append("q17p_widget_family_order_mismatch")
    for key in (
        "warroom_widget_implementation_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_mount_patch_allowed",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "d_hot_actual_read_allowed",
        "confidence_increase_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
    ):
        if report.get(key) is not False:
            failures.append(f"q17p_boundary_not_false:{key}")
    return not failures, failures


def _safe_q17x_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17X_SOURCE_CHECKER_VERSION:
        failures.append("q17x_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17x_report_not_ok")
    if report.get("review_row_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17x_review_row_count_mismatch")
    if report.get("review_zone_count") != 3:
        failures.append("q17x_review_zone_count_mismatch")
    if report.get("page_body_review_mount_applied") is not True:
        failures.append("q17x_page_body_review_mount_missing")
    if report.get("visible_review_rows_rendered") is not True:
        failures.append("q17x_visible_review_rows_missing")
    for key in (
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
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
    ):
        if report.get(key) is not False:
            failures.append(f"q17x_boundary_not_false:{key}")
    return not failures, failures


def _preflight_row(row: Mapping[str, Any]) -> dict[str, Any]:
    widget_id = str(row.get("widget_family_id") or "")
    return {
        "widget_family_id": widget_id,
        "source_packet_id": str(row.get("source_packet_id") or ""),
        "source_checker_version": str(row.get("source_checker_version") or ""),
        "freshness_field": str(row.get("freshness_field") or ""),
        "source_artifact_ref_field": str(row.get("source_artifact_ref_field") or ""),
        "release_gate_field": str(row.get("release_gate_field") or ""),
        "mount_zone_hint": str(row.get("mount_zone_hint") or ""),
        "dependency_note": str(row.get("dependency_note") or ""),
        "actual_source_preflight_state": "source_contract_ready_actual_read_deferred",
        "actual_source_binding_ready": True,
        "actual_source_bound": False,
        "source_artifact_resolved": False,
        "freshness_checked_against_d_hot": False,
        "readiness_row_visible_in_warroom": False,
        "real_widget_render_ready": False,
        "render_allowed": False,
        "actual_source_read_allowed": False,
        "d_hot_actual_read_allowed": False,
        "refresh_invocation_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "confidence_increase_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "next_validation": f"{widget_id}_actual_source_binding_guard",
    }


def _preflight_rows(q17p_report: Mapping[str, Any]) -> list[dict[str, Any]]:
    source_rows = [_as_mapping(row) for row in _as_list(q17p_report.get("integration_rows"))]
    rows = [_preflight_row(row) for row in source_rows]
    return sorted(rows, key=lambda row: WIDGET_FAMILY_ORDER.index(str(row["widget_family_id"])))


def _validate_preflight_rows(rows: list[Mapping[str, Any]]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if len(rows) != len(WIDGET_FAMILY_ORDER):
        failures.append("preflight_row_count_mismatch")
    if [str(row.get("widget_family_id") or "") for row in rows] != list(WIDGET_FAMILY_ORDER):
        failures.append("preflight_widget_order_mismatch")
    for row in rows:
        widget_id = str(row.get("widget_family_id") or "")
        for field in REQUIRED_INTEGRATION_FIELDS:
            if field not in row and field not in ("page_mutation_allowed",):
                failures.append(f"required_field_missing:{widget_id}:{field}")
        for field in ("source_packet_id", "freshness_field", "source_artifact_ref_field", "release_gate_field"):
            if not str(row.get(field) or ""):
                failures.append(f"source_binding_field_empty:{widget_id}:{field}")
        if row.get("actual_source_binding_ready") is not True:
            failures.append(f"binding_not_ready:{widget_id}")
        for key in (
            "actual_source_bound",
            "source_artifact_resolved",
            "freshness_checked_against_d_hot",
            "readiness_row_visible_in_warroom",
            "real_widget_render_ready",
            "render_allowed",
            "actual_source_read_allowed",
            "d_hot_actual_read_allowed",
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
                failures.append(f"preflight_false_boundary_not_false:{widget_id}:{key}")
    return not failures, failures


def build_report(*, supplied_q17p_report: Mapping[str, Any] | Any | None = None, supplied_q17x_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17p_report = _as_mapping(supplied_q17p_report)
    q17x_report = _as_mapping(supplied_q17x_report)
    if use_observed_fixture:
        if not q17p_report:
            q17p_report = _fixture_q17p_report()
        if not q17x_report:
            q17x_report = _fixture_q17x_report()
    safe_q17p, q17p_failures = _safe_q17p_boundary(q17p_report)
    safe_q17x, q17x_failures = _safe_q17x_boundary(q17x_report)
    rows = _preflight_rows(q17p_report) if safe_q17p and safe_q17x else []
    rows_valid, row_failures = _validate_preflight_rows(rows) if rows else (False, [])
    source_packet_ids = sorted({str(row.get("source_packet_id") or "") for row in rows})
    ok = bool(safe_q17p and safe_q17x and rows_valid and len(rows) == len(WIDGET_FAMILY_ORDER))
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "actual_source_preflight_version": ACTUAL_SOURCE_PREFLIGHT_VERSION,
        "stage": "warroom_prediction_widget_actual_source_preflight_before_d_hot_read_and_real_widget_rendering",
        "source_q17p_checker_version": PS_Q17P_SOURCE_CHECKER_VERSION,
        "source_q17x_checker_version": PS_Q17X_SOURCE_CHECKER_VERSION,
        "source_q17p_report_valid": safe_q17p,
        "source_q17x_report_valid": safe_q17x,
        "source_q17p_validation_failures": q17p_failures,
        "source_q17x_validation_failures": q17x_failures,
        "preflight_row_validation_failures": row_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "widget_family_order": list(WIDGET_FAMILY_ORDER),
        "preflight_rows": rows,
        "preflight_row_count": len(rows),
        "unique_source_packet_ids": source_packet_ids,
        "unique_source_packet_count": len(source_packet_ids),
        "required_integration_fields": list(REQUIRED_INTEGRATION_FIELDS),
        "recommended_first_validation": "latest_prediction_summary_widget_actual_source_preflight_guard" if ok else "",
        "recommended_next_slice": "PS-Q17Z WarRoom prediction widget source readiness row mount or actual-source read probe; real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q17Y validates actual-source binding readiness from the existing integration contract and page review mount, but does not bind or read actual sources yet. It emits preflight rows only; D-hot reads, refreshes, writes, real widget rendering, and parameter actions remain disabled.",
        "read_only": True,
        "non_executing": True,
        "actual_source_preflight_only": True,
        "source_binding_contract_ready": ok,
        "source_artifact_resolution_allowed": False,
        "actual_source_bound": False,
        "source_artifact_resolved": False,
        "freshness_checked_against_d_hot": False,
        "readiness_row_visible_in_warroom": False,
        "real_prediction_widget_rendering_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "warroom_page_mutation_allowed": False,
        "warroom_mount_patch_allowed": False,
        "actual_source_read_allowed": False,
        "d_hot_actual_read_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17Y WarRoom prediction widget actual-source preflight")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use PS-Q17P/PS-Q17X observed fixtures; no D-hot read, actual binding, real widget render, refresh, or artifact write is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
