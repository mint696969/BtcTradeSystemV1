# path: ./tools/test_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount_guard.py
# desc: Focused guard for PS-Q18N latest_prediction_summary_widget real-source handoff preflight mount.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount import CHECKER_VERSION, REAL_SOURCE_HANDOFF_PREFLIGHT_MOUNT_VERSION, WARROOM_PAGE_TARGET, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
WARROOM_PAGE = REPO_ROOT / WARROOM_PAGE_TARGET
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18N_LATEST_PREDICTION_SUMMARY_WIDGET_REAL_SOURCE_HANDOFF_PREFLIGHT_MOUNT_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel.py",
    "tools/check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.py",
    "tools/test_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18N_LATEST_PREDICTION_SUMMARY_WIDGET_REAL_SOURCE_HANDOFF_PREFLIGHT_MOUNT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18n_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount_guard.py",
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
        "LATEST_PREDICTION_SUMMARY_WIDGET_REAL_SOURCE_HANDOFF_PREFLIGHT_PANEL_VERSION",
        "HANDOFF_ITEMS",
        "build_latest_prediction_summary_widget_real_source_handoff_preflight_rows",
        "build_latest_prediction_summary_widget_real_source_handoff_preflight_packet",
        "latest_prediction_summary_widget_real_source_handoff_preflight_mount_only",
        "warroom_handoff_preflight_rows_ready",
        "real_source_handoff_preflight_only",
        "real_source_handoff_invoked",
        "actual_source_resolution_allowed",
        "actual_source_read_invoked",
        "d_hot_actual_read_allowed",
        "handoff_candidate_ready",
    ):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in ("import streamlit", "st.", "Path(", "open(", "read_text(", "read_bytes(", "write_text(", "data_read", "data_slice", "glob(", "rglob(", "render_latest_prediction_summary_widget(", "send_order(", "create_order("):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")
    page_text = _read(WARROOM_PAGE) if WARROOM_PAGE.exists() else ""
    for marker in (
        "from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel import (",
        "build_latest_prediction_summary_widget_real_source_handoff_preflight_packet",
        "def _prediction_warroom_latest_prediction_summary_real_source_handoff_preflight_display_rows(packet: dict) -> list[dict]:",
        "def _render_prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_section() -> None:",
        "with live_shell.render_folded_section(\"Prediction WarRoom latest summary real source handoff preflight\", expanded=False):",
        "_render_prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_section()",
        "latest summary real-source handoff rows={rows} / candidate_ready={ready} / real_handoff=false / actual_read=false / render=false",
        "st.dataframe(handoff_rows, width=\"stretch\", hide_index=True)",
    ):
        if marker not in page_text:
            failures.append(f"missing page marker: {marker}")
    if page_text.count("_render_prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_section(") != 2:
        failures.append("real source handoff preflight render function should have definition and page-body call only")
    for forbidden in ("build_ps_q18m_report(", "build_ps_q18j_report(", "actual_source_resolution_allowed=True", "actual_source_read_invoked=True", "source_discovery_allowed=True", "d_hot_actual_read_allowed=True", "send_order(", "create_order("):
        if forbidden in page_text:
            failures.append(f"forbidden page token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        'CHECKER = "ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.v1"',
        'REAL_SOURCE_HANDOFF_PREFLIGHT_MOUNT_VERSION = "latest_prediction_summary_widget_real_source_handoff_preflight_mount.v1"',
        "build_ps_q18m_report",
        "build_latest_prediction_summary_widget_real_source_handoff_preflight_packet",
        "latest_prediction_summary_widget_real_source_handoff_preflight_mount_only",
        "actual_source_resolution_allowed",
        "actual_source_read_invoked",
        "PS-Q18O explicit one-source handoff design checkpoint",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.v1":
        failures.append("checker version mismatch")
    if REAL_SOURCE_HANDOFF_PREFLIGHT_MOUNT_VERSION != "latest_prediction_summary_widget_real_source_handoff_preflight_mount.v1":
        failures.append("mount version mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture handoff preflight should be ok: {report}")
    if report.get("source_q18m_report_valid") is not True:
        failures.append("source Q18M report should validate")
    if report.get("handoff_packet_valid") is not True:
        failures.append("handoff packet should validate")
    if report.get("page_handoff_packet_valid") is not True:
        failures.append("page handoff packet should validate")
    if report.get("handoff_row_count") != 6:
        failures.append("expected 6 observed handoff rows")
    if report.get("page_handoff_row_count") != 6:
        failures.append("expected 6 page-safe handoff rows")
    if report.get("handoff_candidate_ready") is not True:
        failures.append("observed handoff candidate should be ready")
    if report.get("page_handoff_candidate_ready") is not False:
        failures.append("page-safe handoff candidate should not be ready")
    for key, value in {"candidate_generated_at": "2026-06-22T00:00:00Z", "candidate_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json", "candidate_market_uid": "BTC-USD"}.items():
        if report.get(key) != value:
            failures.append(f"candidate mismatch: {key}")
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_real_source_handoff_preflight_mount_only", "warroom_handoff_preflight_rows_ready", "real_source_handoff_preflight_only", "warroom_page_mutation_allowed"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in ("real_source_handoff_invoked", "actual_source_resolution_allowed", "actual_source_resolved", "actual_source_read_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18m_validation_invoked_by_mount", "q18j_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.v1",
        "real_source_handoff_preflight_mount_version=latest_prediction_summary_widget_real_source_handoff_preflight_mount.v1",
        "panel_version=prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel.ps_q18n.v1",
        "source_q18m_checker=check_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount.v1",
        "handoff_row_count=6",
        "page_handoff_row_count=6",
        "handoff_candidate_ready=true",
        "page_handoff_candidate_ready=false",
        "actual_source_resolution_allowed=false",
        "actual_source_read_invoked=false",
        "d_hot_actual_read_allowed=false",
        "no_source_artifact_resolution",
        "no_actual_source_read",
        "PS-Q18O: Explicit one-source handoff design checkpoint",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
