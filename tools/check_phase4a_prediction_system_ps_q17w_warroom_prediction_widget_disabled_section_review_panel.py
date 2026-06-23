# path: ./tools/check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.py
# desc: PS-Q17W WarRoom prediction widget disabled section review panel checker. It validates a pure-data review packet over disabled skeleton packets only; it never renders widgets, reads D-hot, writes artifacts, invokes refresh, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation import CHECKER_VERSION as PS_Q17S_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation import WIDGET_FAMILY_ORDER, build_report as build_ps_q17s_report
from check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch import CHECKER_VERSION as PS_Q17V_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch import build_report as build_ps_q17v_report

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC_ROOT = os.path.join(_REPO_ROOT, "btcts_next", "src")
if _SRC_ROOT not in sys.path:
    sys.path.insert(0, _SRC_ROOT)

CHECKER = "ps_q17w_warroom_prediction_widget_disabled_section_review_panel"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.v1"
PS_Q17S_SOURCE_CHECKER_VERSION = PS_Q17S_CHECKER_VERSION
PS_Q17V_SOURCE_CHECKER_VERSION = PS_Q17V_CHECKER_VERSION
DISABLED_SECTION_REVIEW_PANEL_VERSION = "warroom_prediction_widget_disabled_section_review_panel.v1"
PANEL_MODULE = "btcts.apps.operator_ui.components.prediction_warroom_prediction_widgets_disabled_section_review_panel"
PANEL_FUNCTION = "build_prediction_warroom_prediction_widgets_disabled_section_review_packet"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _safe_q17v_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17V_SOURCE_CHECKER_VERSION:
        failures.append("q17v_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17v_report_not_ok")
    if report.get("imported_widget_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17v_imported_widget_count_mismatch")
    if report.get("disabled_section_defined") is not True:
        failures.append("q17v_disabled_section_missing")
    if report.get("page_body_call_enabled") is not False:
        failures.append("q17v_page_body_call_enabled")
    for key in (
        "future_section_call_enabled",
        "streamlit_render_allowed",
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
            failures.append(f"q17v_boundary_not_false:{key}")
    return not failures, failures


def _safe_q17s_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17S_SOURCE_CHECKER_VERSION:
        failures.append("q17s_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17s_report_not_ok")
    if report.get("component_packet_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17s_component_packet_count_mismatch")
    packets = [_as_mapping(packet) for packet in _as_list(report.get("component_packets"))]
    packet_ids = [str(packet.get("widget_family_id") or "") for packet in packets]
    if packet_ids != list(WIDGET_FAMILY_ORDER):
        failures.append("q17s_packet_order_mismatch")
    return not failures, failures


def _fixture_q17v_report() -> dict[str, Any]:
    return build_ps_q17v_report(use_observed_fixture=True)


def _fixture_q17s_report() -> dict[str, Any]:
    return build_ps_q17s_report(use_observed_fixture=True)


def _call_panel(packets: list[Mapping[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    try:
        module = importlib.import_module(PANEL_MODULE)
    except Exception as exc:  # pragma: no cover - surfaced as JSON
        return {}, [f"panel_module_import_failed:{type(exc).__name__}:{exc}"]
    fn = getattr(module, PANEL_FUNCTION, None)
    if not callable(fn):
        return {}, ["panel_function_missing"]
    packet = _as_mapping(fn(packets=packets, source_checker_version=PS_Q17S_SOURCE_CHECKER_VERSION, page_patch_checker_version=PS_Q17V_SOURCE_CHECKER_VERSION))
    if not packet:
        failures.append("panel_packet_empty")
    return dict(packet), failures


def build_report(*, supplied_q17v_report: Mapping[str, Any] | Any | None = None, supplied_q17s_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17v_report = _as_mapping(supplied_q17v_report)
    q17s_report = _as_mapping(supplied_q17s_report)
    if use_observed_fixture:
        if not q17v_report:
            q17v_report = _fixture_q17v_report()
        if not q17s_report:
            q17s_report = _fixture_q17s_report()
    safe_q17v, q17v_failures = _safe_q17v_boundary(q17v_report)
    safe_q17s, q17s_failures = _safe_q17s_boundary(q17s_report)
    packets = [_as_mapping(packet) for packet in _as_list(q17s_report.get("component_packets"))] if safe_q17s else []
    panel_packet, panel_failures = _call_panel(packets) if safe_q17v and safe_q17s else ({}, [])
    panel_validation_failures = _as_list(panel_packet.get("validation_failures")) if panel_packet else []
    ok = bool(safe_q17v and safe_q17s and panel_packet and panel_packet.get("ok") is True and not panel_failures and not panel_validation_failures and panel_packet.get("review_row_count") == len(WIDGET_FAMILY_ORDER))
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "disabled_section_review_panel_version": DISABLED_SECTION_REVIEW_PANEL_VERSION,
        "stage": "warroom_prediction_widget_disabled_section_review_panel_before_page_body_call_and_visible_rendering",
        "use_observed_fixture": bool(use_observed_fixture),
        "source_q17s_checker_version": PS_Q17S_SOURCE_CHECKER_VERSION,
        "source_q17v_checker_version": PS_Q17V_SOURCE_CHECKER_VERSION,
        "source_q17s_report_valid": safe_q17s,
        "source_q17v_report_valid": safe_q17v,
        "source_q17s_validation_failures": q17s_failures,
        "source_q17v_validation_failures": q17v_failures,
        "panel_module": PANEL_MODULE,
        "panel_function": PANEL_FUNCTION,
        "panel_import_for_validation": bool(panel_packet),
        "panel_validation_failures": panel_failures + [str(item) for item in panel_validation_failures],
        "panel_packet": panel_packet,
        "review_row_count": int(panel_packet.get("review_row_count") or 0) if panel_packet else 0,
        "review_zone_count": int(panel_packet.get("review_zone_count") or 0) if panel_packet else 0,
        "widget_family_order": list(WIDGET_FAMILY_ORDER),
        "recommended_first_validation": "latest_prediction_summary_widget_disabled_section_review_panel_guard" if ok else "",
        "recommended_next_slice": "PS-Q17X WarRoom prediction widget disabled section page-body review mount or actual-source preflight; visible widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q17W creates a pure-data disabled-section review packet over the Prediction widget skeleton packets. It does not call the WarRoom page section, render Streamlit widgets, read D-hot, refresh, write artifacts, or stage/apply parameters.",
        "read_only": True,
        "non_executing": True,
        "disabled_section_review_only": True,
        "pure_data_review_packet": True,
        "warroom_page_mutation_allowed": False,
        "page_body_call_enabled": False,
        "future_section_call_enabled": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17W WarRoom prediction widget disabled section review panel")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use PS-Q17V/PS-Q17S observed fixture path; no WarRoom page call, D-hot read, widget render, refresh, or artifact write is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
