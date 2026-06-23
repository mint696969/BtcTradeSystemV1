# path: ./tools/check_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight.py
# desc: PS-Q17U non-executing WarRoom prediction widget page import/mount implementation preflight. It consumes PS-Q17T contracts and emits future patch fragments plus safety checks only; it never edits warroom_page.py, imports widgets into WarRoom, renders widgets, reads D-hot, writes artifacts, invokes refresh, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract import CHECKER_VERSION as PS_Q17T_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract import WIDGET_FAMILY_ORDER, build_report as build_ps_q17t_report

CHECKER = "ps_q17u_warroom_prediction_widget_page_import_mount_preflight"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight.v1"
PS_Q17T_SOURCE_CHECKER_VERSION = PS_Q17T_CHECKER_VERSION
PAGE_IMPORT_MOUNT_PREFLIGHT_VERSION = "warroom_prediction_widget_page_import_mount_preflight.v1"
WARROOM_PAGE_TARGET = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
IMPORT_INSERT_AFTER_MODULE = "prediction_warroom_non_ui_scheduled_producer_status_panel"
SECTION_INSERT_AFTER_FUNCTION = "_render_prediction_warroom_lowered_display_packet_visibility_review_section"
FUTURE_SECTION_FUNCTION = "_render_prediction_warroom_prediction_widgets_skeleton_section"
FUTURE_PAGE_BODY_CALL_ANCHOR = "_render_prediction_warroom_lowered_display_packet_visibility_review_section()"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _safe_q17t_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17T_SOURCE_CHECKER_VERSION:
        failures.append("q17t_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17t_report_not_ok")
    if report.get("page_mount_import_contract_only") is not True:
        failures.append("q17t_contract_only_flag_missing")
    if report.get("target_page_path") != WARROOM_PAGE_TARGET:
        failures.append("q17t_target_page_mismatch")
    if report.get("page_import_row_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17t_import_row_count_mismatch")
    if report.get("page_mount_row_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17t_mount_row_count_mismatch")
    if report.get("page_zone_row_count") != 3:
        failures.append("q17t_zone_row_count_mismatch")
    for key in (
        "warroom_page_import_patch_allowed",
        "warroom_page_mutation_allowed",
        "warroom_mount_patch_allowed",
        "component_import_allowed_by_warroom_page",
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
            failures.append(f"q17t_boundary_not_false:{key}")
    import_ids = [str(row.get("widget_family_id") or "") for row in _as_list(report.get("page_import_rows"))]
    mount_ids = [str(row.get("widget_family_id") or "") for row in _as_list(report.get("page_mount_rows"))]
    if import_ids != list(WIDGET_FAMILY_ORDER):
        failures.append("q17t_import_order_mismatch")
    if mount_ids != list(WIDGET_FAMILY_ORDER):
        failures.append("q17t_mount_order_mismatch")
    return not failures, failures


def _fixture_q17t_report() -> dict[str, Any]:
    return build_ps_q17t_report(use_observed_fixture=True)


def _future_import_block(report: Mapping[str, Any]) -> list[str]:
    rows = [_as_mapping(row) for row in _as_list(report.get("page_import_rows"))]
    return [str(row.get("future_import_statement") or "") for row in rows]


def _future_section_stub(report: Mapping[str, Any]) -> list[str]:
    mount_rows = [_as_mapping(row) for row in _as_list(report.get("page_mount_rows"))]
    lines = [
        f"def {FUTURE_SECTION_FUNCTION}() -> None:",
        "    # PS-Q17U preflight only: future section remains disabled until a later patch slice.",
        "    # Each skeleton callable currently returns a read-only disabled packet; no Streamlit render is invoked here.",
        "    prediction_widget_packets = [",
    ]
    for row in mount_rows:
        lines.append(f"        {row.get('component_function_name')}(props=None),  # {row.get('widget_family_id')}")
    lines.extend([
        "    ]",
        "    return None  # future render adapter will consume packets after explicit approval",
    ])
    return lines


def _future_page_body_call_block() -> list[str]:
    return [
        "        # PS-Q17U preflight only: future call remains disabled until explicit page patch slice.",
        f"        # {FUTURE_SECTION_FUNCTION}()",
    ]


def _mount_invocation_rows(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in [_as_mapping(item) for item in _as_list(report.get("page_mount_rows"))]:
        widget_id = str(row.get("widget_family_id") or "")
        rows.append({
            "widget_family_id": widget_id,
            "component_function_name": str(row.get("component_function_name") or ""),
            "mount_zone_id": str(row.get("mount_zone_id") or ""),
            "future_section_function": FUTURE_SECTION_FUNCTION,
            "future_invocation_line": f"{row.get('component_function_name')}(props=None)",
            "page_patch_preflight_only": True,
            "page_import_patch_allowed": False,
            "page_body_call_patch_allowed": False,
            "warroom_mount_patch_allowed": False,
            "streamlit_render_allowed": False,
            "actual_source_read_allowed": False,
            "refresh_invocation_allowed": False,
            "preflight_state": "ready_for_future_page_patch_still_disabled",
        })
    return rows


def build_report(*, supplied_q17t_report: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17t_report = _as_mapping(supplied_q17t_report)
    if not q17t_report and use_observed_fixture:
        q17t_report = _fixture_q17t_report()
    safe_q17t, validation_failures = _safe_q17t_boundary(q17t_report)
    import_block = _future_import_block(q17t_report) if safe_q17t else []
    section_stub = _future_section_stub(q17t_report) if safe_q17t else []
    body_call_block = _future_page_body_call_block() if safe_q17t else []
    invocation_rows = _mount_invocation_rows(q17t_report) if safe_q17t else []
    ok = bool(safe_q17t and len(import_block) == len(WIDGET_FAMILY_ORDER) and len(invocation_rows) == len(WIDGET_FAMILY_ORDER) and bool(section_stub) and bool(body_call_block))
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "page_import_mount_preflight_version": PAGE_IMPORT_MOUNT_PREFLIGHT_VERSION,
        "stage": "warroom_prediction_widget_page_import_mount_preflight_before_warroom_page_patch_and_rendering",
        "source_checker_version": PS_Q17T_SOURCE_CHECKER_VERSION,
        "source_q17t_report_valid": safe_q17t,
        "source_q17t_validation_failures": validation_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "target_page_path": WARROOM_PAGE_TARGET,
        "import_insert_after_module": IMPORT_INSERT_AFTER_MODULE,
        "section_insert_after_function": SECTION_INSERT_AFTER_FUNCTION,
        "future_section_function": FUTURE_SECTION_FUNCTION,
        "future_page_body_call_anchor": FUTURE_PAGE_BODY_CALL_ANCHOR,
        "widget_family_order": list(WIDGET_FAMILY_ORDER),
        "future_import_block": import_block,
        "future_section_stub": section_stub,
        "future_page_body_call_block": body_call_block,
        "mount_invocation_rows": invocation_rows,
        "future_import_line_count": len(import_block),
        "future_section_stub_line_count": len(section_stub),
        "future_mount_invocation_count": len(invocation_rows),
        "preflight_patch_fragment_count": int(bool(import_block)) + int(bool(section_stub)) + int(bool(body_call_block)),
        "page_patch_preflight_ready": ok,
        "recommended_first_validation": "latest_prediction_summary_widget_page_import_mount_preflight_guard" if ok else "",
        "recommended_next_slice": "PS-Q17V WarRoom prediction widget page import/mount patch or actual-source preflight; widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q17U prepares future warroom_page.py import/mount patch fragments and conflict checks only. It does not edit warroom_page.py, call the future section, render Streamlit widgets, read D-hot, refresh, write artifacts, or stage/apply parameters.",
        "read_only": True,
        "non_executing": True,
        "page_import_mount_preflight_only": True,
        "preflight_only": True,
        "diagnostic_only": True,
        "warroom_widget_design_premise": True,
        "warroom_page_patch_allowed": False,
        "warroom_page_import_patch_allowed": False,
        "warroom_page_mutation_allowed": False,
        "warroom_mount_patch_allowed": False,
        "component_import_allowed_by_warroom_page": False,
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
        "would_write_warroom_page": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q17U WarRoom prediction widget page import/mount implementation preflight")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use the PS-Q17T observed fixture path; no warroom_page.py patch, D-hot read, widget render, refresh, or write is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
