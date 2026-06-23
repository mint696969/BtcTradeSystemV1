# path: ./tools/test_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel_guard.py
# desc: Focused guard for PS-Q17W WarRoom prediction widget disabled section review panel.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel import CHECKER_VERSION, DISABLED_SECTION_REVIEW_PANEL_VERSION, WIDGET_FAMILY_ORDER, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_widgets_disabled_section_review_panel.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17W_WARROOM_PREDICTION_WIDGET_DISABLED_SECTION_REVIEW_PANEL_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_widgets_disabled_section_review_panel.py",
    "tools/check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.py",
    "tools/test_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17W_WARROOM_PREDICTION_WIDGET_DISABLED_SECTION_REVIEW_PANEL_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17w_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def main_guard() -> int:
    failures: list[str] = []
    for path in (COMPONENT, TOOL, UNIT, DOC):
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
        "PREDICTION_WARROOM_DISABLED_SECTION_REVIEW_PANEL_VERSION",
        "build_prediction_widget_disabled_section_review_rows",
        "build_prediction_widget_disabled_section_zone_rows",
        "build_prediction_warroom_prediction_widgets_disabled_section_review_packet",
        "disabled_section_review_packet_ready_render_still_disabled",
        "streamlit_render_allowed",
        "actual_source_read_allowed",
    ):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in (
        "import streamlit",
        "st.",
        "Path(",
        "read_text(",
        "write_text(",
        "open(",
        "data_read",
        "data_slice",
        "allow_actual_read=True",
        "append_decision(",
        "append_command(",
        "send_order(",
        "create_order(",
    ):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        'CHECKER = "ps_q17w_warroom_prediction_widget_disabled_section_review_panel"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.v1"',
        'DISABLED_SECTION_REVIEW_PANEL_VERSION = "warroom_prediction_widget_disabled_section_review_panel.v1"',
        "PANEL_MODULE",
        "review_row_count",
        "review_zone_count",
        "page_body_call_enabled",
        "future_section_call_enabled",
        "streamlit_render_allowed",
        "PS-Q17X WarRoom prediction widget disabled section page-body review mount",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    for forbidden in (
        "from pathlib import Path",
        "write_text(",
        "write_bytes(",
        "mkdir(",
        "unlink(",
        "replace(",
        "data_read",
        "data_slice",
        "allow_actual_read=True",
        "build_report(hot_root=",
        "append_decision(",
        "append_command(",
        "send_order(",
        "create_order(",
    ):
        if forbidden in tool_text:
            failures.append(f"forbidden tool token: {forbidden}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.v1":
        failures.append("checker version mismatch")
    if DISABLED_SECTION_REVIEW_PANEL_VERSION != "warroom_prediction_widget_disabled_section_review_panel.v1":
        failures.append("panel version mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture review should be ok: {report}")
    if report.get("use_observed_fixture") is not True:
        failures.append("observed fixture flag should be true")
    if report.get("review_row_count") != 12:
        failures.append("expected 12 review rows")
    if report.get("review_zone_count") != 3:
        failures.append("expected 3 review zones")
    if report.get("panel_validation_failures"):
        failures.append(f"panel validation failures: {report.get('panel_validation_failures')}")
    packet = report.get("panel_packet", {})
    if [row.get("widget_family_id") for row in packet.get("review_rows", [])] != list(WIDGET_FAMILY_ORDER):
        failures.append("review row order mismatch")
    for key in (
        "warroom_page_mutation_allowed",
        "page_body_call_enabled",
        "future_section_call_enabled",
        "streamlit_render_allowed",
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
        "checker=check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.v1",
        "disabled_section_review_panel_version=warroom_prediction_widget_disabled_section_review_panel.v1",
        "review_row_count=12",
        "review_zone_count=3",
        "disabled_section_review_only=true",
        "pure_data_review_packet=true",
        "page_body_call_enabled=false",
        "future_section_call_enabled=false",
        "streamlit_render_allowed=false",
        "no_warroom_page_body_call",
        "PS-Q17X: WarRoom prediction widget disabled section page-body review mount",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "page_body_call_enabled=true",
        "future_section_call_enabled=true",
        "streamlit_render_allowed=true",
        "warroom_widget_rendering_allowed=true",
        "d_hot_actual_read_allowed=true",
        "actual_source_read_allowed=true",
        "confidence_increase_allowed=true",
        "parameter_apply_allowed=true",
        "parameter_staging_write_allowed=true",
        "ledger_append_allowed=true",
        "autotrade_trigger_allowed=true",
        "broker_private_api_allowed=true",
        "warroom_ui_trigger_enabled=true",
        "refresh_invocation_allowed=true",
        "scheduler_enabled=true",
    ):
        if forbidden in doc_text:
            failures.append(f"forbidden doc marker present: {forbidden}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q17w_warroom_prediction_widget_disabled_section_review_panel_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17w_warroom_prediction_widget_disabled_section_review_panel_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
