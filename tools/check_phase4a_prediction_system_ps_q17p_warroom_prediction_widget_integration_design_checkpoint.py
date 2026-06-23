# path: ./tools/check_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint.py
# desc: PS-Q17P non-executing WarRoom prediction widget integration design checkpoint. It consumes prior review-packet checker fixtures and emits a widget-to-source integration contract; it never mutates WarRoom UI, renders widgets, reads D-hot, writes artifacts, invokes refresh, stages/applies parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter import CHECKER_VERSION as PS_Q17E_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17e_tier0_source_quality_gate_contract_adapter import build_report as build_ps_q17e_report
from check_phase4a_prediction_system_ps_q17g_calibration_reference_adapter import CHECKER_VERSION as PS_Q17G_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17g_calibration_reference_adapter import build_report as build_ps_q17g_report
from check_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter import CHECKER_VERSION as PS_Q17I_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17i_prediction_delta_history_adapter import build_report as build_ps_q17i_report
from check_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter import CHECKER_VERSION as PS_Q17K_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17k_replay_outcome_calibration_adapter import build_report as build_ps_q17k_report
from check_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter import CHECKER_VERSION as PS_Q17M_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17m_scenario_trace_semantic_mapping_adapter import build_report as build_ps_q17m_report
from check_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter import CHECKER_VERSION as PS_Q17O_CHECKER_VERSION
from check_phase4a_prediction_system_ps_q17o_parameter_candidate_evidence_adapter import build_report as build_ps_q17o_report

CHECKER = "ps_q17p_warroom_prediction_widget_integration_design_checkpoint"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q17p_warroom_prediction_widget_integration_design_checkpoint.v1"
CHECKPOINT_VERSION = "warroom_prediction_widget_integration_design_checkpoint.v1"

SOURCE_CHECKER_VERSIONS = {
    "tier0_source_quality_gate_packet": PS_Q17E_CHECKER_VERSION,
    "calibration_reference_packet": PS_Q17G_CHECKER_VERSION,
    "prediction_delta_review_packet": PS_Q17I_CHECKER_VERSION,
    "replay_outcome_calibration_review_packet": PS_Q17K_CHECKER_VERSION,
    "scenario_trace_semantic_mapping_review_packet": PS_Q17M_CHECKER_VERSION,
    "parameter_candidate_evidence_review_packet": PS_Q17O_CHECKER_VERSION,
}

WIDGET_FAMILY_ORDER = (
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

REQUIRED_INTEGRATION_FIELDS = (
    "widget_family_id",
    "source_packet_id",
    "source_checker_version",
    "freshness_field",
    "source_artifact_ref_field",
    "release_gate_field",
    "render_allowed",
    "page_mutation_allowed",
    "refresh_invocation_allowed",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _source_reports(*, use_observed_fixture: bool) -> dict[str, Mapping[str, Any]]:
    if not use_observed_fixture:
        return {}
    return {
        "tier0_source_quality_gate_packet": build_ps_q17e_report(use_observed_fixture=True),
        "calibration_reference_packet": build_ps_q17g_report(use_observed_fixture=True),
        "prediction_delta_review_packet": build_ps_q17i_report(use_observed_fixture=True),
        "replay_outcome_calibration_review_packet": build_ps_q17k_report(use_observed_fixture=True),
        "scenario_trace_semantic_mapping_review_packet": build_ps_q17m_report(use_observed_fixture=True),
        "parameter_candidate_evidence_review_packet": build_ps_q17o_report(use_observed_fixture=True),
    }


def _safe_source_packet_reports(reports: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for packet_id, expected_version in SOURCE_CHECKER_VERSIONS.items():
        report = _as_mapping(reports.get(packet_id))
        if not report:
            failures.append(f"source_report_missing:{packet_id}")
            continue
        if report.get("checker_version") != expected_version:
            failures.append(f"source_checker_version_mismatch:{packet_id}")
        if report.get("ok") is not True:
            failures.append(f"source_report_not_ok:{packet_id}")
        for key in (
            "warroom_widget_implementation_allowed",
            "d_hot_actual_read_allowed",
            "runtime_artifact_write_allowed",
            "status_artifact_write_allowed",
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
                failures.append(f"source_boundary_not_false:{packet_id}:{key}")
    return not failures, failures


def _integration_row(widget_family_id: str, source_packet_id: str, *, source_checker_version: str, source_packet_state: str, release_gate_field: str, freshness_field: str, source_artifact_ref_field: str, mount_zone_hint: str, dependency_note: str) -> dict[str, Any]:
    return {
        "widget_family_id": widget_family_id,
        "source_packet_id": source_packet_id,
        "source_checker_version": source_checker_version,
        "source_packet_state": source_packet_state,
        "freshness_field": freshness_field,
        "source_artifact_ref_field": source_artifact_ref_field,
        "release_gate_field": release_gate_field,
        "mount_zone_hint": mount_zone_hint,
        "dependency_note": dependency_note,
        "integration_state": "design_checkpoint_only",
        "render_allowed": False,
        "page_mutation_allowed": False,
        "refresh_invocation_allowed": False,
        "write_or_apply_allowed": False,
        "next_validation": f"{widget_family_id}_integration_guard",
    }


def _build_integration_rows(reports: Mapping[str, Any]) -> list[dict[str, Any]]:
    source_state = {
        packet_id: "verified_fixture" if _as_mapping(reports.get(packet_id)).get("ok") is True else "missing_or_unverified"
        for packet_id in SOURCE_CHECKER_VERSIONS
    }
    rows = [
        _integration_row(
            "latest_prediction_summary_widget",
            "latest_prediction_source_review_packet",
            source_checker_version="existing_prediction_warroom_latest_prediction_source_review_panel_contract",
            source_packet_state="existing_panel_design_only",
            release_gate_field="latest_prediction_summary_release_gate.render_allowed",
            freshness_field="latest_prediction.generated_at",
            source_artifact_ref_field="latest_prediction.source_artifact_ref",
            mount_zone_hint="prediction_summary_zone",
            dependency_note="Existing latest prediction source panel remains read-only; no UI mutation in PS-Q17P.",
        ),
        _integration_row(
            "prediction_delta_widget",
            "prediction_delta_review_packet",
            source_checker_version=PS_Q17I_CHECKER_VERSION,
            source_packet_state=source_state["prediction_delta_review_packet"],
            release_gate_field="prediction_delta_release_gate.widget_reliability_claim_allowed",
            freshness_field="prediction_delta_history.latest_snapshot.generated_at",
            source_artifact_ref_field="prediction_delta_history.latest_snapshot.source_artifact_ref",
            mount_zone_hint="prediction_change_zone",
            dependency_note="Delta packet is review-only; rendering and reliability remain deferred.",
        ),
        _integration_row(
            "scenario_trace_widget",
            "scenario_trace_semantic_mapping_review_packet",
            source_checker_version=PS_Q17M_CHECKER_VERSION,
            source_packet_state=source_state["scenario_trace_semantic_mapping_review_packet"],
            release_gate_field="warroom_scenario_trace_release_gate.render_allowed",
            freshness_field="scenario_trace.scenario_core.generated_at",
            source_artifact_ref_field="scenario_trace.source_artifact_ref",
            mount_zone_hint="scenario_trace_zone",
            dependency_note="Scenario trace semantics are normalized for review only; render remains deferred.",
        ),
        _integration_row(
            "evidence_weighting_widget",
            "scenario_trace_semantic_mapping_review_packet",
            source_checker_version=PS_Q17M_CHECKER_VERSION,
            source_packet_state=source_state["scenario_trace_semantic_mapping_review_packet"],
            release_gate_field="warroom_scenario_trace_release_gate.evidence_reliability_claim_allowed",
            freshness_field="scenario_trace.scenario_core.generated_at",
            source_artifact_ref_field="scenario_trace.source_artifact_ref",
            mount_zone_hint="evidence_weighting_zone",
            dependency_note="Evidence weighting trace is mapped for review only; reliability claim remains false.",
        ),
        _integration_row(
            "invalidation_rewrite_widget",
            "scenario_trace_semantic_mapping_review_packet",
            source_checker_version=PS_Q17M_CHECKER_VERSION,
            source_packet_state=source_state["scenario_trace_semantic_mapping_review_packet"],
            release_gate_field="warroom_scenario_trace_release_gate.invalidation_reliability_claim_allowed",
            freshness_field="scenario_trace.scenario_core.generated_at",
            source_artifact_ref_field="scenario_trace.source_artifact_ref",
            mount_zone_hint="invalidation_rewrite_zone",
            dependency_note="Invalidation rewrite trace is mapped for review only; reliability claim remains false.",
        ),
        _integration_row(
            "source_quality_freshness_widget",
            "tier0_source_quality_gate_packet",
            source_checker_version=PS_Q17E_CHECKER_VERSION,
            source_packet_state=source_state["tier0_source_quality_gate_packet"],
            release_gate_field="confidence_release_gate.source_quality_gate_passed",
            freshness_field="tier0_source_quality_gate.generated_at",
            source_artifact_ref_field="tier0_source_quality_gate.source_artifact_ref",
            mount_zone_hint="source_quality_zone",
            dependency_note="Tier0 source-quality packet remains review-only; confidence increase remains false.",
        ),
        _integration_row(
            "warning_blocker_widget",
            "tier0_source_quality_gate_packet",
            source_checker_version=PS_Q17E_CHECKER_VERSION,
            source_packet_state=source_state["tier0_source_quality_gate_packet"],
            release_gate_field="confidence_release_gate.confidence_increase_allowed",
            freshness_field="tier0_source_quality_gate.generated_at",
            source_artifact_ref_field="tier0_source_quality_gate.source_artifact_ref",
            mount_zone_hint="warning_blocker_zone",
            dependency_note="Warnings can be displayed later as blockers; no freshness bypass or confidence release.",
        ),
        _integration_row(
            "signal_strength_calibration_widget",
            "calibration_reference_packet",
            source_checker_version=PS_Q17G_CHECKER_VERSION,
            source_packet_state=source_state["calibration_reference_packet"],
            release_gate_field="calibration_release_gate.confidence_band_claim_allowed",
            freshness_field="calibration_refs.signal_strength.sample_window.end_at",
            source_artifact_ref_field="calibration_refs.source_artifact_ref",
            mount_zone_hint="calibration_zone",
            dependency_note="Calibration reference packet is review-only; no confidence or tuning release.",
        ),
        _integration_row(
            "parameter_candidate_comparison_widget",
            "parameter_candidate_evidence_review_packet",
            source_checker_version=PS_Q17O_CHECKER_VERSION,
            source_packet_state=source_state["parameter_candidate_evidence_review_packet"],
            release_gate_field="parameter_candidate_release_gate.parameter_staging_allowed",
            freshness_field="parameter_candidate.generated_at",
            source_artifact_ref_field="parameter_candidate.source_artifact_ref",
            mount_zone_hint="parameter_candidate_zone",
            dependency_note="Parameter candidate evidence is complete for review only; staging/apply remain false.",
        ),
        _integration_row(
            "replay_outcome_calibration_widget",
            "replay_outcome_calibration_review_packet",
            source_checker_version=PS_Q17K_CHECKER_VERSION,
            source_packet_state=source_state["replay_outcome_calibration_review_packet"],
            release_gate_field="replay_calibration_release_gate.confidence_reliability_claim_allowed",
            freshness_field="replay_outcome_calibration.replay_feedback.generated_at",
            source_artifact_ref_field="replay_outcome_calibration.replay_feedback.source_artifact_ref",
            mount_zone_hint="replay_outcome_zone",
            dependency_note="Replay outcome packet is review-only; confidence, reliability, and tuning remain false.",
        ),
        _integration_row(
            "producer_freshness_status_widget",
            "producer_status_review_packet",
            source_checker_version="existing_prediction_warroom_non_ui_scheduled_producer_status_panel_contract",
            source_packet_state="existing_panel_design_only",
            release_gate_field="producer_status_release_gate.render_allowed",
            freshness_field="producer_status.generated_at",
            source_artifact_ref_field="producer_status.source_artifact_ref",
            mount_zone_hint="producer_status_zone",
            dependency_note="Producer status panel remains status-read only; no scheduler or refresh trigger.",
        ),
        _integration_row(
            "runtime_boundary_safety_widget",
            "runtime_boundary_safety_review_packet",
            source_checker_version="ps_q17p_derived_from_all_prior_false_boundaries",
            source_packet_state="design_checkpoint_only",
            release_gate_field="runtime_boundary_safety_gate.render_allowed",
            freshness_field="all_source_packets.generated_at",
            source_artifact_ref_field="all_source_packets.source_artifact_ref",
            mount_zone_hint="runtime_safety_zone",
            dependency_note="Runtime boundary widget is a derived review surface only; all unsafe actions stay false.",
        ),
    ]
    return sorted(rows, key=lambda row: WIDGET_FAMILY_ORDER.index(str(row["widget_family_id"])))


def build_report(*, source_reports: Mapping[str, Any] | Any | None = None, use_observed_fixture: bool = False) -> dict[str, Any]:
    reports = _as_mapping(source_reports)
    if not reports and use_observed_fixture:
        reports = _source_reports(use_observed_fixture=True)
    safe_sources, source_failures = _safe_source_packet_reports(reports)
    rows = _build_integration_rows(reports) if safe_sources else []
    render_blockers = [row["widget_family_id"] for row in rows if row.get("render_allowed") is False]
    page_mutation_blockers = [row["widget_family_id"] for row in rows if row.get("page_mutation_allowed") is False]
    verified_source_packet_count = sum(1 for row in rows if row.get("source_packet_state") == "verified_fixture")
    ok = bool(safe_sources and len(rows) == len(WIDGET_FAMILY_ORDER) and render_blockers == list(WIDGET_FAMILY_ORDER))
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "checkpoint_version": CHECKPOINT_VERSION,
        "stage": "warroom_prediction_widget_integration_design_checkpoint_before_ui_mount_and_rendering",
        "source_checker_versions": dict(SOURCE_CHECKER_VERSIONS),
        "source_packet_reports_valid": safe_sources,
        "source_packet_validation_failures": source_failures,
        "use_observed_fixture": bool(use_observed_fixture),
        "widget_family_order": list(WIDGET_FAMILY_ORDER),
        "required_integration_fields": list(REQUIRED_INTEGRATION_FIELDS),
        "integration_rows": rows,
        "widget_family_count": len(rows),
        "verified_source_packet_count": verified_source_packet_count,
        "render_blockers": render_blockers,
        "page_mutation_blockers": page_mutation_blockers,
        "recommended_first_validation": "latest_prediction_summary_widget_integration_guard" if rows else "",
        "recommended_next_slice": "PS-Q17Q WarRoom prediction widget mount contract or actual-source preflight; UI implementation, widget rendering, refresh invocation, confidence increase, and parameter staging/apply remain deferred.",
        "human_interpretation": "PS-Q17P maps verified review packets to WarRoom widget families as a design checkpoint only. It does not mutate WarRoom UI, render widgets, read D-hot, invoke refresh, write artifacts, stage/apply parameters, or trigger generation.",
        "read_only": True,
        "non_executing": True,
        "design_checkpoint_only": True,
        "contract_only": True,
        "diagnostic_only": True,
        "warroom_widget_design_premise": True,
        "warroom_widget_implementation_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "warroom_page_mutation_allowed": False,
        "warroom_mount_patch_allowed": False,
        "warroom_ui_trigger_enabled": False,
        "refresh_invocation_allowed": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "d_hot_actual_read_allowed": False,
        "confidence_increase_allowed": False,
        "signal_reliability_claim_allowed": False,
        "parameter_candidate_reliability_claim_allowed": False,
        "parameter_tuning_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PS-Q17P WarRoom prediction widget integration design checkpoint")
    parser.add_argument("--use-observed-fixture", action="store_true", help="Use prior static review-packet fixtures; no D-hot read or WarRoom UI mutation is performed.")
    args = parser.parse_args(argv)
    report = build_report(use_observed_fixture=args.use_observed_fixture)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
