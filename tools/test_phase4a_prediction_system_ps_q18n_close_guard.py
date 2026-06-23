# path: ./tools/test_phase4a_prediction_system_ps_q18n_close_guard.py
# desc: Close guard for PS-Q18N latest_prediction_summary_widget real-source handoff preflight mount.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount import CHECKER_VERSION, REAL_SOURCE_HANDOFF_PREFLIGHT_MOUNT_VERSION, WARROOM_PAGE_TARGET, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
WARROOM_PAGE = REPO_ROOT / WARROOM_PAGE_TARGET
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18N_LATEST_PREDICTION_SUMMARY_WIDGET_REAL_SOURCE_HANDOFF_PREFLIGHT_MOUNT_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount_guard.py"
CLOSE_REL = "tools/test_phase4a_prediction_system_ps_q18n_close_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel.py",
    "tools/check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.py",
    "tools/test_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18N_LATEST_PREDICTION_SUMMARY_WIDGET_REAL_SOURCE_HANDOFF_PREFLIGHT_MOUNT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18n_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in (
        "real_source_handoff_invoked",
        "actual_source_resolution_allowed",
        "actual_source_resolved",
        "actual_source_read_allowed",
        "actual_source_read_invoked",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
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
    for path in (WARROOM_PAGE, COMPONENT, TOOL, UNIT, DOC, REPO_ROOT / FOCUSED_GUARD):
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
        "LATEST_PREDICTION_SUMMARY_WIDGET_REAL_SOURCE_HANDOFF_PREFLIGHT_PANEL_VERSION",
        "HANDOFF_ITEMS",
        "build_latest_prediction_summary_widget_real_source_handoff_preflight_rows",
        "build_latest_prediction_summary_widget_real_source_handoff_preflight_packet",
        "latest_prediction_summary_widget_real_source_handoff_preflight_mount_only",
        "warroom_handoff_preflight_rows_ready",
        "operator_summary_report_display_only",
        "real_source_handoff_preflight_only",
        "real_source_handoff_invoked",
        "actual_source_resolution_allowed",
        "actual_source_resolved",
        "actual_source_read_allowed",
        "actual_source_read_invoked",
        "source_discovery_allowed",
        "d_hot_actual_read_allowed",
        "handoff_candidate_ready",
        "candidate_generated_at",
        "candidate_source_artifact_ref",
        "candidate_market_uid",
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

    page_text = _read(WARROOM_PAGE) if WARROOM_PAGE.exists() else ""
    for marker in (
        "from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel import (",
        "build_latest_prediction_summary_widget_real_source_handoff_preflight_packet",
        "def _prediction_warroom_latest_prediction_summary_real_source_handoff_preflight_display_rows(packet: dict) -> list[dict]:",
        "def _render_prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_section() -> None:",
        "with live_shell.render_folded_section(\"Prediction WarRoom latest summary real source handoff preflight\", expanded=False):",
        "_render_prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_section()",
        "latest summary real-source handoff rows={rows} / candidate_ready={ready} / real_handoff=false / actual_read=false / render=false",
        "st.dataframe(handoff_rows, width=\"stretch\", hide_index=True)",
    ):
        if marker not in page_text:
            failures.append(f"missing page marker: {marker}")
    if page_text.count("_render_prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_section(") != 2:
        failures.append("real source handoff preflight render function should have definition and page-body call only")
    for forbidden in (
        "build_ps_q18m_report(",
        "build_ps_q18j_report(",
        "actual_source_resolution_allowed=True",
        "actual_source_read_invoked=True",
        "source_discovery_allowed=True",
        "d_hot_actual_read_allowed=True",
        "streamlit_render_invoked=True",
        "real_prediction_widget_rendering_allowed=True",
        "send_order(",
        "create_order(",
        "parameter_apply_allowed=True",
    ):
        if forbidden in page_text:
            failures.append(f"forbidden page token: {forbidden}")

    tool_text = _read(TOOL) if TOOL.exists() else ""
    unit_text = _read(UNIT) if UNIT.exists() else ""
    focused_text = _read(REPO_ROOT / FOCUSED_GUARD) if (REPO_ROOT / FOCUSED_GUARD).exists() else ""
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        'CHECKER = "ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.v1"',
        'REAL_SOURCE_HANDOFF_PREFLIGHT_MOUNT_VERSION = "latest_prediction_summary_widget_real_source_handoff_preflight_mount.v1"',
        "build_ps_q18m_report",
        "build_latest_prediction_summary_widget_real_source_handoff_preflight_packet",
        "latest_prediction_summary_widget_real_source_handoff_preflight_mount_only",
        "actual_source_resolution_allowed",
        "actual_source_read_invoked",
        "PS-Q18O explicit one-source handoff design checkpoint",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if "test_ps_q18n_validates_real_source_handoff_preflight_from_q18m_fixture" not in unit_text:
        failures.append("unit test must cover Q18M fixture handoff preflight")
    if "test_ps_q18n_page_safe_packet_has_no_candidate_and_no_resolution_or_read" not in unit_text:
        failures.append("unit test must cover page-safe packet no candidate/read")
    if CLOSE_REL not in focused_text:
        failures.append("focused guard expected dirty set must include close guard")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.v1":
        failures.append("checker version mismatch")
    if REAL_SOURCE_HANDOFF_PREFLIGHT_MOUNT_VERSION != "latest_prediction_summary_widget_real_source_handoff_preflight_mount.v1":
        failures.append("mount version mismatch")

    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture handoff preflight should be ok: {report}")
    if report.get("use_observed_fixture") is not True:
        failures.append("observed fixture flag should be true")
    if report.get("source_q18m_report_valid") is not True:
        failures.append("source Q18M report should validate")
    if report.get("handoff_packet_valid") is not True:
        failures.append("handoff packet should validate")
    if report.get("page_handoff_packet_valid") is not True:
        failures.append("page handoff packet should validate")
    if report.get("handoff_validation_failures"):
        failures.append(f"handoff validation failures: {report.get('handoff_validation_failures')}")
    if report.get("page_handoff_validation_failures"):
        failures.append(f"page handoff validation failures: {report.get('page_handoff_validation_failures')}")
    if report.get("page_validation_failures"):
        failures.append(f"page validation failures: {report.get('page_validation_failures')}")
    if report.get("handoff_row_count") != 6:
        failures.append("expected 6 observed handoff rows")
    if report.get("page_handoff_row_count") != 6:
        failures.append("expected 6 page-safe handoff rows")
    if report.get("handoff_candidate_ready") is not True:
        failures.append("observed handoff candidate should be ready")
    if report.get("page_handoff_candidate_ready") is not False:
        failures.append("page-safe handoff candidate should not be ready")
    for key, value in {
        "candidate_generated_at": "2026-06-22T00:00:00Z",
        "candidate_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
        "candidate_market_uid": "BTC-USD",
    }.items():
        if report.get(key) != value:
            failures.append(f"candidate mismatch: {key}")
    for key in (
        "read_only",
        "non_executing",
        "latest_prediction_summary_widget_real_source_handoff_preflight_mount_only",
        "warroom_handoff_preflight_rows_ready",
        "operator_summary_report_display_only",
        "real_source_handoff_preflight_only",
        "warroom_page_mutation_allowed",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    _assert_false_boundaries(report, failures)
    if report.get("recommended_first_validation") != "latest_prediction_summary_widget_real_source_handoff_preflight_mount_guard":
        failures.append("recommended first validation mismatch")

    blocked = build_report(page_text="")
    if blocked.get("ok") is not False:
        failures.append("missing source should block")
    if blocked.get("handoff_row_count") != 0:
        failures.append("blocked report should not emit observed handoff rows")
    if blocked.get("actual_source_read_invoked") is not False:
        failures.append("blocked report should not invoke actual read")
    if blocked.get("actual_source_resolution_allowed") is not False:
        failures.append("blocked report should not allow source resolution")
    if blocked.get("q18m_validation_invoked_by_mount") is not False:
        failures.append("blocked report should not invoke Q18M from mount")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")

    for marker in (
        "checker=check_phase4a_prediction_system_ps_q18n_latest_prediction_summary_widget_real_source_handoff_preflight_mount.v1",
        "real_source_handoff_preflight_mount_version=latest_prediction_summary_widget_real_source_handoff_preflight_mount.v1",
        "panel_version=prediction_warroom_latest_prediction_summary_widget_real_source_handoff_preflight_panel.ps_q18n.v1",
        "source_q18m_checker=check_phase4a_prediction_system_ps_q18m_latest_prediction_summary_widget_operator_value_summary_mount.v1",
        "candidate_generated_at=2026-06-22T00:00:00Z",
        "candidate_source_artifact_ref=fixture://ps_q18i/latest_prediction.json",
        "candidate_market_uid=BTC-USD",
        "handoff_row_count=6",
        "page_handoff_row_count=6",
        "handoff_candidate_ready=true",
        "page_handoff_candidate_ready=false",
        "latest_prediction_summary_widget_real_source_handoff_preflight_mount_only=true",
        "warroom_handoff_preflight_rows_ready=true",
        "real_source_handoff_preflight_only=true",
        "real_source_handoff_invoked=false",
        "actual_source_resolution_allowed=false",
        "actual_source_resolved=false",
        "actual_source_read_allowed=false",
        "actual_source_read_invoked=false",
        "source_discovery_allowed=false",
        "d_hot_directory_scan_allowed=false",
        "d_hot_actual_read_allowed=false",
        "q18m_validation_invoked_by_mount=false",
        "q18j_validation_invoked_by_mount=false",
        "component_packet_builder_invoked_by_mount=false",
        "streamlit_render_invoked=false",
        "no_source_artifact_resolution",
        "no_actual_source_read",
        "PS-Q18O: Explicit one-source handoff design checkpoint",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "real_source_handoff_invoked=true",
        "actual_source_resolution_allowed=true",
        "actual_source_resolved=true",
        "actual_source_read_allowed=true",
        "actual_source_read_invoked=true",
        "payload_reparse_allowed=true",
        "source_discovery_allowed=true",
        "d_hot_directory_scan_allowed=true",
        "d_hot_actual_read_allowed=true",
        "q18m_validation_invoked_by_mount=true",
        "q18j_validation_invoked_by_mount=true",
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
        "guard": "ps_q18n_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_real_source_handoff_preflight_mount_closed_before_resolution_read_render_refresh_and_writes",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q18n_closed": not failures,
            "latest_prediction_summary_widget_real_source_handoff_preflight_mount_only": True,
            "warroom_handoff_preflight_rows_ready": True,
            "operator_summary_report_display_only": True,
            "real_source_handoff_preflight_only": True,
            "handoff_row_count": int(report.get("handoff_row_count") or 0),
            "page_handoff_row_count": int(report.get("page_handoff_row_count") or 0),
            "handoff_candidate_ready": bool(report.get("handoff_candidate_ready")),
            "page_handoff_candidate_ready": bool(report.get("page_handoff_candidate_ready")),
            "candidate_generated_at": report.get("candidate_generated_at"),
            "candidate_source_artifact_ref": report.get("candidate_source_artifact_ref"),
            "candidate_market_uid": report.get("candidate_market_uid"),
            "warroom_page_mutation_allowed": True,
            "real_source_handoff_invoked": False,
            "actual_source_resolution_allowed": False,
            "actual_source_resolved": False,
            "actual_source_read_allowed": False,
            "actual_source_read_invoked": False,
            "payload_reparse_allowed": False,
            "source_discovery_allowed": False,
            "d_hot_directory_scan_allowed": False,
            "d_hot_actual_read_allowed": False,
            "q18m_validation_invoked_by_mount": False,
            "q18j_validation_invoked_by_mount": False,
            "component_packet_builder_invoked_by_mount": False,
            "streamlit_render_invoked": False,
            "real_prediction_widget_rendering_allowed": False,
            "refresh_invocation_allowed": False,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_parameter_apply": True,
            "no_parameter_staging_write": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
            "next_slice": "PS-Q18O explicit one-source handoff design checkpoint",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18n_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
