# path: ./tools/test_phase4a_prediction_system_ps_q17m_close_guard.py
# desc: Close guard for PS-Q17M scenario-trace semantic mapping adapter.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from check_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter import ADAPTER_VERSION, CHECKER_VERSION, SEMANTIC_TRACE_FIELDS, TRACE_PACKET_VERSION, adapt_scenario_trace, build_report, main

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q17M_SCENARIO_TRACE_SEMANTIC_MAPPING_ADAPTER_2026-06-22.md"
FOCUSED_GUARD = "tools/test_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter.py",
    "tools/test_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q17M_SCENARIO_TRACE_SEMANTIC_MAPPING_ADAPTER_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter_guard.py",
    "tools/test_phase4a_prediction_system_ps_q17m_close_guard.py",
}
REQUIRED_PACKET_KEYS = (
    "scenario_trace",
    "warroom_scenario_trace_release_gate",
    "contract_completeness",
    "warroom_scenario_trace_widget",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip()}


def _assert_false_boundaries(report: dict, failures: list[str]) -> None:
    for key in (
        "read_only",
        "non_executing",
        "adapter_only",
        "contract_only",
        "diagnostic_only",
        "warroom_widget_design_premise",
    ):
        if report.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "warroom_widget_implementation_allowed",
        "scenario_trace_actual_read_allowed",
        "scenario_trace_widget_rendering_allowed",
        "scenario_trace_reliability_claim_allowed",
        "evidence_weighting_reliability_claim_allowed",
        "invalidation_rewrite_reliability_claim_allowed",
        "scenario_switch_reliability_claim_allowed",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "d_hot_actual_read_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
        "warroom_ui_trigger_enabled",
        "refresh_invocation_allowed",
        "scheduler_enabled",
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
        "CHECKER = \"ps_q17m_scenario_trace_semantic_mapping_adapter\"",
        "CHECKER_VERSION = \"check_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter.v1\"",
        "ADAPTER_VERSION = \"scenario_trace_semantic_mapping_adapter.v1\"",
        "TRACE_PACKET_VERSION = \"scenario_trace_semantic_mapping_review_packet.v1\"",
        "PS_Q17L_SOURCE_CHECKER_VERSION",
        "SEMANTIC_TRACE_FIELDS",
        "adapt_scenario_trace",
        "_safe_q17l_boundary",
        "_adapter_valid",
        "scenario_trace",
        "semantic_mapping",
        "warroom_scenario_trace_release_gate",
        "warroom_scenario_trace_widget",
        "semantic_confidence_state",
        "mapped_review_only_unreleased",
        "scenario_trace_actual_read_allowed",
        "scenario_trace_widget_rendering_allowed",
        "scenario_trace_reliability_claim_allowed",
        "evidence_weighting_reliability_claim_allowed",
        "invalidation_rewrite_reliability_claim_allowed",
        "scenario_switch_reliability_claim_allowed",
        "PS-Q17N parameter-candidate evidence contract",
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
    if "test_ps_q17m_adapts_supplied_scenario_trace_to_review_packet" not in unit_text:
        failures.append("unit test must cover supplied scenario trace adaptation")
    if "test_ps_q17m_blocks_invalid_source_contract_or_missing_trace" not in unit_text:
        failures.append("unit test must cover invalid source/missing trace blocking")

    if CHECKER_VERSION != "check_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter.v1":
        failures.append("checker version mismatch")
    if ADAPTER_VERSION != "scenario_trace_semantic_mapping_adapter.v1":
        failures.append("adapter version mismatch")
    if TRACE_PACKET_VERSION != "scenario_trace_semantic_mapping_review_packet.v1":
        failures.append("trace packet version mismatch")
    if tuple(SEMANTIC_TRACE_FIELDS) != ("evidence_weighting", "invalidation_rewrite", "scenario_switch"):
        failures.append("semantic trace fields mismatch")

    report = build_report(use_observed_fixture=True)
    if report.get("ok") is not True:
        failures.append(f"observed fixture adapter should be ok: {report}")
    if report.get("stage") != "scenario_trace_semantic_mapping_adapter_before_reliability_and_widget_rendering":
        failures.append("stage mismatch")
    if report.get("source_q17l_report_valid") is not True:
        failures.append("observed fixture source Q17L should validate")
    if report.get("adapter_valid") is not True:
        failures.append("adapter should validate")
    if report.get("adapter_validation_failures"):
        failures.append(f"adapter validation failures should be empty: {report.get('adapter_validation_failures')}")

    packet = report.get("adapted_packet", {})
    for key in REQUIRED_PACKET_KEYS:
        if key not in packet:
            failures.append(f"adapted packet missing: {key}")
    if packet.get("adapter_version") != "scenario_trace_semantic_mapping_adapter.v1":
        failures.append("adapter version in packet mismatch")
    if packet.get("trace_packet_version") != "scenario_trace_semantic_mapping_review_packet.v1":
        failures.append("trace packet version in packet mismatch")
    scenario_trace = packet.get("scenario_trace", {})
    semantic = scenario_trace.get("semantic_mapping", {})
    gate = packet.get("warroom_scenario_trace_release_gate", {})
    completeness = packet.get("contract_completeness", {})
    widget = packet.get("warroom_scenario_trace_widget", {})

    if scenario_trace.get("source_artifact_ref") != "fixture://prediction/scenario_trace.json":
        failures.append("fixture source artifact ref mismatch")
    if scenario_trace.get("scenario_core", {}).get("generated_at") != "2026-06-22T01:30:00Z":
        failures.append("fixture generated_at mismatch")
    if semantic.get("semantic_confidence_state") != "mapped_review_only_unreleased":
        failures.append("semantic confidence state mismatch")
    for key in ("evidence_weighting_trace_present", "invalidation_rewrite_trace_present", "scenario_switch_trace_present"):
        if semantic.get(key) is not True:
            failures.append(f"semantic mapping should be present: {key}")
    if semantic.get("evidence_weighting_trace_key") != "context_evidence_profiles":
        failures.append("evidence weighting trace key mismatch")
    if semantic.get("invalidation_rewrite_trace_key") != "invalidation_rewrite_candidates":
        failures.append("invalidation rewrite trace key mismatch")
    if semantic.get("scenario_switch_trace_key") != "what_to_watch_next":
        failures.append("scenario switch trace key mismatch")
    if semantic.get("unmapped_trace_keys") != ["tier0_source_quality_gate"]:
        failures.append("unmapped trace keys mismatch")
    if gate.get("semantic_mapping_present") is not True:
        failures.append("semantic mapping present should be true")
    if gate.get("blocking_reason_codes") != ["adapter_stage_no_scenario_trace_reliability_release"]:
        failures.append("release gate should retain adapter-stage blocker")
    for key in ("evidence_reliability_claim_allowed", "invalidation_reliability_claim_allowed", "scenario_switch_reliability_claim_allowed", "render_allowed"):
        if gate.get(key) is not False:
            failures.append(f"release gate must keep false: {key}")
    if widget.get("render_allowed") is not False:
        failures.append("WarRoom scenario trace widget render must remain false")
    if widget.get("mapped_trace_key_count") != 3:
        failures.append("mapped trace key count should be 3")
    if widget.get("unmapped_trace_key_count") != 1:
        failures.append("unmapped trace key count should be 1")
    for key in ("has_source_artifact_ref", "has_scenario_core_keys", "has_evidence_mapping", "has_invalidation_mapping", "has_scenario_switch_mapping", "has_release_gate", "has_operator_taxonomy"):
        if completeness.get(key) is not True:
            failures.append(f"contract completeness should be true: {key}")
    _assert_false_boundaries(report, failures)

    direct_packet = adapt_scenario_trace({
        "source_artifact_ref": "fixture://trace",
        "scenario_core": {"generated_at": "2026-06-22T01:30:00Z", "scenario_trace_keys": ["context_evidence_profiles", "invalidation_rewrite_candidates", "what_to_watch_next"]},
        "semantic_mapping": {
            "evidence_weighting_trace_key": "context_evidence_profiles",
            "invalidation_rewrite_trace_key": "invalidation_rewrite_candidates",
            "scenario_switch_trace_key": "what_to_watch_next",
        },
        "operator_explanation_trace_taxonomy": {"evidence_label": "Evidence", "invalidation_label": "Invalidation", "scenario_switch_label": "Switch"},
    })
    direct_gate = direct_packet.get("warroom_scenario_trace_release_gate", {})
    for key in ("evidence_reliability_claim_allowed", "invalidation_reliability_claim_allowed", "scenario_switch_reliability_claim_allowed", "render_allowed"):
        if direct_gate.get(key) is not False:
            failures.append(f"direct adapter gate should remain false: {key}")
    if direct_packet.get("warroom_scenario_trace_widget", {}).get("render_allowed") is not False:
        failures.append("direct adapter render should remain false")

    blocked = build_report()
    if blocked.get("ok") is not False:
        failures.append("missing Q17L source/scenario trace should block")
    if blocked.get("adapted_packet"):
        failures.append("blocked report must not emit adapted packet")
    _assert_false_boundaries(blocked, failures)
    if main(["--use-observed-fixture"]) != 0:
        failures.append("CLI observed fixture should return 0")
    if main([]) != 1:
        failures.append("CLI without source should return 1")

    for marker in (
        "checker=check_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter.v1",
        "adapter_version=scenario_trace_semantic_mapping_adapter.v1",
        "source_checker=check_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract.v1",
        "adapter_only=true",
        "contract_only=true",
        "diagnostic_only=true",
        "warroom_widget_implementation_allowed=false",
        "scenario_trace_actual_read_allowed=false",
        "scenario_trace_widget_rendering_allowed=false",
        "scenario_trace_reliability_claim_allowed=false",
        "evidence_weighting_reliability_claim_allowed=false",
        "invalidation_rewrite_reliability_claim_allowed=false",
        "scenario_switch_reliability_claim_allowed=false",
        "d_hot_actual_read_allowed=false",
        "scenario_trace.source_artifact_ref",
        "scenario_trace.scenario_core.generated_at",
        "scenario_trace.semantic_mapping.evidence_weighting_trace_key",
        "scenario_trace.semantic_mapping.invalidation_rewrite_trace_present",
        "scenario_trace.semantic_mapping.scenario_switch_trace_present",
        "scenario_trace.semantic_mapping.semantic_confidence_state=mapped_review_only_unreleased",
        "warroom_scenario_trace_release_gate.semantic_mapping_present",
        "warroom_scenario_trace_release_gate.render_allowed=false",
        "warroom_scenario_trace_widget.render_allowed=false",
        "no_scenario_trace_actual_read",
        "no_live_semantic_inference",
        "PS-Q17N: parameter-candidate evidence contract",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for forbidden in (
        "warroom_widget_implementation_allowed=true",
        "scenario_trace_actual_read_allowed=true",
        "scenario_trace_widget_rendering_allowed=true",
        "scenario_trace_reliability_claim_allowed=true",
        "evidence_weighting_reliability_claim_allowed=true",
        "invalidation_rewrite_reliability_claim_allowed=true",
        "scenario_switch_reliability_claim_allowed=true",
        "d_hot_actual_read_allowed=true",
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
        "guard": "ps_q17m_close_guard",
        "phase": "phase3_scenario_trace_semantic_mapping_adapter_closed_before_reliability_and_widget_rendering",
        "focused_guards_to_run_before_commit": [FOCUSED_GUARD],
        "contract": {
            "ps_q17m_closed": not failures,
            "adapter_only": True,
            "source_q17l_required": True,
            "warroom_widget_design_premise": True,
            "warroom_widget_implementation_allowed": False,
            "scenario_trace_actual_read_allowed": False,
            "scenario_trace_widget_rendering_allowed": False,
            "scenario_trace_reliability_claim_allowed": False,
            "evidence_weighting_reliability_claim_allowed": False,
            "invalidation_rewrite_reliability_claim_allowed": False,
            "scenario_switch_reliability_claim_allowed": False,
            "no_d_hot_actual_read": True,
            "no_runtime_write": True,
            "no_status_write": True,
            "no_parameter_apply": True,
            "no_parameter_staging_write": True,
            "no_ledger_append": True,
            "no_autotrade": True,
            "no_broker": True,
            "next_slice": "PS-Q17N parameter-candidate evidence contract or WarRoom prediction widget integration design checkpoint",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q17m_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
