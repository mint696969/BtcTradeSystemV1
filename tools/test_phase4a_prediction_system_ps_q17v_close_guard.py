# path: ./tools/test_phase4a_prediction_system_ps_q17v_close_guard.py
# desc: Close guard for PS-Q17V WarRoom prediction widget page import/mount patch.

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
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch_guard.py"
CLOSE_REL = "tools/test_phase4a_prediction_system_ps_q17v_close_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "tools/check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.py",
    "tools/test_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17V_WARROOM_PREDICTION_WIDGET_PAGE_IMPORT_MOUNT_PATCH_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17v_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in (
        "read_only",
        "non_executing",
        "warroom_page_patch_applied",
        "warroom_page_import_patch_applied",
        "disabled_section_defined_only",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
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
        "signal_reliability_claim_allowed",
        "parameter_candidate_reliability_claim_allowed",
        "parameter_tuning_allowed",
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
            failures.append(f"{key} must stay false")


def main_guard() -> int:
    failures: list[str] = []
    for path in (WARROOM_PAGE, TOOL, UNIT, DOC, REPO_ROOT / FOCUSED_GUARD):
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
    if page_text.count("_build_prediction_warroom_prediction_widgets_skeleton_packets(") != 2:
        failures.append("packet builder should have definition and disabled-section call only")
    if "with live_shell.render_folded_section(\"Prediction WarRoom real payload review\", expanded=True):" not in page_text:
        failures.append("real payload review section anchor missing")
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
            failures.append(f"forbidden page token: {forbidden}")

    tool_text = _read(TOOL) if TOOL.exists() else ""
    unit_text = _read(UNIT) if UNIT.exists() else ""
    focused_text = _read(REPO_ROOT / FOCUSED_GUARD) if (REPO_ROOT / FOCUSED_GUARD).exists() else ""
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        'CHECKER = "ps_q17v_warroom_prediction_widget_page_import_mount_patch"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.v1"',
        'PAGE_IMPORT_MOUNT_PATCH_VERSION = "warroom_prediction_widget_page_import_mount_patch.v1"',
        "warroom_page_import_patch_applied",
        "disabled_section_defined_only",
        "page_body_call_enabled",
        "future_section_call_enabled",
        "streamlit_render_allowed",
        "PS-Q17W WarRoom prediction widget disabled section review panel",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if "test_ps_q17v_validates_page_imports_and_disabled_section_from_q17u_fixture" not in unit_text:
        failures.append("unit test must cover page imports and disabled section")
    if "test_ps_q17v_keeps_page_body_call_and_rendering_disabled" not in unit_text:
        failures.append("unit test must cover disabled page body/rendering")
    if CLOSE_REL not in focused_text:
        failures.append("focused guard expected dirty set must include close guard")

    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.v1":
        failures.append("checker version mismatch")
    if PAGE_IMPORT_MOUNT_PATCH_VERSION != "warroom_prediction_widget_page_import_mount_patch.v1":
        failures.append("patch version mismatch")
    if len(WIDGET_FAMILY_ORDER) != 12:
        failures.append("widget family order should have 12 entries")

    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture patch should be ok: {report}")
    if report.get("stage") != "warroom_prediction_widget_page_import_mount_patch_imports_and_disabled_section_before_render_enablement":
        failures.append("stage mismatch")
    if report.get("source_q17u_report_valid") is not True:
        failures.append("source Q17U report should validate")
    if report.get("imported_widget_count") != 12:
        failures.append("expected 12 imported widgets")
    if report.get("imported_widget_family_ids") != list(WIDGET_FAMILY_ORDER):
        failures.append("imported widget family order mismatch")
    if report.get("disabled_section_defined") is not True:
        failures.append("disabled section should be defined")
    if report.get("disabled_section_call_count") != 1:
        failures.append("disabled section should only have definition occurrence")
    if report.get("packet_builder_call_count") != 2:
        failures.append("packet builder should have definition and disabled-section call only")
    if report.get("page_validation_failures"):
        failures.append(f"page validation failures: {report.get('page_validation_failures')}")
    if report.get("recommended_first_validation") != "latest_prediction_summary_widget_page_import_mount_patch_guard":
        failures.append("recommended first validation mismatch")
    _assert_false_boundaries(report, failures)

    blocked = build_report(page_text="")
    if blocked.get("ok") is not False:
        failures.append("missing Q17U source should block")
    if blocked.get("imported_widget_count") != 0:
        failures.append("blocked report should not import widgets")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")

    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.v1",
        "page_import_mount_patch_version=warroom_prediction_widget_page_import_mount_patch.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight.v1",
        "imported_widget_count=12",
        "disabled_section_defined=true",
        "disabled_section_call_count=1",
        "packet_builder_call_count=2",
        "warroom_page_patch_applied=true",
        "warroom_page_import_patch_applied=true",
        "disabled_section_defined_only=true",
        "page_body_call_enabled=false",
        "future_section_call_enabled=false",
        "streamlit_render_allowed=false",
        "no_visible_widget_rendering",
        "PS-Q17W: WarRoom prediction widget disabled section review panel",
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
    missing_dirty = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing_dirty:
        failures.append(f"missing expected dirty paths: {sorted(missing_dirty)}")
    result = {
        "ok": not failures,
        "guard": "ps_q17v_close_guard",
        "phase": "phase3_warroom_prediction_widget_page_import_mount_patch_closed_before_render_enablement",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17v_closed": not failures,
            "warroom_page_patch_applied": True,
            "warroom_page_import_patch_applied": True,
            "disabled_section_defined_only": True,
            "page_body_call_enabled": False,
            "future_section_call_enabled": False,
            "streamlit_render_allowed": False,
            "actual_source_read_allowed": False,
            "refresh_invocation_allowed": False,
            "no_d_hot_actual_read": True,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_parameter_apply": True,
            "no_parameter_staging_write": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
            "next_slice": "PS-Q17W WarRoom prediction widget disabled section review panel or actual-source preflight",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17v_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
