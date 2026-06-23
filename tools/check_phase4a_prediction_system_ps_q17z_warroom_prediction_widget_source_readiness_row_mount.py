# path: ./tools/check_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount.py
# desc: PS-Q17Z WarRoom prediction widget source readiness row mount checker. It validates visible readiness rows only; it never resolves source artifacts, reads D-hot, renders real Prediction widgets, invokes refresh, writes artifacts, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Mapping

BTCTS_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "btcts_next", "src")
if BTCTS_SRC not in sys.path:
    sys.path.insert(0, BTCTS_SRC)

from check_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight import CHECKER_VERSION as PS_Q17Y_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight import WIDGET_FAMILY_ORDER, build_report as build_ps_q17y_report
from btcts.apps.operator_ui.components.prediction_warroom_prediction_widget_source_readiness_preflight_panel import PREDICTION_WARROOM_SOURCE_READINESS_PREFLIGHT_PANEL_VERSION, build_prediction_warroom_prediction_widget_source_readiness_preflight_packet

CHECKER = "ps_q17z_warroom_prediction_widget_source_readiness_row_mount"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount.v1"
SOURCE_READINESS_ROW_MOUNT_VERSION = "warroom_prediction_widget_source_readiness_row_mount.v1"
PS_Q17Y_SOURCE_CHECKER_VERSION = PS_Q17Y_CHECKER_VERSION
WARROOM_PAGE_TARGET = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
SOURCE_READINESS_SECTION_TITLE = "Prediction WarRoom source readiness preflight"
SOURCE_READINESS_RENDER_FUNCTION = "_render_prediction_warroom_prediction_widget_source_readiness_preflight_section"


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


def _safe_q17y_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17Y_SOURCE_CHECKER_VERSION:
        failures.append("q17y_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17y_report_not_ok")
    if report.get("preflight_row_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17y_preflight_row_count_mismatch")
    if report.get("source_binding_contract_ready") is not True:
        failures.append("q17y_source_binding_contract_not_ready")
    for key in (
        "source_artifact_resolution_allowed",
        "actual_source_bound",
        "source_artifact_resolved",
        "freshness_checked_against_d_hot",
        "readiness_row_visible_in_warroom",
        "real_prediction_widget_rendering_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
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
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
    ):
        if report.get(key) is not False:
            failures.append(f"q17y_boundary_not_false:{key}")
    return not failures, failures


def _safe_panel_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("panel_version") != PREDICTION_WARROOM_SOURCE_READINESS_PREFLIGHT_PANEL_VERSION:
        failures.append("panel_version_mismatch")
    if packet.get("ok") is not True:
        failures.append("panel_packet_not_ok")
    if packet.get("readiness_row_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("panel_readiness_row_count_mismatch")
    if packet.get("unique_source_packet_count") != 9:
        failures.append("panel_unique_source_packet_count_mismatch")
    if packet.get("readiness_row_visible_in_warroom") is not True:
        failures.append("panel_readiness_visible_not_true")
    rows = list(packet.get("readiness_rows") or [])
    if [str(_as_mapping(row).get("widget_family_id") or "") for row in rows] != list(WIDGET_FAMILY_ORDER):
        failures.append("panel_widget_order_mismatch")
    for row_value in rows:
        row = _as_mapping(row_value)
        widget_id = str(row.get("widget_family_id") or "")
        if row.get("actual_source_binding_ready") is not True:
            failures.append(f"row_binding_not_ready:{widget_id}")
        if row.get("readiness_row_visible_in_warroom") is not True:
            failures.append(f"row_visibility_not_true:{widget_id}")
        for key in (
            "actual_source_bound",
            "source_artifact_resolution_allowed",
            "source_artifact_resolved",
            "freshness_checked_against_d_hot",
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
                failures.append(f"row_boundary_not_false:{widget_id}:{key}")
    return not failures, failures


def _page_validation(page_text: str) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for marker in (
        "from btcts.apps.operator_ui.components.prediction_warroom_prediction_widget_source_readiness_preflight_panel import (",
        "build_prediction_warroom_prediction_widget_source_readiness_preflight_packet",
        "def _prediction_warroom_source_readiness_display_rows(packet: dict) -> list[dict]:",
        f"def {SOURCE_READINESS_RENDER_FUNCTION}() -> None:",
        f'with live_shell.render_folded_section("{SOURCE_READINESS_SECTION_TITLE}", expanded=False):',
        f"{SOURCE_READINESS_RENDER_FUNCTION}()",
        "source readiness rows={rows} / source packets={packets} / actual_source_read=false / d_hot_read=false / render=false",
        "st.dataframe(readiness_rows, width=\"stretch\", hide_index=True)",
    ):
        if marker not in page_text:
            failures.append(f"missing_page_marker:{marker}")
    if page_text.count(f"{SOURCE_READINESS_RENDER_FUNCTION}(") != 2:
        failures.append("source_readiness_render_function_should_have_definition_and_page_body_call_only")
    for forbidden in (
        "allow_actual_read=True",
        "actual_source_read_allowed=True",
        "d_hot_actual_read_allowed=True",
        "append_decision(",
        "append_command(",
        "send_order(",
        "create_order(",
        "parameter_apply_allowed=True",
        "parameter_staging_write_allowed=True",
    ):
        if forbidden in page_text:
            failures.append(f"forbidden_page_token:{forbidden}")
    return not failures, failures


def build_report(*, supplied_q17y_report: Mapping[str, Any] | Any | None = None, page_text: str | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17y_report = _as_mapping(supplied_q17y_report)
    if not q17y_report and use_observed_fixture:
        q17y_report = build_ps_q17y_report(use_observed_fixture=True)
    safe_q17y, q17y_failures = _safe_q17y_boundary(q17y_report)
    panel_packet = build_prediction_warroom_prediction_widget_source_readiness_preflight_packet() if safe_q17y else {}
    safe_panel, panel_failures = _safe_panel_packet(panel_packet) if panel_packet else (False, [])
    actual_page_text = page_text if page_text is not None else (_read_warroom_page() if safe_q17y and safe_panel else "")
    page_valid, page_failures = _page_validation(actual_page_text) if safe_q17y and safe_panel else (False, [])
    ok = bool(safe_q17y and safe_panel and page_valid)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "source_readiness_row_mount_version": SOURCE_READINESS_ROW_MOUNT_VERSION,
        "stage": "warroom_prediction_widget_source_readiness_row_mount_before_source_resolution_d_hot_read_and_real_widget_rendering",
        "source_q17y_checker_version": PS_Q17Y_SOURCE_CHECKER_VERSION,
        "source_q17y_report_valid": safe_q17y,
        "source_q17y_validation_failures": q17y_failures,
        "panel_packet_valid": safe_panel,
        "panel_validation_failures": panel_failures,
        "page_validation_failures": page_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "target_page_path": WARROOM_PAGE_TARGET,
        "source_readiness_section_title": SOURCE_READINESS_SECTION_TITLE,
        "source_readiness_render_function": SOURCE_READINESS_RENDER_FUNCTION,
        "panel_version": PREDICTION_WARROOM_SOURCE_READINESS_PREFLIGHT_PANEL_VERSION,
        "readiness_row_count": int(panel_packet.get("readiness_row_count") or 0) if panel_packet else 0,
        "unique_source_packet_count": int(panel_packet.get("unique_source_packet_count") or 0) if panel_packet else 0,
        "unique_source_packet_ids": list(panel_packet.get("unique_source_packet_ids") or []) if panel_packet else [],
        "widget_family_order": list(WIDGET_FAMILY_ORDER),
        "recommended_first_validation": "latest_prediction_summary_widget_source_readiness_row_mount_guard" if ok else "",
        "recommended_next_slice": "PS-Q18A WarRoom prediction widget source artifact resolution preflight or first bounded actual-source read probe; real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q17Z mounts visible source readiness rows in WarRoom. It shows binding metadata only and does not resolve/read source artifacts, read D-hot, refresh, write artifacts, render real Prediction widgets, stage/apply parameters, append ledgers, trigger AutoTrade, or call broker/private APIs.",
        "read_only": True,
        "non_executing": True,
        "source_readiness_row_mount_only": True,
        "source_binding_contract_ready": True,
        "readiness_row_visible_in_warroom": True,
        "streamlit_review_render_allowed": True,
        "source_artifact_resolution_allowed": False,
        "actual_source_bound": False,
        "source_artifact_resolved": False,
        "freshness_checked_against_d_hot": False,
        "real_prediction_widget_rendering_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q17Z WarRoom prediction widget source readiness row mount")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use PS-Q17Y observed fixture; validates visible readiness rows without D-hot read, source resolution, real widget render, refresh, or artifact write.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
