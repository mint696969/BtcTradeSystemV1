# path: ./tools/test_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight_guard.py
# desc: Focused guard for PS-Q18A WarRoom prediction widget source artifact resolution preflight.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight import CHECKER_VERSION, SOURCE_ARTIFACT_RESOLUTION_PREFLIGHT_VERSION, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_widget_source_artifact_resolution_preflight_panel.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18A_WARROOM_PREDICTION_WIDGET_SOURCE_ARTIFACT_RESOLUTION_PREFLIGHT_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_widget_source_artifact_resolution_preflight_panel.py",
    "tools/check_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight.py",
    "tools/test_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18A_WARROOM_PREDICTION_WIDGET_SOURCE_ARTIFACT_RESOLUTION_PREFLIGHT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18a_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight_guard.py",
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
        "PREDICTION_WARROOM_SOURCE_ARTIFACT_RESOLUTION_PREFLIGHT_PANEL_VERSION",
        "build_prediction_warroom_prediction_widget_source_artifact_resolution_rows",
        "build_prediction_warroom_prediction_widget_source_artifact_resolution_preflight_packet",
        "artifact_resolution_key",
        "source_artifact_resolution_preflight_ready",
        "source_artifact_resolution_allowed",
        "source_artifact_path_materialized",
        "source_artifact_exists_checked",
        "source_artifact_schema_checked",
        "actual_source_read_allowed",
        "d_hot_actual_read_allowed",
    ):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in (
        "import streamlit",
        "st.",
        "Path(",
        "open(",
        "read_text(",
        "write_text(",
        "data_read",
        "data_slice",
        "allow_actual_read=True",
        "send_order(",
        "create_order(",
    ):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        'CHECKER = "ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight.v1"',
        'SOURCE_ARTIFACT_RESOLUTION_PREFLIGHT_VERSION = "warroom_prediction_widget_source_artifact_resolution_preflight.v1"',
        "build_ps_q17z_report",
        "build_prediction_warroom_prediction_widget_source_artifact_resolution_preflight_packet",
        "source_artifact_resolution_preflight_only",
        "source_artifact_resolution_preflight_ready",
        "source_artifact_resolution_allowed",
        "source_artifact_path_materialized",
        "source_artifact_exists_checked",
        "PS-Q18B first bounded actual-source read probe",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight.v1":
        failures.append("checker version mismatch")
    if SOURCE_ARTIFACT_RESOLUTION_PREFLIGHT_VERSION != "warroom_prediction_widget_source_artifact_resolution_preflight.v1":
        failures.append("preflight version mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture artifact resolution preflight should be ok: {report}")
    if report.get("source_q17z_report_valid") is not True:
        failures.append("source Q17Z report should validate")
    if report.get("panel_packet_valid") is not True:
        failures.append("panel packet should validate")
    if report.get("artifact_resolution_row_count") != 12:
        failures.append("expected 12 artifact resolution rows")
    if report.get("unique_artifact_resolution_key_count") != 9:
        failures.append("expected 9 unique artifact resolution keys")
    if report.get("unique_source_packet_count") != 9:
        failures.append("expected 9 unique source packets")
    for key in ("read_only", "non_executing", "source_artifact_resolution_preflight_only", "source_artifact_resolution_preflight_ready"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "source_artifact_resolution_allowed",
        "source_artifact_resolved",
        "source_artifact_path_materialized",
        "source_artifact_exists_checked",
        "source_artifact_schema_checked",
        "actual_source_bound",
        "actual_source_read_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "real_prediction_widget_rendering_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
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
        "checker=check_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight.v1",
        "source_artifact_resolution_preflight_version=warroom_prediction_widget_source_artifact_resolution_preflight.v1",
        "source_q17z_checker=check_phase4a_prediction_system_ps_q17z_warroom_prediction_widget_source_readiness_row_mount.v1",
        "panel_version=prediction_warroom_prediction_widget_source_artifact_resolution_preflight_panel.ps_q18a.v1",
        "artifact_resolution_row_count=12",
        "unique_artifact_resolution_key_count=9",
        "unique_source_packet_count=9",
        "source_artifact_resolution_preflight_only=true",
        "source_artifact_resolution_preflight_ready=true",
        "source_artifact_resolution_allowed=false",
        "source_artifact_path_materialized=false",
        "source_artifact_exists_checked=false",
        "source_artifact_schema_checked=false",
        "actual_source_read_allowed=false",
        "d_hot_actual_read_allowed=false",
        "no_path_materialization",
        "no_actual_source_read",
        "PS-Q18B: First bounded actual-source read probe",
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
        "d_hot_actual_read_allowed=true",
        "freshness_checked_against_d_hot=true",
        "real_prediction_widget_rendering_allowed=true",
        "confidence_increase_allowed=true",
        "parameter_apply_allowed=true",
        "parameter_staging_write_allowed=true",
        "ledger_append_allowed=true",
        "autotrade_trigger_allowed=true",
        "broker_private_api_allowed=true",
        "refresh_invocation_allowed=true",
        "scheduler_enabled=true",
    ):
        if forbidden in doc_text:
            failures.append(f"forbidden doc marker present: {forbidden}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
