# path: ./tools/check_phase4a_prediction_system_ps_q18c_warroom_prediction_widget_source_read_probe_status_row_mount.py
# desc: PS-Q18C checker for WarRoom source read probe status row mount. It validates display-only rows and page mount; it never invokes bounded read probe from WarRoom, discovers D-hot, refreshes, writes, renders real widgets, AutoTrades, or calls broker APIs.

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Mapping

BTCTS_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "btcts_next", "src")
if BTCTS_SRC not in sys.path:
    sys.path.insert(0, BTCTS_SRC)

from check_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe import CHECKER_VERSION as PS_Q18B_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe import build_report as build_ps_q18b_report
from btcts.apps.operator_ui.components.prediction_warroom_prediction_widget_source_read_probe_status_panel import PREDICTION_WARROOM_SOURCE_READ_PROBE_STATUS_PANEL_VERSION, build_prediction_warroom_prediction_widget_source_read_probe_status_packet

CHECKER = "ps_q18c_warroom_prediction_widget_source_read_probe_status_row_mount"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18c_warroom_prediction_widget_source_read_probe_status_row_mount.v1"
SOURCE_READ_PROBE_STATUS_ROW_MOUNT_VERSION = "warroom_prediction_widget_source_read_probe_status_row_mount.v1"
PS_Q18B_SOURCE_CHECKER_VERSION = PS_Q18B_CHECKER_VERSION
WARROOM_PAGE_TARGET = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
SOURCE_READ_PROBE_STATUS_SECTION_TITLE = "Prediction WarRoom source read probe status"
SOURCE_READ_PROBE_STATUS_RENDER_FUNCTION = "_render_prediction_warroom_prediction_widget_source_read_probe_status_section"


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


def _safe_q18b_boundary(report: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q18B_SOURCE_CHECKER_VERSION:
        failures.append("q18b_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q18b_report_not_ok")
    if report.get("probe_packet_valid") is not True:
        failures.append("q18b_probe_packet_not_valid")
    for key in ("bounded_actual_source_read_probe_only", "single_file_probe_only", "actual_file_read_attempted", "payload_decode_succeeded", "schema_probe_ok"):
        if report.get(key) is not True:
            failures.append(f"q18b_true_boundary_missing:{key}")
    for key in (
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
        "real_prediction_widget_rendering_allowed",
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
            failures.append(f"q18b_boundary_not_false:{key}")
    return not failures, failures


def _safe_status_packet(packet: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if packet.get("panel_version") != PREDICTION_WARROOM_SOURCE_READ_PROBE_STATUS_PANEL_VERSION:
        failures.append("panel_version_mismatch")
    if packet.get("ok") is not True:
        failures.append("status_packet_not_ok")
    if packet.get("status_row_count") != 7:
        failures.append("status_row_count_mismatch")
    if packet.get("warroom_status_rows_ready") is not True:
        failures.append("warroom_status_rows_not_ready")
    for key in (
        "bounded_actual_source_read_probe_called_by_mount",
        "actual_source_read_invoked_by_mount",
        "actual_source_read_allowed_by_warroom_mount",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "warroom_widget_rendering_allowed",
        "real_prediction_widget_rendering_allowed",
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
    ):
        if packet.get(key) is not False:
            failures.append(f"status_boundary_not_false:{key}")
    return not failures, failures


def _page_validation(page_text: str) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for marker in (
        "from btcts.apps.operator_ui.components.prediction_warroom_prediction_widget_source_read_probe_status_panel import (",
        "build_prediction_warroom_prediction_widget_source_read_probe_status_packet",
        "def _prediction_warroom_source_read_probe_status_display_rows(packet: dict) -> list[dict]:",
        f"def {SOURCE_READ_PROBE_STATUS_RENDER_FUNCTION}() -> None:",
        f'with live_shell.render_folded_section("{SOURCE_READ_PROBE_STATUS_SECTION_TITLE}", expanded=False):',
        f"{SOURCE_READ_PROBE_STATUS_RENDER_FUNCTION}()",
        "source read probe status rows={rows} / warroom_actual_read_invoked=false / d_hot_scan=false / render=false",
        "st.dataframe(status_rows, width=\"stretch\", hide_index=True)",
    ):
        if marker not in page_text:
            failures.append(f"missing_page_marker:{marker}")
    if page_text.count(f"{SOURCE_READ_PROBE_STATUS_RENDER_FUNCTION}(") != 2:
        failures.append("source_read_probe_status_render_function_should_have_definition_and_page_body_call_only")
    for forbidden in (
        "build_ps_q18b_report(",
        "build_prediction_warroom_prediction_widget_bounded_actual_source_read_probe_packet(",
        "allow_actual_read=True",
        "PS_Q18B_ALLOW_ONE_BOUNDED_READ_ONLY_JSON_PROBE",
        "d_hot_directory_scan_allowed=True",
        "actual_source_read_invoked_by_mount=True",
        "send_order(",
        "create_order(",
        "parameter_apply_allowed=True",
        "parameter_staging_write_allowed=True",
    ):
        if forbidden in page_text:
            failures.append(f"forbidden_page_token:{forbidden}")
    return not failures, failures


def build_report(*, supplied_q18b_report: Mapping[str, Any] | Any | None = None, page_text: str | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    q18b_report = _as_mapping(supplied_q18b_report)
    if not q18b_report and use_observed_fixture:
        q18b_report = build_ps_q18b_report(use_observed_fixture=True)
    safe_q18b, q18b_failures = _safe_q18b_boundary(q18b_report)
    status_packet = build_prediction_warroom_prediction_widget_source_read_probe_status_packet(supplied_probe_report=q18b_report) if safe_q18b else {}
    safe_status, status_failures = _safe_status_packet(status_packet) if status_packet else (False, [])
    page_status_packet = build_prediction_warroom_prediction_widget_source_read_probe_status_packet()
    safe_page_status, page_status_failures = _safe_status_packet(page_status_packet)
    actual_page_text = page_text if page_text is not None else (_read_warroom_page() if safe_status and safe_page_status else "")
    page_valid, page_failures = _page_validation(actual_page_text) if safe_status and safe_page_status else (False, [])
    ok = bool(safe_q18b and safe_status and safe_page_status and page_valid)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "source_read_probe_status_row_mount_version": SOURCE_READ_PROBE_STATUS_ROW_MOUNT_VERSION,
        "stage": "warroom_prediction_widget_source_read_probe_status_row_mount_before_probe_invocation_d_hot_discovery_real_widget_rendering_and_refresh",
        "source_q18b_checker_version": PS_Q18B_SOURCE_CHECKER_VERSION,
        "source_q18b_report_valid": safe_q18b,
        "source_q18b_validation_failures": q18b_failures,
        "status_packet_valid": safe_status,
        "status_validation_failures": status_failures,
        "page_status_packet_valid": safe_page_status,
        "page_status_validation_failures": page_status_failures,
        "page_validation_failures": page_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "target_page_path": WARROOM_PAGE_TARGET,
        "source_read_probe_status_section_title": SOURCE_READ_PROBE_STATUS_SECTION_TITLE,
        "source_read_probe_status_render_function": SOURCE_READ_PROBE_STATUS_RENDER_FUNCTION,
        "panel_version": PREDICTION_WARROOM_SOURCE_READ_PROBE_STATUS_PANEL_VERSION,
        "status_row_count": int(status_packet.get("status_row_count") or 0) if status_packet else 0,
        "page_status_row_count": int(page_status_packet.get("status_row_count") or 0),
        "recommended_first_validation": "latest_prediction_summary_widget_source_read_probe_status_row_mount_guard" if ok else "",
        "recommended_next_slice": "PS-Q18D bounded schema-specific probe or first real-widget data adapter binding preflight; real widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q18C mounts WarRoom source read probe status rows only. The page mount displays status and never invokes the Q18B bounded read probe, never discovers/scans D-hot, never refreshes, writes, renders real widgets, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker APIs.",
        "read_only": True,
        "non_executing": True,
        "source_read_probe_status_row_mount_only": True,
        "warroom_status_rows_ready": True,
        "bounded_probe_report_display_only": True,
        "bounded_actual_source_read_probe_called_by_mount": False,
        "actual_source_read_invoked_by_mount": False,
        "actual_source_read_allowed_by_warroom_mount": False,
        "source_discovery_allowed": False,
        "d_hot_directory_scan_allowed": False,
        "d_hot_actual_read_allowed": False,
        "freshness_checked_against_d_hot": False,
        "warroom_page_mutation_allowed": True,
        "warroom_widget_rendering_allowed": False,
        "real_prediction_widget_rendering_allowed": False,
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
    parser = argparse.ArgumentParser(description="PS-Q18C WarRoom source read probe status row mount")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use Q18B observed fixture report; WarRoom page mount still does not invoke bounded read probe.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
