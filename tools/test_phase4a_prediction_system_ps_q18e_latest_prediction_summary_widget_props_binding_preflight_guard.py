# path: ./tools/test_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight_guard.py
# desc: Focused guard for PS-Q18E latest_prediction_summary_widget props binding preflight.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight import CHECKER_VERSION, LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_CHECK_VERSION, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_props_binding_preflight.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18E_LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_props_binding_preflight.py",
    "tools/check_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight.py",
    "tools/test_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18E_LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18e_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight_guard.py",
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
        "LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_VERSION",
        "REQUIRED_COMPONENT_PROPS",
        "build_latest_prediction_summary_widget_props_candidate",
        "build_latest_prediction_summary_widget_props_binding_preflight_packet",
        "source_generated_at",
        "source_artifact_ref",
        "props_binding_preflight_only",
        "props_value_binding_deferred",
        "real_payload_values_bound",
        "widget_props_binding_allowed",
        "widget_props_bound_to_component",
        "render_invocation_allowed",
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
        "data_read",
        "data_slice",
        "glob(",
        "rglob(",
        "render_latest_prediction_summary_widget(",
        "send_order(",
        "create_order(",
    ):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        'CHECKER = "ps_q18e_latest_prediction_summary_widget_props_binding_preflight"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight.v1"',
        'LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_CHECK_VERSION = "latest_prediction_summary_widget_props_binding_preflight.v1"',
        "build_ps_q18d_report",
        "build_latest_prediction_summary_widget_props_binding_preflight_packet",
        "latest_prediction_summary_widget_props_binding_preflight_only",
        "props_candidate_ready",
        "props_contract_complete",
        "widget_props_bound_to_component",
        "render_invocation_allowed",
        "PS-Q18F latest_prediction_summary_widget props candidate status row mount",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight.v1":
        failures.append("checker version mismatch")
    if LATEST_PREDICTION_SUMMARY_WIDGET_PROPS_BINDING_PREFLIGHT_CHECK_VERSION != "latest_prediction_summary_widget_props_binding_preflight.v1":
        failures.append("props binding check version mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture props preflight should be ok: {report}")
    if report.get("source_q18d_report_valid") is not True:
        failures.append("source Q18D report should validate")
    if report.get("props_packet_valid") is not True:
        failures.append("props packet should validate")
    if report.get("missing_required_component_props") != []:
        failures.append("missing required component props should be empty")
    if report.get("schema_probe_row_count") != 4:
        failures.append("expected schema row count 4")
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_props_binding_preflight_only", "props_candidate_ready", "props_contract_complete", "props_value_binding_deferred"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "real_payload_values_bound",
        "widget_props_binding_allowed",
        "widget_props_bound_to_component",
        "render_invocation_allowed",
        "real_prediction_widget_rendering_allowed",
        "actual_source_read_invoked_by_props_preflight",
        "actual_source_read_allowed_by_props_preflight",
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
        "parameter_staging_write_allowed",
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
        "checker=check_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight.v1",
        "latest_prediction_summary_widget_props_binding_preflight_check_version=latest_prediction_summary_widget_props_binding_preflight.v1",
        "preflight_version=prediction_warroom_latest_prediction_summary_widget_props_binding_preflight.ps_q18e.v1",
        "source_q18d_checker=check_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe.v1",
        "missing_required_component_props=[]",
        "latest_prediction_summary_widget_props_binding_preflight_only=true",
        "props_candidate_ready=true",
        "props_contract_complete=true",
        "props_value_binding_deferred=true",
        "real_payload_values_bound=false",
        "widget_props_binding_allowed=false",
        "widget_props_bound_to_component=false",
        "render_invocation_allowed=false",
        "actual_source_read_invoked_by_props_preflight=false",
        "payload_reparse_allowed=false",
        "no_component_props_binding",
        "no_render_latest_prediction_summary_widget_call",
        "PS-Q18F: latest_prediction_summary_widget props candidate status row mount",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "real_payload_values_bound=true",
        "widget_props_binding_allowed=true",
        "widget_props_bound_to_component=true",
        "render_invocation_allowed=true",
        "real_prediction_widget_rendering_allowed=true",
        "actual_source_read_invoked_by_props_preflight=true",
        "actual_source_read_allowed_by_props_preflight=true",
        "payload_reparse_allowed=true",
        "source_discovery_allowed=true",
        "d_hot_directory_scan_allowed=true",
        "d_hot_actual_read_allowed=true",
        "warroom_page_mutation_allowed=true",
        "confidence_increase_allowed=true",
        "parameter_apply_allowed=true",
        "broker_private_api_allowed=true",
    ):
        if forbidden in doc_text:
            failures.append(f"forbidden doc marker present: {forbidden}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q18e_latest_prediction_summary_widget_props_binding_preflight_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18e_latest_prediction_summary_widget_props_binding_preflight_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
