# path: ./tools/test_phase4a_prediction_system_ps_q17w_close_guard.py
# desc: Close guard for PS-Q17W WarRoom prediction widget disabled section review panel.

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
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel_guard.py"
CLOSE_REL = "tools/test_phase4a_prediction_system_ps_q17w_close_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_widgets_disabled_section_review_panel.py",
    "tools/check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.py",
    "tools/test_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17W_WARROOM_PREDICTION_WIDGET_DISABLED_SECTION_REVIEW_PANEL_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17w_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in ("read_only", "non_executing", "disabled_section_review_only", "pure_data_review_packet"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "warroom_page_mutation_allowed",
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
    for path in (COMPONENT, TOOL, UNIT, DOC, REPO_ROOT / FOCUSED_GUARD):
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
        "disabled_section_review_row_ready_render_still_disabled",
        "disabled_section_zone_review_ready_render_still_disabled",
        "streamlit_render_allowed",
        "actual_source_read_allowed",
        "refresh_invocation_allowed",
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
    unit_text = _read(UNIT) if UNIT.exists() else ""
    focused_text = _read(REPO_ROOT / FOCUSED_GUARD) if (REPO_ROOT / FOCUSED_GUARD).exists() else ""
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        'CHECKER = "ps_q17w_warroom_prediction_widget_disabled_section_review_panel"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.v1"',
        'DISABLED_SECTION_REVIEW_PANEL_VERSION = "warroom_prediction_widget_disabled_section_review_panel.v1"',
        '"use_observed_fixture": bool(use_observed_fixture)',
        "PANEL_MODULE",
        "review_row_count",
        "review_zone_count",
        "panel_validation_failures",
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
    if "test_ps_q17w_builds_disabled_section_review_packet_from_q17s_and_q17v_fixtures" not in unit_text:
        failures.append("unit test must cover Q17S/Q17V fixtures")
    if "test_ps_q17w_review_rows_keep_render_source_refresh_and_write_disabled" not in unit_text:
        failures.append("unit test must cover disabled row boundaries")
    if CLOSE_REL not in focused_text:
        failures.append("focused guard expected dirty set must include close guard")

    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.v1":
        failures.append("checker version mismatch")
    if DISABLED_SECTION_REVIEW_PANEL_VERSION != "warroom_prediction_widget_disabled_section_review_panel.v1":
        failures.append("panel version mismatch")
    if len(WIDGET_FAMILY_ORDER) != 12:
        failures.append("widget family order should have 12 entries")

    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture review should be ok: {report}")
    if report.get("use_observed_fixture") is not True:
        failures.append("observed fixture flag should be true")
    if report.get("source_q17s_report_valid") is not True:
        failures.append("source Q17S report should validate")
    if report.get("source_q17v_report_valid") is not True:
        failures.append("source Q17V report should validate")
    if report.get("review_row_count") != 12:
        failures.append("expected 12 review rows")
    if report.get("review_zone_count") != 3:
        failures.append("expected 3 review zones")
    if report.get("panel_validation_failures"):
        failures.append(f"panel validation failures: {report.get('panel_validation_failures')}")
    if report.get("recommended_first_validation") != "latest_prediction_summary_widget_disabled_section_review_panel_guard":
        failures.append("recommended first validation mismatch")
    packet = report.get("panel_packet", {})
    if packet.get("ok") is not True:
        failures.append("panel packet should be ok")
    if packet.get("review_row_count") != 12:
        failures.append("panel packet should have 12 review rows")
    if packet.get("review_zone_count") != 3:
        failures.append("panel packet should have 3 zone rows")
    if [row.get("widget_family_id") for row in packet.get("review_rows", [])] != list(WIDGET_FAMILY_ORDER):
        failures.append("review row order mismatch")
    for row in packet.get("review_rows", []):
        widget_id = row.get("widget_family_id")
        for key in ("read_only", "non_executing", "component_skeleton_only", "fallback_component_only", "display_packet_only"):
            if row.get(key) is not True:
                failures.append(f"row true boundary missing: {widget_id}:{key}")
        for key in (
            "streamlit_render_allowed",
            "actual_source_read_allowed",
            "refresh_invocation_allowed",
            "runtime_artifact_write_allowed",
            "status_artifact_write_allowed",
            "parameter_apply_allowed",
            "parameter_staging_write_allowed",
            "ledger_append_allowed",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
        ):
            if row.get(key) is not False:
                failures.append(f"row false boundary not false: {widget_id}:{key}")
    for zone in packet.get("zone_rows", []):
        if zone.get("all_render_disabled") is not True:
            failures.append(f"zone render should be disabled: {zone.get('mount_zone_id')}")
        if zone.get("all_actual_source_read_disabled") is not True:
            failures.append(f"zone actual read should be disabled: {zone.get('mount_zone_id')}")
    _assert_false_boundaries(report, failures)

    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing sources should block")
    if blocked.get("panel_packet") != {}:
        failures.append("blocked report should not emit panel packet")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")

    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17w_warroom_prediction_widget_disabled_section_review_panel.v1",
        "disabled_section_review_panel_version=warroom_prediction_widget_disabled_section_review_panel.v1",
        "source_q17s_checker=check_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation.v1",
        "source_q17v_checker=check_phase4a_prediction_system_ps_q17v_warroom_prediction_widget_page_import_mount_patch.v1",
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
    missing_dirty = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing_dirty:
        failures.append(f"missing expected dirty paths: {sorted(missing_dirty)}")
    result = {
        "ok": not failures,
        "guard": "ps_q17w_close_guard",
        "phase": "phase3_warroom_prediction_widget_disabled_section_review_panel_closed_before_page_body_call_and_visible_rendering",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17w_closed": not failures,
            "disabled_section_review_only": True,
            "pure_data_review_packet": True,
            "review_row_count": int(report.get("review_row_count") or 0),
            "review_zone_count": int(report.get("review_zone_count") or 0),
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
            "next_slice": "PS-Q17X WarRoom prediction widget disabled section page-body review mount or actual-source preflight",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17w_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
