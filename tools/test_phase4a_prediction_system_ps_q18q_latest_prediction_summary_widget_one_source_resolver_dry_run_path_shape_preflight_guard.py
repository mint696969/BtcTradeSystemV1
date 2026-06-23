# path: ./tools/test_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight_guard.py
# desc: Focused guard for PS-Q18Q latest_prediction_summary_widget one-source resolver dry-run path-shape preflight.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import CHECKER_VERSION, EXPECTED_PATH_SHAPE_PREVIEW, ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_PREFLIGHT_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight import ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_ACK, PATH_SHAPE_KIND

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18Q_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_PREFLIGHT_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight.py",
    "tools/check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight.py",
    "tools/test_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18Q_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_PREFLIGHT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18q_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight_guard.py",
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
        "LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_PREFLIGHT_VERSION",
        "ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_ACK",
        "PS_Q18Q_DECLARE_ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_PREFLIGHT_ONLY",
        "PATH_SHAPE_KIND",
        "PATH_SHAPE_TEMPLATE",
        "build_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight_rows",
        "build_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight_packet",
        "latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight_only",
        "path_shape_declared",
        "path_shape_preview_string_only",
        "source_artifact_resolver_invoked",
        "source_artifact_path_materialized",
        "source_artifact_exists_checked",
        "actual_source_read_invoked",
    ):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in ("import streamlit", "st.", "Path(", "open(", "read_text(", "read_bytes(", "write_text(", "data_read", "data_slice", "glob(", "rglob(", "render_latest_prediction_summary_widget(", "send_order(", "create_order("):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        'CHECKER = "ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight.v1"',
        'ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_PREFLIGHT_CHECK_VERSION = "latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight.v1"',
        "build_ps_q18p_report",
        "build_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight_packet",
        "EXPECTED_PATH_SHAPE_PREVIEW",
        "latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight_only",
        "source_artifact_path_materialized",
        "actual_source_read_invoked",
        "PS-Q18R explicit one-source resolver dry-run path-shape close guard",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight.v1":
        failures.append("checker version mismatch")
    if ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_PREFLIGHT_CHECK_VERSION != "latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight.v1":
        failures.append("check version mismatch")
    if ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_ACK != "PS_Q18Q_DECLARE_ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_PREFLIGHT_ONLY":
        failures.append("path shape ack mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture path shape should be ok: {report}")
    if report.get("source_q18p_report_valid") is not True:
        failures.append("source Q18P report should validate")
    if report.get("path_shape_packet_valid") is not True:
        failures.append("path shape packet should validate")
    if report.get("path_shape_row_count") != 13:
        failures.append("expected 13 path shape rows")
    if report.get("source_candidate_count") != 1:
        failures.append("expected one source candidate")
    if report.get("path_shape_candidate_ready") is not True:
        failures.append("path shape candidate should be ready")
    if report.get("resolver_input_ref_kind") != "artifact_ref_string_only":
        failures.append("resolver input ref kind mismatch")
    if report.get("path_shape_kind") != PATH_SHAPE_KIND:
        failures.append("path shape kind mismatch")
    if report.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("path shape preview mismatch")
    for key, value in {"selected_candidate_generated_at": "2026-06-22T00:00:00Z", "selected_candidate_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json", "selected_candidate_market_uid": "BTC-USD"}.items():
        if report.get(key) != value:
            failures.append(f"selected candidate mismatch: {key}")
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight_only", "one_source_resolver_dry_run_path_shape_preflight_ready", "path_shape_declared", "path_shape_preview_string_only", "one_source_candidate_preserved", "source_candidate_count_fixed_to_one", "explicit_path_shape_ack_matched"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in ("warroom_page_mutation_allowed", "source_artifact_resolver_invoked", "source_artifact_resolution_allowed", "source_artifact_resolved", "source_artifact_path_materialized", "source_artifact_exists_checked", "source_artifact_schema_checked", "actual_source_read_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18p_validation_invoked_by_mount", "q18o_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q18Q_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_PREFLIGHT_2026-06-22.md",
        "# desc: PS-Q18Q latest_prediction_summary_widget one-source resolver dry-run path-shape preflight after PS-Q18P.",
        "checker=check_phase4a_prediction_system_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight.v1",
        "one_source_resolver_dry_run_path_shape_preflight_check_version=latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight.v1",
        "path_shape_preflight_version=prediction_warroom_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight.ps_q18q.v1",
        "source_q18p_checker=check_phase4a_prediction_system_ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight.v1",
        "source_candidate_count=1",
        "resolver_input_ref_kind=artifact_ref_string_only",
        "path_shape_preview=D:/btc_ts_hot/prediction_sources/BTC-USD/2026-06-22T00:00:00Z/latest_prediction.json",
        "one_source_resolver_dry_run_path_shape_ack=PS_Q18Q_DECLARE_ONE_SOURCE_RESOLVER_DRY_RUN_PATH_SHAPE_PREFLIGHT_ONLY",
        "source_artifact_path_materialized=false",
        "source_artifact_exists_checked=false",
        "actual_source_read_invoked=false",
        "no_source_artifact_path_materialization",
        "no_actual_source_read",
        "PS-Q18R: Explicit one-source resolver dry-run path-shape close guard",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18q_latest_prediction_summary_widget_one_source_resolver_dry_run_path_shape_preflight_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
