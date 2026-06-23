# path: ./tools/test_phase4a_prediction_system_ps_q17u_close_guard.py
# desc: Close guard for PS-Q17U WarRoom prediction widget page import/mount implementation preflight.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight import CHECKER_VERSION, PAGE_IMPORT_MOUNT_PREFLIGHT_VERSION, WARROOM_PAGE_TARGET, WIDGET_FAMILY_ORDER, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17U_WARROOM_PREDICTION_WIDGET_PAGE_IMPORT_MOUNT_PREFLIGHT_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight_guard.py"
CLOSE_REL = "tools/test_phase4a_prediction_system_ps_q17u_close_guard.py"
WARROOM_PAGE = REPO_ROOT / WARROOM_PAGE_TARGET
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight.py",
    "tools/test_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17U_WARROOM_PREDICTION_WIDGET_PAGE_IMPORT_MOUNT_PREFLIGHT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17u_close_guard.py",
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
        "page_import_mount_preflight_only",
        "preflight_only",
        "diagnostic_only",
        "warroom_widget_design_premise",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "warroom_page_patch_allowed",
        "warroom_page_import_patch_allowed",
        "warroom_page_mutation_allowed",
        "warroom_mount_patch_allowed",
        "component_import_allowed_by_warroom_page",
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
        "would_write_warroom_page",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
    ):
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")


def main_guard() -> int:
    failures: list[str] = []
    for path in (TOOL, UNIT, DOC, REPO_ROOT / FOCUSED_GUARD):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")

    if not WARROOM_PAGE.exists():
        failures.append("warroom_page.py target missing")
    else:
        page_text = _read(WARROOM_PAGE)
        for marker in (
            "from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_status_panel import",
            "def _render_prediction_warroom_lowered_display_packet_visibility_review_section()",
            "_render_prediction_warroom_lowered_display_packet_visibility_review_section()",
        ):
            if marker not in page_text:
                failures.append(f"warroom_page target marker missing: {marker}")
        for forbidden_marker in (
            "prediction_widgets.latest_prediction_summary_widget",
            "render_latest_prediction_summary_widget(",
            "_render_prediction_warroom_prediction_widgets_skeleton_section",
        ):
            if forbidden_marker in page_text:
                failures.append(f"PS-Q17U must not mutate warroom_page.py yet: {forbidden_marker}")

    tool_text = _read(TOOL) if TOOL.exists() else ""
    unit_text = _read(UNIT) if UNIT.exists() else ""
    focused_text = _read(REPO_ROOT / FOCUSED_GUARD) if (REPO_ROOT / FOCUSED_GUARD).exists() else ""
    doc_text = _read(DOC) if DOC.exists() else ""

    for marker in (
        'CHECKER = "ps_q17u_warroom_prediction_widget_page_import_mount_preflight"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight.v1"',
        'PAGE_IMPORT_MOUNT_PREFLIGHT_VERSION = "warroom_prediction_widget_page_import_mount_preflight.v1"',
        "FUTURE_SECTION_FUNCTION",
        "future_import_block",
        "future_section_stub",
        "future_page_body_call_block",
        "page_patch_preflight_ready",
        "would_write_warroom_page",
        "PS-Q17V WarRoom prediction widget page import/mount patch",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    for forbidden in (
        "from pathlib import Path",
        "read_text(",
        "write_text(",
        "write_bytes(",
        "open(",
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
    if "test_ps_q17u_builds_patch_fragments_from_q17t_fixture" not in unit_text:
        failures.append("unit test must cover Q17T fixture patch fragments")
    if "test_ps_q17u_invocation_rows_stay_disabled" not in unit_text:
        failures.append("unit test must cover disabled invocation rows")
    if CLOSE_REL not in focused_text:
        failures.append("focused guard expected dirty set must include close guard")

    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight.v1":
        failures.append("checker version mismatch")
    if PAGE_IMPORT_MOUNT_PREFLIGHT_VERSION != "warroom_prediction_widget_page_import_mount_preflight.v1":
        failures.append("preflight version mismatch")
    if len(WIDGET_FAMILY_ORDER) != 12:
        failures.append("widget family order should have 12 entries")

    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture preflight should be ok: {report}")
    if report.get("target_page_path") != WARROOM_PAGE_TARGET:
        failures.append("target page path mismatch")
    if report.get("stage") != "warroom_prediction_widget_page_import_mount_preflight_before_warroom_page_patch_and_rendering":
        failures.append("stage mismatch")
    if report.get("source_q17t_report_valid") is not True:
        failures.append("source Q17T report should validate")
    if report.get("future_import_line_count") != 12:
        failures.append("expected 12 future import lines")
    if report.get("future_mount_invocation_count") != 12:
        failures.append("expected 12 future mount invocations")
    if report.get("preflight_patch_fragment_count") != 3:
        failures.append("expected 3 patch fragments")
    if report.get("page_patch_preflight_ready") is not True:
        failures.append("preflight should be ready")
    if report.get("recommended_first_validation") != "latest_prediction_summary_widget_page_import_mount_preflight_guard":
        failures.append("recommended first validation mismatch")
    if not any(str(line).startswith("def _render_prediction_warroom_prediction_widgets_skeleton_section") for line in report.get("future_section_stub", [])):
        failures.append("future section stub must define the skeleton section")
    for widget_id in WIDGET_FAMILY_ORDER:
        if not any(f"render_{widget_id}" in str(line) for line in report.get("future_import_block", [])):
            failures.append(f"missing future import for {widget_id}")
    invocation_ids = [row.get("widget_family_id") for row in report.get("mount_invocation_rows", [])]
    if invocation_ids != list(WIDGET_FAMILY_ORDER):
        failures.append("mount invocation order mismatch")
    for row in report.get("mount_invocation_rows", []):
        if row.get("page_patch_preflight_only") is not True:
            failures.append(f"row must be preflight only: {row.get('widget_family_id')}")
        for key in (
            "page_import_patch_allowed",
            "page_body_call_patch_allowed",
            "warroom_mount_patch_allowed",
            "streamlit_render_allowed",
            "actual_source_read_allowed",
            "refresh_invocation_allowed",
        ):
            if row.get(key) is not False:
                failures.append(f"row boundary should stay false: {row.get('widget_family_id')}:{key}")
    _assert_false_boundaries(report, failures)

    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing Q17T source should block")
    if blocked.get("future_import_block") or blocked.get("mount_invocation_rows"):
        failures.append("blocked report must not emit patch fragments")
    if blocked.get("page_patch_preflight_ready") is not False:
        failures.append("blocked report should not be preflight-ready")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")

    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17u_warroom_prediction_widget_page_import_mount_preflight.v1",
        "page_import_mount_preflight_version=warroom_prediction_widget_page_import_mount_preflight.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract.v1",
        "target_page_path=btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
        "page_import_mount_preflight_only=true",
        "future_import_line_count=12",
        "future_mount_invocation_count=12",
        "preflight_patch_fragment_count=3",
        "page_patch_preflight_ready=true",
        "would_write_warroom_page=false",
        "no_warroom_page_import_patch",
        "no_future_section_call_enablement",
        "PS-Q17V: WarRoom prediction widget page import/mount patch",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "warroom_page_patch_allowed=true",
        "warroom_page_import_patch_allowed=true",
        "warroom_page_mutation_allowed=true",
        "warroom_mount_patch_allowed=true",
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
        "guard": "ps_q17u_close_guard",
        "phase": "phase3_warroom_prediction_widget_page_import_mount_preflight_closed_before_warroom_page_patch_and_rendering",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17u_closed": not failures,
            "page_import_mount_preflight_only": True,
            "page_patch_preflight_ready": bool(report.get("page_patch_preflight_ready")),
            "warroom_page_patch_allowed": False,
            "warroom_page_import_patch_allowed": False,
            "warroom_page_mutation_allowed": False,
            "warroom_mount_patch_allowed": False,
            "future_section_call_enabled": False,
            "streamlit_render_allowed": False,
            "actual_source_read_allowed": False,
            "refresh_invocation_allowed": False,
            "would_write_warroom_page": False,
            "no_d_hot_actual_read": True,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_parameter_apply": True,
            "no_parameter_staging_write": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
            "next_slice": "PS-Q17V WarRoom prediction widget page import/mount patch or actual-source preflight",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17u_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
