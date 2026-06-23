# path: ./tools/test_phase4a_prediction_system_ps_q18d_close_guard.py
# desc: Close guard for PS-Q18D latest_prediction_summary_widget schema-specific probe.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe import CHECKER_VERSION, LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_CHECK_VERSION, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_schema_probe.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18D_LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe_guard.py"
CLOSE_REL = "tools/test_phase4a_prediction_system_ps_q18d_close_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_schema_probe.py",
    "tools/check_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe.py",
    "tools/test_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18D_LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18d_close_guard.py",
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
        "latest_prediction_summary_widget_schema_probe_only",
        "schema_specific_probe_ready",
        "preview_key_contract_only",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "payload_reparse_allowed",
        "actual_source_read_invoked_by_schema_probe",
        "actual_source_read_allowed_by_schema_probe",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
        "real_prediction_widget_rendering_allowed",
        "widget_props_binding_allowed",
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
        "LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_VERSION",
        "REQUIRED_SUMMARY_SCHEMA_KEYS",
        "prediction_run_id",
        "generated_at",
        "market_uid",
        "source_artifact_ref",
        "build_latest_prediction_summary_widget_schema_probe_rows",
        "build_latest_prediction_summary_widget_schema_probe_packet",
        "latest_prediction_summary_widget_schema_probe_only",
        "schema_specific_probe_ready",
        "preview_key_contract_only",
        "payload_reparse_allowed",
        "widget_props_binding_allowed",
        "actual_source_read_invoked_by_schema_probe",
        "actual_source_read_allowed_by_schema_probe",
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
        'CHECKER = "ps_q18d_latest_prediction_summary_widget_schema_probe"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe.v1"',
        'LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_CHECK_VERSION = "latest_prediction_summary_widget_schema_probe.v1"',
        "build_ps_q18b_report",
        "build_q18b_fixture_probe_packet",
        "build_latest_prediction_summary_widget_schema_probe_packet",
        "latest_prediction_summary_widget_schema_probe_only",
        "schema_specific_probe_ready",
        "preview_key_contract_only",
        "actual_source_read_invoked_by_schema_probe",
        "widget_props_binding_allowed",
        "PS-Q18E first latest_prediction_summary_widget props binding preflight",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if "test_ps_q18d_validates_latest_summary_schema_from_q18b_fixture" not in unit_text:
        failures.append("unit test must cover Q18B fixture schema probe")
    if "test_ps_q18d_blocks_missing_required_schema_key" not in unit_text:
        failures.append("unit test must cover missing schema key")
    if CLOSE_REL not in focused_text:
        failures.append("focused guard expected dirty set must include close guard")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe.v1":
        failures.append("checker version mismatch")
    if LATEST_PREDICTION_SUMMARY_WIDGET_SCHEMA_PROBE_CHECK_VERSION != "latest_prediction_summary_widget_schema_probe.v1":
        failures.append("schema probe check version mismatch")

    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture schema probe should be ok: {report}")
    if report.get("use_observed_fixture") is not True:
        failures.append("observed fixture flag should be true")
    if report.get("source_q18b_report_valid") is not True:
        failures.append("source Q18B report should validate")
    if report.get("schema_packet_valid") is not True:
        failures.append("schema packet should validate")
    if report.get("schema_validation_failures"):
        failures.append(f"schema validation failures: {report.get('schema_validation_failures')}")
    if report.get("widget_family_id") != "latest_prediction_summary_widget":
        failures.append("widget family mismatch")
    if report.get("source_packet_id") != "latest_prediction_source_review_packet":
        failures.append("source packet mismatch")
    if report.get("schema_probe_row_count") != 4:
        failures.append("expected 4 schema rows")
    if report.get("required_schema_keys") != ["prediction_run_id", "generated_at", "market_uid", "source_artifact_ref"]:
        failures.append("required schema keys mismatch")
    if report.get("missing_required_schema_keys") != []:
        failures.append("missing required schema keys should be empty")
    if report.get("recommended_first_validation") != "latest_prediction_summary_widget_minimum_schema_probe_guard":
        failures.append("recommended first validation mismatch")
    _assert_boundary(report, failures)

    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing source should block")
    if blocked.get("schema_probe_row_count") != 0:
        failures.append("blocked report should not emit schema rows")
    if blocked.get("actual_source_read_invoked_by_schema_probe") is not False:
        failures.append("blocked report should not invoke read")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")

    for marker in (
        "checker=check_phase4a_prediction_system_ps_q18d_latest_prediction_summary_widget_schema_probe.v1",
        "latest_prediction_summary_widget_schema_probe_check_version=latest_prediction_summary_widget_schema_probe.v1",
        "schema_probe_version=prediction_warroom_latest_prediction_summary_widget_schema_probe.ps_q18d.v1",
        "source_q18b_checker=check_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe.v1",
        "widget_family_id=latest_prediction_summary_widget",
        "source_packet_id=latest_prediction_source_review_packet",
        "schema_probe_row_count=4",
        "missing_required_schema_keys=[]",
        "latest_prediction_summary_widget_schema_probe_only=true",
        "schema_specific_probe_ready=true",
        "preview_key_contract_only=true",
        "payload_reparse_allowed=false",
        "actual_source_read_invoked_by_schema_probe=false",
        "actual_source_read_allowed_by_schema_probe=false",
        "source_discovery_allowed=false",
        "d_hot_directory_scan_allowed=false",
        "warroom_page_mutation_allowed=false",
        "widget_props_binding_allowed=false",
        "real_prediction_widget_rendering_allowed=false",
        "no_new_actual_source_read",
        "no_payload_reparse",
        "no_widget_props_binding",
        "PS-Q18E: First latest_prediction_summary_widget props binding preflight",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "payload_reparse_allowed=true",
        "actual_source_read_invoked_by_schema_probe=true",
        "actual_source_read_allowed_by_schema_probe=true",
        "source_discovery_allowed=true",
        "d_hot_directory_scan_allowed=true",
        "d_hot_actual_read_allowed=true",
        "freshness_checked_against_d_hot=true",
        "warroom_page_mutation_allowed=true",
        "warroom_widget_rendering_allowed=true",
        "real_prediction_widget_rendering_allowed=true",
        "widget_props_binding_allowed=true",
        "confidence_increase_allowed=true",
        "parameter_apply_allowed=true",
        "parameter_staging_write_allowed=true",
        "ledger_append_allowed=true",
        "autotrade_trigger_allowed=true",
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
        "guard": "ps_q18d_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_schema_probe_closed_before_props_binding_real_widget_rendering_refresh_and_writes",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q18d_closed": not failures,
            "latest_prediction_summary_widget_schema_probe_only": True,
            "schema_specific_probe_ready": True,
            "preview_key_contract_only": True,
            "schema_probe_row_count": int(report.get("schema_probe_row_count") or 0),
            "missing_required_schema_keys": list(report.get("missing_required_schema_keys") or []),
            "payload_reparse_allowed": False,
            "actual_source_read_invoked_by_schema_probe": False,
            "actual_source_read_allowed_by_schema_probe": False,
            "source_discovery_allowed": False,
            "d_hot_directory_scan_allowed": False,
            "d_hot_actual_read_allowed": False,
            "warroom_page_mutation_allowed": False,
            "widget_props_binding_allowed": False,
            "real_prediction_widget_rendering_allowed": False,
            "refresh_invocation_allowed": False,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_parameter_apply": True,
            "no_parameter_staging_write": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
            "next_slice": "PS-Q18E first latest_prediction_summary_widget props binding preflight or schema-specific probe status row mount",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18d_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
