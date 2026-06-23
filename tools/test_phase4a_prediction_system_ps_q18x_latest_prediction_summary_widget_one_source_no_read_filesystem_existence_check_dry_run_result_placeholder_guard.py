# path: ./tools/test_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_guard.py
# desc: Focused guard for PS-Q18X latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run result placeholder.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import EXPECTED_PATH_SHAPE_PREVIEW
from check_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder import CHECKER_VERSION, ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder import FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_KIND, FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_STATE, ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_ACK

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18X_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder.py",
    "tools/check_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder.py",
    "tools/test_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18X_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18x_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_guard.py",
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
    for marker in ("PS_Q18X_DECLARE_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_ONLY", "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_KIND", "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_STATE", "build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_packet", "filesystem_existence_check_dry_run_result_available", "source_artifact_exists_result_available", "actual_source_read_invoked"):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in ("import streamlit", "st.", "Path(", "open(", "read_text(", "read_bytes(", "write_text(", "data_read", "data_slice", "glob(", "rglob(", "exists(", "is_file(", "stat(", "render_latest_prediction_summary_widget(", "send_order(", "create_order("):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (CHECKER_VERSION, ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_CHECK_VERSION, "build_ps_q18w_report", "PS-Q18Y explicit one-source no-read filesystem existence-check dry-run result display contract"):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture result placeholder should be ok: {report}")
    if report.get("source_q18w_report_valid") is not True:
        failures.append("source Q18W report should validate")
    if report.get("dry_run_result_placeholder_packet_valid") is not True:
        failures.append("result placeholder packet should validate")
    if report.get("dry_run_result_placeholder_row_count") != 14:
        failures.append("expected 14 result placeholder rows")
    if report.get("source_candidate_count") != 1:
        failures.append("expected one source candidate")
    if report.get("filesystem_existence_check_dry_run_result_placeholder_kind") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_KIND:
        failures.append("result placeholder kind mismatch")
    if report.get("filesystem_existence_check_dry_run_result_placeholder_state") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_STATE:
        failures.append("result placeholder state mismatch")
    for key in ("filesystem_existence_check_dry_run_result_available", "filesystem_existence_check_dry_run_execution_allowed", "filesystem_existence_check_dry_run_executed", "source_artifact_exists_checked", "source_artifact_exists_result_available", "actual_source_read_invoked", "runtime_artifact_write_allowed", "broker_private_api_allowed"):
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")
    for key in ("latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_only", "filesystem_existence_check_dry_run_result_placeholder_declared", "source_candidate_count_fixed_to_one", "path_shape_preview_string_only"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    if report.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("path shape preview mismatch")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in ("filesystem_existence_check_dry_run_result_available=false", "source_artifact_exists_result_available=false", "no_source_artifact_exists_result", "PS-Q18Y: Explicit one-source no-read filesystem existence-check dry-run result display contract"):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
