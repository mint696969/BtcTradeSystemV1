# path: ./tools/check_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation.py
# desc: PS-Q17S non-executing WarRoom prediction widget read-only component skeleton implementation checker. It validates pure-data skeleton modules only; it never mutates WarRoom UI, imports modules into warroom_page.py, renders widgets, reads D-hot, writes artifacts, invokes refresh, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract import CHECKER_VERSION as PS_Q17R_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract import REQUIRED_COMPONENT_PROPS, WIDGET_FAMILY_ORDER, build_report as build_ps_q17r_report

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC_ROOT = os.path.join(_REPO_ROOT, "btcts_next", "src")
if _SRC_ROOT not in sys.path:
    sys.path.insert(0, _SRC_ROOT)

CHECKER = "ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation.v1"
PS_Q17R_SOURCE_CHECKER_VERSION = PS_Q17R_CHECKER_VERSION
COMPONENT_SKELETON_IMPLEMENTATION_VERSION = "warroom_prediction_widget_read_only_component_skeleton_implementation.v1"
COMPONENT_PACKAGE = "btcts.apps.operator_ui.components.prediction_widgets"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _component_rows(report: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [_as_mapping(row) for row in _as_list(report.get("component_rows"))]


def _safe_q17r_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17R_SOURCE_CHECKER_VERSION:
        failures.append("q17r_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17r_report_not_ok")
    if report.get("component_skeleton_contract_only") is not True:
        failures.append("q17r_component_skeleton_contract_only_missing")
    if report.get("component_row_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17r_component_row_count_mismatch")
    if report.get("fallback_component_required_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17r_fallback_component_required_count_mismatch")
    for key in (
        "component_file_creation_allowed",
        "component_import_allowed",
        "streamlit_render_allowed",
        "warroom_widget_implementation_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_page_import_patch_allowed",
        "warroom_mount_patch_allowed",
        "actual_source_read_allowed",
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
            failures.append(f"q17r_boundary_not_false:{key}")
    row_ids = [str(row.get("widget_family_id") or "") for row in _component_rows(report)]
    if row_ids != list(WIDGET_FAMILY_ORDER):
        failures.append("q17r_widget_family_order_mismatch")
    return not failures, failures


def _fixture_q17r_report() -> dict[str, Any]:
    return build_ps_q17r_report(use_observed_fixture=True)


def _call_component(row: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    widget_id = str(row.get("widget_family_id") or "")
    module_path = str(row.get("component_module_path") or f"{COMPONENT_PACKAGE}.{widget_id}")
    function_name = str(row.get("component_function_name") or f"render_{widget_id}")
    try:
        module = importlib.import_module(module_path)
    except Exception as exc:  # pragma: no cover - failure is reported in JSON for guard readability
        return {}, [f"component_module_import_failed:{widget_id}:{type(exc).__name__}:{exc}"]
    fn = getattr(module, function_name, None)
    if not callable(fn):
        return {}, [f"component_function_missing:{widget_id}:{function_name}"]
    packet = _as_mapping(fn())
    if not packet:
        failures.append(f"component_packet_empty:{widget_id}")
        return {}, failures
    if packet.get("widget_family_id") != widget_id:
        failures.append(f"widget_id_mismatch:{widget_id}")
    if packet.get("source_packet_id") != row.get("source_packet_id"):
        failures.append(f"source_packet_id_mismatch:{widget_id}")
    if packet.get("mount_zone_id") != row.get("mount_zone_id"):
        failures.append(f"mount_zone_id_mismatch:{widget_id}")
    if packet.get("component_module_path") != module_path:
        failures.append(f"component_module_path_mismatch:{widget_id}")
    if packet.get("component_function_name") != function_name:
        failures.append(f"component_function_name_mismatch:{widget_id}")
    if packet.get("props_contract_fields") != list(REQUIRED_COMPONENT_PROPS):
        failures.append(f"props_contract_fields_mismatch:{widget_id}")
    if packet.get("component_state") != "read_only_component_skeleton_render_disabled":
        failures.append(f"component_state_mismatch:{widget_id}")
    for key in (
        "read_only",
        "non_executing",
        "component_skeleton_only",
        "fallback_component_only",
        "display_packet_only",
    ):
        if packet.get(key) is not True:
            failures.append(f"packet_true_boundary_missing:{widget_id}:{key}")
    for key in (
        "warroom_page_mutation_allowed",
        "warroom_page_import_patch_allowed",
        "warroom_mount_patch_allowed",
        "component_import_allowed_by_warroom_page",
        "streamlit_render_allowed",
        "streamlit_render_invoked",
        "actual_source_read_allowed",
        "actual_source_read_attempted",
        "d_hot_actual_read_allowed",
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
        if packet.get(key) is not False:
            failures.append(f"packet_false_boundary_not_false:{widget_id}:{key}")
    return dict(packet), failures


def build_report(*, supplied_q17r_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17r_report = _as_mapping(supplied_q17r_report)
    if not q17r_report and use_observed_fixture:
        q17r_report = _fixture_q17r_report()
    safe_q17r, validation_failures = _safe_q17r_boundary(q17r_report)
    packets: list[dict[str, Any]] = []
    module_failures: list[str] = []
    if safe_q17r:
        for row in _component_rows(q17r_report):
            packet, failures = _call_component(row)
            if packet:
                packets.append(packet)
            module_failures.extend(failures)
    ok = bool(safe_q17r and not module_failures and len(packets) == len(WIDGET_FAMILY_ORDER))
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "component_skeleton_implementation_version": COMPONENT_SKELETON_IMPLEMENTATION_VERSION,
        "stage": "warroom_prediction_widget_read_only_component_skeleton_implementation_before_warroom_import_mount_and_rendering",
        "source_checker_version": PS_Q17R_SOURCE_CHECKER_VERSION,
        "source_q17r_report_valid": safe_q17r,
        "source_q17r_validation_failures": validation_failures,
        "component_module_validation_failures": module_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "widget_family_order": list(WIDGET_FAMILY_ORDER),
        "required_component_props": list(REQUIRED_COMPONENT_PROPS),
        "component_package": COMPONENT_PACKAGE,
        "component_module_count": len(packets),
        "component_packet_count": len(packets),
        "component_packets": packets,
        "component_file_creation_completed": bool(len(packets) == len(WIDGET_FAMILY_ORDER)),
        "component_package_import_for_validation": bool(len(packets) == len(WIDGET_FAMILY_ORDER)),
        "streamlit_render_blockers": [packet["widget_family_id"] for packet in packets if packet.get("streamlit_render_allowed") is False],
        "warroom_page_import_blockers": [packet["widget_family_id"] for packet in packets if packet.get("warroom_page_import_patch_allowed") is False],
        "actual_source_read_blockers": [packet["widget_family_id"] for packet in packets if packet.get("actual_source_read_allowed") is False],
        "recommended_first_validation": "latest_prediction_summary_widget_component_skeleton_implementation_guard" if packets else "",
        "recommended_next_slice": "PS-Q17T WarRoom prediction widget page mount/import contract or actual-source preflight; widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q17S creates pure-data read-only component skeleton modules for WarRoom prediction widgets. They return disabled skeleton packets only and do not mutate WarRoom UI, render Streamlit widgets, read D-hot, refresh, write artifacts, or stage/apply parameters.",
        "read_only": True,
        "non_executing": True,
        "component_skeleton_implementation": True,
        "component_files_created": bool(len(packets) == len(WIDGET_FAMILY_ORDER)),
        "contract_only": False,
        "diagnostic_only": True,
        "warroom_widget_design_premise": True,
        "component_import_allowed_by_warroom_page": False,
        "streamlit_render_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "warroom_page_mutation_allowed": False,
        "warroom_page_import_patch_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17S WarRoom prediction widget read-only component skeleton implementation")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use the PS-Q17R observed fixture path; no D-hot read, WarRoom page import/mount patch, or rendering is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
