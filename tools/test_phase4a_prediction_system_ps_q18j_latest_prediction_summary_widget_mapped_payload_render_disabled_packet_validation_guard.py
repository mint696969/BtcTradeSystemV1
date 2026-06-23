# path: ./tools/test_phase4a_prediction_system_ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation_guard.py
# desc: Focused guard for PS-Q18J latest_prediction_summary_widget render-disabled packet validation with mapped real payload values.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation import CHECKER_VERSION, MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_VALIDATION_CHECK_VERSION, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18J_LATEST_PREDICTION_SUMMARY_WIDGET_MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_VALIDATION_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.py",
    "tools/check_phase4a_prediction_system_ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.py",
    "tools/test_phase4a_prediction_system_ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18J_LATEST_PREDICTION_SUMMARY_WIDGET_MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_VALIDATION_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18j_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation_guard.py",
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
        "LATEST_PREDICTION_SUMMARY_WIDGET_MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_VALIDATION_VERSION",
        "render_latest_prediction_summary_widget(props=candidate)",
        "build_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation",
        "read_only_component_skeleton_render_disabled",
        "component_packet_builder_invoked",
        "component_packet_valid",
        "mapped_payload_values_supplied_to_packet_builder",
        "real_payload_values_visible_in_component_packet",
        "component_source_generated_at",
        "component_source_artifact_ref",
        "actual_source_read_invoked_by_validation",
    ):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in ("import streamlit", "st.", "Path(", "open(", "read_text(", "read_bytes(", "write_text(", "data_read", "data_slice", "glob(", "rglob(", "send_order(", "create_order("):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        'CHECKER = "ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.v1"',
        'MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_VALIDATION_CHECK_VERSION = "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.v1"',
        "build_ps_q18i_report",
        "build_latest_prediction_summary_widget_real_payload_value_mapping_preflight_packet",
        "build_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation",
        "component_packet_builder_invoked",
        "real_payload_values_visible_in_component_packet",
        "PS-Q18K WarRoom mapped real payload render-disabled packet status row mount",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.v1":
        failures.append("checker version mismatch")
    if MAPPED_PAYLOAD_RENDER_DISABLED_PACKET_VALIDATION_CHECK_VERSION != "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.v1":
        failures.append("validation check version mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture validation should be ok: {report}")
    if report.get("source_q18i_report_valid") is not True:
        failures.append("source Q18I report should validate")
    if report.get("validation_packet_valid") is not True:
        failures.append("validation packet should validate")
    if report.get("component_packet_builder_invoked") is not True:
        failures.append("component packet builder should be invoked")
    if report.get("component_packet_valid") is not True:
        failures.append("component packet should be valid")
    if report.get("component_packet_state") != "read_only_component_skeleton_render_disabled":
        failures.append("component packet should remain render disabled")
    if report.get("component_missing_props") != []:
        failures.append("component missing props should be empty")
    for key, value in {
        "mapped_prediction_run_id": "ps_q18i_fixture_run",
        "mapped_market_uid": "BTC-USD",
        "mapped_source_generated_at": "2026-06-22T00:00:00Z",
        "mapped_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
        "component_source_generated_at": "2026-06-22T00:00:00Z",
        "component_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
    }.items():
        if report.get(key) != value:
            failures.append(f"mapped/component value mismatch: {key}")
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation_only", "render_disabled_component_packet_validation_only", "component_skeleton_packet_only", "mapped_payload_values_supplied_to_packet_builder", "real_payload_values_bound_to_props_candidate", "real_payload_values_visible_in_component_packet"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "real_payload_values_bound_to_component",
        "component_props_binding_allowed",
        "component_props_bound_to_component",
        "component_runtime_binding_allowed",
        "streamlit_render_allowed",
        "streamlit_render_invoked",
        "render_invocation_allowed",
        "real_prediction_widget_rendering_allowed",
        "actual_source_read_invoked_by_validation",
        "actual_source_read_allowed_by_validation",
        "payload_reparse_allowed",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
        "refresh_invocation_allowed",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "parameter_apply_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
    ):
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "checker=check_phase4a_prediction_system_ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.v1",
        "mapped_payload_render_disabled_packet_validation_check_version=latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.v1",
        "validation_version=prediction_warroom_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation.ps_q18j.v1",
        "source_q18i_checker=check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.v1",
        "validation_packet_valid=true",
        "component_packet_builder_invoked=true",
        "component_packet_valid=true",
        "component_packet_state=read_only_component_skeleton_render_disabled",
        "component_missing_props=[]",
        "mapped_prediction_run_id=ps_q18i_fixture_run",
        "mapped_market_uid=BTC-USD",
        "component_source_generated_at=2026-06-22T00:00:00Z",
        "component_source_artifact_ref=fixture://ps_q18i/latest_prediction.json",
        "real_payload_values_visible_in_component_packet=true",
        "streamlit_render_invoked=false",
        "actual_source_read_invoked_by_validation=false",
        "no_streamlit_render",
        "no_real_prediction_widget_rendering",
        "PS-Q18K: WarRoom mapped real payload render-disabled packet status row mount",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18j_latest_prediction_summary_widget_mapped_payload_render_disabled_packet_validation_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
