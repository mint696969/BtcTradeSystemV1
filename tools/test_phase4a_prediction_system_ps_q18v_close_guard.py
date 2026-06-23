# path: ./tools/test_phase4a_prediction_system_ps_q18v_close_guard.py
# desc: Close guard for PS-Q18V latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run plan.

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
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_guard.py"
CLOSE_REL = "tools/test_phase4a_prediction_system_ps_q18v_close_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.py",
    "tools/check_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.py",
    "tools/test_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18V_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18v_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in (
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
        "freshness_checked_against_d_hot",
        "q18u_validation_invoked_by_mount",
        "q18t_validation_invoked_by_mount",
        "q18s_validation_invoked_by_mount",
        "q18r_validation_invoked_by_mount",
        "q18q_validation_invoked_by_mount",
        "q18p_validation_invoked_by_mount",
        "q18o_validation_invoked_by_mount",
        "q18n_validation_invoked_by_mount",
        "q18m_validation_invoked_by_mount",
        "q18j_validation_invoked_by_mount",
        "component_packet_builder_invoked_by_mount",
        "component_packet_builder_allowed_by_mount",
        "component_runtime_binding_allowed",
        "streamlit_render_allowed",
        "streamlit_render_invoked",
        "real_prediction_widget_rendering_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "confidence_increase_allowed",
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
        "LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_VERSION",
        "ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ACK",
        "PS_Q18V_DECLARE_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ONLY",
        "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_KIND",
        "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_STATE",
        "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ITEMS",
        "build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_rows",
        "build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_packet",
        "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_only",
        "one_source_no_read_filesystem_existence_check_dry_run_plan_ready",
        "filesystem_existence_check_dry_run_plan_declared",
        "filesystem_existence_check_dry_run_execution_allowed",
        "filesystem_existence_check_dry_run_executed",
        "one_source_candidate_preserved",
        "source_candidate_count_fixed_to_one",
        "explicit_dry_run_plan_ack_matched",
        "path_shape_preview_string_only",
        "source_artifact_exists_check_allowed",
        "source_artifact_exists_checked",
        "source_artifact_exists_result_available",
        "source_artifact_schema_check_allowed",
        "source_artifact_schema_checked",
        "actual_source_read_allowed",
        "actual_source_read_invoked",
        "d_hot_actual_read_allowed",
        "q18u_validation_invoked_by_mount",
        "component_packet_builder_invoked_by_mount",
        "streamlit_render_invoked",
    ):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in (
        "import streamlit",
        "st.",
        "Path(",
        "open(",
        "read_text(",
        "read_bytes(",
        "write_text(",
        "write_bytes(",
        "data_read",
        "data_slice",
        "glob(",
        "rglob(",
        "exists(",
        "is_file(",
        "stat(",
        "render_latest_prediction_summary_widget(",
        "build_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation(",
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
        'CHECKER = "ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.v1"',
        'ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_CHECK_VERSION = "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.v1"',
        "build_ps_q18u_report",
        "build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_packet",
        "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_KIND",
        "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_STATE",
        "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_only",
        "source_artifact_exists_checked",
        "source_artifact_schema_checked",
        "actual_source_read_invoked",
        "PS-Q18W explicit one-source no-read filesystem existence-check dry-run packet",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if "test_ps_q18v_validates_dry_run_plan_from_q18u_fixture" not in unit_text:
        failures.append("unit test must cover Q18U fixture dry-run plan")
    if "test_ps_q18v_packet_without_source_is_plan_only_but_candidate_not_ready" not in unit_text:
        failures.append("unit test must cover dry-run plan packet without candidate")
    if CLOSE_REL not in focused_text:
        failures.append("focused guard expected dirty set must include close guard")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.v1":
        failures.append("checker version mismatch")
    if ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_CHECK_VERSION != "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.v1":
        failures.append("check version mismatch")
    if ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ACK != "PS_Q18V_DECLARE_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ONLY":
        failures.append("dry-run plan ack mismatch")

    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture dry-run plan should be ok: {report}")
    if report.get("use_observed_fixture") is not True:
        failures.append("observed fixture flag should be true")
    if report.get("source_q18u_report_valid") is not True:
        failures.append("source Q18U report should validate")
    if report.get("dry_run_plan_packet_valid") is not True:
        failures.append("dry-run plan packet should validate")
    if report.get("dry_run_plan_validation_failures"):
        failures.append(f"dry-run plan validation failures: {report.get('dry_run_plan_validation_failures')}")
    if report.get("dry_run_plan_row_count") != 14:
        failures.append("expected 14 dry-run plan rows")
    if report.get("source_candidate_count") != 1:
        failures.append("expected exactly one source candidate")
    if report.get("dry_run_plan_candidate_ready") is not True:
        failures.append("dry-run plan candidate should be ready")
    if report.get("filesystem_existence_check_dry_run_plan_kind") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_KIND:
        failures.append("dry-run plan kind mismatch")
    if report.get("filesystem_existence_check_dry_run_plan_state") != FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_STATE:
        failures.append("dry-run plan state mismatch")
    if report.get("filesystem_existence_check_dry_run_execution_allowed") is not False:
        failures.append("dry-run execution must not be allowed")
    if report.get("filesystem_existence_check_dry_run_executed") is not False:
        failures.append("dry-run execution must not run")
    if report.get("path_shape_preview") != EXPECTED_PATH_SHAPE_PREVIEW:
        failures.append("path-shape preview mismatch")
    for key, value in {
        "selected_candidate_generated_at": "2026-06-22T00:00:00Z",
        "selected_candidate_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
        "selected_candidate_market_uid": "BTC-USD",
    }.items():
        if report.get(key) != value:
            failures.append(f"selected candidate mismatch: {key}")
    for key in (
        "read_only",
        "non_executing",
        "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_only",
        "one_source_no_read_filesystem_existence_check_dry_run_plan_ready",
        "filesystem_existence_check_dry_run_plan_declared",
        "one_source_candidate_preserved",
        "source_candidate_count_fixed_to_one",
        "explicit_dry_run_plan_ack_matched",
        "path_shape_preview_string_only",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    _assert_false_boundaries(report, failures)
    if report.get("recommended_first_validation") != "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_guard":
        failures.append("recommended first validation mismatch")

    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing source should block checker report")
    if blocked.get("dry_run_plan_row_count") != 0:
        failures.append("blocked report should not emit observed dry-run plan rows")
    if blocked.get("filesystem_existence_check_dry_run_execution_allowed") is not False:
        failures.append("blocked report should not allow dry-run execution")
    if blocked.get("filesystem_existence_check_dry_run_executed") is not False:
        failures.append("blocked report should not execute dry-run")
    if blocked.get("source_artifact_exists_check_allowed") is not False:
        failures.append("blocked report should not allow existence check")
    if blocked.get("source_artifact_exists_checked") is not False:
        failures.append("blocked report should not check existence")
    if blocked.get("source_artifact_schema_checked") is not False:
        failures.append("blocked report should not check schema")
    if blocked.get("actual_source_read_invoked") is not False:
        failures.append("blocked report should not invoke actual read")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")

    for marker in (
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q18V_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_2026-06-22.md",
        "# desc: PS-Q18V latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run plan after PS-Q18U.",
        "checker=check_phase4a_prediction_system_ps_q18v_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.v1",
        "one_source_no_read_filesystem_existence_check_dry_run_plan_check_version=latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.v1",
        "no_read_filesystem_existence_check_dry_run_plan_version=prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan.ps_q18v.v1",
        "source_q18u_checker=check_phase4a_prediction_system_ps_q18u_latest_prediction_summary_widget_one_source_no_read_existence_check_gate_open_contract.v1",
        "selected_candidate_generated_at=2026-06-22T00:00:00Z",
        "selected_candidate_source_artifact_ref=fixture://ps_q18i/latest_prediction.json",
        "selected_candidate_market_uid=BTC-USD",
        "source_candidate_count=1",
        "path_shape_preview=D:/btc_ts_hot/prediction_sources/BTC-USD/2026-06-22T00:00:00Z/latest_prediction.json",
        "filesystem_existence_check_dry_run_plan_declared=true",
        "filesystem_existence_check_dry_run_execution_allowed=false",
        "filesystem_existence_check_dry_run_executed=false",
        "filesystem_existence_check_dry_run_plan_kind=no_read_filesystem_existence_check_dry_run_plan",
        "filesystem_existence_check_dry_run_plan_state=plan_declared_not_executed",
        "one_source_no_read_filesystem_existence_check_dry_run_plan_ack=PS_Q18V_DECLARE_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_PLAN_ONLY",
        "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_only=true",
        "one_source_no_read_filesystem_existence_check_dry_run_plan_ready=true",
        "path_shape_preview_string_only=true",
        "source_artifact_exists_check_allowed=false",
        "source_artifact_exists_checked=false",
        "source_artifact_exists_result_available=false",
        "source_artifact_schema_check_allowed=false",
        "source_artifact_schema_checked=false",
        "actual_source_read_allowed=false",
        "actual_source_read_invoked=false",
        "no_source_artifact_exists_check_allowed",
        "no_source_artifact_exists_check_execution",
        "no_source_artifact_schema_check_execution",
        "no_actual_source_read",
        "PS-Q18W: Explicit one-source no-read filesystem existence-check dry-run packet",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "filesystem_existence_check_dry_run_execution_allowed=true",
        "filesystem_existence_check_dry_run_executed=true",
        "source_artifact_resolver_invoked=true",
        "source_artifact_resolution_allowed=true",
        "source_artifact_resolved=true",
        "source_artifact_path_materialized=true",
        "source_artifact_exists_check_allowed=true",
        "source_artifact_exists_checked=true",
        "source_artifact_exists_result_available=true",
        "source_artifact_schema_check_allowed=true",
        "source_artifact_schema_checked=true",
        "actual_source_read_allowed=true",
        "actual_source_read_invoked=true",
        "payload_reparse_allowed=true",
        "source_discovery_allowed=true",
        "d_hot_directory_scan_allowed=true",
        "d_hot_actual_read_allowed=true",
        "q18u_validation_invoked_by_mount=true",
        "component_packet_builder_invoked_by_mount=true",
        "streamlit_render_invoked=true",
        "real_prediction_widget_rendering_allowed=true",
        "refresh_invocation_allowed=true",
        "runtime_artifact_write_allowed=true",
        "parameter_apply_allowed=true",
        "broker_private_api_allowed=true",
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
        "guard": "ps_q18v_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_before_exists_schema_read_render_refresh_and_writes",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q18v_closed": not failures,
            "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_plan_only": True,
            "one_source_no_read_filesystem_existence_check_dry_run_plan_ready": True,
            "filesystem_existence_check_dry_run_plan_declared": True,
            "filesystem_existence_check_dry_run_execution_allowed": False,
            "filesystem_existence_check_dry_run_executed": False,
            "path_shape_preview_string_only": True,
            "one_source_candidate_preserved": True,
            "source_candidate_count_fixed_to_one": True,
            "explicit_dry_run_plan_ack_matched": True,
            "dry_run_plan_row_count": int(report.get("dry_run_plan_row_count") or 0),
            "source_candidate_count": int(report.get("source_candidate_count") or 0),
            "dry_run_plan_candidate_ready": bool(report.get("dry_run_plan_candidate_ready")),
            "filesystem_existence_check_dry_run_plan_kind": report.get("filesystem_existence_check_dry_run_plan_kind"),
            "filesystem_existence_check_dry_run_plan_state": report.get("filesystem_existence_check_dry_run_plan_state"),
            "path_shape_preview": report.get("path_shape_preview"),
            "selected_candidate_generated_at": report.get("selected_candidate_generated_at"),
            "selected_candidate_source_artifact_ref": report.get("selected_candidate_source_artifact_ref"),
            "selected_candidate_market_uid": report.get("selected_candidate_market_uid"),
            "warroom_page_mutation_allowed": False,
            "source_artifact_resolver_invoked": False,
            "source_artifact_resolution_allowed": False,
            "source_artifact_path_materialized": False,
            "source_artifact_exists_check_allowed": False,
            "source_artifact_exists_checked": False,
            "source_artifact_exists_result_available": False,
            "source_artifact_schema_check_allowed": False,
            "source_artifact_schema_checked": False,
            "actual_source_read_allowed": False,
            "actual_source_read_invoked": False,
            "payload_reparse_allowed": False,
            "source_discovery_allowed": False,
            "d_hot_directory_scan_allowed": False,
            "d_hot_actual_read_allowed": False,
            "refresh_invocation_allowed": False,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_parameter_apply": True,
            "no_parameter_staging_write": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
            "next_slice": "PS-Q18W explicit one-source no-read filesystem existence-check dry-run packet",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18v_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
