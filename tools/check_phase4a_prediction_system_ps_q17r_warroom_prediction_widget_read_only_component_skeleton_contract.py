# path: ./tools/check_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract.py
# desc: PS-Q17R non-executing WarRoom prediction widget read-only component skeleton contract. It consumes the PS-Q17Q mount contract and emits future component skeleton props/fallback contracts only; it never creates component files, imports panels, mutates WarRoom UI, renders widgets, reads D-hot, writes artifacts, invokes refresh, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract import CHECKER_VERSION as PS_Q17Q_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract import MOUNT_ZONE_ORDER, WIDGET_FAMILY_ORDER, build_report as build_ps_q17q_report

CHECKER = "ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract.v1"
PS_Q17Q_SOURCE_CHECKER_VERSION = PS_Q17Q_CHECKER_VERSION
COMPONENT_SKELETON_CONTRACT_VERSION = "warroom_prediction_widget_read_only_component_skeleton_contract.v1"
COMPONENT_MODULE_PREFIX = "btcts.apps.operator_ui.components.prediction_widgets"

REQUIRED_COMPONENT_PROPS = (
    "widget_family_id",
    "source_packet_id",
    "mount_zone_id",
    "mount_slot_id",
    "source_generated_at",
    "source_artifact_ref",
    "release_gate_state",
    "fallback_reason_codes",
    "operator_summary_ja",
    "read_only",
)

REQUIRED_COMPONENT_ROW_FIELDS = (
    "widget_family_id",
    "source_packet_id",
    "mount_zone_id",
    "component_module_path",
    "component_function_name",
    "props_contract_fields",
    "fallback_component_required",
    "component_file_creation_allowed",
    "component_import_allowed",
    "streamlit_render_allowed",
    "page_mutation_allowed",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _mount_rows(report: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [_as_mapping(row) for row in _as_list(report.get("mount_rows"))]


def _safe_q17q_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17Q_SOURCE_CHECKER_VERSION:
        failures.append("q17q_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17q_report_not_ok")
    if report.get("mount_contract_only") is not True:
        failures.append("q17q_mount_contract_only_missing")
    if report.get("mount_row_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17q_mount_row_count_mismatch")
    if report.get("mount_zone_count") != len(MOUNT_ZONE_ORDER):
        failures.append("q17q_mount_zone_count_mismatch")
    if report.get("fallback_display_required_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17q_fallback_display_required_count_mismatch")
    for key in (
        "warroom_widget_implementation_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_page_import_patch_allowed",
        "warroom_mount_patch_allowed",
        "component_import_allowed",
        "streamlit_render_allowed",
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
            failures.append(f"q17q_boundary_not_false:{key}")
    row_ids = [str(row.get("widget_family_id") or "") for row in _mount_rows(report)]
    if row_ids != list(WIDGET_FAMILY_ORDER):
        failures.append("q17q_widget_family_order_mismatch")
    for row in _mount_rows(report):
        for key in (
            "component_import_allowed",
            "streamlit_render_allowed",
            "page_mutation_allowed",
            "warroom_mount_patch_allowed",
            "refresh_invocation_allowed",
            "write_or_apply_allowed",
        ):
            if row.get(key) is not False:
                failures.append(f"q17q_row_boundary_not_false:{row.get('widget_family_id')}:{key}")
        if row.get("fallback_display_required") is not True:
            failures.append(f"q17q_fallback_not_required:{row.get('widget_family_id')}")
    return not failures, failures


def _fixture_q17q_report() -> dict[str, Any]:
    return build_ps_q17q_report(use_observed_fixture=True)


def _component_module_path(widget_family_id: str) -> str:
    return f"{COMPONENT_MODULE_PREFIX}.{widget_family_id}"


def _component_function_name(widget_family_id: str) -> str:
    return f"render_{widget_family_id}"


def _operator_summary(widget_family_id: str) -> str:
    return f"{widget_family_id} is specified as a future read-only WarRoom prediction widget skeleton; rendering and imports remain disabled in PS-Q17R."


def _build_component_rows(q17q_report: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for mount in _mount_rows(q17q_report):
        widget_id = str(mount.get("widget_family_id") or "")
        rows.append({
            "widget_family_id": widget_id,
            "source_packet_id": str(mount.get("source_packet_id") or ""),
            "source_checker_version": str(mount.get("source_checker_version") or ""),
            "mount_zone_id": str(mount.get("mount_zone_id") or ""),
            "mount_slot_id": str(mount.get("mount_slot_id") or ""),
            "component_module_path": _component_module_path(widget_id),
            "component_function_name": _component_function_name(widget_id),
            "props_contract_fields": list(REQUIRED_COMPONENT_PROPS),
            "required_fallback_props": ["fallback_reason_codes", "operator_summary_ja", "read_only"],
            "fallback_component_required": True,
            "fallback_display_state": "component_skeleton_contract_defined_render_disabled",
            "component_contract_state": "ready_for_future_read_only_component_skeleton_render_disabled",
            "operator_summary_ja": _operator_summary(widget_id),
            "component_file_creation_allowed": False,
            "component_import_allowed": False,
            "streamlit_render_allowed": False,
            "page_mutation_allowed": False,
            "warroom_mount_patch_allowed": False,
            "refresh_invocation_allowed": False,
            "actual_source_read_allowed": False,
            "write_or_apply_allowed": False,
            "next_validation": f"{widget_id}_component_skeleton_contract_guard",
        })
    return rows


def build_report(*, supplied_q17q_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17q_report = _as_mapping(supplied_q17q_report)
    if not q17q_report and use_observed_fixture:
        q17q_report = _fixture_q17q_report()
    safe_q17q, validation_failures = _safe_q17q_boundary(q17q_report)
    component_rows = _build_component_rows(q17q_report) if safe_q17q else []
    ok = bool(safe_q17q and len(component_rows) == len(WIDGET_FAMILY_ORDER))
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "component_skeleton_contract_version": COMPONENT_SKELETON_CONTRACT_VERSION,
        "stage": "warroom_prediction_widget_read_only_component_skeleton_contract_before_component_file_creation_import_and_rendering",
        "source_checker_version": PS_Q17Q_SOURCE_CHECKER_VERSION,
        "source_q17q_report_valid": safe_q17q,
        "source_q17q_validation_failures": validation_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "widget_family_order": list(WIDGET_FAMILY_ORDER),
        "mount_zone_order": list(MOUNT_ZONE_ORDER),
        "required_component_props": list(REQUIRED_COMPONENT_PROPS),
        "required_component_row_fields": list(REQUIRED_COMPONENT_ROW_FIELDS),
        "component_rows": component_rows,
        "component_row_count": len(component_rows),
        "fallback_component_required_count": sum(1 for row in component_rows if row.get("fallback_component_required") is True),
        "component_file_creation_blockers": [row["widget_family_id"] for row in component_rows if row.get("component_file_creation_allowed") is False],
        "component_import_blockers": [row["widget_family_id"] for row in component_rows if row.get("component_import_allowed") is False],
        "streamlit_render_blockers": [row["widget_family_id"] for row in component_rows if row.get("streamlit_render_allowed") is False],
        "actual_source_read_blockers": [row["widget_family_id"] for row in component_rows if row.get("actual_source_read_allowed") is False],
        "recommended_first_validation": "latest_prediction_summary_widget_component_skeleton_contract_guard" if component_rows else "",
        "recommended_next_slice": "PS-Q17S WarRoom prediction widget read-only component skeleton implementation or actual-source preflight; page import patch, widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q17R defines future read-only component skeleton props and fallback requirements for WarRoom prediction widgets. It does not create component files, import them, mutate warroom_page.py, render widgets, read D-hot, refresh, write artifacts, or stage/apply parameters.",
        "read_only": True,
        "non_executing": True,
        "component_skeleton_contract_only": True,
        "contract_only": True,
        "diagnostic_only": True,
        "warroom_widget_design_premise": True,
        "component_file_creation_allowed": False,
        "component_import_allowed": False,
        "streamlit_render_allowed": False,
        "warroom_widget_implementation_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "warroom_page_mutation_allowed": False,
        "warroom_page_import_patch_allowed": False,
        "warroom_mount_patch_allowed": False,
        "fallback_component_only": True,
        "warroom_ui_trigger_enabled": False,
        "refresh_invocation_allowed": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "d_hot_actual_read_allowed": False,
        "actual_source_read_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17R WarRoom prediction widget read-only component skeleton contract")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use the PS-Q17Q observed fixture path; no D-hot read, component file creation, import, page patch, or rendering is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
