# path: ./tools/test_phase4a_prediction_system_ps_q18i_close_guard.py
# desc: Close guard for PS-Q18I latest_prediction_summary_widget real decoded-payload value mapping preflight.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight import CHECKER_VERSION, REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_CHECK_VERSION, build_report, main, observed_decoded_payload_fixture

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_real_payload_value_mapping_preflight.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18I_LATEST_PREDICTION_SUMMARY_WIDGET_REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight_guard.py"
CLOSE_REL = "tools/test_phase4a_prediction_system_ps_q18i_close_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_real_payload_value_mapping_preflight.py",
    "tools/check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.py",
    "tools/test_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18I_LATEST_PREDICTION_SUMMARY_WIDGET_REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18i_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_boundary(report: dict, failures: list[str]) -> None:
    for key in (
        "read_only",
        "non_executing",
        "latest_prediction_summary_widget_real_payload_value_mapping_preflight_only",
        "decoded_payload_supplied",
        "decoded_payload_values_mapped_to_props_candidate",
        "real_payload_values_bound_to_props_candidate",
    ):
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
        "freshness_checked_against_d_hot",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "confidence_increase_allowed",
        "signal_reliability_claim_allowed",
        "parameter_candidate_reliability_claim_allowed",
        "parameter_tuning_allowed",
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
        "LATEST_PREDICTION_SUMMARY_WIDGET_REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_VERSION",
        "REQUIRED_REAL_PAYLOAD_VALUE_KEYS",
        "build_latest_prediction_summary_widget_real_payload_value_mapping_candidate",
        "build_latest_prediction_summary_widget_real_payload_value_mapping_preflight_packet",
        "prediction_run_id",
        "generated_at",
        "market_uid",
        "source_artifact_ref",
        "real_payload_value_mapping_preflight_only",
        "decoded_payload_values_mapped_to_props_candidate",
        "props_value_binding_deferred",
        "real_payload_values_bound_to_props_candidate",
        "real_payload_values_bound_to_component",
        "component_props_binding_allowed",
        "actual_source_read_invoked_by_mapping",
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
        'CHECKER = "ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.v1"',
        'REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_CHECK_VERSION = "latest_prediction_summary_widget_real_payload_value_mapping_preflight.v1"',
        "observed_decoded_payload_fixture",
        "build_ps_q18e_report",
        "build_latest_prediction_summary_widget_props_binding_preflight_packet",
        "build_latest_prediction_summary_widget_real_payload_value_mapping_preflight_packet",
        "mapped_prediction_run_id",
        "mapped_source_generated_at",
        "real_payload_values_bound_to_props_candidate",
        "PS-Q18J render-disabled latest_prediction_summary_widget packet validation",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if "test_ps_q18i_maps_real_payload_values_from_observed_fixture" not in unit_text:
        failures.append("unit test must cover observed payload value mapping")
    if "test_ps_q18i_component_packet_mapping_blocks_missing_payload" not in unit_text:
        failures.append("unit test must cover missing payload block")
    if CLOSE_REL not in focused_text:
        failures.append("focused guard expected dirty set must include close guard")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18i_latest_prediction_summary_widget_real_payload_value_mapping_preflight.v1":
        failures.append("checker version mismatch")
    if REAL_PAYLOAD_VALUE_MAPPING_PREFLIGHT_CHECK_VERSION != "latest_prediction_summary_widget_real_payload_value_mapping_preflight.v1":
        failures.append("check version mismatch")

    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture mapping should be ok: {report}")
    if report.get("use_observed_fixture") is not True:
        failures.append("observed fixture flag should be true")
    if report.get("source_q18e_report_valid") is not True:
        failures.append("source Q18E report should validate")
    if report.get("mapping_packet_valid") is not True:
        failures.append("mapping packet should validate")
    if report.get("mapping_validation_failures"):
        failures.append(f"mapping validation failures: {report.get('mapping_validation_failures')}")
    for key, value in {
        "mapped_prediction_run_id": "ps_q18i_fixture_run",
        "mapped_market_uid": "BTC-USD",
        "mapped_source_generated_at": "2026-06-22T00:00:00Z",
        "mapped_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json",
    }.items():
        if report.get(key) != value:
            failures.append(f"mapped value mismatch: {key}")
    if int(report.get("mapped_props_candidate_key_count") or 0) < 14:
        failures.append("mapped props candidate should contain extended mapped fields")
    if report.get("missing_required_payload_value_keys") != []:
        failures.append("missing required payload value keys must be empty")
    if report.get("missing_required_component_props") != []:
        failures.append("missing required component props must be empty")
    if report.get("recommended_first_validation") != "latest_prediction_summary_widget_real_payload_value_mapping_preflight_guard":
        failures.append("recommended first validation mismatch")
    _assert_boundary(report, failures)

    blocked = build_report(supplied_decoded_payload=observed_decoded_payload_fixture())
    if blocked.get("ok") is not False:
        failures.append("missing Q18E source should block")
    if blocked.get("source_q18e_report_valid") is not False:
        failures.append("blocked report should not validate Q18E")
    if blocked.get("decoded_payload_values_mapped_to_props_candidate") is not False:
        failures.append("blocked report should not map decoded payload")
    if blocked.get("actual_source_read_invoked_by_mapping") is not False:
        failures.append("blocked report should not read sources")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")

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
        "latest_prediction_summary_widget_real_payload_value_mapping_preflight_only=true",
        "decoded_payload_supplied=true",
        "decoded_payload_values_mapped_to_props_candidate=true",
        "props_value_binding_deferred=false",
        "real_payload_values_bound_to_props_candidate=true",
        "real_payload_values_bound_to_component=false",
        "component_props_binding_allowed=false",
        "streamlit_render_invoked=false",
        "actual_source_read_invoked_by_mapping=false",
        "no_file_read",
        "no_payload_reparse",
        "no_component_props_binding",
        "no_render_latest_prediction_summary_widget_call",
        "no_streamlit_render",
        "PS-Q18J: Render-disabled latest_prediction_summary_widget packet validation with mapped real payload values",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "real_payload_values_bound_to_component=true",
        "component_props_binding_allowed=true",
        "component_props_bound_to_component=true",
        "component_runtime_binding_allowed=true",
        "streamlit_render_allowed=true",
        "streamlit_render_invoked=true",
        "render_invocation_allowed=true",
        "real_prediction_widget_rendering_allowed=true",
        "actual_source_read_invoked_by_mapping=true",
        "actual_source_read_allowed_by_mapping=true",
        "payload_reparse_allowed=true",
        "source_discovery_allowed=true",
        "d_hot_directory_scan_allowed=true",
        "d_hot_actual_read_allowed=true",
        "confidence_increase_allowed=true",
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
        "guard": "ps_q18i_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_real_payload_value_mapping_preflight_closed_before_component_binding_real_rendering_refresh_and_writes",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q18i_closed": not failures,
            "latest_prediction_summary_widget_real_payload_value_mapping_preflight_only": True,
            "decoded_payload_supplied": True,
            "decoded_payload_values_mapped_to_props_candidate": True,
            "props_value_binding_deferred": False,
            "real_payload_values_bound_to_props_candidate": True,
            "mapped_prediction_run_id": report.get("mapped_prediction_run_id"),
            "mapped_market_uid": report.get("mapped_market_uid"),
            "mapped_source_generated_at": report.get("mapped_source_generated_at"),
            "mapped_source_artifact_ref": report.get("mapped_source_artifact_ref"),
            "real_payload_values_bound_to_component": False,
            "component_props_binding_allowed": False,
            "component_props_bound_to_component": False,
            "component_runtime_binding_allowed": False,
            "streamlit_render_allowed": False,
            "streamlit_render_invoked": False,
            "render_invocation_allowed": False,
            "real_prediction_widget_rendering_allowed": False,
            "actual_source_read_invoked_by_mapping": False,
            "actual_source_read_allowed_by_mapping": False,
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
            "next_slice": "PS-Q18J render-disabled latest_prediction_summary_widget packet validation with mapped real payload values",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18i_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
