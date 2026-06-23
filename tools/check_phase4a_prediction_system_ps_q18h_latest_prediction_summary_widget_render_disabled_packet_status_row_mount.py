# path: ./tools/check_phase4a_prediction_system_ps_q18h_latest_prediction_summary_widget_render_disabled_packet_status_row_mount.py
# desc: PS-Q18H checker for WarRoom latest_prediction_summary_widget render-disabled packet status row mount. It validates display-only rows and page mount; it never invokes Q18G, component packet builders, Streamlit render, source reads, D-hot discovery, refresh, writes, AutoTrade, or broker APIs.

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Mapping

BTCTS_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "btcts_next", "src")
if BTCTS_SRC not in sys.path:
    sys.path.insert(0, BTCTS_SRC)

from check_phase4a_prediction_system_ps_q18g_latest_prediction_summary_widget_render_disabled_packet_validation import CHECKER_VERSION as PS_Q18G_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q18g_latest_prediction_summary_widget_render_disabled_packet_validation import build_report as build_ps_q18g_report
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_render_disabled_packet_status_panel import LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_STATUS_PANEL_VERSION, build_latest_prediction_summary_widget_render_disabled_packet_status_packet

CHECKER = "ps_q18h_latest_prediction_summary_widget_render_disabled_packet_status_row_mount"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18h_latest_prediction_summary_widget_render_disabled_packet_status_row_mount.v1"
RENDER_DISABLED_PACKET_STATUS_ROW_MOUNT_VERSION = "latest_prediction_summary_widget_render_disabled_packet_status_row_mount.v1"
PS_Q18G_SOURCE_CHECKER_VERSION = PS_Q18G_CHECKER_VERSION
WARROOM_PAGE_TARGET = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
SECTION_TITLE = "Prediction WarRoom latest summary render-disabled packet status"
RENDER_FUNCTION = "_render_prediction_warroom_latest_prediction_summary_widget_render_disabled_packet_status_section"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_warroom_page() -> str:
    with open(os.path.join(_repo_root(), WARROOM_PAGE_TARGET), "r", encoding="utf-8-sig") as handle:
        return handle.read()


def _safe_q18g_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q18G_SOURCE_CHECKER_VERSION:
        failures.append("q18g_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q18g_report_not_ok")
    if report.get("validation_packet_valid") is not True:
        failures.append("q18g_validation_packet_not_valid")
    if report.get("component_packet_state") != "read_only_component_skeleton_render_disabled":
        failures.append("q18g_component_packet_state_mismatch")
    if report.get("component_missing_props") != []:
        failures.append("q18g_component_missing_props_present")
    for key in ("latest_prediction_summary_widget_render_disabled_packet_validation_only", "render_disabled_component_packet_validation_only", "component_skeleton_packet_only", "component_packet_builder_invoked", "component_packet_valid", "props_candidate_supplied_to_packet_builder", "props_value_binding_deferred"):
        if report.get(key) is not True:
            failures.append(f"q18g_true_boundary_missing:{key}")
    for key in (
        "real_payload_values_bound",
        "streamlit_render_allowed",
        "streamlit_render_invoked",
        "real_prediction_widget_rendering_allowed",
        "component_runtime_binding_allowed",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
        "actual_source_read_invoked_by_validation",
        "actual_source_read_allowed_by_validation",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "confidence_increase_allowed",
        "parameter_apply_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
    ):
        if report.get(key) is not False:
            failures.append(f"q18g_boundary_not_false:{key}")
    return not failures, failures


def _safe_status_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("panel_version") != LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_STATUS_PANEL_VERSION:
        failures.append("panel_version_mismatch")
    if packet.get("ok") is not True:
        failures.append("status_packet_not_ok")
    if packet.get("status_row_count") != 8:
        failures.append("status_row_count_mismatch")
    for key in ("latest_prediction_summary_widget_render_disabled_packet_status_row_mount_only", "warroom_status_rows_ready", "validation_report_display_only", "render_disabled_packet_status_display_only"):
        if packet.get(key) is not True:
            failures.append(f"status_true_boundary_missing:{key}")
    for key in (
        "q18g_validation_invoked_by_mount",
        "component_packet_builder_invoked_by_mount",
        "component_packet_builder_allowed_by_mount",
        "component_runtime_binding_allowed",
        "streamlit_render_allowed",
        "streamlit_render_invoked",
        "real_prediction_widget_rendering_allowed",
        "actual_source_read_invoked_by_mount",
        "actual_source_read_allowed_by_mount",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
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
            failures.append(f"status_boundary_not_false:{key}")
    return not failures, failures


def _page_validation(page_text: str) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for marker in (
        "from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_render_disabled_packet_status_panel import (",
        "build_latest_prediction_summary_widget_render_disabled_packet_status_packet",
        "def _prediction_warroom_latest_prediction_summary_render_disabled_packet_status_display_rows(packet: dict) -> list[dict]:",
        f"def {RENDER_FUNCTION}() -> None:",
        f'with live_shell.render_folded_section("{SECTION_TITLE}", expanded=False):',
        f"{RENDER_FUNCTION}()",
        "latest summary render-disabled packet rows={rows} / streamlit_render=false / real_render=false / actual_read=false",
        "st.dataframe(status_rows, width=\"stretch\", hide_index=True)",
    ):
        if marker not in page_text:
            failures.append(f"missing_page_marker:{marker}")
    if page_text.count(f"{RENDER_FUNCTION}(") != 2:
        failures.append("render_disabled_packet_status_render_function_should_have_definition_and_page_body_call_only")
    for forbidden in (
        "build_ps_q18g_report(",
        "build_latest_prediction_summary_widget_render_disabled_packet_validation(",
        "q18g_validation_invoked_by_mount=True",
        "component_packet_builder_invoked_by_mount=True",
        "streamlit_render_invoked=True",
        "real_prediction_widget_rendering_allowed=True",
        "actual_source_read_invoked_by_mount=True",
        "send_order(",
        "create_order(",
        "parameter_apply_allowed=True",
    ):
        if forbidden in page_text:
            failures.append(f"forbidden_page_token:{forbidden}")
    return not failures, failures


def build_report(*, supplied_q18g_report: Mapping[str, Any] | Any | None = None, page_text: str | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18g_report = _as_mapping(supplied_q18g_report)
    if not q18g_report and use_observed_fixture:
        q18g_report = build_ps_q18g_report(use_observed_fixture=True)
    safe_q18g, q18g_failures = _safe_q18g_boundary(q18g_report)
    status_packet = build_latest_prediction_summary_widget_render_disabled_packet_status_packet(supplied_validation_report=q18g_report) if safe_q18g else {}
    safe_status, status_failures = _safe_status_packet(status_packet) if status_packet else (False, [])
    page_status_packet = build_latest_prediction_summary_widget_render_disabled_packet_status_packet()
    safe_page_status, page_status_failures = _safe_status_packet(page_status_packet)
    actual_page_text = page_text if page_text is not None else (_read_warroom_page() if safe_status and safe_page_status else "")
    page_valid, page_failures = _page_validation(actual_page_text) if safe_status and safe_page_status else (False, [])
    ok = bool(safe_q18g and safe_status and safe_page_status and page_valid)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "render_disabled_packet_status_row_mount_version": RENDER_DISABLED_PACKET_STATUS_ROW_MOUNT_VERSION,
        "stage": "latest_prediction_summary_widget_render_disabled_packet_status_row_mount_before_real_rendering_refresh_and_writes",
        "source_q18g_checker_version": PS_Q18G_SOURCE_CHECKER_VERSION,
        "source_q18g_report_valid": safe_q18g,
        "source_q18g_validation_failures": q18g_failures,
        "status_packet_valid": safe_status,
        "status_validation_failures": status_failures,
        "page_status_packet_valid": safe_page_status,
        "page_status_validation_failures": page_status_failures,
        "page_validation_failures": page_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "target_page_path": WARROOM_PAGE_TARGET,
        "section_title": SECTION_TITLE,
        "render_function": RENDER_FUNCTION,
        "panel_version": LATEST_PREDICTION_SUMMARY_WIDGET_RENDER_DISABLED_PACKET_STATUS_PANEL_VERSION,
        "status_row_count": int(status_packet.get("status_row_count") or 0) if status_packet else 0,
        "page_status_row_count": int(page_status_packet.get("status_row_count") or 0),
        "recommended_first_validation": "latest_prediction_summary_widget_render_disabled_packet_status_row_mount_guard" if ok else "",
        "recommended_next_slice": "PS-Q18I first real payload value mapping preflight for latest_prediction_summary_widget; real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18H mounts WarRoom status rows for latest_prediction_summary_widget render-disabled packet validation only. The page mount never runs Q18G, never invokes the component packet builder, never invokes Streamlit rendering, never reads sources, never discovers D-hot, never refreshes, writes, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker APIs.",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_render_disabled_packet_status_row_mount_only": True,
        "warroom_status_rows_ready": True,
        "validation_report_display_only": True,
        "render_disabled_packet_status_display_only": True,
        "warroom_page_mutation_allowed": True,
        "q18g_validation_invoked_by_mount": False,
        "component_packet_builder_invoked_by_mount": False,
        "component_packet_builder_allowed_by_mount": False,
        "component_runtime_binding_allowed": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
        "real_prediction_widget_rendering_allowed": False,
        "actual_source_read_invoked_by_mount": False,
        "actual_source_read_allowed_by_mount": False,
        "payload_reparse_allowed": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
        "warroom_widget_rendering_allowed": False,
        "warroom_ui_trigger_enabled": False,
        "refresh_invocation_allowed": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "confidence_increase_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q18H latest prediction summary widget render-disabled packet status row mount")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use Q18G observed fixture report; WarRoom page mount still does not invoke Q18G or render widgets.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
