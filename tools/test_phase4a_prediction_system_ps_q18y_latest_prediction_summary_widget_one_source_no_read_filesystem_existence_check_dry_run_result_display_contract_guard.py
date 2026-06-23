# path: ./tools/test_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_guard.py
# desc: Focused guard for PS-Q18Y latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run result display contract.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import EXPECTED_PATH_SHAPE_PREVIEW
from check_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract import CHECKER_VERSION, ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract import FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_KIND, FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_STATE, ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ACK

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18Y_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.py",
    "tools/check_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.py",
    "tools/test_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18Y_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18y_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_guard.py",
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
    for marker in ("PS_Q18Y_DECLARE_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ONLY", "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_KIND", "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_STATE", "build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_packet", "filesystem_existence_check_dry_run_result_display_mount_allowed", "streamlit_render_invoked", "actual_source_read_invoked"):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in ("import streamlit", "st.", "Path(", "open(", "read_text(", "read_bytes(", "write_text(", "data_read", "data_slice", "glob(", "rglob(", "exists(", "is_file(", "stat(", "render_latest_prediction_summary_widget(", "send_order(", "create_order("):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (CHECKER_VERSION, ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_CHECK_VERSION, "build_ps_q18x_report", "PS-Q18Z explicit one-source no-read filesystem existence-check dry-run result display packet"):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture display contract should be ok: {report}")
    if report.get("source_q18x_report_valid") is not True:
        failures.append("source Q18X report should validate")
    if report.get("dry_run_result_display_contract_packet_valid") is not True:
        failures.append("display contract packet should validate")
    if report.get("dry_run_result_display_contract_row_count") != 14:
        failures.append("expected 14 display contract rows")
    if report.get("source_candidate_count") != 1:
        failures.append("expected one source candidate")
    if report.get("dry_run_result_display_contract_candidate_ready") is not True:
        failures.append("display contract candidate should be ready")
    if report.get("filesystem_existence_check_dry_run_result_display_contract_kind") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_KIND:
        failures.append("display contract kind mismatch")
    if report.get("filesystem_existence_check_dry_run_result_display_contract_state") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_STATE:
        failures.append("display contract state mismatch")
    if report.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("path shape preview mismatch")
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_only", "filesystem_existence_check_dry_run_result_display_contract_declared", "filesystem_existence_check_dry_run_result_placeholder_preserved", "source_candidate_count_fixed_to_one", "path_shape_preview_string_only"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in ("filesystem_existence_check_dry_run_result_available", "filesystem_existence_check_dry_run_result_display_mount_allowed", "filesystem_existence_check_dry_run_result_display_mounted", "filesystem_existence_check_dry_run_execution_allowed", "filesystem_existence_check_dry_run_executed", "source_artifact_exists_checked", "source_artifact_exists_result_available", "actual_source_read_invoked", "streamlit_render_allowed", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "runtime_artifact_write_allowed", "broker_private_api_allowed"):
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in ("filesystem_existence_check_dry_run_result_display_mount_allowed=false", "streamlit_render_invoked=false", "no_warroom_display_mount", "PS-Q18Z: Explicit one-source no-read filesystem existence-check dry-run result display packet"):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
