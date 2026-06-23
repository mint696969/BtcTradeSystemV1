# path: ./tools/test_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount_guard.py
# desc: Focused guard for PS-Q18M latest_prediction_summary_widget operator value summary mount.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount import CHECKER_VERSION, EXPECTED_COMPACT_LINE, OPERATOR_VALUE_SUMMARY_MOUNT_VERSION, WARROOM_PAGE_TARGET, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
WARROOM_PAGE = REPO_ROOT / WARROOM_PAGE_TARGET
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_operator_value_summary_panel.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18M_LATEST_PREDICTION_SUMMARY_WIDGET_OPERATOR_VALUE_SUMMARY_MOUNT_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_operator_value_summary_panel.py",
    "tools/check_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount.py",
    "tools/test_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18M_LATEST_PREDICTION_SUMMARY_WIDGET_OPERATOR_VALUE_SUMMARY_MOUNT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18m_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount_guard.py",
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
        "LATEST_PREDICTION_SUMMARY_WIDGET_OPERATOR_VALUE_SUMMARY_PANEL_VERSION",
        "SUMMARY_ITEMS",
        "build_latest_prediction_summary_widget_operator_value_summary_rows",
        "build_latest_prediction_summary_widget_operator_value_summary_packet",
        "latest_prediction_summary_widget_operator_value_summary_mount_only",
        "warroom_operator_summary_rows_ready",
        "operator_summary_display_only",
        "compact_line_ready",
        "q18j_validation_invoked_by_mount",
        "component_packet_builder_invoked_by_mount",
        "observed_mapped_prediction_run_id",
        "observed_component_source_artifact_ref",
    ):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in ("import streamlit", "st.", "Path(", "open(", "read_text(", "read_bytes(", "write_text(", "data_read", "data_slice", "glob(", "rglob(", "render_latest_prediction_summary_widget(", "build_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation(", "send_order(", "create_order("):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")
    page_text = _read(WARROOM_PAGE) if WARROOM_PAGE.exists() else ""
    for marker in (
        "from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_operator_value_summary_panel import (",
        "build_latest_prediction_summary_widget_operator_value_summary_packet",
        "def _prediction_warroom_latest_prediction_summary_operator_value_summary_display_rows(packet: dict) -> list[dict]:",
        "def _render_prediction_warroom_latest_prediction_summary_widget_operator_value_summary_section() -> None:",
        "with live_shell.render_folded_section(\"Prediction WarRoom latest summary operator value summary\", expanded=False):",
        "_render_prediction_warroom_latest_prediction_summary_widget_operator_value_summary_section()",
        "latest summary operator value rows={rows} / compact_line_ready={compact} / values_supplied={values} / q18j_mount=false / render=false / actual_read=false",
        "st.dataframe(summary_rows, width=\"stretch\", hide_index=True)",
        "_render_warroom_reading_caption(compact_line, max_height_px=90)",
    ):
        if marker not in page_text:
            failures.append(f"missing page marker: {marker}")
    if page_text.count("_render_prediction_warroom_latest_prediction_summary_widget_operator_value_summary_section(") != 2:
        failures.append("operator value summary render function should have definition and page-body call only")
    for forbidden in ("build_ps_q18j_report(", "build_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation(", "q18j_validation_invoked_by_mount=True", "component_packet_builder_invoked_by_mount=True", "streamlit_render_invoked=True", "actual_source_read_invoked_by_mount=True", "send_order(", "create_order("):
        if forbidden in page_text:
            failures.append(f"forbidden page token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        'CHECKER = "ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount.v1"',
        'OPERATOR_VALUE_SUMMARY_MOUNT_VERSION = "latest_prediction_summary_widget_operator_value_summary_mount.v1"',
        "EXPECTED_COMPACT_LINE",
        "build_ps_q18j_report",
        "build_latest_prediction_summary_widget_operator_value_summary_packet",
        "latest_prediction_summary_widget_operator_value_summary_mount_only",
        "q18j_validation_invoked_by_mount",
        "observed_mapped_prediction_run_id",
        "PS-Q18N latest summary operator value summary close guard",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount.v1":
        failures.append("checker version mismatch")
    if OPERATOR_VALUE_SUMMARY_MOUNT_VERSION != "latest_prediction_summary_widget_operator_value_summary_mount.v1":
        failures.append("mount version mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture operator summary should be ok: {report}")
    if report.get("source_q18j_report_valid") is not True:
        failures.append("source Q18J report should validate")
    if report.get("summary_packet_valid") is not True:
        failures.append("summary packet should validate")
    if report.get("page_summary_packet_valid") is not True:
        failures.append("page-safe summary packet should validate")
    if report.get("summary_row_count") != 7:
        failures.append("expected 7 observed summary rows")
    if report.get("page_summary_row_count") != 7:
        failures.append("expected 7 page-safe summary rows")
    if report.get("values_supplied") is not True:
        failures.append("observed summary should have supplied values")
    if report.get("page_values_supplied") is not False:
        failures.append("page-safe summary should not have supplied values")
    if report.get("compact_line_ready") is not True:
        failures.append("observed compact line should be ready")
    if report.get("page_compact_line_ready") is not False:
        failures.append("page-safe compact line should not be ready")
    if report.get("compact_line") != EXPECTED_COMPACT_LINE:
        failures.append("compact line mismatch")
    for key, value in {
        "observed_mapped_prediction_run_id": "ps_q18i_fixture_run",
        "observed_mapped_market_uid": "BTC-USD",
        "observed_mapped_source_generated_at": "2026-06-22T00:00:00Z",
        "observed_mapped_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
        "observed_component_source_generated_at": "2026-06-22T00:00:00Z",
        "observed_component_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
    }.items():
        if report.get(key) != value:
            failures.append(f"observed value mismatch: {key}")
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_operator_value_summary_mount_only", "warroom_operator_summary_rows_ready", "operator_summary_display_only", "mapped_payload_values_display_only", "warroom_page_mutation_allowed"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in ("q18j_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "component_packet_builder_allowed_by_mount", "streamlit_render_invoked", "actual_source_read_invoked_by_mount", "actual_source_read_allowed_by_mount", "payload_reparse_allowed", "d_hot_directory_scan_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount.v1",
        "operator_value_summary_mount_version=latest_prediction_summary_widget_operator_value_summary_mount.v1",
        "panel_version=prediction_warroom_latest_prediction_summary_widget_operator_value_summary_panel.ps_q18m.v1",
        "source_q18j_checker=check_phase4a_prediction_system_ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.v1",
        "summary_row_count=7",
        "page_summary_row_count=7",
        "values_supplied=true",
        "page_values_supplied=false",
        "compact_line_ready=true",
        "page_compact_line_ready=false",
        "latest_prediction_summary_widget_operator_value_summary_mount_only=true",
        "warroom_operator_summary_rows_ready=true",
        "operator_summary_display_only=true",
        "q18j_validation_invoked_by_mount=false",
        "component_packet_builder_invoked_by_mount=false",
        "streamlit_render_invoked=false",
        "actual_source_read_invoked_by_mount=false",
        "no_q18j_checker_invocation_from_warroom",
        "no_component_packet_builder_invocation_from_warroom",
        "no_streamlit_render",
        "PS-Q18N: Latest summary operator value summary close guard",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
