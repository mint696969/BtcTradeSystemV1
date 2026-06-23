# path: ./tools/test_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract_guard.py
# desc: Focused guard for PS-Q17T WarRoom prediction widget page mount/import contract.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract import CHECKER_VERSION, PAGE_MOUNT_IMPORT_CONTRACT_VERSION, WARROOM_PAGE_TARGET, WIDGET_FAMILY_ORDER, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17T_WARROOM_PREDICTION_WIDGET_PAGE_MOUNT_IMPORT_CONTRACT_2026-06-22.md"
WARROOM_PAGE = REPO_ROOT / WARROOM_PAGE_TARGET
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract.py",
    "tools/test_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17T_WARROOM_PREDICTION_WIDGET_PAGE_MOUNT_IMPORT_CONTRACT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17t_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in ("read_only", "non_executing", "page_mount_import_contract_only", "contract_only", "diagnostic_only", "warroom_widget_design_premise", "warroom_page_target_observed"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "warroom_page_import_patch_allowed",
        "warroom_page_mutation_allowed",
        "warroom_mount_patch_allowed",
        "component_import_allowed_by_warroom_page",
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
    for path in (TOOL, UNIT, DOC):
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
            "render_prediction_warroom_non_ui_scheduled_producer_status_panel()",
        ):
            if marker not in page_text:
                failures.append(f"warroom_page target marker missing: {marker}")
        for forbidden_marker in (
            "prediction_widgets.latest_prediction_summary_widget",
            "render_latest_prediction_summary_widget(",
            "_render_prediction_warroom_prediction_widgets_skeleton_section",
        ):
            if forbidden_marker in page_text:
                failures.append(f"PS-Q17T must not mutate warroom_page.py yet: {forbidden_marker}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        'CHECKER = "ps_q17t_warroom_prediction_widget_page_mount_import_contract"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract.v1"',
        'PAGE_MOUNT_IMPORT_CONTRACT_VERSION = "warroom_prediction_widget_page_mount_import_contract.v1"',
        "WARROOM_PAGE_TARGET",
        "IMPORT_ANCHOR_MODULE",
        "MOUNT_SECTION_ANCHOR",
        "FUTURE_SECTION_FUNCTION",
        "page_import_patch_allowed",
        "warroom_mount_patch_allowed",
        "streamlit_render_allowed",
        "PS-Q17U WarRoom prediction widget page import/mount implementation preflight",
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
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract.v1":
        failures.append("checker version mismatch")
    if PAGE_MOUNT_IMPORT_CONTRACT_VERSION != "warroom_prediction_widget_page_mount_import_contract.v1":
        failures.append("contract version mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture contract should be ok: {report}")
    if report.get("target_page_path") != WARROOM_PAGE_TARGET:
        failures.append("target page path mismatch")
    if report.get("page_import_row_count") != 12:
        failures.append("expected 12 page import rows")
    if report.get("page_mount_row_count") != 12:
        failures.append("expected 12 page mount rows")
    if report.get("page_zone_row_count") != 3:
        failures.append("expected 3 page zone rows")
    if report.get("page_import_patch_blockers") != list(WIDGET_FAMILY_ORDER):
        failures.append("all widget families must block page import patch")
    if report.get("warroom_mount_patch_blockers") != list(WIDGET_FAMILY_ORDER):
        failures.append("all widget families must block mount patch")
    if report.get("streamlit_render_blockers") != list(WIDGET_FAMILY_ORDER):
        failures.append("all widget families must block Streamlit render")
    imports = {row.get("widget_family_id"): row for row in report.get("page_import_rows", [])}
    mounts = {row.get("widget_family_id"): row for row in report.get("page_mount_rows", [])}
    for widget_id in WIDGET_FAMILY_ORDER:
        import_row = imports.get(widget_id, {})
        mount_row = mounts.get(widget_id, {})
        if not import_row:
            failures.append(f"missing import row: {widget_id}")
        if not mount_row:
            failures.append(f"missing mount row: {widget_id}")
        if import_row and f"render_{widget_id}" not in str(import_row.get("future_import_statement")):
            failures.append(f"future import should reference render function: {widget_id}")
        for row, row_name in ((import_row, "import"), (mount_row, "mount")):
            for key in ("page_import_patch_allowed", "warroom_mount_patch_allowed", "streamlit_render_allowed", "actual_source_read_allowed", "refresh_invocation_allowed"):
                if key in row and row.get(key) is not False:
                    failures.append(f"{row_name} row boundary should stay false: {widget_id}:{key}")
    _assert_false_boundaries(report, failures)
    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing Q17S source should block")
    if blocked.get("page_import_rows") or blocked.get("page_mount_rows"):
        failures.append("blocked report must not emit page rows")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17t_warroom_prediction_widget_page_mount_import_contract.v1",
        "page_mount_import_contract_version=warroom_prediction_widget_page_mount_import_contract.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17s_warroom_prediction_widget_read_only_component_skeleton_implementation.v1",
        "target_page_path=btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
        "page_mount_import_contract_only=true",
        "page_import_row_count=12",
        "page_mount_row_count=12",
        "page_zone_row_count=3",
        "no_warroom_page_import_patch",
        "no_warroom_mount_patch",
        "no_streamlit_render",
        "PS-Q17U: WarRoom prediction widget page import/mount implementation preflight",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "warroom_page_import_patch_allowed=true",
        "warroom_page_mutation_allowed=true",
        "warroom_mount_patch_allowed=true",
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
    result = {"ok": not failures, "guard": "ps_q17t_warroom_prediction_widget_page_mount_import_contract_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17t_warroom_prediction_widget_page_mount_import_contract_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
