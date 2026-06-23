# path: ./tools/test_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract_guard.py
# desc: Focused guard for PS-Q17Q WarRoom prediction widget mount contract.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract import CHECKER_VERSION, MOUNT_CONTRACT_VERSION, MOUNT_ZONE_ORDER, REQUIRED_MOUNT_FIELDS, WIDGET_FAMILY_ORDER, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17Q_WARROOM_PREDICTION_WIDGET_MOUNT_CONTRACT_2026-06-22.md"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract.py",
    "tools/test_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17Q_WARROOM_PREDICTION_WIDGET_MOUNT_CONTRACT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17q_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in ("read_only", "non_executing", "mount_contract_only", "contract_only", "diagnostic_only", "warroom_widget_design_premise", "fallback_display_only"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "warroom_widget_implementation_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_page_import_patch_allowed",
        "warroom_mount_patch_allowed",
        "component_import_allowed",
        "streamlit_render_allowed",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "d_hot_actual_read_allowed",
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
    for path in (TOOL, UNIT, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        "CHECKER = \"ps_q17q_warroom_prediction_widget_mount_contract\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract.v1\"",
        "MOUNT_CONTRACT_VERSION = \"warroom_prediction_widget_mount_contract.v1\"",
        "PS_Q17P_SOURCE_CHECKER_VERSION",
        "MOUNT_ZONE_ORDER",
        "MOUNT_ZONE_BY_WIDGET",
        "REQUIRED_MOUNT_FIELDS",
        "prediction_overview_zone",
        "prediction_realtime_review_zone",
        "prediction_operator_support_zone",
        "component_import_allowed",
        "streamlit_render_allowed",
        "fallback_display_required",
        "warroom_page_import_patch_allowed",
        "PS-Q17R WarRoom prediction widget read-only component skeleton contract",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    for forbidden in (
        "from pathlib import Path",
        "read_text(",
        "write_text(",
        "write_bytes(",
        "open(",
        "mkdir(",
        "unlink(",
        "replace(",
        "data_read",
        "data_slice",
        "allow_actual_read=True",
        "build_report(hot_root=",
        "append_decision(",
        "append_command(",
        "send_order(",
        "create_order(",
    ):
        if forbidden in tool_text:
            failures.append(f"forbidden tool token: {forbidden}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract.v1":
        failures.append("checker version mismatch")
    if MOUNT_CONTRACT_VERSION != "warroom_prediction_widget_mount_contract.v1":
        failures.append("mount contract version mismatch")
    if tuple(MOUNT_ZONE_ORDER) != ("prediction_overview_zone", "prediction_realtime_review_zone", "prediction_operator_support_zone"):
        failures.append("mount zone order mismatch")
    if len(WIDGET_FAMILY_ORDER) != 12:
        failures.append("widget family order should have 12 entries")
    for field in ("widget_family_id", "source_packet_id", "mount_zone_id", "mount_slot_id", "attach_after_widget_family_id", "component_module_contract", "component_import_allowed", "streamlit_render_allowed", "fallback_display_required", "page_mutation_allowed"):
        if field not in REQUIRED_MOUNT_FIELDS:
            failures.append(f"required mount field missing: {field}")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture mount contract should be ok: {report}")
    if report.get("mount_row_count") != 12:
        failures.append("expected 12 mount rows")
    if report.get("mount_zone_count") != 3:
        failures.append("expected 3 mount zones")
    if report.get("fallback_display_required_count") != 12:
        failures.append("expected fallback display for all rows")
    if report.get("component_import_blockers") != list(WIDGET_FAMILY_ORDER):
        failures.append("all widget families must block component imports")
    if report.get("streamlit_render_blockers") != list(WIDGET_FAMILY_ORDER):
        failures.append("all widget families must block streamlit rendering")
    if report.get("page_mutation_blockers") != list(WIDGET_FAMILY_ORDER):
        failures.append("all widget families must block page mutation")
    rows = {row.get("widget_family_id"): row for row in report.get("mount_rows", [])}
    expected_zones = {
        "latest_prediction_summary_widget": "prediction_overview_zone",
        "source_quality_freshness_widget": "prediction_overview_zone",
        "warning_blocker_widget": "prediction_overview_zone",
        "producer_freshness_status_widget": "prediction_overview_zone",
        "runtime_boundary_safety_widget": "prediction_overview_zone",
        "prediction_delta_widget": "prediction_realtime_review_zone",
        "scenario_trace_widget": "prediction_realtime_review_zone",
        "evidence_weighting_widget": "prediction_realtime_review_zone",
        "invalidation_rewrite_widget": "prediction_realtime_review_zone",
        "signal_strength_calibration_widget": "prediction_realtime_review_zone",
        "parameter_candidate_comparison_widget": "prediction_operator_support_zone",
        "replay_outcome_calibration_widget": "prediction_operator_support_zone",
    }
    for widget_id, zone in expected_zones.items():
        if rows.get(widget_id, {}).get("mount_zone_id") != zone:
            failures.append(f"mount zone mismatch: {widget_id}")
    for row in report.get("mount_rows", []):
        if row.get("mount_contract_state") != "ready_for_future_mount_contract_render_disabled":
            failures.append(f"mount contract state mismatch: {row}")
        for key in ("component_import_allowed", "streamlit_render_allowed", "page_mutation_allowed", "warroom_mount_patch_allowed", "refresh_invocation_allowed", "write_or_apply_allowed"):
            if row.get(key) is not False:
                failures.append(f"row boundary should stay false: {row.get('widget_family_id')}:{key}")
        if row.get("fallback_display_required") is not True:
            failures.append(f"fallback display must be required: {row}")
        if not str(row.get("next_validation", "")).endswith("_mount_contract_guard"):
            failures.append(f"next validation should be mount contract guard: {row}")
    _assert_false_boundaries(report, failures)
    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing Q17P source should block")
    if blocked.get("mount_rows") or blocked.get("mount_zone_rows"):
        failures.append("blocked report must not emit mount rows")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract.v1",
        "mount_contract_version=warroom_prediction_widget_mount_contract.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint.v1",
        "mount_contract_only=true",
        "warroom_widget_rendering_allowed=false",
        "warroom_page_mutation_allowed=false",
        "warroom_page_import_patch_allowed=false",
        "component_import_allowed=false",
        "streamlit_render_allowed=false",
        "fallback_display_only=true",
        "prediction_overview_zone",
        "prediction_realtime_review_zone",
        "prediction_operator_support_zone",
        "fallback_display_required=true",
        "no_warroom_page_import_patch",
        "no_component_import_patch",
        "no_streamlit_render",
        "PS-Q17R: WarRoom prediction widget read-only component skeleton contract",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "warroom_widget_implementation_allowed=true",
        "warroom_widget_rendering_allowed=true",
        "warroom_page_mutation_allowed=true",
        "warroom_page_import_patch_allowed=true",
        "warroom_mount_patch_allowed=true",
        "component_import_allowed=true",
        "streamlit_render_allowed=true",
        "d_hot_actual_read_allowed=true",
        "confidence_increase_allowed=true",
        "parameter_apply_allowed=true",
        "parameter_staging_write_allowed=true",
        "ledger_append_allowed=true",
        "autotrade_trigger_allowed=true",
        "broker_private_api_allowed=true",
        "warroom_ui_trigger_enabled=true",
        "refresh_invocation_allowed=true",
        "scheduler_enabled=true",
    ):
        if forbidden in doc_text:
            failures.append(f"forbidden doc marker present: {forbidden}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q17q_warroom_prediction_widget_mount_contract_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17q_warroom_prediction_widget_mount_contract_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
