# path: ./tools/test_phase4a_prediction_system_ps_q18k_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount_guard.py
# desc: Focused guard for PS-Q18K latest_prediction_summary_widget mapped-payload render-disabled packet status row mount.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18k_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount import CHECKER_VERSION, MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_STATUS_ROW_MOUNT_VERSION, WARROOM_PAGE_TARGET, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
WARROOM_PAGE = REPO_ROOT / WARROOM_PAGE_TARGET
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_panel.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18k_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18k_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18K_LATEST_PREDICTION_SUMMARY_WIDGET_MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_STATUS_ROW_MOUNT_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_panel.py",
    "tools/check_phase4a_prediction_system_ps_q18k_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount.py",
    "tools/test_phase4a_prediction_system_ps_q18k_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18K_LATEST_PREDICTION_SUMMARY_WIDGET_MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_STATUS_ROW_MOUNT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18k_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18k_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def main_guard() -> int:
    failures: list[str] = []
    for path in (WARROOM_PAGE, COMPONENT, TOOL, UNIT, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    component_text = _read(COMPONENT) if COMPONENT.exists() else ""
    for marker in (
        "LATEST_PREDICTION_SUMMARY_WIDGET_MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_STATUS_PANEL_VERSION",
        "build_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_rows",
        "build_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_packet",
        "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount_only",
        "warroom_status_rows_ready",
        "validation_report_display_only",
        "mapped_payload_render_disabled_packet_status_display_only",
        "q18j_validation_invoked_by_mount",
        "component_packet_builder_invoked_by_mount",
        "component_packet_builder_allowed_by_mount",
        "streamlit_render_invoked",
        "actual_source_read_invoked_by_mount",
        "observed_component_source_generated_at",
        "observed_component_source_artifact_ref",
    ):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in ("import streamlit", "st.", "Path(", "open(", "read_text(", "read_bytes(", "write_text(", "data_read", "data_slice", "glob(", "rglob(", "render_latest_prediction_summary_widget(", "send_order(", "create_order("):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")
    page_text = _read(WARROOM_PAGE) if WARROOM_PAGE.exists() else ""
    for marker in (
        "from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_panel import (",
        "build_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_packet",
        "def _prediction_warroom_latest_prediction_summary_mapped_payload_render_disabled_packet_status_display_rows(packet: dict) -> list[dict]:",
        "def _render_prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_section() -> None:",
        "with live_shell.render_folded_section(\"Prediction WarRoom latest summary mapped payload render-disabled packet status\", expanded=False):",
        "_render_prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_section()",
        "latest summary mapped payload render-disabled packet rows={rows} / q18j_mount=false / render=false / actual_read=false",
        "st.dataframe(status_rows, width=\"stretch\", hide_index=True)",
    ):
        if marker not in page_text:
            failures.append(f"missing page marker: {marker}")
    if page_text.count("_render_prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_section(") != 2:
        failures.append("mapped payload render-disabled packet status render function should have definition and page-body call only")
    for forbidden in (
        "build_ps_q18j_report(",
        "build_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation(",
        "q18j_validation_invoked_by_mount=True",
        "component_packet_builder_invoked_by_mount=True",
        "component_packet_builder_allowed_by_mount=True",
        "streamlit_render_invoked=True",
        "actual_source_read_invoked_by_mount=True",
        "send_order(",
        "create_order(",
    ):
        if forbidden in page_text:
            failures.append(f"forbidden page token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        'CHECKER = "ps_q18k_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18k_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount.v1"',
        'MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_STATUS_ROW_MOUNT_VERSION = "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount.v1"',
        "build_ps_q18j_report",
        "build_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_packet",
        "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount_only",
        "q18j_validation_invoked_by_mount",
        "component_packet_builder_invoked_by_mount",
        "observed_component_source_generated_at",
        "PS-Q18L first operator-visible latest summary value panel",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18k_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount.v1":
        failures.append("checker version mismatch")
    if MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_STATUS_ROW_MOUNT_VERSION != "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount.v1":
        failures.append("mount version mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture status mount should be ok: {report}")
    if report.get("source_q18j_report_valid") is not True:
        failures.append("source Q18J report should validate")
    if report.get("status_packet_valid") is not True:
        failures.append("status packet should validate")
    if report.get("page_status_packet_valid") is not True:
        failures.append("page-safe status packet should validate")
    if report.get("status_row_count") != 12:
        failures.append("expected 12 status rows")
    if report.get("page_status_row_count") != 12:
        failures.append("expected 12 page-safe status rows")
    if report.get("observed_component_packet_builder_invoked") is not True:
        failures.append("observed builder should be true in supplied report path")
    if report.get("observed_component_packet_valid") is not True:
        failures.append("observed component packet should be valid")
    if report.get("observed_component_packet_state") != "read_only_component_skeleton_render_disabled":
        failures.append("observed component packet state mismatch")
    if report.get("observed_component_source_generated_at") != "2026-06-22T00:00:00Z":
        failures.append("observed generated_at mismatch")
    if report.get("observed_component_source_artifact_ref") != "fixture://ps_q18i/latest_prediction.json":
        failures.append("observed artifact ref mismatch")
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount_only", "warroom_status_rows_ready", "validation_report_display_only", "mapped_payload_render_disabled_packet_status_display_only", "warroom_page_mutation_allowed"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "q18j_validation_invoked_by_mount",
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
        "parameter_apply_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
    ):
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q18k_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount.v1",
        "mapped_payload_render_disabled_packet_status_row_mount_version=latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount.v1",
        "panel_version=prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_panel.ps_q18k.v1",
        "source_q18j_checker=check_phase4a_prediction_system_ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.v1",
        "status_row_count=12",
        "page_status_row_count=12",
        "observed_component_packet_builder_invoked=true",
        "observed_component_source_generated_at=2026-06-22T00:00:00Z",
        "observed_component_source_artifact_ref=fixture://ps_q18i/latest_prediction.json",
        "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount_only=true",
        "warroom_status_rows_ready=true",
        "q18j_validation_invoked_by_mount=false",
        "component_packet_builder_invoked_by_mount=false",
        "streamlit_render_invoked=false",
        "actual_source_read_invoked_by_mount=false",
        "no_q18j_checker_invocation_from_warroom",
        "no_component_packet_builder_invocation_from_warroom",
        "no_streamlit_render",
        "PS-Q18L: First operator-visible latest summary value panel",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q18k_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18k_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_status_row_mount_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
