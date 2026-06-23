# path: ./tools/check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.py
# desc: PS-Q18N checker for WarRoom latest_prediction_summary_widget real-source handoff preflight mount. No source resolution/read, D-hot discovery, Q18J/page execution, render, refresh, writes, AutoTrade, or broker APIs.

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Mapping

BTCTS_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "btcts_next", "src")
if BTCTS_SRC not in sys.path:
    sys.path.insert(0, BTCTS_SRC)

from check_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount import CHECKER_VERSION as PS_Q18M_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount import build_report as build_ps_q18m_report
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel import LATEST_PREDICTION_SUMMARY_WIDGET_REAL_SOURCE_HANDOFF_PREFLIGHT_PANEL_VERSION, build_latest_prediction_summary_widget_real_source_handoff_preflight_packet

CHECKER = "ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.v1"
REAL_SOURCE_HANDOFF_PREFLIGHT_MOUNT_VERSION = "latest_prediction_summary_widget_real_source_handoff_preflight_mount.v1"
PS_Q18M_SOURCE_CHECKER_VERSION = PS_Q18M_CHECKER_VERSION
WARROOM_PAGE_TARGET = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
SECTION_TITLE = "Prediction WarRoom latest summary real source handoff preflight"
RENDER_FUNCTION = "_render_prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_section"
EXPECTED_CANDIDATES = {
    "candidate_generated_at": "2026-06-22T00:00:00Z",
    "candidate_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
    "candidate_market_uid": "BTC-USD",
}


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


def _safe_q18m_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q18M_SOURCE_CHECKER_VERSION:
        failures.append("q18m_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q18m_report_not_ok")
    if report.get("summary_packet_valid") is not True:
        failures.append("q18m_summary_packet_not_valid")
    if report.get("compact_line_ready") is not True:
        failures.append("q18m_compact_line_not_ready")
    for key, value in {
        "observed_mapped_source_generated_at": "2026-06-22T00:00:00Z",
        "observed_mapped_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
        "observed_mapped_market_uid": "BTC-USD",
    }.items():
        if report.get(key) != value:
            failures.append(f"q18m_candidate_mismatch:{key}")
    for key in ("latest_prediction_summary_widget_operator_value_summary_mount_only", "operator_summary_display_only"):
        if report.get(key) is not True:
            failures.append(f"q18m_true_boundary_missing:{key}")
    for key in ("q18j_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "actual_source_read_invoked_by_mount", "payload_reparse_allowed", "d_hot_directory_scan_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if report.get(key) is not False:
            failures.append(f"q18m_boundary_not_false:{key}")
    return not failures, failures


def _safe_handoff_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("panel_version") != LATEST_PREDICTION_SUMMARY_WIDGET_REAL_SOURCE_HANDOFF_PREFLIGHT_PANEL_VERSION:
        failures.append("panel_version_mismatch")
    if packet.get("ok") is not True:
        failures.append("handoff_packet_not_ok")
    if packet.get("handoff_row_count") != 6:
        failures.append("handoff_row_count_mismatch")
    for key in ("latest_prediction_summary_widget_real_source_handoff_preflight_mount_only", "warroom_handoff_preflight_rows_ready", "operator_summary_report_display_only", "real_source_handoff_preflight_only"):
        if packet.get(key) is not True:
            failures.append(f"handoff_true_boundary_missing:{key}")
    for key in ("real_source_handoff_invoked", "actual_source_resolution_allowed", "actual_source_resolved", "actual_source_read_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18j_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if packet.get(key) is not False:
            failures.append(f"handoff_boundary_not_false:{key}")
    return not failures, failures


def _page_validation(page_text: str) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for marker in (
        "from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel import (",
        "build_latest_prediction_summary_widget_real_source_handoff_preflight_packet",
        "def _prediction_warroom_latest_prediction_summary_real_source_handoff_preflight_display_rows(packet: dict) -> list[dict]:",
        f"def {RENDER_FUNCTION}() -> None:",
        f'with live_shell.render_folded_section("{SECTION_TITLE}", expanded=False):',
        f"{RENDER_FUNCTION}()",
        "latest summary real-source handoff rows={rows} / candidate_ready={ready} / real_handoff=false / actual_read=false / render=false",
        "st.dataframe(handoff_rows, width=\"stretch\", hide_index=True)",
    ):
        if marker not in page_text:
            failures.append(f"missing_page_marker:{marker}")
    if page_text.count(f"{RENDER_FUNCTION}(") != 2:
        failures.append("real_source_handoff_preflight_render_function_should_have_definition_and_page_body_call_only")
    for forbidden in ("build_ps_q18m_report(", "build_ps_q18j_report(", "actual_source_resolution_allowed=True", "actual_source_read_invoked=True", "source_discovery_allowed=True", "d_hot_actual_read_allowed=True", "send_order(", "create_order("):
        if forbidden in page_text:
            failures.append(f"forbidden_page_token:{forbidden}")
    return not failures, failures


def build_report(*, supplied_q18m_report: Mapping[str, Any] | Any | None = None, page_text: str | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18m_report = _as_mapping(supplied_q18m_report)
    if not q18m_report and use_observed_fixture:
        q18m_report = build_ps_q18m_report(use_observed_fixture=True)
    safe_q18m, q18m_failures = _safe_q18m_boundary(q18m_report)
    handoff_packet = build_latest_prediction_summary_widget_real_source_handoff_preflight_packet(supplied_operator_summary_report=q18m_report) if safe_q18m else {}
    safe_handoff, handoff_failures = _safe_handoff_packet(handoff_packet) if handoff_packet else (False, [])
    page_handoff_packet = build_latest_prediction_summary_widget_real_source_handoff_preflight_packet()
    safe_page_handoff, page_handoff_failures = _safe_handoff_packet(page_handoff_packet)
    actual_page_text = page_text if page_text is not None else (_read_warroom_page() if safe_handoff and safe_page_handoff else "")
    page_valid, page_failures = _page_validation(actual_page_text) if safe_handoff and safe_page_handoff else (False, [])
    ok = bool(safe_q18m and safe_handoff and safe_page_handoff and page_valid)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "real_source_handoff_preflight_mount_version": REAL_SOURCE_HANDOFF_PREFLIGHT_MOUNT_VERSION,
        "stage": "latest_prediction_summary_widget_real_source_handoff_preflight_mount_before_resolution_read_render_refresh_and_writes",
        "source_q18m_checker_version": PS_Q18M_SOURCE_CHECKER_VERSION,
        "source_q18m_report_valid": safe_q18m,
        "source_q18m_validation_failures": q18m_failures,
        "handoff_packet_valid": safe_handoff,
        "handoff_validation_failures": handoff_failures,
        "page_handoff_packet_valid": safe_page_handoff,
        "page_handoff_validation_failures": page_handoff_failures,
        "page_validation_failures": page_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "target_page_path": WARROOM_PAGE_TARGET,
        "section_title": SECTION_TITLE,
        "render_function": RENDER_FUNCTION,
        "panel_version": LATEST_PREDICTION_SUMMARY_WIDGET_REAL_SOURCE_HANDOFF_PREFLIGHT_PANEL_VERSION,
        "handoff_row_count": int(handoff_packet.get("handoff_row_count") or 0) if handoff_packet else 0,
        "page_handoff_row_count": int(page_handoff_packet.get("handoff_row_count") or 0),
        "handoff_candidate_ready": bool(handoff_packet.get("handoff_candidate_ready")) if handoff_packet else False,
        "page_handoff_candidate_ready": bool(page_handoff_packet.get("handoff_candidate_ready")),
        **EXPECTED_CANDIDATES,
        "recommended_first_validation": "latest_prediction_summary_widget_real_source_handoff_preflight_mount_guard" if ok else "",
        "recommended_next_slice": "PS-Q18O explicit one-source handoff design checkpoint; actual source resolution/read, real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18N mounts WarRoom real-source handoff preflight rows only. It declares the candidate generated_at/source_artifact_ref/market_uid handoff contract from the supplied Q18M report, but the page mount never runs Q18M/Q18J, never resolves source artifacts, never reads D-hot, never reparses payloads, never renders real widgets, never refreshes, writes, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker APIs.",
        "read_only": True,
        "non_executing": True,
        "latest_prediction_summary_widget_real_source_handoff_preflight_mount_only": True,
        "warroom_handoff_preflight_rows_ready": True,
        "operator_summary_report_display_only": True,
        "real_source_handoff_preflight_only": True,
        "warroom_page_mutation_allowed": True,
        "real_source_handoff_invoked": False,
        "actual_source_resolution_allowed": False,
        "actual_source_resolved": False,
        "actual_source_read_allowed": False,
        "actual_source_read_invoked": False,
        "payload_reparse_allowed": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
        "q18j_validation_invoked_by_mount": False,
        "q18m_validation_invoked_by_mount": False,
        "component_packet_builder_invoked_by_mount": False,
        "component_packet_builder_allowed_by_mount": False,
        "component_runtime_binding_allowed": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
        "real_prediction_widget_rendering_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q18N latest prediction summary widget real source handoff preflight mount")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use Q18M observed fixture report; WarRoom page mount still does not invoke Q18M/Q18J, resolve, read, or render.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
