# path: ./tools/test_phase4a_prediction_system_ps_q18y_close_guard.py
# desc: Close guard for PS-Q18Y latest_prediction_summary_widget one-source no-read filesystem existence-check dry-run result display contract.

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
FOCUSED_GUARD = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.py",
    "tools/check_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.py",
    "tools/test_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18Y_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18y_close_guard.py",
}
TRUE_KEYS = (
    "read_only",
    "non_executing",
    "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_only",
    "one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_ready",
    "filesystem_existence_check_dry_run_result_display_contract_declared",
    "filesystem_existence_check_dry_run_result_placeholder_preserved",
    "one_source_candidate_preserved",
    "source_candidate_count_fixed_to_one",
    "explicit_dry_run_result_display_contract_ack_matched",
    "path_shape_preview_string_only",
)
FALSE_KEYS = (
    "filesystem_existence_check_dry_run_result_available",
    "filesystem_existence_check_dry_run_result_display_mount_allowed",
    "filesystem_existence_check_dry_run_result_display_mounted",
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
    "q18x_validation_invoked_by_mount",
    "q18w_validation_invoked_by_mount",
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
        "PS_Q18Y_DECLARE_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ONLY",
        "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_KIND",
        "FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_STATE",
        "build_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_packet",
        "filesystem_existence_check_dry_run_result_display_mount_allowed",
        "filesystem_existence_check_dry_run_result_display_mounted",
        "streamlit_render_allowed",
        "streamlit_render_invoked",
        "actual_source_read_invoked",
        "TRUE_BOUNDARIES",
        "FALSE_BOUNDARIES",
    ):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in (
        "import streamlit", "st.", "Path(", "open(", "read_text(", "read_bytes(", "write_text(", "write_bytes(",
        "data_read", "data_slice", "glob(", "rglob(", "exists(", "is_file(", "stat(", "render_latest_prediction_summary_widget(",
        "send_order(", "create_order(",
    ):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")

    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        CHECKER_VERSION,
        ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_CHECK_VERSION,
        "build_ps_q18x_report",
        "PS-Q18Z explicit one-source no-read filesystem existence-check dry-run result display packet",
        '"filesystem_existence_check_dry_run_result_display_mount_allowed"',
        '"streamlit_render_allowed"',
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    focused_text = _read(FOCUSED_GUARD) if FOCUSED_GUARD.exists() else ""
    if "tools/test_phase4a_prediction_system_ps_q18y_close_guard.py" not in focused_text:
        failures.append("focused guard expected dirty set must include close guard")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18y_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.v1":
        failures.append("checker version mismatch")
    if ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_CHECK_VERSION != "latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract.v1":
        failures.append("check version mismatch")
    if ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ACK != "PS_Q18Y_DECLARE_ONE_SOURCE_NO_READ_FILESYSTEM_EXISTENCE_CHECK_DRY_RUN_RESULT_DISPLAY_CONTRACT_ONLY":
        failures.append("display contract ack mismatch")

    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture display contract should be ok: {report}")
    if report.get("source_q18x_report_valid") is not True:
        failures.append("source Q18X report should validate")
    if report.get("dry_run_result_display_contract_packet_valid") is not True:
        failures.append("display contract packet should validate")
    if report.get("dry_run_result_display_contract_validation_failures"):
        failures.append(f"display contract validation failures: {report.get('dry_run_result_display_contract_validation_failures')}")
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
    if blocked.get("dry_run_result_display_contract_row_count") != 0:
        failures.append("blocked report should not emit observed display contract rows")
    for key in ("filesystem_existence_check_dry_run_result_available", "filesystem_existence_check_dry_run_result_display_mount_allowed", "filesystem_existence_check_dry_run_result_display_mounted", "streamlit_render_invoked", "actual_source_read_invoked"):
        if blocked.get(key) is not False:
            failures.append(f"blocked {key} must stay false")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")

    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "read_only=true",
        "non_executing=true",
        "filesystem_existence_check_dry_run_result_display_mount_allowed=false",
        "filesystem_existence_check_dry_run_result_display_mounted=false",
        "streamlit_render_allowed=false",
        "streamlit_render_invoked=false",
        "real_prediction_widget_rendering_allowed=false",
        "no_warroom_display_mount",
        "PS-Q18Z: Explicit one-source no-read filesystem existence-check dry-run result display packet",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "filesystem_existence_check_dry_run_result_display_mount_allowed=true",
        "filesystem_existence_check_dry_run_result_display_mounted=true",
        "streamlit_render_allowed=true",
        "streamlit_render_invoked=true",
        "real_prediction_widget_rendering_allowed=true",
        "source_artifact_exists_checked=true",
        "source_artifact_exists_result_available=true",
        "actual_source_read_invoked=true",
        "runtime_artifact_write_allowed=true",
        "broker_private_api_allowed=true",
    ):
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
        "guard": "ps_q18y_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_one_source_no_read_filesystem_existence_check_dry_run_result_display_contract_before_mount_render_exists_result_schema_read_refresh_and_writes",
        "contract": {
            "ps_q18y_closed": not failures,
            "dry_run_result_display_contract_row_count": int(report.get("dry_run_result_display_contract_row_count") or 0),
            "source_candidate_count": int(report.get("source_candidate_count") or 0),
            "dry_run_result_display_contract_candidate_ready": bool(report.get("dry_run_result_display_contract_candidate_ready")),
            "filesystem_existence_check_dry_run_result_display_contract_kind": report.get("filesystem_existence_check_dry_run_result_display_contract_kind"),
            "filesystem_existence_check_dry_run_result_display_contract_state": report.get("filesystem_existence_check_dry_run_result_display_contract_state"),
            "filesystem_existence_check_dry_run_result_available": False,
            "filesystem_existence_check_dry_run_result_display_mount_allowed": False,
            "filesystem_existence_check_dry_run_result_display_mounted": False,
            "streamlit_render_allowed": False,
            "streamlit_render_invoked": False,
            "real_prediction_widget_rendering_allowed": False,
            "actual_source_read_invoked": False,
            "path_shape_preview": report.get("path_shape_preview"),
            "next_slice": "PS-Q18Z explicit one-source no-read filesystem existence-check dry-run result display packet",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18y_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
