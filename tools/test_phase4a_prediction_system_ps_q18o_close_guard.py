# path: ./tools/test_phase4a_prediction_system_ps_q18o_close_guard.py
# desc: Close guard for PS-Q18O latest_prediction_summary_widget explicit one-source handoff design checkpoint.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint import CHECKER_VERSION, ONE_SOURCE_HANDOFF_DESIGN_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_handoff_design_checkpoint import ONE_SOURCE_HANDOFF_DESIGN_ACK

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18O_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_HANDOFF_DESIGN_CHECKPOINT_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint_guard.py"
CLOSE_REL = "tools/test_phase4a_prediction_system_ps_q18o_close_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.py",
    "tools/check_phase4a_prediction_system_ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.py",
    "tools/test_phase4a_prediction_system_ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18O_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_HANDOFF_DESIGN_CHECKPOINT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18o_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in (
        "warroom_page_mutation_allowed",
        "real_source_handoff_invoked",
        "source_artifact_resolution_allowed",
        "source_artifact_resolved",
        "source_artifact_path_materialized",
        "source_artifact_exists_checked",
        "source_artifact_schema_checked",
        "actual_source_read_allowed",
        "actual_source_read_invoked",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
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
        "LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_HANDOFF_DESIGN_CHECKPOINT_VERSION",
        "ONE_SOURCE_HANDOFF_DESIGN_ACK",
        "PS_Q18O_DECLARE_ONE_SOURCE_HANDOFF_DESIGN_ONLY",
        "DESIGN_ITEMS",
        "build_latest_prediction_summary_widget_one_source_handoff_design_checkpoint_rows",
        "build_latest_prediction_summary_widget_one_source_handoff_design_checkpoint_packet",
        "latest_prediction_summary_widget_one_source_handoff_design_checkpoint_only",
        "one_source_handoff_design_checkpoint_ready",
        "one_source_candidate_declared",
        "source_candidate_count_fixed_to_one",
        "explicit_design_ack_matched",
        "source_artifact_resolution_allowed",
        "source_artifact_path_materialized",
        "source_artifact_exists_checked",
        "source_artifact_schema_checked",
        "actual_source_read_allowed",
        "actual_source_read_invoked",
        "d_hot_actual_read_allowed",
        "q18n_validation_invoked_by_mount",
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
        'CHECKER = "ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.v1"',
        'ONE_SOURCE_HANDOFF_DESIGN_CHECK_VERSION = "latest_prediction_summary_widget_one_source_handoff_design_checkpoint.v1"',
        "build_ps_q18n_report",
        "build_latest_prediction_summary_widget_one_source_handoff_design_checkpoint_packet",
        "latest_prediction_summary_widget_one_source_handoff_design_checkpoint_only",
        "source_candidate_count_fixed_to_one",
        "source_artifact_path_materialized",
        "source_artifact_exists_checked",
        "actual_source_read_invoked",
        "PS-Q18P explicit one-source resolver contract preflight",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if "test_ps_q18o_validates_one_source_handoff_design_from_q18n_fixture" not in unit_text:
        failures.append("unit test must cover Q18N fixture design checkpoint")
    if "test_ps_q18o_packet_without_source_is_design_only_but_candidate_not_ready" not in unit_text:
        failures.append("unit test must cover design-only packet without candidate")
    if CLOSE_REL not in focused_text:
        failures.append("focused guard expected dirty set must include close guard")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.v1":
        failures.append("checker version mismatch")
    if ONE_SOURCE_HANDOFF_DESIGN_CHECK_VERSION != "latest_prediction_summary_widget_one_source_handoff_design_checkpoint.v1":
        failures.append("check version mismatch")
    if ONE_SOURCE_HANDOFF_DESIGN_ACK != "PS_Q18O_DECLARE_ONE_SOURCE_HANDOFF_DESIGN_ONLY":
        failures.append("design ack mismatch")

    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture design checkpoint should be ok: {report}")
    if report.get("use_observed_fixture") is not True:
        failures.append("observed fixture flag should be true")
    if report.get("source_q18n_report_valid") is not True:
        failures.append("source Q18N report should validate")
    if report.get("design_packet_valid") is not True:
        failures.append("design packet should validate")
    if report.get("design_validation_failures"):
        failures.append(f"design validation failures: {report.get('design_validation_failures')}")
    if report.get("design_row_count") != 8:
        failures.append("expected 8 design rows")
    if report.get("source_candidate_count") != 1:
        failures.append("expected exactly one source candidate")
    if report.get("handoff_candidate_ready") is not True:
        failures.append("handoff candidate should be ready")
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
        "latest_prediction_summary_widget_one_source_handoff_design_checkpoint_only",
        "one_source_handoff_design_checkpoint_ready",
        "one_source_candidate_declared",
        "source_candidate_count_fixed_to_one",
        "explicit_design_ack_matched",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    _assert_false_boundaries(report, failures)
    if report.get("recommended_first_validation") != "latest_prediction_summary_widget_one_source_handoff_design_checkpoint_guard":
        failures.append("recommended first validation mismatch")

    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing source should block checker report")
    if blocked.get("design_row_count") != 0:
        failures.append("blocked report should not emit observed design rows")
    if blocked.get("actual_source_read_invoked") is not False:
        failures.append("blocked report should not invoke actual read")
    if blocked.get("source_artifact_resolution_allowed") is not False:
        failures.append("blocked report should not allow source resolution")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")

    for marker in (
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q18O_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_HANDOFF_DESIGN_CHECKPOINT_2026-06-22.md",
        "# desc: PS-Q18O latest_prediction_summary_widget explicit one-source handoff design checkpoint after PS-Q18N.",
        "checker=check_phase4a_prediction_system_ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.v1",
        "one_source_handoff_design_check_version=latest_prediction_summary_widget_one_source_handoff_design_checkpoint.v1",
        "design_checkpoint_version=prediction_warroom_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.ps_q18o.v1",
        "source_q18n_checker=check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.v1",
        "selected_candidate_generated_at=2026-06-22T00:00:00Z",
        "selected_candidate_source_artifact_ref=fixture://ps_q18i/latest_prediction.json",
        "selected_candidate_market_uid=BTC-USD",
        "source_candidate_count=1",
        "one_source_handoff_design_ack=PS_Q18O_DECLARE_ONE_SOURCE_HANDOFF_DESIGN_ONLY",
        "latest_prediction_summary_widget_one_source_handoff_design_checkpoint_only=true",
        "one_source_handoff_design_checkpoint_ready=true",
        "source_candidate_count_fixed_to_one=true",
        "warroom_page_mutation_allowed=false",
        "source_artifact_resolution_allowed=false",
        "source_artifact_path_materialized=false",
        "source_artifact_exists_checked=false",
        "source_artifact_schema_checked=false",
        "actual_source_read_allowed=false",
        "actual_source_read_invoked=false",
        "payload_reparse_allowed=false",
        "d_hot_directory_scan_allowed=false",
        "d_hot_actual_read_allowed=false",
        "no_warroom_page_mutation",
        "no_source_artifact_resolution",
        "no_actual_source_read",
        "PS-Q18P: Explicit one-source resolver contract preflight",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "source_artifact_resolution_allowed=true",
        "source_artifact_resolved=true",
        "source_artifact_path_materialized=true",
        "source_artifact_exists_checked=true",
        "source_artifact_schema_checked=true",
        "actual_source_read_allowed=true",
        "actual_source_read_invoked=true",
        "payload_reparse_allowed=true",
        "source_discovery_allowed=true",
        "d_hot_directory_scan_allowed=true",
        "d_hot_actual_read_allowed=true",
        "q18n_validation_invoked_by_mount=true",
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
        "guard": "ps_q18o_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_one_source_handoff_design_checkpoint_closed_before_resolution_read_render_refresh_and_writes",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q18o_closed": not failures,
            "latest_prediction_summary_widget_one_source_handoff_design_checkpoint_only": True,
            "one_source_handoff_design_checkpoint_ready": True,
            "one_source_candidate_declared": True,
            "source_candidate_count_fixed_to_one": True,
            "explicit_design_ack_matched": True,
            "design_row_count": int(report.get("design_row_count") or 0),
            "source_candidate_count": int(report.get("source_candidate_count") or 0),
            "handoff_candidate_ready": bool(report.get("handoff_candidate_ready")),
            "selected_candidate_generated_at": report.get("selected_candidate_generated_at"),
            "selected_candidate_source_artifact_ref": report.get("selected_candidate_source_artifact_ref"),
            "selected_candidate_market_uid": report.get("selected_candidate_market_uid"),
            "warroom_page_mutation_allowed": False,
            "source_artifact_resolution_allowed": False,
            "source_artifact_path_materialized": False,
            "source_artifact_exists_checked": False,
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
            "next_slice": "PS-Q18P explicit one-source resolver contract preflight",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18o_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
