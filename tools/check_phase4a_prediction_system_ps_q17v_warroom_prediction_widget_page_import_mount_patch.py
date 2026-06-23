# path: ./tools/check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.py
# desc: PS-Q17V WarRoom prediction widget page import/mount patch checker. It validates safe import insertion and disabled packet-builder section in warroom_page.py. It never reads D-hot, writes artifacts, invokes refresh, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight import CHECKER_VERSION as PS_Q17U_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight import WIDGET_FAMILY_ORDER, build_report as build_ps_q17u_report

CHECKER = "ps_q17v_warroom_prediction_widget_page_import_mount_patch"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.v1"
PS_Q17U_SOURCE_CHECKER_VERSION = PS_Q17U_CHECKER_VERSION
PAGE_IMPORT_MOUNT_PATCH_VERSION = "warroom_prediction_widget_page_import_mount_patch.v1"
WARROOM_PAGE_TARGET = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PACKET_BUILDER_FUNCTION = "_build_prediction_warroom_prediction_widgets_skeleton_packets"
DISABLED_SECTION_FUNCTION = "_render_prediction_warroom_prediction_widgets_skeleton_section"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_warroom_page() -> str:
    path = os.path.join(_repo_root(), WARROOM_PAGE_TARGET)
    with open(path, "r", encoding="utf-8-sig") as handle:
        return handle.read()


def _safe_q17u_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17U_SOURCE_CHECKER_VERSION:
        failures.append("q17u_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17u_report_not_ok")
    if report.get("page_import_mount_preflight_only") is not True:
        failures.append("q17u_preflight_flag_missing")
    if report.get("page_patch_preflight_ready") is not True:
        failures.append("q17u_page_patch_preflight_not_ready")
    if report.get("future_import_line_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17u_future_import_line_count_mismatch")
    if report.get("future_mount_invocation_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17u_future_mount_invocation_count_mismatch")
    for key in (
        "warroom_page_patch_allowed",
        "warroom_page_import_patch_allowed",
        "warroom_page_mutation_allowed",
        "warroom_mount_patch_allowed",
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
        "would_write_warroom_page",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
    ):
        if report.get(key) is not False:
            failures.append(f"q17u_boundary_not_false:{key}")
    return not failures, failures


def _fixture_q17u_report() -> dict[str, Any]:
    return build_ps_q17u_report(use_observed_fixture=True)


def _page_validation(page_text: str, q17u_report: Mapping[str, Any]) -> tuple[bool, list[str], list[str]]:
    failures: list[str] = []
    imported_widgets: list[str] = []
    for widget_id in WIDGET_FAMILY_ORDER:
        import_token = f"prediction_widgets.{widget_id} import ("
        fn_token = f"render_{widget_id}"
        if import_token not in page_text or fn_token not in page_text:
            failures.append(f"missing_page_import:{widget_id}")
        else:
            imported_widgets.append(widget_id)
        call_token = f"render_{widget_id}(props=None)"
        if call_token not in page_text:
            failures.append(f"missing_disabled_packet_builder_call:{widget_id}")
    if f"def {PACKET_BUILDER_FUNCTION}() -> list[dict]:" not in page_text:
        failures.append("packet_builder_function_missing")
    if f"def {DISABLED_SECTION_FUNCTION}() -> list[dict]:" not in page_text:
        failures.append("disabled_section_function_missing")
    if page_text.count(f"{DISABLED_SECTION_FUNCTION}(") != 1:
        failures.append("disabled_section_must_not_be_called_by_page_body")
    if page_text.count(f"{PACKET_BUILDER_FUNCTION}(") != 2:
        failures.append("packet_builder_should_have_definition_and_disabled_section_call_only")
    if "with live_shell.render_folded_section(\"Prediction WarRoom real payload review\", expanded=True):" not in page_text:
        failures.append("real_payload_review_section_anchor_missing")
    for forbidden in (
        "st.dataframe(_build_prediction_warroom_prediction_widgets_skeleton_packets",
        "st.json(_build_prediction_warroom_prediction_widgets_skeleton_packets",
        "st.write(_build_prediction_warroom_prediction_widgets_skeleton_packets",
        "live_shell.render_fragment_slot(\n            warroom_widget_slot(\"latest_prediction_summary_widget\")",
        "allow_actual_read=True",
        "append_decision(",
        "append_command(",
        "send_order(",
        "create_order(",
    ):
        if forbidden in page_text:
            failures.append(f"forbidden_page_token:{forbidden}")
    return not failures, failures, imported_widgets


def build_report(*, supplied_q17u_report: Mapping[str, Any] | Any | None = None, page_text: str | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17u_report = _as_mapping(supplied_q17u_report)
    if not q17u_report and use_observed_fixture:
        q17u_report = _fixture_q17u_report()
    safe_q17u, source_failures = _safe_q17u_boundary(q17u_report)
    actual_page_text = page_text if page_text is not None else (_read_warroom_page() if safe_q17u else "")
    page_valid, page_failures, imported_widgets = _page_validation(actual_page_text, q17u_report) if safe_q17u else (False, [], [])
    ok = bool(safe_q17u and page_valid and imported_widgets == list(WIDGET_FAMILY_ORDER))
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "page_import_mount_patch_version": PAGE_IMPORT_MOUNT_PATCH_VERSION,
        "stage": "warroom_prediction_widget_page_import_mount_patch_imports_and_disabled_section_before_render_enablement",
        "source_checker_version": PS_Q17U_SOURCE_CHECKER_VERSION,
        "source_q17u_report_valid": safe_q17u,
        "source_q17u_validation_failures": source_failures,
        "page_validation_failures": page_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "target_page_path": WARROOM_PAGE_TARGET,
        "widget_family_order": list(WIDGET_FAMILY_ORDER),
        "imported_widget_count": len(imported_widgets),
        "imported_widget_family_ids": imported_widgets,
        "packet_builder_function": PACKET_BUILDER_FUNCTION,
        "disabled_section_function": DISABLED_SECTION_FUNCTION,
        "disabled_section_defined": f"def {DISABLED_SECTION_FUNCTION}() -> list[dict]:" in actual_page_text,
        "disabled_section_call_count": actual_page_text.count(f"{DISABLED_SECTION_FUNCTION}(") if actual_page_text else 0,
        "packet_builder_call_count": actual_page_text.count(f"{PACKET_BUILDER_FUNCTION}(") if actual_page_text else 0,
        "recommended_first_validation": "latest_prediction_summary_widget_page_import_mount_patch_guard" if ok else "",
        "recommended_next_slice": "PS-Q17W WarRoom prediction widget disabled section review panel or actual-source preflight; visible widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q17V imports Prediction widget skeleton modules into warroom_page.py and defines a disabled packet-builder section, but the page body does not call it yet. It performs no visible widget rendering, no D-hot read, no refresh, no artifact write, and no parameter action.",
        "read_only": True,
        "non_executing": True,
        "warroom_page_patch_applied": True,
        "warroom_page_import_patch_applied": True,
        "disabled_section_defined_only": True,
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
    parser = argparse.ArgumentParser(description="PS-Q17V WarRoom prediction widget page import/mount patch")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use the PS-Q17U observed fixture path; validates warroom_page.py patch without D-hot read, widget render, refresh, or artifact write.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
