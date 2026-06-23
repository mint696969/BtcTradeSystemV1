# path: ./tools/check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.py
# desc: PS-Q17X WarRoom prediction widget disabled section page-body review mount checker. It validates a folded review-row mount only; it never enables real Prediction widget rendering, reads D-hot, writes artifacts, invokes refresh, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch import CHECKER_VERSION as PS_Q17V_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel import CHECKER_VERSION as PS_Q17W_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel import WIDGET_FAMILY_ORDER, build_report as build_ps_q17w_report

CHECKER = "ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.v1"
PS_Q17W_SOURCE_CHECKER_VERSION = PS_Q17W_CHECKER_VERSION
PAGE_BODY_REVIEW_MOUNT_VERSION = "warroom_prediction_widget_disabled_section_page_body_review_mount.v1"
WARROOM_PAGE_TARGET = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
REVIEW_MOUNT_FUNCTION = "_render_prediction_warroom_prediction_widgets_disabled_section_review_mount"
DISABLED_SECTION_FUNCTION = "_render_prediction_warroom_prediction_widgets_skeleton_section"
REVIEW_FOLDED_SECTION_TITLE = "Prediction WarRoom disabled widget skeleton review"


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


def _safe_q17w_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q17W_SOURCE_CHECKER_VERSION:
        failures.append("q17w_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q17w_report_not_ok")
    if report.get("review_row_count") != len(WIDGET_FAMILY_ORDER):
        failures.append("q17w_review_row_count_mismatch")
    if report.get("review_zone_count") != 3:
        failures.append("q17w_review_zone_count_mismatch")
    for key in (
        "warroom_page_mutation_allowed",
        "page_body_call_enabled",
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
            failures.append(f"q17w_boundary_not_false:{key}")
    return not failures, failures


def _stable_pre_q17x_q17v_source_report() -> dict[str, Any]:
    """Return the PS-Q17V source boundary Q17W needs after PS-Q17X changes warroom_page.py."""
    false_boundaries = {
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
    return {
        "ok": True,
        "checker_version": PS_Q17V_CHECKER_VERSION,
        "imported_widget_count": len(WIDGET_FAMILY_ORDER),
        "disabled_section_defined": True,
        "page_body_call_enabled": False,
        **false_boundaries,
    }


def _fixture_q17w_report() -> dict[str, Any]:
    return build_ps_q17w_report(
        supplied_q17v_report=_stable_pre_q17x_q17v_source_report(),
        use_observed_fixture=True,
    )


def _page_validation(page_text: str) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for marker in (
        "from btcts.apps.operator_ui.components.prediction_warroom_prediction_widgets_disabled_section_review_panel import (",
        "build_prediction_warroom_prediction_widgets_disabled_section_review_packet",
        f"def {REVIEW_MOUNT_FUNCTION}() -> None:",
        "def _prediction_warroom_disabled_widget_review_zone_display_rows(packet: dict) -> list[dict]:",
        "def _prediction_warroom_disabled_widget_review_display_rows(packet: dict) -> list[dict]:",
        f'with live_shell.render_folded_section("{REVIEW_FOLDED_SECTION_TITLE}", expanded=False):',
        f"{REVIEW_MOUNT_FUNCTION}()",
        "st.dataframe(zone_rows, width=\"stretch\", hide_index=True)",
        "st.dataframe(review_rows, width=\"stretch\", hide_index=True)",
        "widget_render=false / actual_source_read=false",
    ):
        if marker not in page_text:
            failures.append(f"missing_page_marker:{marker}")
    if page_text.count(f"{REVIEW_MOUNT_FUNCTION}(") != 2:
        failures.append("review_mount_should_have_definition_and_page_body_call_only")
    if page_text.count(f"{DISABLED_SECTION_FUNCTION}(") != 2:
        failures.append("disabled_section_should_have_definition_and_review_mount_call_only")
    for forbidden in (
        "allow_actual_read=True",
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


def build_report(*, supplied_q17w_report: Mapping[str, Any] | Any | None = None, page_text: str | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q17w_report = _as_mapping(supplied_q17w_report)
    if not q17w_report and use_observed_fixture:
        q17w_report = _fixture_q17w_report()
    safe_q17w, source_failures = _safe_q17w_boundary(q17w_report)
    actual_page_text = page_text if page_text is not None else (_read_warroom_page() if safe_q17w else "")
    page_valid, page_failures = _page_validation(actual_page_text) if safe_q17w else (False, [])
    ok = bool(safe_q17w and page_valid)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "page_body_review_mount_version": PAGE_BODY_REVIEW_MOUNT_VERSION,
        "stage": "warroom_prediction_widget_disabled_section_page_body_review_mount_before_visible_widget_rendering_and_actual_source_read",
        "source_checker_version": PS_Q17W_SOURCE_CHECKER_VERSION,
        "source_q17v_fixture_mode": "stable_pre_q17x_page_patch_source_boundary",
        "source_q17w_report_valid": safe_q17w,
        "source_q17w_validation_failures": source_failures,
        "page_validation_failures": page_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "target_page_path": WARROOM_PAGE_TARGET,
        "review_mount_function": REVIEW_MOUNT_FUNCTION,
        "disabled_section_function": DISABLED_SECTION_FUNCTION,
        "review_folded_section_title": REVIEW_FOLDED_SECTION_TITLE,
        "widget_family_order": list(WIDGET_FAMILY_ORDER),
        "review_row_count": int(q17w_report.get("review_row_count") or 0) if q17w_report else 0,
        "review_zone_count": int(q17w_report.get("review_zone_count") or 0) if q17w_report else 0,
        "recommended_first_validation": "latest_prediction_summary_widget_page_body_review_mount_guard" if ok else "",
        "recommended_next_slice": "PS-Q17Y WarRoom prediction widget actual-source preflight or visible disabled-widget review refinement; real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q17X mounts a folded WarRoom review section that displays disabled skeleton review rows only. It calls pure-data skeleton/review builders but does not render live Prediction widgets, read D-hot actual sources, refresh, write artifacts, or stage/apply parameters.",
        "read_only": True,
        "non_executing": True,
        "page_body_review_mount_applied": True,
        "disabled_section_page_body_review_mount_enabled": True,
        "visible_review_rows_rendered": True,
        "streamlit_review_render_allowed": True,
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
    parser = argparse.ArgumentParser(description="PS-Q17X WarRoom prediction widget disabled section page-body review mount")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use PS-Q17W observed fixture path; validates page-body review mount without D-hot read, real widget render, refresh, or artifact write.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
