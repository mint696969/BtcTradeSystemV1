# path: ./tools/test_phase4a_prediction_system_ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_guard.py
# desc: Focused guard for PS-Q18T latest_prediction_summary_widget one-source no-read existence-check execution preflight.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import EXPECTED_PATH_SHAPE_PREVIEW
from check_phase4a_prediction_system_ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight import CHECKER_VERSION, ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight import EXISTENCE_EXECUTION_PREFLIGHT_KIND, EXISTENCE_EXECUTION_PREFLIGHT_STATE, ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ACK

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18T_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.py",
    "tools/check_phase4a_prediction_system_ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.py",
    "tools/test_phase4a_prediction_system_ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18T_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18t_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_guard.py",
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
        "LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_VERSION",
        "ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ACK",
        "PS_Q18T_DECLARE_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ONLY",
        "EXISTENCE_EXECUTION_PREFLIGHT_KIND",
        "EXISTENCE_EXECUTION_PREFLIGHT_STATE",
        "EXISTENCE_EXECUTION_PREFLIGHT_ITEMS",
        "build_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_rows",
        "build_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_packet",
        "latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_only",
        "existence_check_execution_preflight_declared",
        "existence_check_execution_preflight_would_open_gate",
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
        'CHECKER = "ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.v1"',
        'ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_CHECK_VERSION = "latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.v1"',
        "build_ps_q18s_report",
        "build_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_packet",
        "EXISTENCE_EXECUTION_PREFLIGHT_KIND",
        "EXISTENCE_EXECUTION_PREFLIGHT_STATE",
        "latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_only",
        "source_artifact_exists_checked",
        "actual_source_read_invoked",
        "PS-Q18U explicit one-source no-read existence check execution gate-open contract",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.v1":
        failures.append("checker version mismatch")
    if ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_CHECK_VERSION != "latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.v1":
        failures.append("check version mismatch")
    if ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ACK != "PS_Q18T_DECLARE_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ONLY":
        failures.append("execution preflight ack mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture execution preflight should be ok: {report}")
    if report.get("source_q18s_report_valid") is not True:
        failures.append("source Q18S report should validate")
    if report.get("execution_preflight_packet_valid") is not True:
        failures.append("execution preflight packet should validate")
    if report.get("execution_preflight_row_count") != 14:
        failures.append("expected 14 execution preflight rows")
    if report.get("source_candidate_count") != 1:
        failures.append("expected one source candidate")
    if report.get("execution_preflight_candidate_ready") is not True:
        failures.append("execution preflight candidate should be ready")
    if report.get("existence_execution_preflight_kind") != EXISTENCE_EXECUTION_PREFLIGHT_KIND:
        failures.append("execution preflight kind mismatch")
    if report.get("existence_execution_preflight_state") != EXISTENCE_EXECUTION_PREFLIGHT_STATE:
        failures.append("execution preflight state mismatch")
    if report.get("existence_check_execution_preflight_would_open_gate") is not False:
        failures.append("execution preflight must not open gate")
    if report.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("path shape preview mismatch")
    for key, value in {"selected_candidate_generated_at": "2026-06-22T00:00:00Z", "selected_candidate_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json", "selected_candidate_market_uid": "BTC-USD"}.items():
        if report.get(key) != value:
            failures.append(f"selected candidate mismatch: {key}")
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_only", "one_source_no_read_existence_check_execution_preflight_ready", "existence_check_execution_preflight_declared", "one_source_candidate_preserved", "source_candidate_count_fixed_to_one", "explicit_execution_preflight_ack_matched", "path_shape_preview_string_only"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in ("existence_check_execution_preflight_would_open_gate", "warroom_page_mutation_allowed", "source_artifact_resolver_invoked", "source_artifact_resolution_allowed", "source_artifact_resolved", "source_artifact_path_materialized", "source_artifact_exists_check_allowed", "source_artifact_exists_checked", "source_artifact_exists_result_available", "source_artifact_schema_check_allowed", "source_artifact_schema_checked", "actual_source_read_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18s_validation_invoked_by_mount", "q18r_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q18T_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_2026-06-22.md",
        "# desc: PS-Q18T latest_prediction_summary_widget one-source no-read existence-check execution preflight after PS-Q18S.",
        "checker=check_phase4a_prediction_system_ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.v1",
        "one_source_no_read_existence_check_execution_preflight_check_version=latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.v1",
        "no_read_existence_check_execution_preflight_version=prediction_warroom_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight.ps_q18t.v1",
        "source_q18s_checker=check_phase4a_prediction_system_ps_q18s_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_gate.v1",
        "source_candidate_count=1",
        "path_shape_preview=D:/btc_ts_hot/prediction_sources/BTC-USD/2026-06-22T00:00:00Z/latest_prediction.json",
        "existence_check_execution_preflight_would_open_gate=false",
        "existence_execution_preflight_state=preflight_declared_not_executed",
        "one_source_no_read_existence_check_execution_preflight_ack=PS_Q18T_DECLARE_ONE_SOURCE_NO_READ_EXISTENCE_CHECK_EXECUTION_PREFLIGHT_ONLY",
        "source_artifact_exists_check_allowed=false",
        "source_artifact_exists_checked=false",
        "source_artifact_schema_checked=false",
        "actual_source_read_invoked=false",
        "no_source_artifact_exists_check_execution",
        "no_actual_source_read",
        "PS-Q18U: Explicit one-source no-read existence check execution gate-open contract",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18t_latest_prediction_summary_widget_one_source_no_read_existence_check_execution_preflight_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
