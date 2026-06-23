# path: ./tools/test_phase4a_prediction_system_ps_q17x_close_guard.py
# desc: Close guard for PS-Q17X WarRoom prediction widget disabled section page-body review mount.

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
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount_guard.py"
CLOSE_REL = "tools/test_phase4a_prediction_system_ps_q17x_close_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "tools/check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.py",
    "tools/test_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17X_WARROOM_PREDICTION_WIDGET_DISABLED_SECTION_PAGE_BODY_REVIEW_MOUNT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17x_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_boundary(report: dict, failures: list[str]) -> None:
    for key in (
        "read_only",
        "non_executing",
        "page_body_review_mount_applied",
        "disabled_section_page_body_review_mount_enabled",
        "visible_review_rows_rendered",
        "streamlit_review_render_allowed",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "real_prediction_widget_rendering_allowed",
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
    for marker in (
        "from btcts.apps.operator_ui.components.prediction_warroom_prediction_widgets_disabled_section_review_panel import (",
        "build_prediction_warroom_prediction_widgets_disabled_section_review_packet",
        "def _prediction_warroom_disabled_widget_review_zone_display_rows(packet: dict) -> list[dict]:",
        "def _prediction_warroom_disabled_widget_review_display_rows(packet: dict) -> list[dict]:",
        "def _render_prediction_warroom_prediction_widgets_disabled_section_review_mount() -> None:",
        "with live_shell.render_folded_section(\"Prediction WarRoom disabled widget skeleton review\", expanded=False):",
        "_render_prediction_warroom_prediction_widgets_disabled_section_review_mount()",
        "st.dataframe(zone_rows, width=\"stretch\", hide_index=True)",
        "st.dataframe(review_rows, width=\"stretch\", hide_index=True)",
        "widget_render=false / actual_source_read=false",
        "render_latest_prediction_summary_widget(props=None)",
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
    unit_text = _read(UNIT) if UNIT.exists() else ""
    focused_text = _read(REPO_ROOT / FOCUSED_GUARD) if (REPO_ROOT / FOCUSED_GUARD).exists() else ""
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        'CHECKER = "ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.v1"',
        'PAGE_BODY_REVIEW_MOUNT_VERSION = "warroom_prediction_widget_disabled_section_page_body_review_mount.v1"',
        "stable_pre_q17x_page_patch_source_boundary",
        "source_q17v_fixture_mode",
        "visible_review_rows_rendered",
        "streamlit_review_render_allowed",
        "real_prediction_widget_rendering_allowed",
        "actual_source_read_allowed",
        "PS-Q17Y WarRoom prediction widget actual-source preflight",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if "test_ps_q17x_validates_page_body_review_mount_from_q17w_fixture" not in unit_text:
        failures.append("unit test must cover page body review mount")
    if "test_ps_q17x_keeps_real_widget_render_source_refresh_and_writes_disabled" not in unit_text:
        failures.append("unit test must cover disabled real widget/source/refresh/write boundaries")
    if CLOSE_REL not in focused_text:
        failures.append("focused guard expected dirty set must include close guard")

    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.v1":
        failures.append("checker version mismatch")
    if PAGE_BODY_REVIEW_MOUNT_VERSION != "warroom_prediction_widget_disabled_section_page_body_review_mount.v1":
        failures.append("mount version mismatch")

    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture review mount should be ok: {report}")
    if report.get("use_observed_fixture") is not True:
        failures.append("observed fixture flag should be true")
    if report.get("source_q17v_fixture_mode") != "stable_pre_q17x_page_patch_source_boundary":
        failures.append("source Q17V fixture mode mismatch")
    if report.get("source_q17w_report_valid") is not True:
        failures.append("source Q17W report should validate")
    if report.get("page_validation_failures"):
        failures.append(f"page validation failures: {report.get('page_validation_failures')}")
    if report.get("review_row_count") != 12:
        failures.append("expected 12 review rows")
    if report.get("review_zone_count") != 3:
        failures.append("expected 3 review zones")
    if report.get("recommended_first_validation") != "latest_prediction_summary_widget_page_body_review_mount_guard":
        failures.append("recommended first validation mismatch")
    if report.get("review_folded_section_title") != "Prediction WarRoom disabled widget skeleton review":
        failures.append("review folded section title mismatch")
    _assert_boundary(report, failures)

    blocked = build_report(page_text="")
    if blocked.get("ok") is not False:
        failures.append("missing source should block")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")

    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17x_warroom_prediction_widget_disabled_section_page_body_review_mount.v1",
        "page_body_review_mount_version=warroom_prediction_widget_disabled_section_page_body_review_mount.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.v1",
        "source_q17v_fixture_mode=stable_pre_q17x_page_patch_source_boundary",
        "review_folded_section_title=Prediction WarRoom disabled widget skeleton review",
        "review_row_count=12",
        "review_zone_count=3",
        "page_body_review_mount_applied=true",
        "disabled_section_page_body_review_mount_enabled=true",
        "visible_review_rows_rendered=true",
        "streamlit_review_render_allowed=true",
        "real_prediction_widget_rendering_allowed=false",
        "warroom_widget_rendering_allowed=false",
        "actual_source_read_allowed=false",
        "d_hot_actual_read_allowed=false",
        "refresh_invocation_allowed=false",
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
    missing_dirty = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing_dirty:
        failures.append(f"missing expected dirty paths: {sorted(missing_dirty)}")
    result = {
        "ok": not failures,
        "guard": "ps_q17x_close_guard",
        "phase": "phase3_warroom_prediction_widget_disabled_section_page_body_review_mount_closed_before_real_widget_rendering_and_actual_source_read",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17x_closed": not failures,
            "page_body_review_mount_applied": True,
            "disabled_section_page_body_review_mount_enabled": True,
            "visible_review_rows_rendered": True,
            "streamlit_review_render_allowed": True,
            "real_prediction_widget_rendering_allowed": False,
            "actual_source_read_allowed": False,
            "d_hot_actual_read_allowed": False,
            "refresh_invocation_allowed": False,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_parameter_apply": True,
            "no_parameter_staging_write": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
            "review_row_count": int(report.get("review_row_count") or 0),
            "review_zone_count": int(report.get("review_zone_count") or 0),
            "next_slice": "PS-Q17Y WarRoom prediction widget actual-source preflight or visible disabled-widget review refinement",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17x_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
