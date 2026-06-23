# path: ./tools/test_phase4a_prediction_system_ps_q18x_close_guard.py
# desc: Close guard for PS-Q18X latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run result placeholder.

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
FOCUSED_GUARD = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder.py",
    "tools/check_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder.py",
    "tools/test_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18X_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18x_close_guard.py",
}
TRUE_KEYS = (
    "read_only",
    "non_executing",
    "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_only",
    "one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_ready",
    "filesystem_existence_check_dry_run_result_placeholder_declared",
    "one_source_candidate_preserved",
    "source_candidate_count_fixed_to_one",
    "explicit_dry_run_result_placeholder_ack_matched",
    "path_shape_preview_string_only",
)
FALSE_KEYS = (
    "filesystem_existence_check_dry_run_result_available",
    "filesystem_existence_check_dry_run_execution_allowed",
    "filesystem_existence_check_dry_run_executed",
    "warroom_page_mutation_allowed",
    "source_artifact_resolver_invoked",
    "source_artifact_resolution_allowed",
    "source_artifact_resolved",
    "source_artifact_path_materialized",
    "source_artifact_exists_check_allowed",
    "source_artifact_exists_checked",
    "source_artifact_exists_result_available",
    "source_artifact_schema_check_allowed",
    "source_artifact_schema_checked",
    "actual_source_read_allowed",
    "actual_source_read_invoked",
    "payload_reparse_allowed",
    "source_discovery_allowed",
    "d_hot_directory_scan_allowed",
    "d_hot_actual_read_allowed",
    "q18w_validation_invoked_by_mount",
    "q18v_validation_invoked_by_mount",
    "component_packet_builder_invoked_by_mount",
    "streamlit_render_invoked",
    "real_prediction_widget_rendering_allowed",
    "refresh_invocation_allowed",
    "runtime_artifact_write_allowed",
    "parameter_apply_allowed",
    "broker_private_api_allowed",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def main_guard() -> int:
    failures: list[str] = []
    for path in (COMPONENT, TOOL, UNIT, DOC, FOCUSED_GUARD):
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
        "PS_Q18X_DECLARE_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_ONLY",
        "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_KIND",
        "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_STATE",
        "build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_packet",
        "filesystem_existence_check_dry_run_result_available",
        "source_artifact_exists_result_available",
        "actual_source_read_invoked",
        "TRUE_BOUNDARIES",
        "FALSE_BOUNDARIES",
    ):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in ("import streamlit", "st.", "Path(", "open(", "read_text(", "read_bytes(", "write_text(", "write_bytes(", "data_read", "data_slice", "glob(", "rglob(", "exists(", "is_file(", "stat(", "render_latest_prediction_summary_widget(", "send_order(", "create_order("):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (CHECKER_VERSION, ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_CHECK_VERSION, "build_ps_q18w_report", "PS-Q18Y explicit one-source no-read filesystem existence-check dry-run result display contract", '"read_only"', '"non_executing"'):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    focused_text = _read(FOCUSED_GUARD) if FOCUSED_GUARD.exists() else ""
    if "tools/test_phase4a_prediction_system_ps_q18x_close_guard.py" not in focused_text:
        failures.append("focused guard expected dirty set must include close guard")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18x_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder.v1":
        failures.append("checker version mismatch")
    if ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_CHECK_VERSION != "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder.v1":
        failures.append("check version mismatch")
    if ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_ACK != "PS_Q18X_DECLARE_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_ONLY":
        failures.append("placeholder ack mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture result placeholder should be ok: {report}")
    if report.get("source_q18w_report_valid") is not True:
        failures.append("source Q18W report should validate")
    if report.get("dry_run_result_placeholder_packet_valid") is not True:
        failures.append("result placeholder packet should validate")
    if report.get("dry_run_result_placeholder_validation_failures"):
        failures.append(f"result placeholder validation failures: {report.get('dry_run_result_placeholder_validation_failures')}")
    if report.get("dry_run_result_placeholder_row_count") != 14:
        failures.append("expected 14 result placeholder rows")
    if report.get("source_candidate_count") != 1:
        failures.append("expected one source candidate")
    if report.get("dry_run_result_placeholder_candidate_ready") is not True:
        failures.append("result placeholder candidate should be ready")
    if report.get("filesystem_existence_check_dry_run_result_placeholder_kind") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_KIND:
        failures.append("result placeholder kind mismatch")
    if report.get("filesystem_existence_check_dry_run_result_placeholder_state") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_PLACEHOLDER_STATE:
        failures.append("result placeholder state mismatch")
    if report.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("path shape preview mismatch")
    for key, value in {"selected_candidate_generated_at": "2026-06-22T00:00:00Z", "selected_candidate_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json", "selected_candidate_market_uid": "BTC-USD"}.items():
        if report.get(key) != value:
            failures.append(f"selected candidate mismatch: {key}")
    for key in TRUE_KEYS:
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_KEYS:
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")
    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing source should block checker report")
    if blocked.get("dry_run_result_placeholder_row_count") != 0:
        failures.append("blocked report should not emit observed placeholder rows")
    for key in ("filesystem_existence_check_dry_run_result_available", "filesystem_existence_check_dry_run_execution_allowed", "filesystem_existence_check_dry_run_executed", "source_artifact_exists_checked", "source_artifact_exists_result_available", "actual_source_read_invoked"):
        if blocked.get(key) is not False:
            failures.append(f"blocked {key} must stay false")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in ("read_only=true", "non_executing=true", "filesystem_existence_check_dry_run_result_available=false", "source_artifact_exists_result_available=false", "no_source_artifact_exists_result", "PS-Q18Y: Explicit one-source no-read filesystem existence-check dry-run result display contract"):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in ("filesystem_existence_check_dry_run_result_available=true", "filesystem_existence_check_dry_run_execution_allowed=true", "filesystem_existence_check_dry_run_executed=true", "source_artifact_exists_checked=true", "source_artifact_exists_result_available=true", "actual_source_read_invoked=true", "runtime_artifact_write_allowed=true", "broker_private_api_allowed=true"):
        if forbidden in doc_text:
            failures.append(f"forbidden doc marker present: {forbidden}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q18x_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_placeholder_before_exists_result_schema_read_render_refresh_and_writes",
        "contract": {
            "ps_q18x_closed": not failures,
            "dry_run_result_placeholder_row_count": int(report.get("dry_run_result_placeholder_row_count") or 0),
            "source_candidate_count": int(report.get("source_candidate_count") or 0),
            "dry_run_result_placeholder_candidate_ready": bool(report.get("dry_run_result_placeholder_candidate_ready")),
            "filesystem_existence_check_dry_run_result_placeholder_kind": report.get("filesystem_existence_check_dry_run_result_placeholder_kind"),
            "filesystem_existence_check_dry_run_result_placeholder_state": report.get("filesystem_existence_check_dry_run_result_placeholder_state"),
            "filesystem_existence_check_dry_run_result_available": False,
            "filesystem_existence_check_dry_run_execution_allowed": False,
            "filesystem_existence_check_dry_run_executed": False,
            "path_shape_preview": report.get("path_shape_preview"),
            "selected_candidate_generated_at": report.get("selected_candidate_generated_at"),
            "selected_candidate_source_artifact_ref": report.get("selected_candidate_source_artifact_ref"),
            "selected_candidate_market_uid": report.get("selected_candidate_market_uid"),
            "source_artifact_exists_checked": False,
            "source_artifact_exists_result_available": False,
            "source_artifact_schema_checked": False,
            "actual_source_read_invoked": False,
            "next_slice": "PS-Q18Y explicit one-source no-read filesystem existence-check dry-run result display contract",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18x_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
