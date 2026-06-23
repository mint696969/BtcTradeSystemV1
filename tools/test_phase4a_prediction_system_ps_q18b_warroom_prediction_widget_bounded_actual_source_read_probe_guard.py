# path: ./tools/test_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe_guard.py
# desc: Focused guard for PS-Q18B WarRoom prediction widget bounded actual-source read probe.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe import CHECKER_VERSION, BOUNDED_ACTUAL_SOURCE_READ_PROBE_CHECK_VERSION, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_widget_bounded_actual_source_read_probe.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18B_WARROOM_PREDICTION_WIDGET_BOUNDED_ACTUAL_SOURCE_READ_PROBE_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_widget_bounded_actual_source_read_probe.py",
    "tools/check_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe.py",
    "tools/test_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18B_WARROOM_PREDICTION_WIDGET_BOUNDED_ACTUAL_SOURCE_READ_PROBE_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18b_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe_guard.py",
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
        "BOUNDED_ACTUAL_SOURCE_READ_PROBE_VERSION",
        "ALLOW_ACK",
        "build_prediction_warroom_prediction_widget_bounded_actual_source_read_probe_packet",
        "allow_actual_read_false",
        "explicit_ack_missing_or_mismatch",
        "path.read_bytes()",
        "json.loads",
        "single_file_probe_only",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "runtime_artifact_write_allowed",
    ):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in (
        "import streamlit",
        "st.",
        "write_text(",
        "write_bytes(",
        "open(",
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
    for marker in (
        'CHECKER = "ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe.v1"',
        'BOUNDED_ACTUAL_SOURCE_READ_PROBE_CHECK_VERSION = "warroom_prediction_widget_bounded_actual_source_read_probe.v1"',
        "build_ps_q18a_report",
        "build_prediction_warroom_prediction_widget_bounded_actual_source_read_probe_packet",
        "NamedTemporaryFile",
        "bounded_actual_source_read_probe_only",
        "single_file_probe_only",
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "PS-Q18C WarRoom source read probe status row mount",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe.v1":
        failures.append("checker version mismatch")
    if BOUNDED_ACTUAL_SOURCE_READ_PROBE_CHECK_VERSION != "warroom_prediction_widget_bounded_actual_source_read_probe.v1":
        failures.append("probe check version mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture bounded probe should be ok: {report}")
    if report.get("source_q18a_report_valid") is not True:
        failures.append("source Q18A report should validate")
    if report.get("probe_packet_valid") is not True:
        failures.append("probe packet should validate")
    for key in (
        "read_only",
        "non_executing",
        "bounded_actual_source_read_probe_only",
        "single_file_probe_only",
        "actual_source_read_allowed",
        "actual_file_read_attempted",
        "actual_file_read_succeeded",
        "payload_decode_attempted",
        "payload_decode_succeeded",
        "schema_probe_checked",
        "schema_probe_ok",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "source_discovery_allowed",
        "d_hot_directory_scan_allowed",
        "d_hot_actual_read_allowed",
        "freshness_checked_against_d_hot",
        "warroom_page_mutation_allowed",
        "warroom_widget_rendering_allowed",
        "real_prediction_widget_rendering_allowed",
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
        "checker=check_phase4a_prediction_system_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe.v1",
        "bounded_actual_source_read_probe_check_version=warroom_prediction_widget_bounded_actual_source_read_probe.v1",
        "probe_version=prediction_warroom_prediction_widget_bounded_actual_source_read_probe.ps_q18b.v1",
        "source_q18a_checker=check_phase4a_prediction_system_ps_q18a_warroom_prediction_widget_source_artifact_resolution_preflight.v1",
        "bounded_actual_source_read_probe_only=true",
        "single_file_probe_only=true",
        "actual_source_read_allowed=true",
        "actual_file_read_attempted=true",
        "payload_decode_succeeded=true",
        "schema_probe_ok=true",
        "source_discovery_allowed=false",
        "d_hot_directory_scan_allowed=false",
        "d_hot_actual_read_allowed=false",
        "warroom_page_mutation_allowed=false",
        "runtime_artifact_write_allowed=false",
        "no_d_hot_discovery",
        "no_d_hot_directory_scan",
        "PS-Q18C: WarRoom source read probe status row mount",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "source_discovery_allowed=true",
        "d_hot_directory_scan_allowed=true",
        "d_hot_actual_read_allowed=true",
        "freshness_checked_against_d_hot=true",
        "warroom_page_mutation_allowed=true",
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
    result = {"ok": not failures, "guard": "ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18b_warroom_prediction_widget_bounded_actual_source_read_probe_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
