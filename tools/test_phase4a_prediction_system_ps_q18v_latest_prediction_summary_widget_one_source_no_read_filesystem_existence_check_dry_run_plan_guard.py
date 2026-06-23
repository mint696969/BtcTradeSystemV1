# path: ./tools/test_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_guard.py
# desc: Focused guard for PS-Q18V latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run plan.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import EXPECTED_PATH_SHAPE_PREVIEW
from check_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan import CHECKER_VERSION, ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan import FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_KIND, FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_STATE, ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ACK

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18V_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.py",
    "tools/check_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.py",
    "tools/test_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18V_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18v_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_guard.py",
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
        "LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_VERSION",
        "ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ACK",
        "PS_Q18V_DECLARE_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ONLY",
        "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_KIND",
        "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_STATE",
        "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ITEMS",
        "build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_rows",
        "build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_packet",
        "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_only",
        "filesystem_existence_check_dry_run_plan_declared",
        "filesystem_existence_check_dry_run_execution_allowed",
        "filesystem_existence_check_dry_run_executed",
        "source_artifact_exists_check_allowed",
        "source_artifact_exists_checked",
        "source_artifact_schema_checked",
        "actual_source_read_invoked",
    ):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in ("import streamlit", "st.", "Path(", "open(", "read_text(", "read_bytes(", "write_text(", "data_read", "data_slice", "glob(", "rglob(", "exists(", "is_file(", "stat(", "render_latest_prediction_summary_widget(", "send_order(", "create_order("):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        'CHECKER = "ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.v1"',
        'ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_CHECK_VERSION = "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.v1"',
        "build_ps_q18u_report",
        "build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_packet",
        "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_KIND",
        "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_STATE",
        "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_only",
        "source_artifact_exists_checked",
        "actual_source_read_invoked",
        "PS-Q18W explicit one-source no-read filesystem existence-check dry-run packet",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.v1":
        failures.append("checker version mismatch")
    if ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_CHECK_VERSION != "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.v1":
        failures.append("check version mismatch")
    if ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ACK != "PS_Q18V_DECLARE_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ONLY":
        failures.append("dry-run plan ack mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture dry-run plan should be ok: {report}")
    if report.get("source_q18u_report_valid") is not True:
        failures.append("source Q18U report should validate")
    if report.get("dry_run_plan_packet_valid") is not True:
        failures.append("dry-run plan packet should validate")
    if report.get("dry_run_plan_row_count") != 14:
        failures.append("expected 14 dry-run plan rows")
    if report.get("source_candidate_count") != 1:
        failures.append("expected one source candidate")
    if report.get("dry_run_plan_candidate_ready") is not True:
        failures.append("dry-run plan candidate should be ready")
    if report.get("filesystem_existence_check_dry_run_plan_kind") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_KIND:
        failures.append("dry-run plan kind mismatch")
    if report.get("filesystem_existence_check_dry_run_plan_state") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_STATE:
        failures.append("dry-run plan state mismatch")
    if report.get("filesystem_existence_check_dry_run_execution_allowed") is not False:
        failures.append("dry-run plan must not allow execution")
    if report.get("filesystem_existence_check_dry_run_executed") is not False:
        failures.append("dry-run must not be executed")
    if report.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("path shape preview mismatch")
    for key, value in {"selected_candidate_generated_at": "2026-06-22T00:00:00Z", "selected_candidate_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json", "selected_candidate_market_uid": "BTC-USD"}.items():
        if report.get(key) != value:
            failures.append(f"selected candidate mismatch: {key}")
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_only", "one_source_no_read_filesystem_existence_check_dry_run_plan_ready", "filesystem_existence_check_dry_run_plan_declared", "one_source_candidate_preserved", "source_candidate_count_fixed_to_one", "explicit_dry_run_plan_ack_matched", "path_shape_preview_string_only"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in ("filesystem_existence_check_dry_run_execution_allowed", "filesystem_existence_check_dry_run_executed", "warroom_page_mutation_allowed", "source_artifact_resolver_invoked", "source_artifact_resolution_allowed", "source_artifact_resolved", "source_artifact_path_materialized", "source_artifact_exists_check_allowed", "source_artifact_exists_checked", "source_artifact_exists_result_available", "source_artifact_schema_check_allowed", "source_artifact_schema_checked", "actual_source_read_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18u_validation_invoked_by_mount", "q18t_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q18V_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_2026-06-22.md",
        "# desc: PS-Q18V latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run plan after PS-Q18U.",
        "checker=check_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.v1",
        "one_source_no_read_filesystem_existence_check_dry_run_plan_check_version=latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.v1",
        "no_read_filesystem_existence_check_dry_run_plan_version=prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.ps_q18v.v1",
        "source_q18u_checker=check_phase4a_prediction_system_ps_q18u_latest_prediction_summary_widget_one_source_no_read_existence_check_gate_open_contract.v1",
        "source_candidate_count=1",
        "path_shape_preview=D:/btc_ts_hot/prediction_sources/BTC-USD/2026-06-22T00:00:00Z/latest_prediction.json",
        "filesystem_existence_check_dry_run_execution_allowed=false",
        "filesystem_existence_check_dry_run_executed=false",
        "filesystem_existence_check_dry_run_plan_state=plan_declared_not_executed",
        "one_source_no_read_filesystem_existence_check_dry_run_plan_ack=PS_Q18V_DECLARE_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ONLY",
        "source_artifact_exists_check_allowed=false",
        "source_artifact_exists_checked=false",
        "source_artifact_schema_checked=false",
        "actual_source_read_invoked=false",
        "no_source_artifact_exists_check_allowed",
        "no_source_artifact_exists_check_execution",
        "no_actual_source_read",
        "PS-Q18W: Explicit one-source no-read filesystem existence-check dry-run packet",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
