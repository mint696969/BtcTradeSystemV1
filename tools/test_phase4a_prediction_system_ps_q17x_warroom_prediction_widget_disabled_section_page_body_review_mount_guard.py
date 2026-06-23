# path: ./tools/test_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount_guard.py
# desc: Focused guard for PS-Q17X WarRoom prediction widget disabled section page-body review mount.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount import CHECKER_VERSION, PAGE_BODY_REVIEW_MOUNT_VERSION, WARROOM_PAGE_TARGET, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
WARROOM_PAGE = REPO_ROOT / WARROOM_PAGE_TARGET
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17X_WARROOM_PREDICTION_WIDGET_DISABLED_SECTION_PAGE_BODY_REVIEW_MOUNT_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "tools/check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.py",
    "tools/test_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17X_WARROOM_PREDICTION_WIDGET_DISABLED_SECTION_PAGE_BODY_REVIEW_MOUNT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17x_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def main_guard() -> int:
    failures: list[str] = []
    for path in (WARROOM_PAGE, TOOL, UNIT, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    page_text = _read(WARROOM_PAGE) if WARROOM_PAGE.exists() else ""
    for marker in (
        "from btcts.apps.operator_ui.components.prediction_warroom_prediction_widgets_disabled_section_review_panel import (",
        "build_prediction_warroom_prediction_widgets_disabled_section_review_packet",
        "def _render_prediction_warroom_prediction_widgets_disabled_section_review_mount() -> None:",
        "def _prediction_warroom_disabled_widget_review_zone_display_rows(packet: dict) -> list[dict]:",
        "def _prediction_warroom_disabled_widget_review_display_rows(packet: dict) -> list[dict]:",
        "with live_shell.render_folded_section(\"Prediction WarRoom disabled widget skeleton review\", expanded=False):",
        "_render_prediction_warroom_prediction_widgets_disabled_section_review_mount()",
        "st.dataframe(zone_rows, width=\"stretch\", hide_index=True)",
        "st.dataframe(review_rows, width=\"stretch\", hide_index=True)",
        "widget_render=false / actual_source_read=false",
    ):
        if marker not in page_text:
            failures.append(f"missing page marker: {marker}")
    if page_text.count("_render_prediction_warroom_prediction_widgets_disabled_section_review_mount(") != 2:
        failures.append("review mount should have definition and page-body call only")
    if page_text.count("_render_prediction_warroom_prediction_widgets_skeleton_section(") != 2:
        failures.append("disabled section should have definition and review-mount call only")
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
            failures.append(f"forbidden page token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        'CHECKER = "ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.v1"',
        'PAGE_BODY_REVIEW_MOUNT_VERSION = "warroom_prediction_widget_disabled_section_page_body_review_mount.v1"',
        "visible_review_rows_rendered",
        "streamlit_review_render_allowed",
        "real_prediction_widget_rendering_allowed",
        "actual_source_read_allowed",
        "PS-Q17Y WarRoom prediction widget actual-source preflight",
        "stable_pre_q17x_page_patch_source_boundary",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.v1":
        failures.append("checker version mismatch")
    if PAGE_BODY_REVIEW_MOUNT_VERSION != "warroom_prediction_widget_disabled_section_page_body_review_mount.v1":
        failures.append("mount version mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture review mount should be ok: {report}")
    if report.get("use_observed_fixture") is not True:
        failures.append("observed fixture flag should be true")
    if report.get("review_row_count") != 12:
        failures.append("expected 12 review rows")
    if report.get("review_zone_count") != 3:
        failures.append("expected 3 review zones")
    for key in ("page_body_review_mount_applied", "disabled_section_page_body_review_mount_enabled", "visible_review_rows_rendered", "streamlit_review_render_allowed"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
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
        "checker=check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.v1",
        "page_body_review_mount_version=warroom_prediction_widget_disabled_section_page_body_review_mount.v1",
        "review_row_count=12",
        "review_zone_count=3",
        "page_body_review_mount_applied=true",
        "disabled_section_page_body_review_mount_enabled=true",
        "visible_review_rows_rendered=true",
        "streamlit_review_render_allowed=true",
        "real_prediction_widget_rendering_allowed=false",
        "no_real_prediction_widget_rendering",
        "PS-Q17Y: WarRoom prediction widget actual-source preflight",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "real_prediction_widget_rendering_allowed=true",
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
    result = {"ok": not failures, "guard": "ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
