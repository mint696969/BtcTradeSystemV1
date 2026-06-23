# path: ./tools/test_phase4a_prediction_system_ps_q17p_close_guard.py
# desc: Close guard for PS-Q17P WarRoom prediction widget integration design checkpoint.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint import CHECKER_VERSION, CHECKPOINT_VERSION, REQUIRED_INTEGRATION_FIELDS, SOURCE_CHECKER_VERSIONS, WIDGET_FAMILY_ORDER, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17P_WARROOM_PREDICTION_WIDGET_INTEGRATION_DESIGN_CHECKPOINT_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint.py",
    "tools/test_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17P_WARROOM_PREDICTION_WIDGET_INTEGRATION_DESIGN_CHECKPOINT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17p_close_guard.py",
}
EXPECTED_WIDGETS = (
    "latest_prediction_summary_widget",
    "prediction_delta_widget",
    "scenario_trace_widget",
    "evidence_weighting_widget",
    "invalidation_rewrite_widget",
    "source_quality_freshness_widget",
    "warning_blocker_widget",
    "signal_strength_calibration_widget",
    "parameter_candidate_comparison_widget",
    "replay_outcome_calibration_widget",
    "producer_freshness_status_widget",
    "runtime_boundary_safety_widget",
)
EXPECTED_SOURCE_PACKETS = {
    "prediction_delta_widget": "prediction_delta_review_packet",
    "scenario_trace_widget": "scenario_trace_semantic_mapping_review_packet",
    "evidence_weighting_widget": "scenario_trace_semantic_mapping_review_packet",
    "invalidation_rewrite_widget": "scenario_trace_semantic_mapping_review_packet",
    "source_quality_freshness_widget": "tier0_source_quality_gate_packet",
    "warning_blocker_widget": "tier0_source_quality_gate_packet",
    "signal_strength_calibration_widget": "calibration_reference_packet",
    "parameter_candidate_comparison_widget": "parameter_candidate_evidence_review_packet",
    "replay_outcome_calibration_widget": "replay_outcome_calibration_review_packet",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in (
        "read_only",
        "non_executing",
        "design_checkpoint_only",
        "contract_only",
        "diagnostic_only",
        "warroom_widget_design_premise",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "warroom_widget_implementation_allowed",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_mount_patch_allowed",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "d_hot_actual_read_allowed",
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
    unit_text = _read(UNIT) if UNIT.exists() else ""
    doc_text = _read(DOC) if DOC.exists() else ""

    for marker in (
        "CHECKER = \"ps_q17p_warroom_prediction_widget_integration_design_checkpoint\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint.v1\"",
        "CHECKPOINT_VERSION = \"warroom_prediction_widget_integration_design_checkpoint.v1\"",
        "SOURCE_CHECKER_VERSIONS",
        "WIDGET_FAMILY_ORDER",
        "REQUIRED_INTEGRATION_FIELDS",
        "latest_prediction_summary_widget",
        "prediction_delta_widget",
        "scenario_trace_widget",
        "evidence_weighting_widget",
        "invalidation_rewrite_widget",
        "source_quality_freshness_widget",
        "warning_blocker_widget",
        "signal_strength_calibration_widget",
        "parameter_candidate_comparison_widget",
        "replay_outcome_calibration_widget",
        "producer_freshness_status_widget",
        "runtime_boundary_safety_widget",
        "verified_source_packet_count",
        "warroom_widget_rendering_allowed",
        "warroom_page_mutation_allowed",
        "warroom_mount_patch_allowed",
        "PS-Q17Q WarRoom prediction widget mount contract",
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
        "warroom_page.py",
    ):
        if forbidden in tool_text:
            failures.append(f"forbidden tool token: {forbidden}")
    if 'assert report["verified_source_packet_count"] == 9' not in unit_text:
        failures.append("unit test must expect 9 verified fixture row mappings")
    if "expected 9 verified fixture row mappings" not in _read(REPO_ROOT / FOCUSED_GUARD):
        failures.append("focused guard must expect 9 verified fixture row mappings")
    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint.v1":
        failures.append("checker version mismatch")
    if CHECKPOINT_VERSION != "warroom_prediction_widget_integration_design_checkpoint.v1":
        failures.append("checkpoint version mismatch")
    if tuple(WIDGET_FAMILY_ORDER) != EXPECTED_WIDGETS:
        failures.append("widget family order mismatch")
    for field in ("widget_family_id", "source_packet_id", "source_checker_version", "freshness_field", "source_artifact_ref_field", "release_gate_field", "render_allowed", "page_mutation_allowed", "refresh_invocation_allowed"):
        if field not in REQUIRED_INTEGRATION_FIELDS:
            failures.append(f"required integration field missing: {field}")
    for packet_id in (
        "tier0_source_quality_gate_packet",
        "calibration_reference_packet",
        "prediction_delta_review_packet",
        "replay_outcome_calibration_review_packet",
        "scenario_trace_semantic_mapping_review_packet",
        "parameter_candidate_evidence_review_packet",
    ):
        if packet_id not in SOURCE_CHECKER_VERSIONS:
            failures.append(f"source checker version missing: {packet_id}")

    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture checkpoint should be ok: {report}")
    if report.get("stage") != "warroom_prediction_widget_integration_design_checkpoint_before_ui_mount_and_rendering":
        failures.append("stage mismatch")
    if report.get("source_packet_reports_valid") is not True:
        failures.append("source packet reports should validate")
    if report.get("widget_family_count") != 12:
        failures.append("expected 12 widget families")
    if report.get("verified_source_packet_count") != 9:
        failures.append("expected 9 verified fixture row mappings")
    if report.get("render_blockers") != list(WIDGET_FAMILY_ORDER):
        failures.append("all widget families must block rendering")
    if report.get("page_mutation_blockers") != list(WIDGET_FAMILY_ORDER):
        failures.append("all widget families must block page mutation")
    if report.get("recommended_first_validation") != "latest_prediction_summary_widget_integration_guard":
        failures.append("recommended first validation mismatch")

    rows = {row.get("widget_family_id"): row for row in report.get("integration_rows", [])}
    for widget_id in EXPECTED_WIDGETS:
        if widget_id not in rows:
            failures.append(f"missing widget integration row: {widget_id}")
    for widget_id, packet_id in EXPECTED_SOURCE_PACKETS.items():
        if rows.get(widget_id, {}).get("source_packet_id") != packet_id:
            failures.append(f"packet mapping mismatch: {widget_id}")
    if rows.get("latest_prediction_summary_widget", {}).get("source_packet_state") != "existing_panel_design_only":
        failures.append("latest summary widget should be existing-panel design only")
    if rows.get("producer_freshness_status_widget", {}).get("source_packet_state") != "existing_panel_design_only":
        failures.append("producer freshness widget should be existing-panel design only")
    if rows.get("runtime_boundary_safety_widget", {}).get("source_packet_state") != "design_checkpoint_only":
        failures.append("runtime boundary widget should be design checkpoint only")
    for row in report.get("integration_rows", []):
        if row.get("integration_state") != "design_checkpoint_only":
            failures.append(f"row should be design checkpoint only: {row}")
        for key in ("render_allowed", "page_mutation_allowed", "refresh_invocation_allowed", "write_or_apply_allowed"):
            if row.get(key) is not False:
                failures.append(f"row boundary should stay false: {row.get('widget_family_id')}:{key}")
        if not str(row.get("next_validation", "")).endswith("_integration_guard"):
            failures.append(f"row next validation should be integration guard: {row}")
    _assert_false_boundaries(report, failures)

    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing source reports should block")
    if blocked.get("integration_rows"):
        failures.append("blocked report must not emit integration rows")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source reports should return 1")

    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint.v1",
        "checkpoint_version=warroom_prediction_widget_integration_design_checkpoint.v1",
        "design_checkpoint_only=true",
        "contract_only=true",
        "diagnostic_only=true",
        "warroom_widget_implementation_allowed=false",
        "warroom_widget_rendering_allowed=false",
        "warroom_page_mutation_allowed=false",
        "warroom_mount_patch_allowed=false",
        "latest_prediction_summary_widget -> latest_prediction_source_review_packet",
        "prediction_delta_widget -> prediction_delta_review_packet",
        "scenario_trace_widget -> scenario_trace_semantic_mapping_review_packet",
        "evidence_weighting_widget -> scenario_trace_semantic_mapping_review_packet",
        "invalidation_rewrite_widget -> scenario_trace_semantic_mapping_review_packet",
        "source_quality_freshness_widget -> tier0_source_quality_gate_packet",
        "warning_blocker_widget -> tier0_source_quality_gate_packet",
        "signal_strength_calibration_widget -> calibration_reference_packet",
        "parameter_candidate_comparison_widget -> parameter_candidate_evidence_review_packet",
        "replay_outcome_calibration_widget -> replay_outcome_calibration_review_packet",
        "producer_freshness_status_widget -> producer_status_review_packet",
        "runtime_boundary_safety_widget -> runtime_boundary_safety_review_packet",
        "render_allowed=false",
        "page_mutation_allowed=false",
        "refresh_invocation_allowed=false",
        "no_warroom_page_mutation",
        "no_warroom_page_import_patch",
        "no_widget_rendering_patch",
        "PS-Q17Q: WarRoom prediction widget mount contract",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "warroom_widget_implementation_allowed=true",
        "warroom_widget_rendering_allowed=true",
        "warroom_page_mutation_allowed=true",
        "warroom_mount_patch_allowed=true",
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
    result = {
        "ok": not failures,
        "guard": "ps_q17p_close_guard",
        "phase": "phase3_warroom_prediction_widget_integration_design_checkpoint_closed_before_ui_mount_and_rendering",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17p_closed": not failures,
            "design_checkpoint_only": True,
            "warroom_widget_design_premise": True,
            "warroom_widget_implementation_allowed": False,
            "warroom_widget_rendering_allowed": False,
            "warroom_page_mutation_allowed": False,
            "warroom_mount_patch_allowed": False,
            "refresh_invocation_allowed": False,
            "no_d_hot_actual_read": True,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_parameter_apply": True,
            "no_parameter_staging_write": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
            "next_slice": "PS-Q17Q WarRoom prediction widget mount contract or actual-source preflight",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17p_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
