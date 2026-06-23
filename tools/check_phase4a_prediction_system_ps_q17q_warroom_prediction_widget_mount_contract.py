# path: ./tools/check_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract.py
# desc: PS-Q17Q non-executing WarRoom prediction widget mount contract. It consumes the PS-Q17P integration design checkpoint and emits future mount-zone/import/fallback contracts only; it never mutates WarRoom UI, imports new panels, renders widgets, reads D-hot, writes artifacts, invokes refresh, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint import CHECKER_VERSION as PS_Q17P_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint import WIDGET_FAMILY_ORDER, build_report as build_ps_q17p_report

CHECKER = "ps_q17q_warroom_prediction_widget_mount_contract"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract.v1"
PS_Q17P_SOURCE_CHECKER_VERSION = PS_Q17P_CHECKER_VERSION
MOUNT_CONTRACT_VERSION = "warroom_prediction_widget_mount_contract.v1"
MOUNT_ZONE_ORDER = ("prediction_overview_zone", "prediction_realtime_review_zone", "prediction_operator_support_zone")

MOUNT_ZONE_BY_WIDGET = {
    "latest_prediction_summary_widget": "prediction_overview_zone",
    "source_quality_freshness_widget": "prediction_overview_zone",
    "warning_blocker_widget": "prediction_overview_zone",
    "producer_freshness_status_widget": "prediction_overview_zone",
    "runtime_boundary_safety_widget": "prediction_overview_zone",
    "prediction_delta_widget": "prediction_realtime_review_zone",
    "scenario_trace_widget": "prediction_realtime_review_zone",
    "evidence_weighting_widget": "prediction_realtime_review_zone",
    "invalidation_rewrite_widget": "prediction_realtime_review_zone",
    "signal_strength_calibration_widget": "prediction_realtime_review_zone",
    "parameter_candidate_comparison_widget": "prediction_operator_support_zone",
    "replay_outcome_calibration_widget": "prediction_operator_support_zone",
}

REQUIRED_MOUNT_FIELDS = (
    "widget_family_id",
    "source_packet_id",
    "mount_zone_id",
    "mount_slot_id",
    "attach_after_widget_family_id",
    "component_module_contract",
    "component_import_allowed",
    "streamlit_render_allowed",
    "fallback_display_required",
    "page_mutation_allowed",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _integration_rows(report: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [_as_mapping(row) for row in _as_list(report.get("integration_rows"))]


def _safe_q17p_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17P_SOURCE_CHECKER_VERSION:
        failures.append("q17p_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17p_report_not_ok")
    if report.get("design_checkpoint_only") is not True:
        failures.append("q17p_design_checkpoint_only_missing")
    if report.get("widget_family_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17p_widget_family_count_mismatch")
    if report.get("verified_source_packet_count") != 9:
        failures.append("q17p_verified_source_packet_count_mismatch")
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
    row_ids = [str(row.get("widget_family_id") or "") for row in _integration_rows(report)]
    if row_ids != list(WIDGET_FAMILY_ORDER):
        failures.append("q17p_widget_family_order_mismatch")
    for row in _integration_rows(report):
        for key in ("render_allowed", "page_mutation_allowed", "refresh_invocation_allowed", "write_or_apply_allowed"):
            if row.get(key) is not False:
                failures.append(f"q17p_row_boundary_not_false:{row.get('widget_family_id')}:{key}")
    return not failures, failures


def _fixture_q17p_report() -> dict[str, Any]:
    return build_ps_q17p_report(use_observed_fixture=True)


def _slot_id(widget_family_id: str) -> str:
    return f"{widget_family_id}_slot"


def _component_contract(widget_family_id: str) -> str:
    return f"future_component_contract::{widget_family_id}::render_disabled"


def _build_mount_rows(q17p_report: Mapping[str, Any]) -> list[dict[str, Any]]:
    prior_by_widget = {str(row.get("widget_family_id") or ""): row for row in _integration_rows(q17p_report)}
    rows: list[dict[str, Any]] = []
    previous_by_zone: dict[str, str] = {}
    for widget_id in WIDGET_FAMILY_ORDER:
        prior = prior_by_widget.get(widget_id, {})
        zone = MOUNT_ZONE_BY_WIDGET[widget_id]
        attach_after = previous_by_zone.get(zone, "")
        previous_by_zone[zone] = widget_id
        rows.append({
            "widget_family_id": widget_id,
            "source_packet_id": str(prior.get("source_packet_id") or ""),
            "source_checker_version": str(prior.get("source_checker_version") or ""),
            "mount_zone_id": zone,
            "mount_slot_id": _slot_id(widget_id),
            "mount_order_index": len([row for row in rows if row.get("mount_zone_id") == zone]),
            "attach_after_widget_family_id": attach_after,
            "component_module_contract": _component_contract(widget_id),
            "fallback_display_required": True,
            "fallback_display_state": "contract_defined_render_disabled",
            "mount_contract_state": "ready_for_future_mount_contract_render_disabled",
            "component_import_allowed": False,
            "streamlit_render_allowed": False,
            "page_mutation_allowed": False,
            "warroom_mount_patch_allowed": False,
            "refresh_invocation_allowed": False,
            "write_or_apply_allowed": False,
            "next_validation": f"{widget_id}_mount_contract_guard",
        })
    return rows


def _zone_rows(mount_rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    zones: list[dict[str, Any]] = []
    for zone in MOUNT_ZONE_ORDER:
        rows = [row for row in mount_rows if row.get("mount_zone_id") == zone]
        zones.append({
            "mount_zone_id": zone,
            "widget_family_count": len(rows),
            "widget_family_ids": [str(row.get("widget_family_id")) for row in rows],
            "fallback_display_required_count": sum(1 for row in rows if row.get("fallback_display_required") is True),
            "component_import_allowed": False,
            "streamlit_render_allowed": False,
            "page_mutation_allowed": False,
            "warroom_mount_patch_allowed": False,
            "refresh_invocation_allowed": False,
            "zone_contract_state": "ready_for_future_mount_contract_render_disabled",
        })
    return zones


def build_report(*, supplied_q17p_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17p_report = _as_mapping(supplied_q17p_report)
    if not q17p_report and use_observed_fixture:
        q17p_report = _fixture_q17p_report()
    safe_q17p, validation_failures = _safe_q17p_boundary(q17p_report)
    mount_rows = _build_mount_rows(q17p_report) if safe_q17p else []
    zone_rows = _zone_rows(mount_rows) if mount_rows else []
    ok = bool(safe_q17p and len(mount_rows) == len(WIDGET_FAMILY_ORDER) and len(zone_rows) == len(MOUNT_ZONE_ORDER))
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "mount_contract_version": MOUNT_CONTRACT_VERSION,
        "stage": "warroom_prediction_widget_mount_contract_before_ui_import_page_patch_and_rendering",
        "source_checker_version": PS_Q17P_SOURCE_CHECKER_VERSION,
        "source_q17p_report_valid": safe_q17p,
        "source_q17p_validation_failures": validation_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "widget_family_order": list(WIDGET_FAMILY_ORDER),
        "mount_zone_order": list(MOUNT_ZONE_ORDER),
        "required_mount_fields": list(REQUIRED_MOUNT_FIELDS),
        "mount_rows": mount_rows,
        "mount_zone_rows": zone_rows,
        "mount_row_count": len(mount_rows),
        "mount_zone_count": len(zone_rows),
        "component_import_blockers": [row["widget_family_id"] for row in mount_rows if row.get("component_import_allowed") is False],
        "streamlit_render_blockers": [row["widget_family_id"] for row in mount_rows if row.get("streamlit_render_allowed") is False],
        "page_mutation_blockers": [row["widget_family_id"] for row in mount_rows if row.get("page_mutation_allowed") is False],
        "fallback_display_required_count": sum(1 for row in mount_rows if row.get("fallback_display_required") is True),
        "recommended_first_validation": "latest_prediction_summary_widget_mount_contract_guard" if mount_rows else "",
        "recommended_next_slice": "PS-Q17R WarRoom prediction widget read-only component skeleton contract or actual-source preflight; UI import/page patch, widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q17Q defines future WarRoom prediction widget mount zones, slots, import boundaries, and fallback display requirements. It does not import components, mutate warroom_page.py, render widgets, read D-hot, refresh, write artifacts, or stage/apply parameters.",
        "read_only": True,
        "non_executing": True,
        "mount_contract_only": True,
        "contract_only": True,
        "diagnostic_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "warroom_page_mutation_allowed": False,
        "warroom_page_import_patch_allowed": False,
        "warroom_mount_patch_allowed": False,
        "component_import_allowed": False,
        "streamlit_render_allowed": False,
        "fallback_display_only": True,
        "warroom_ui_trigger_enabled": False,
        "refresh_invocation_allowed": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "d_hot_actual_read_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17Q WarRoom prediction widget mount contract")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use the PS-Q17P observed fixture path; no D-hot read, UI import, page patch, or rendering is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
