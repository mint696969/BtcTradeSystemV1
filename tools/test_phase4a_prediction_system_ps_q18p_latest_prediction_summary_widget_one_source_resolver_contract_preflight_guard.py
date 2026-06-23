# path: ./tools/test_phase4a_prediction_system_ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight_guard.py
# desc: Focused guard for PS-Q18P latest_prediction_summary_widget explicit one-source resolver contract preflight.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight import CHECKER_VERSION, ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_CHECK_VERSION, build_report, main
from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_summary_widget_one_source_resolver_contract_preflight import ONE_SOURCE_RESOLVER_CONTRACT_ACK

REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_resolver_contract_preflight.py"
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18P_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_summary_widget_one_source_resolver_contract_preflight.py",
    "tools/check_phase4a_prediction_system_ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight.py",
    "tools/test_phase4a_prediction_system_ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18P_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q18p_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight_guard.py",
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
        "LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_VERSION",
        "ONE_SOURCE_RESOLVER_CONTRACT_ACK",
        "PS_Q18P_DECLARE_ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_ONLY",
        "RESOLVER_CONTRACT_ITEMS",
        "build_latest_prediction_summary_widget_one_source_resolver_contract_preflight_rows",
        "build_latest_prediction_summary_widget_one_source_resolver_contract_preflight_packet",
        "latest_prediction_summary_widget_one_source_resolver_contract_preflight_only",
        "resolver_contract_declared",
        "resolver_input_ref_kind",
        "source_artifact_resolver_invoked",
        "source_artifact_path_materialized",
        "actual_source_read_invoked",
    ):
        if marker not in component_text:
            failures.append(f"missing component marker: {marker}")
    for forbidden in ("import streamlit", "st.", "Path(", "open(", "read_text(", "read_bytes(", "write_text(", "data_read", "data_slice", "glob(", "rglob(", "render_latest_prediction_summary_widget(", "send_order(", "create_order("):
        if forbidden in component_text:
            failures.append(f"forbidden component token: {forbidden}")
    tool_text = _read(TOOL) if TOOL.exists() else ""
    for marker in (
        'CHECKER = "ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight"',
        'CHECKER_VERSION = "check_phase4a_prediction_system_ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight.v1"',
        'ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_CHECK_VERSION = "latest_prediction_summary_widget_one_source_resolver_contract_preflight.v1"',
        "build_ps_q18o_report",
        "build_latest_prediction_summary_widget_one_source_resolver_contract_preflight_packet",
        "latest_prediction_summary_widget_one_source_resolver_contract_preflight_only",
        "source_artifact_resolver_invoked",
        "source_artifact_path_materialized",
        "actual_source_read_invoked",
        "PS-Q18Q explicit one-source resolver dry-run path-shape preflight",
    ):
        if marker not in tool_text:
            failures.append(f"missing tool marker: {marker}")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight.v1":
        failures.append("checker version mismatch")
    if ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_CHECK_VERSION != "latest_prediction_summary_widget_one_source_resolver_contract_preflight.v1":
        failures.append("check version mismatch")
    if ONE_SOURCE_RESOLVER_CONTRACT_ACK != "PS_Q18P_DECLARE_ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_ONLY":
        failures.append("resolver contract ack mismatch")
    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture resolver contract should be ok: {report}")
    if report.get("source_q18o_report_valid") is not True:
        failures.append("source Q18O report should validate")
    if report.get("resolver_contract_packet_valid") is not True:
        failures.append("resolver contract packet should validate")
    if report.get("resolver_contract_row_count") != 10:
        failures.append("expected 10 resolver contract rows")
    if report.get("source_candidate_count") != 1:
        failures.append("expected one source candidate")
    if report.get("resolver_contract_candidate_ready") is not True:
        failures.append("resolver contract candidate should be ready")
    if report.get("resolver_input_ref_kind") != "artifact_ref_string_only":
        failures.append("resolver input ref kind mismatch")
    for key, value in {"selected_candidate_generated_at": "2026-06-22T00:00:00Z", "selected_candidate_source_artifact_ref": "fixture://ps_q18i/latest_prediction.json", "selected_candidate_market_uid": "BTC-USD"}.items():
        if report.get(key) != value:
            failures.append(f"selected candidate mismatch: {key}")
    for key in ("read_only", "non_executing", "latest_prediction_summary_widget_one_source_resolver_contract_preflight_only", "one_source_resolver_contract_preflight_ready", "resolver_contract_declared", "one_source_candidate_preserved", "source_candidate_count_fixed_to_one", "explicit_resolver_contract_ack_matched"):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in ("warroom_page_mutation_allowed", "source_artifact_resolver_invoked", "source_artifact_resolution_allowed", "source_artifact_resolved", "source_artifact_path_materialized", "source_artifact_exists_checked", "source_artifact_schema_checked", "actual_source_read_allowed", "actual_source_read_invoked", "payload_reparse_allowed", "source_discovery_allowed", "d_hot_directory_scan_allowed", "d_hot_actual_read_allowed", "q18o_validation_invoked_by_mount", "q18n_validation_invoked_by_mount", "component_packet_builder_invoked_by_mount", "streamlit_render_invoked", "real_prediction_widget_rendering_allowed", "refresh_invocation_allowed", "runtime_artifact_write_allowed", "parameter_apply_allowed", "broker_private_api_allowed"):
        if report.get(key) is not False:
            failures.append(f"{key} must stay false")
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q18P_LATEST_PREDICTION_SUMMARY_WIDGET_ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_2026-06-22.md",
        "# desc: PS-Q18P latest_prediction_summary_widget explicit one-source resolver contract preflight after PS-Q18O.",
        "checker=check_phase4a_prediction_system_ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight.v1",
        "one_source_resolver_contract_preflight_check_version=latest_prediction_summary_widget_one_source_resolver_contract_preflight.v1",
        "resolver_contract_preflight_version=prediction_warroom_latest_prediction_summary_widget_one_source_resolver_contract_preflight.ps_q18p.v1",
        "source_q18o_checker=check_phase4a_prediction_system_ps_q18o_latest_prediction_summary_widget_one_source_handoff_design_checkpoint.v1",
        "source_candidate_count=1",
        "resolver_input_ref_kind=artifact_ref_string_only",
        "one_source_resolver_contract_ack=PS_Q18P_DECLARE_ONE_SOURCE_RESOLVER_CONTRACT_PREFLIGHT_ONLY",
        "source_artifact_resolver_invoked=false",
        "source_artifact_path_materialized=false",
        "actual_source_read_invoked=false",
        "no_source_artifact_resolver_invocation",
        "no_actual_source_read",
        "PS-Q18Q: Explicit one-source resolver dry-run path-shape preflight",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    result = {"ok": not failures, "guard": "ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18p_latest_prediction_summary_widget_one_source_resolver_contract_preflight_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
