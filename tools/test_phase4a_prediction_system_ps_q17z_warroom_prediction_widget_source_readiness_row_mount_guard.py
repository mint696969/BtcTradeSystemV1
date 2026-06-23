# path: ./tools/test_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount_guard.py
# desc: Focused guard for PS-Q17Z WarRoom prediction widget source readiness row mount.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount import CHECKER_VERSION, SOURCE_READINESS_ROW_MOUNT_VERSION, WARROOM_PAGE_TARGET, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
WARROOM_PAGE = REPO_ROOT / WARROOM_PAGE_TARGET
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_widget_source_readiness_preflight_panel.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17Z_WARROOM_PREDICTION_WIDGET_SOURCE_READINESS_ROW_MOUNT_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_widget_source_readiness_preflight_panel.py",
    "tools/check_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount.py",
    "tools/test_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17Z_WARROOM_PREDICTION_WIDGET_SOURCE_READINESS_ROW_MOUNT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17z_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount_guard.py",
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
        "PREDICTION_WARROOM_SOURCE_READINESS_PREFLIGHT_PANEL_VERSION",
        "build_prediction_warroom_prediction_widget_source_readiness_rows",
        "build_prediction_warroom_prediction_widget_source_readiness_preflight_packet",
        "readiness_row_visible_in_warroom",
        "source_artifact_resolution_allowed",
        "actual_source_read_allowed",
        "d_hot_actual_read_allowed",
        "source_binding_ready_actual_read_deferred",
    ):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in (
        "import streamlit",
        "st.",
        "Path(",
        "open(",
        "read_text(",
        "write_text(",
        "data_read",
        "data_slice",
        "allow_actual_read=True",
        "send_order(",
        "create_order(",
    ):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")
    page_text = _read(WARROOM_PAGE) if WARROOM_PAGE.exists() else ""
    for marker in (
        "from btcts.apps.operator_ui.components.prediction_warroom_prediction_widget_source_readiness_preflight_panel import (",
        "build_prediction_warroom_prediction_widget_source_readiness_preflight_packet",
        "def _prediction_warroom_source_readiness_display_rows(packet: dict) -> list[dict]:",
        "def _render_prediction_warroom_prediction_widget_source_readiness_preflight_section() -> None:",
        "with live_shell.render_folded_section(\"Prediction WarRoom source readiness preflight\", expanded=False):",
        "_render_prediction_warroom_prediction_widget_source_readiness_preflight_section()",
        "source readiness rows={rows} / source packets={packets} / actual_source_read=false / d_hot_read=false / render=false",
        "st.dataframe(readiness_rows, width=\"stretch\", hide_index=True)",
    ):
        if marker not in page_text:
            failures.append(f"missing page marker: {marker}")
    if page_text.count("_render_prediction_warroom_prediction_widget_source_readiness_preflight_section(") != 2:
        failures.append("source readiness render function should have definition and page-body call only")
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
            failures.append(f"forbidden page token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        'CHECKER = "ps_q17z_warroom_prediction_widget_source_readiness_row_mount"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount.v1"',
        'SOURCE_READINESS_ROW_MOUNT_VERSION = "warroom_prediction_widget_source_readiness_row_mount.v1"',
        "build_ps_q17y_report",
        "build_prediction_warroom_prediction_widget_source_readiness_preflight_packet",
        "source_readiness_row_mount_only",
        "readiness_row_visible_in_warroom",
        "source_artifact_resolution_allowed",
        "actual_source_read_allowed",
        "PS-Q18A WarRoom prediction widget source artifact resolution preflight",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount.v1":
        failures.append("checker version mismatch")
    if SOURCE_READINESS_ROW_MOUNT_VERSION != "warroom_prediction_widget_source_readiness_row_mount.v1":
        failures.append("mount version mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture row mount should be ok: {report}")
    if report.get("readiness_row_count") != 12:
        failures.append("expected 12 readiness rows")
    if report.get("unique_source_packet_count") != 9:
        failures.append("expected 9 unique source packets")
    for key in ("source_readiness_row_mount_only", "source_binding_contract_ready", "readiness_row_visible_in_warroom", "streamlit_review_render_allowed"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "source_artifact_resolution_allowed",
        "actual_source_bound",
        "source_artifact_resolved",
        "freshness_checked_against_d_hot",
        "real_prediction_widget_rendering_allowed",
        "warroom_widget_rendering_allowed",
        "actual_source_read_allowed",
        "d_hot_actual_read_allowed",
        "refresh_invocation_allowed",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
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
        "checker=check_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount.v1",
        "source_readiness_row_mount_version=warroom_prediction_widget_source_readiness_row_mount.v1",
        "source_q17y_checker=check_phase4a_prediction_system_ps_q17y_warroom_prediction_widget_actual_source_preflight.v1",
        "panel_version=prediction_warroom_prediction_widget_source_readiness_preflight_panel.ps_q17z.v1",
        "readiness_row_count=12",
        "unique_source_packet_count=9",
        "source_readiness_row_mount_only=true",
        "readiness_row_visible_in_warroom=true",
        "source_artifact_resolution_allowed=false",
        "actual_source_read_allowed=false",
        "d_hot_actual_read_allowed=false",
        "no_actual_source_read",
        "PS-Q18A: WarRoom prediction widget source artifact resolution preflight",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "source_artifact_resolution_allowed=true",
        "actual_source_read_allowed=true",
        "d_hot_actual_read_allowed=true",
        "freshness_checked_against_d_hot=true",
        "real_prediction_widget_rendering_allowed=true",
        "confidence_increase_allowed=true",
        "parameter_apply_allowed=true",
        "parameter_staging_write_allowed=true",
        "ledger_append_allowed=true",
        "autotrade_trigger_allowed=true",
        "broker_private_api_allowed=true",
        "refresh_invocation_allowed=true",
        "scheduler_enabled=true",
    ):
        if forbidden in doc_text:
            failures.append(f"forbidden doc marker present: {forbidden}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q17z_warroom_prediction_widget_source_readiness_row_mount_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17z_warroom_prediction_widget_source_readiness_row_mount_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
