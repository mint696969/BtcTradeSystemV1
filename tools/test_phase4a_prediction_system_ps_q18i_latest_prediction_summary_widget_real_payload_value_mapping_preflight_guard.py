# path: ./tools/test_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight_guard.py
# desc: Focused guard for PS-Q18I latest_prediction_summary_widget real payload value mapping preflight.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight import CHECKER_VERSION, REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_CHECK_VERSION, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_real_payload_value_mapping_preflight.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18I_LATEST_PREDICTION_SUMMARY_WIDGET_REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_real_payload_value_mapping_preflight.py",
    "tools/check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.py",
    "tools/test_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18I_LATEST_PREDICTION_SUMMARY_WIDGET_REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18i_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight_guard.py",
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
        "LATEST_PREDICTION_SUMMARY_WIDGET_REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_VERSION",
        "REQUIRED_REAL_PAYLOAD_VALUE_KEYS",
        "build_latest_prediction_summary_widget_real_payload_value_mapping_candidate",
        "build_latest_prediction_summary_widget_real_payload_value_mapping_preflight_packet",
        "real_payload_value_mapping_preflight_only",
        "decoded_payload_values_mapped_to_props_candidate",
        "real_payload_values_bound_to_props_candidate",
        "real_payload_values_bound_to_component",
        "actual_source_read_invoked_by_mapping",
    ):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in ("import streamlit", "st.", "Path(", "open(", "read_text(", "read_bytes(", "write_text(", "data_read", "data_slice", "glob(", "rglob(", "render_latest_prediction_summary_widget(", "send_order(", "create_order("):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        'CHECKER = "ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.v1"',
        'REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_CHECK_VERSION = "latest_prediction_summary_widget_real_payload_value_mapping_preflight.v1"',
        "observed_decoded_payload_fixture",
        "build_ps_q18e_report",
        "build_latest_prediction_summary_widget_real_payload_value_mapping_preflight_packet",
        "mapped_prediction_run_id",
        "real_payload_values_bound_to_props_candidate",
        "PS-Q18J render-disabled latest_prediction_summary_widget packet validation",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.v1":
        failures.append("checker version mismatch")
    if REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_CHECK_VERSION != "latest_prediction_summary_widget_real_payload_value_mapping_preflight.v1":
        failures.append("check version mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture mapping should be ok: {report}")
    if report.get("source_q18e_report_valid") is not True:
        failures.append("source Q18E report should validate")
    if report.get("mapping_packet_valid") is not True:
        failures.append("mapping packet should validate")
    for key, value in {
        "mapped_prediction_run_id": "ps_q18i_fixture_run",
        "mapped_market_uid": "BTC-USD",
        "mapped_source_generated_at": "2026-06-22T00:00:00Z",
        "mapped_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
    }.items():
        if report.get(key) != value:
            failures.append(f"mapped value mismatch: {key}")
    if report.get("missing_required_payload_value_keys") != []:
        failures.append("missing required payload value keys must be empty")
    if report.get("missing_required_component_props") != []:
        failures.append("missing required component props must be empty")
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_real_payload_value_mapping_preflight_only", "decoded_payload_supplied", "decoded_payload_values_mapped_to_props_candidate", "real_payload_values_bound_to_props_candidate"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    if report.get("props_value_binding_deferred") is not False:
        failures.append("props_value_binding_deferred must be false after mapping to props candidate")
    for key in (
        "real_payload_values_bound_to_component",
        "component_props_binding_allowed",
        "component_props_bound_to_component",
        "component_runtime_binding_allowed",
        "streamlit_render_allowed",
        "streamlit_render_invoked",
        "render_invocation_allowed",
        "real_prediction_widget_rendering_allowed",
        "actual_source_read_invoked_by_mapping",
        "actual_source_read_allowed_by_mapping",
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
        "checker=check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.v1",
        "real_payload_value_mapping_preflight_check_version=latest_prediction_summary_widget_real_payload_value_mapping_preflight.v1",
        "mapping_preflight_version=prediction_warroom_latest_prediction_summary_widget_real_payload_value_mapping_preflight.ps_q18i.v1",
        "source_q18e_checker=check_phase4a_prediction_system_ps_q18e_latest_prediction_summary_widget_props_binding_preflight.v1",
        "mapping_packet_valid=true",
        "missing_required_payload_value_keys=[]",
        "missing_required_component_props=[]",
        "mapped_prediction_run_id=ps_q18i_fixture_run",
        "mapped_market_uid=BTC-USD",
        "mapped_source_generated_at=2026-06-22T00:00:00Z",
        "mapped_source_artifact_ref=fixture://ps_q18i/latest_prediction.json",
        "decoded_payload_values_mapped_to_props_candidate=true",
        "props_value_binding_deferred=false",
        "real_payload_values_bound_to_props_candidate=true",
        "real_payload_values_bound_to_component=false",
        "actual_source_read_invoked_by_mapping=false",
        "no_file_read",
        "no_component_props_binding",
        "no_streamlit_render",
        "PS-Q18J: Render-disabled latest_prediction_summary_widget packet validation with mapped real payload values",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
