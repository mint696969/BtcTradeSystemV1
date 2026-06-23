# path: ./tools/test_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch_guard.py
# desc: Focused guard for PS-Q17V WarRoom prediction widget page import/mount patch.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch import CHECKER_VERSION, PAGE_IMPORT_MOUNT_PATCH_VERSION, WARROOM_PAGE_TARGET, WIDGET_FAMILY_ORDER, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
WARROOM_PAGE = REPO_ROOT / WARROOM_PAGE_TARGET
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17V_WARROOM_PREDICTION_WIDGET_PAGE_IMPORT_MOUNT_PATCH_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "tools/check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.py",
    "tools/test_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17V_WARROOM_PREDICTION_WIDGET_PAGE_IMPORT_MOUNT_PATCH_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17v_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch_guard.py",
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
    for widget_id in WIDGET_FAMILY_ORDER:
        if f"prediction_widgets.{widget_id} import (" not in page_text:
            failures.append(f"missing widget import: {widget_id}")
        if f"render_{widget_id}(props=None)" not in page_text:
            failures.append(f"missing disabled packet call: {widget_id}")
    if "def _build_prediction_warroom_prediction_widgets_skeleton_packets() -> list[dict]:" not in page_text:
        failures.append("packet builder missing")
    if "def _render_prediction_warroom_prediction_widgets_skeleton_section() -> list[dict]:" not in page_text:
        failures.append("disabled section missing")
    if page_text.count("_render_prediction_warroom_prediction_widgets_skeleton_section(") != 1:
        failures.append("disabled section must be defined but not called by page body")
    for forbidden in (
        "st.dataframe(_build_prediction_warroom_prediction_widgets_skeleton_packets",
        "st.json(_build_prediction_warroom_prediction_widgets_skeleton_packets",
        "st.write(_build_prediction_warroom_prediction_widgets_skeleton_packets",
        "allow_actual_read=True",
        "append_decision(",
        "append_command(",
        "send_order(",
        "create_order(",
    ):
        if forbidden in page_text:
            failures.append(f"forbidden page token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        'CHECKER = "ps_q17v_warroom_prediction_widget_page_import_mount_patch"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.v1"',
        'PAGE_IMPORT_MOUNT_PATCH_VERSION = "warroom_prediction_widget_page_import_mount_patch.v1"',
        "warroom_page_import_patch_applied",
        "disabled_section_defined_only",
        "page_body_call_enabled",
        "streamlit_render_allowed",
        "PS-Q17W WarRoom prediction widget disabled section review panel",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.v1":
        failures.append("checker version mismatch")
    if PAGE_IMPORT_MOUNT_PATCH_VERSION != "warroom_prediction_widget_page_import_mount_patch.v1":
        failures.append("patch version mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture patch should be ok: {report}")
    if report.get("imported_widget_count") != 12:
        failures.append("expected 12 imported widgets")
    if report.get("disabled_section_call_count") != 1:
        failures.append("disabled section should only have definition occurrence")
    if report.get("packet_builder_call_count") != 2:
        failures.append("packet builder should have definition and disabled-section call only")
    for key in (
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
        "checker=check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.v1",
        "page_import_mount_patch_version=warroom_prediction_widget_page_import_mount_patch.v1",
        "imported_widget_count=12",
        "disabled_section_defined=true",
        "page_body_call_enabled=false",
        "future_section_call_enabled=false",
        "streamlit_render_allowed=false",
        "no_visible_widget_rendering",
        "PS-Q17W: WarRoom prediction widget disabled section review panel",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q17v_warroom_prediction_widget_page_import_mount_patch_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17v_warroom_prediction_widget_page_import_mount_patch_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
