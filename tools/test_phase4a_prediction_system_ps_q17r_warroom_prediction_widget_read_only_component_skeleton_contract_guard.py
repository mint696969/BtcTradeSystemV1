# path: ./tools/test_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract_guard.py
# desc: Focused guard for PS-Q17R WarRoom prediction widget read-only component skeleton contract.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract import CHECKER_VERSION, COMPONENT_SKELETON_CONTRACT_VERSION, REQUIRED_COMPONENT_PROPS, REQUIRED_COMPONENT_ROW_FIELDS, WIDGET_FAMILY_ORDER, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17R_WARROOM_PREDICTION_WIDGET_READ_ONLY_COMPONENT_SKELETON_CONTRACT_2026-06-22.md"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract.py",
    "tools/test_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17R_WARROOM_PREDICTION_WIDGET_READ_ONLY_COMPONENT_SKELETON_CONTRACT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17r_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in ("read_only", "non_executing", "component_skeleton_contract_only", "contract_only", "diagnostic_only", "warroom_widget_design_premise", "fallback_component_only"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "component_file_creation_allowed",
        "component_import_allowed",
        "streamlit_render_allowed",
        "warroom_widget_implementation_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_page_import_patch_allowed",
        "warroom_mount_patch_allowed",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "d_hot_actual_read_allowed",
        "actual_source_read_allowed",
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
        "CHECKER = \"ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract.v1\"",
        "COMPONENT_SKELETON_CONTRACT_VERSION = \"warroom_prediction_widget_read_only_component_skeleton_contract.v1\"",
        "PS_Q17Q_SOURCE_CHECKER_VERSION",
        "REQUIRED_COMPONENT_PROPS",
        "REQUIRED_COMPONENT_ROW_FIELDS",
        "COMPONENT_MODULE_PREFIX",
        "component_file_creation_allowed",
        "component_import_allowed",
        "streamlit_render_allowed",
        "fallback_component_required",
        "actual_source_read_allowed",
        "PS-Q17S WarRoom prediction widget read-only component skeleton implementation",
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
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract.v1":
        failures.append("checker version mismatch")
    if COMPONENT_SKELETON_CONTRACT_VERSION != "warroom_prediction_widget_read_only_component_skeleton_contract.v1":
        failures.append("component skeleton contract version mismatch")
    for field in (
        "widget_family_id",
        "source_packet_id",
        "mount_zone_id",
        "mount_slot_id",
        "source_generated_at",
        "source_artifact_ref",
        "release_gate_state",
        "fallback_reason_codes",
        "operator_summary_ja",
        "read_only",
    ):
        if field not in REQUIRED_COMPONENT_PROPS:
            failures.append(f"required component prop missing: {field}")
    for field in (
        "widget_family_id",
        "source_packet_id",
        "mount_zone_id",
        "component_module_path",
        "component_function_name",
        "props_contract_fields",
        "fallback_component_required",
        "component_file_creation_allowed",
        "component_import_allowed",
        "streamlit_render_allowed",
        "page_mutation_allowed",
    ):
        if field not in REQUIRED_COMPONENT_ROW_FIELDS:
            failures.append(f"required component row field missing: {field}")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture component skeleton contract should be ok: {report}")
    if report.get("component_row_count") != 12:
        failures.append("expected 12 component rows")
    if report.get("fallback_component_required_count") != 12:
        failures.append("expected fallback component for all rows")
    if report.get("component_file_creation_blockers") != list(WIDGET_FAMILY_ORDER):
        failures.append("all widget families must block component file creation")
    if report.get("component_import_blockers") != list(WIDGET_FAMILY_ORDER):
        failures.append("all widget families must block component imports")
    if report.get("streamlit_render_blockers") != list(WIDGET_FAMILY_ORDER):
        failures.append("all widget families must block streamlit rendering")
    if report.get("actual_source_read_blockers") != list(WIDGET_FAMILY_ORDER):
        failures.append("all widget families must block actual source reads")
    rows = {row.get("widget_family_id"): row for row in report.get("component_rows", [])}
    for widget_id in WIDGET_FAMILY_ORDER:
        row = rows.get(widget_id, {})
        if not row:
            failures.append(f"missing component row: {widget_id}")
            continue
        if row.get("component_module_path") != f"btcts.apps.operator_ui.components.prediction_widgets.{widget_id}":
            failures.append(f"component module path mismatch: {widget_id}")
        if row.get("component_function_name") != f"render_{widget_id}":
            failures.append(f"component function name mismatch: {widget_id}")
        if row.get("props_contract_fields") != list(REQUIRED_COMPONENT_PROPS):
            failures.append(f"props contract mismatch: {widget_id}")
        if row.get("component_contract_state") != "ready_for_future_read_only_component_skeleton_render_disabled":
            failures.append(f"component contract state mismatch: {widget_id}")
        for key in ("component_file_creation_allowed", "component_import_allowed", "streamlit_render_allowed", "page_mutation_allowed", "warroom_mount_patch_allowed", "refresh_invocation_allowed", "actual_source_read_allowed", "write_or_apply_allowed"):
            if row.get(key) is not False:
                failures.append(f"row boundary should stay false: {widget_id}:{key}")
        if row.get("fallback_component_required") is not True:
            failures.append(f"fallback component must be required: {widget_id}")
        if not str(row.get("next_validation", "")).endswith("_component_skeleton_contract_guard"):
            failures.append(f"next validation should be component skeleton contract guard: {widget_id}")
    _assert_false_boundaries(report, failures)
    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing Q17Q source should block")
    if blocked.get("component_rows"):
        failures.append("blocked report must not emit component rows")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract.v1",
        "component_skeleton_contract_version=warroom_prediction_widget_read_only_component_skeleton_contract.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17q_warroom_prediction_widget_mount_contract.v1",
        "component_skeleton_contract_only=true",
        "component_file_creation_allowed=false",
        "component_import_allowed=false",
        "streamlit_render_allowed=false",
        "fallback_component_only=true",
        "actual_source_read_allowed=false",
        "component_row_count=12",
        "fallback_component_required_count=12",
        "no_component_file_creation",
        "no_component_import_patch",
        "no_streamlit_render",
        "no_actual_source_read",
        "PS-Q17S: WarRoom prediction widget read-only component skeleton implementation",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "component_file_creation_allowed=true",
        "component_import_allowed=true",
        "streamlit_render_allowed=true",
        "warroom_widget_implementation_allowed=true",
        "warroom_widget_rendering_allowed=true",
        "warroom_page_mutation_allowed=true",
        "warroom_page_import_patch_allowed=true",
        "warroom_mount_patch_allowed=true",
        "d_hot_actual_read_allowed=true",
        "actual_source_read_allowed=true",
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
    result = {"ok": not failures, "guard": "ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17r_warroom_prediction_widget_read_only_component_skeleton_contract_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
