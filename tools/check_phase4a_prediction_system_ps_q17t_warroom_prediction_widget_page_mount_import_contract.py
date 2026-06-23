# path: ./tools/check_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract.py
# desc: PS-Q17T non-executing WarRoom prediction widget page mount/import contract. It consumes PS-Q17S component skeleton packets and emits future warroom_page.py import/mount contracts only; it never mutates WarRoom UI, patches imports, renders widgets, reads D-hot, writes artifacts, invokes refresh, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation import CHECKER_VERSION as PS_Q17S_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation import WIDGET_FAMILY_ORDER, build_report as build_ps_q17s_report

CHECKER = "ps_q17t_warroom_prediction_widget_page_mount_import_contract"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract.v1"
PS_Q17S_SOURCE_CHECKER_VERSION = PS_Q17S_CHECKER_VERSION
PAGE_MOUNT_IMPORT_CONTRACT_VERSION = "warroom_prediction_widget_page_mount_import_contract.v1"
WARROOM_PAGE_TARGET = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
IMPORT_ANCHOR_MODULE = "prediction_warroom_non_ui_scheduled_producer_status_panel"
MOUNT_SECTION_ANCHOR = "_render_prediction_warroom_lowered_display_packet_visibility_review_section"
FUTURE_SECTION_FUNCTION = "_render_prediction_warroom_prediction_widgets_skeleton_section"
PAGE_ZONE_ORDER = ("prediction_overview_zone", "prediction_realtime_review_zone", "prediction_operator_support_zone")

REQUIRED_PAGE_CONTRACT_FIELDS = (
    "widget_family_id",
    "component_module_path",
    "component_function_name",
    "target_page_path",
    "import_anchor_module",
    "mount_section_anchor",
    "future_section_function",
    "page_import_patch_allowed",
    "warroom_mount_patch_allowed",
    "streamlit_render_allowed",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _component_packets(report: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [_as_mapping(row) for row in _as_list(report.get("component_packets"))]


def _safe_q17s_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17S_SOURCE_CHECKER_VERSION:
        failures.append("q17s_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17s_report_not_ok")
    if report.get("component_skeleton_implementation") is not True:
        failures.append("q17s_component_skeleton_implementation_missing")
    if report.get("component_files_created") is not True:
        failures.append("q17s_component_files_created_missing")
    if report.get("component_module_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17s_component_module_count_mismatch")
    if report.get("component_packet_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17s_component_packet_count_mismatch")
    if report.get("component_module_validation_failures") not in ([], ()): 
        failures.append("q17s_component_module_validation_failures_present")
    for key in (
        "component_import_allowed_by_warroom_page",
        "streamlit_render_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_page_import_patch_allowed",
        "warroom_mount_patch_allowed",
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
            failures.append(f"q17s_boundary_not_false:{key}")
    packet_ids = [str(packet.get("widget_family_id") or "") for packet in _component_packets(report)]
    if packet_ids != list(WIDGET_FAMILY_ORDER):
        failures.append("q17s_widget_family_order_mismatch")
    for packet in _component_packets(report):
        for key in (
            "streamlit_render_allowed",
            "streamlit_render_invoked",
            "warroom_page_import_patch_allowed",
            "warroom_page_mutation_allowed",
            "warroom_mount_patch_allowed",
            "actual_source_read_allowed",
            "actual_source_read_attempted",
            "d_hot_actual_read_allowed",
            "refresh_invocation_allowed",
            "runtime_artifact_write_allowed",
            "status_artifact_write_allowed",
            "parameter_apply_allowed",
            "parameter_staging_write_allowed",
            "ledger_append_allowed",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
        ):
            if packet.get(key) is not False:
                failures.append(f"q17s_packet_boundary_not_false:{packet.get('widget_family_id')}:{key}")
    return not failures, failures


def _fixture_q17s_report() -> dict[str, Any]:
    return build_ps_q17s_report(use_observed_fixture=True)


def _import_statement(module_path: str, function_name: str) -> str:
    return f"from {module_path} import {function_name}"


def _build_import_rows(q17s_report: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for packet in _component_packets(q17s_report):
        widget_id = str(packet.get("widget_family_id") or "")
        module_path = str(packet.get("component_module_path") or "")
        function_name = str(packet.get("component_function_name") or "")
        rows.append({
            "widget_family_id": widget_id,
            "component_module_path": module_path,
            "component_function_name": function_name,
            "target_page_path": WARROOM_PAGE_TARGET,
            "import_anchor_module": IMPORT_ANCHOR_MODULE,
            "future_import_statement": _import_statement(module_path, function_name),
            "page_import_patch_allowed": False,
            "component_import_allowed_by_warroom_page": False,
            "import_contract_state": "future_import_contract_defined_patch_disabled",
        })
    return rows


def _build_mount_rows(q17s_report: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    previous_by_zone: dict[str, str] = {}
    for packet in _component_packets(q17s_report):
        widget_id = str(packet.get("widget_family_id") or "")
        zone = str(packet.get("mount_zone_id") or "")
        attach_after = previous_by_zone.get(zone, "")
        previous_by_zone[zone] = widget_id
        rows.append({
            "widget_family_id": widget_id,
            "source_packet_id": str(packet.get("source_packet_id") or ""),
            "mount_zone_id": zone,
            "mount_slot_id": str(packet.get("mount_slot_id") or ""),
            "mount_order_index": len([row for row in rows if row.get("mount_zone_id") == zone]),
            "attach_after_widget_family_id": attach_after,
            "component_function_name": str(packet.get("component_function_name") or ""),
            "target_page_path": WARROOM_PAGE_TARGET,
            "mount_section_anchor": MOUNT_SECTION_ANCHOR,
            "future_section_function": FUTURE_SECTION_FUNCTION,
            "future_mount_call": f"{packet.get('component_function_name')}(props=...)  # disabled in PS-Q17T",
            "page_import_patch_allowed": False,
            "warroom_page_mutation_allowed": False,
            "warroom_mount_patch_allowed": False,
            "streamlit_render_allowed": False,
            "actual_source_read_allowed": False,
            "refresh_invocation_allowed": False,
            "mount_contract_state": "future_page_mount_contract_defined_render_disabled",
        })
    return rows


def _zone_rows(mount_rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for zone in PAGE_ZONE_ORDER:
        zone_mounts = [row for row in mount_rows if row.get("mount_zone_id") == zone]
        rows.append({
            "mount_zone_id": zone,
            "widget_family_count": len(zone_mounts),
            "widget_family_ids": [str(row.get("widget_family_id") or "") for row in zone_mounts],
            "future_section_function": FUTURE_SECTION_FUNCTION,
            "page_import_patch_allowed": False,
            "warroom_mount_patch_allowed": False,
            "streamlit_render_allowed": False,
            "zone_contract_state": "future_zone_mount_contract_defined_render_disabled",
        })
    return rows


def build_report(*, supplied_q17s_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17s_report = _as_mapping(supplied_q17s_report)
    if not q17s_report and use_observed_fixture:
        q17s_report = _fixture_q17s_report()
    safe_q17s, validation_failures = _safe_q17s_boundary(q17s_report)
    import_rows = _build_import_rows(q17s_report) if safe_q17s else []
    mount_rows = _build_mount_rows(q17s_report) if safe_q17s else []
    zone_rows = _zone_rows(mount_rows) if mount_rows else []
    ok = bool(safe_q17s and len(import_rows) == len(WIDGET_FAMILY_ORDER) and len(mount_rows) == len(WIDGET_FAMILY_ORDER) and len(zone_rows) == len(PAGE_ZONE_ORDER))
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "page_mount_import_contract_version": PAGE_MOUNT_IMPORT_CONTRACT_VERSION,
        "stage": "warroom_prediction_widget_page_mount_import_contract_before_warroom_page_patch_and_rendering",
        "source_checker_version": PS_Q17S_SOURCE_CHECKER_VERSION,
        "source_q17s_report_valid": safe_q17s,
        "source_q17s_validation_failures": validation_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "target_page_path": WARROOM_PAGE_TARGET,
        "import_anchor_module": IMPORT_ANCHOR_MODULE,
        "mount_section_anchor": MOUNT_SECTION_ANCHOR,
        "future_section_function": FUTURE_SECTION_FUNCTION,
        "widget_family_order": list(WIDGET_FAMILY_ORDER),
        "page_zone_order": list(PAGE_ZONE_ORDER),
        "required_page_contract_fields": list(REQUIRED_PAGE_CONTRACT_FIELDS),
        "page_import_rows": import_rows,
        "page_mount_rows": mount_rows,
        "page_zone_rows": zone_rows,
        "page_import_row_count": len(import_rows),
        "page_mount_row_count": len(mount_rows),
        "page_zone_row_count": len(zone_rows),
        "page_import_patch_blockers": [row["widget_family_id"] for row in import_rows if row.get("page_import_patch_allowed") is False],
        "warroom_mount_patch_blockers": [row["widget_family_id"] for row in mount_rows if row.get("warroom_mount_patch_allowed") is False],
        "streamlit_render_blockers": [row["widget_family_id"] for row in mount_rows if row.get("streamlit_render_allowed") is False],
        "recommended_first_validation": "latest_prediction_summary_widget_page_mount_import_contract_guard" if mount_rows else "",
        "recommended_next_slice": "PS-Q17U WarRoom prediction widget page import/mount implementation preflight or actual-source preflight; widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q17T defines future warroom_page.py import anchors, mount section, zone rows, and mount call contracts for Prediction WarRoom widgets. It does not edit warroom_page.py, import the widgets into WarRoom, render Streamlit widgets, read D-hot, refresh, write artifacts, or stage/apply parameters.",
        "read_only": True,
        "non_executing": True,
        "page_mount_import_contract_only": True,
        "contract_only": True,
        "diagnostic_only": True,
        "warroom_widget_design_premise": True,
        "warroom_page_target_observed": True,
        "warroom_page_import_patch_allowed": False,
        "warroom_page_mutation_allowed": False,
        "warroom_mount_patch_allowed": False,
        "component_import_allowed_by_warroom_page": False,
        "streamlit_render_allowed": False,
        "warroom_widget_rendering_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17T WarRoom prediction widget page mount/import contract")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use the PS-Q17S observed fixture path; no warroom_page.py patch, D-hot read, widget render, refresh, or write is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
