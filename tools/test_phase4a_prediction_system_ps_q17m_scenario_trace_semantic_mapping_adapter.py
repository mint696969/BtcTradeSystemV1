# path: ./tools/test_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter.py
# desc: Unit tests for PS-Q17M scenario-trace semantic mapping adapter.

from __future__ import annotations

import json

from check_phase4a_prediction_system_ps_q17l_scenario_trace_semantic_mapping_contract import CHECKER_VERSION as PS_Q17L_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter import ADAPTER_VERSION, CHECKER_VERSION, adapt_scenario_trace, build_report, main


def _q17l_report() -> dict:
    return {
        "ok": True,
        "checker_version": PS_Q17L_CHECKER_VERSION,
        "contract_only": True,
        "warroom_widget_implementation_allowed": False,
        "scenario_trace_actual_read_allowed": False,
        "scenario_trace_widget_rendering_allowed": False,
        "scenario_trace_reliability_claim_allowed": False,
        "evidence_weighting_reliability_claim_allowed": False,
        "invalidation_rewrite_reliability_claim_allowed": False,
        "scenario_switch_reliability_claim_allowed": False,
        "d_hot_actual_read_allowed": False,
        "contract_rows": [
            {"contract_id": "scenario_trace_source_key_contract", "priority": "P0", "blocks_scenario_trace_reliability_claim": True},
            {"contract_id": "evidence_weighting_trace_semantic_contract", "priority": "P0", "blocks_scenario_trace_reliability_claim": True},
            {"contract_id": "invalidation_rewrite_trace_semantic_contract", "priority": "P0", "blocks_scenario_trace_reliability_claim": True},
            {"contract_id": "scenario_switch_trace_semantic_contract", "priority": "P0", "blocks_scenario_trace_reliability_claim": True},
            {"contract_id": "warroom_scenario_trace_release_gate_contract", "priority": "P0", "blocks_scenario_trace_reliability_claim": True},
        ],
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "warroom_ui_trigger_enabled": False,
        "refresh_invocation_allowed": False,
        "scheduler_enabled": False,
    }


def _trace() -> dict:
    return {
        "source_artifact_ref": "fixture://trace",
        "scenario_core": {"generated_at": "2026-06-22T01:30:00Z", "scenario_trace_keys": ["context_evidence_profiles", "invalidation_rewrite_candidates", "what_to_watch_next"]},
        "semantic_mapping": {
            "evidence_weighting_trace_key": "context_evidence_profiles",
            "invalidation_rewrite_trace_key": "invalidation_rewrite_candidates",
            "scenario_switch_trace_key": "what_to_watch_next",
        },
        "operator_explanation_trace_taxonomy": {"evidence_label": "Evidence", "invalidation_label": "Invalidation", "scenario_switch_label": "Switch"},
    }


def _assert_safe(report: dict) -> None:
    for key in ("read_only", "non_executing", "adapter_only", "contract_only", "diagnostic_only", "warroom_widget_design_premise"):
        assert report[key] is True, key
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
        assert report[key] is False, key


def test_ps_q17m_adapts_supplied_scenario_trace_to_review_packet() -> None:
    report = build_report(supplied_q17l_report=_q17l_report(), supplied_scenario_trace=_trace())
    assert report["ok"] is True
    assert report["checker_version"] == CHECKER_VERSION
    assert report["adapter_version"] == ADAPTER_VERSION
    packet = report["adapted_packet"]
    trace = packet["scenario_trace"]
    assert trace["source_artifact_ref"] == "fixture://trace"
    assert trace["semantic_mapping"]["semantic_confidence_state"] == "mapped_review_only_unreleased"
    assert trace["semantic_mapping"]["evidence_weighting_trace_present"] is True
    assert trace["semantic_mapping"]["invalidation_rewrite_trace_present"] is True
    assert trace["semantic_mapping"]["scenario_switch_trace_present"] is True
    gate = packet["warroom_scenario_trace_release_gate"]
    assert gate["semantic_mapping_present"] is True
    assert gate["evidence_reliability_claim_allowed"] is False
    assert gate["invalidation_reliability_claim_allowed"] is False
    assert gate["scenario_switch_reliability_claim_allowed"] is False
    assert gate["render_allowed"] is False
    assert packet["warroom_scenario_trace_widget"]["render_allowed"] is False
    _assert_safe(report)


def test_ps_q17m_blocks_invalid_source_contract_or_missing_trace() -> None:
    invalid = build_report()
    assert invalid["ok"] is False
    assert "q17l_checker_version_mismatch" in invalid["source_q17l_validation_failures"]
    _assert_safe(invalid)
    unsafe = _q17l_report()
    unsafe["would_send_to_broker"] = True
    report = build_report(supplied_q17l_report=unsafe, supplied_scenario_trace=_trace())
    assert report["ok"] is False
    assert "q17l_boundary_not_false:would_send_to_broker" in report["source_q17l_validation_failures"]
    _assert_safe(report)
    missing = build_report(supplied_q17l_report=_q17l_report())
    assert missing["ok"] is False
    assert "scenario_trace_missing_or_q17l_invalid" in missing["adapter_validation_failures"]


def test_ps_q17m_observed_fixture_cli_and_main(capsys) -> None:
    assert main(["--use-observed-fixture"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["ok"] is True
    assert printed["use_observed_fixture"] is True
    assert printed["adapter_valid"] is True
    assert printed["adapted_packet"]["trace_packet_version"] == "scenario_trace_semantic_mapping_review_packet.v1"
    assert printed["adapted_packet"]["warroom_scenario_trace_release_gate"]["render_allowed"] is False
    _assert_safe(printed)
    assert main([]) == 1
    blocked = json.loads(capsys.readouterr().out)
    assert blocked["ok"] is False
    _assert_safe(blocked)


def test_ps_q17m_adapter_function_is_pure_and_keeps_release_false() -> None:
    packet = adapt_scenario_trace(_trace())
    assert packet["read_only"] is True
    assert packet["write_or_apply_allowed"] is False
    assert packet["scenario_trace_actual_read_allowed"] is False
    assert packet["scenario_trace_widget_rendering_allowed"] is False
    gate = packet["warroom_scenario_trace_release_gate"]
    assert gate["evidence_reliability_claim_allowed"] is False
    assert gate["invalidation_reliability_claim_allowed"] is False
    assert gate["scenario_switch_reliability_claim_allowed"] is False
    assert gate["render_allowed"] is False
    assert packet["warroom_scenario_trace_widget"]["render_allowed"] is False
