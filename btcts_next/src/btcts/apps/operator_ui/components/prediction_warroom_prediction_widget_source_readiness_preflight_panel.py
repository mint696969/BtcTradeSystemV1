# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_widget_source_readiness_preflight_panel.py
# desc: PS-Q17Z pure-data source readiness preflight rows for Prediction WarRoom widgets. No Streamlit import, no D-hot read, no source artifact resolution, no refresh, no writes.

from __future__ import annotations

from typing import Any

PREDICTION_WARROOM_SOURCE_READINESS_PREFLIGHT_PANEL_VERSION = "prediction_warroom_prediction_widget_source_readiness_preflight_panel.ps_q17z.v1"
EXPECTED_WIDGET_FAMILY_ORDER = (
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
READINESS_SOURCE_ROWS = (
    ("latest_prediction_summary_widget", "latest_prediction_source_review_packet", "latest_prediction.generated_at", "latest_prediction.source_artifact_ref", "latest_prediction_summary_release_gate.render_allowed", "prediction_summary_zone"),
    ("prediction_delta_widget", "prediction_delta_review_packet", "prediction_delta_history.latest_snapshot.generated_at", "prediction_delta_history.latest_snapshot.source_artifact_ref", "prediction_delta_release_gate.widget_reliability_claim_allowed", "prediction_change_zone"),
    ("scenario_trace_widget", "scenario_trace_semantic_mapping_review_packet", "scenario_trace.scenario_core.generated_at", "scenario_trace.source_artifact_ref", "warroom_scenario_trace_release_gate.render_allowed", "scenario_trace_zone"),
    ("evidence_weighting_widget", "scenario_trace_semantic_mapping_review_packet", "scenario_trace.scenario_core.generated_at", "scenario_trace.source_artifact_ref", "warroom_scenario_trace_release_gate.evidence_reliability_claim_allowed", "evidence_weighting_zone"),
    ("invalidation_rewrite_widget", "scenario_trace_semantic_mapping_review_packet", "scenario_trace.scenario_core.generated_at", "scenario_trace.source_artifact_ref", "warroom_scenario_trace_release_gate.invalidation_reliability_claim_allowed", "invalidation_rewrite_zone"),
    ("source_quality_freshness_widget", "tier0_source_quality_gate_packet", "tier0_source_quality_gate.generated_at", "tier0_source_quality_gate.source_artifact_ref", "confidence_release_gate.source_quality_gate_passed", "source_quality_zone"),
    ("warning_blocker_widget", "tier0_source_quality_gate_packet", "tier0_source_quality_gate.generated_at", "tier0_source_quality_gate.source_artifact_ref", "confidence_release_gate.confidence_increase_allowed", "warning_blocker_zone"),
    ("signal_strength_calibration_widget", "calibration_reference_packet", "calibration_refs.signal_strength.sample_window.end_at", "calibration_refs.source_artifact_ref", "calibration_release_gate.confidence_band_claim_allowed", "calibration_zone"),
    ("parameter_candidate_comparison_widget", "parameter_candidate_evidence_review_packet", "parameter_candidate.generated_at", "parameter_candidate.source_artifact_ref", "parameter_candidate_release_gate.parameter_staging_allowed", "parameter_candidate_zone"),
    ("replay_outcome_calibration_widget", "replay_outcome_calibration_review_packet", "replay_outcome_calibration.replay_feedback.generated_at", "replay_outcome_calibration.replay_feedback.source_artifact_ref", "replay_calibration_release_gate.confidence_reliability_claim_allowed", "replay_outcome_zone"),
    ("producer_freshness_status_widget", "producer_status_review_packet", "producer_status.generated_at", "producer_status.source_artifact_ref", "producer_status_release_gate.render_allowed", "producer_status_zone"),
    ("runtime_boundary_safety_widget", "runtime_boundary_safety_review_packet", "all_source_packets.generated_at", "all_source_packets.source_artifact_ref", "runtime_boundary_safety_gate.render_allowed", "runtime_safety_zone"),
)


def build_prediction_warroom_prediction_widget_source_readiness_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, (widget_id, source_packet_id, freshness_field, source_artifact_ref_field, release_gate_field, mount_zone_hint) in enumerate(READINESS_SOURCE_ROWS):
        rows.append({
            "row_index": index,
            "widget_family_id": widget_id,
            "source_packet_id": source_packet_id,
            "freshness_field": freshness_field,
            "source_artifact_ref_field": source_artifact_ref_field,
            "release_gate_field": release_gate_field,
            "mount_zone_hint": mount_zone_hint,
            "source_readiness_state": "source_binding_ready_actual_read_deferred",
            "actual_source_binding_ready": True,
            "readiness_row_visible_in_warroom": True,
            "actual_source_bound": False,
            "source_artifact_resolution_allowed": False,
            "source_artifact_resolved": False,
            "freshness_checked_against_d_hot": False,
            "real_widget_render_ready": False,
            "render_allowed": False,
            "actual_source_read_allowed": False,
            "d_hot_actual_read_allowed": False,
            "refresh_invocation_allowed": False,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "confidence_increase_allowed": False,
            "parameter_apply_allowed": False,
            "parameter_staging_write_allowed": False,
            "ledger_append_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
        })
    return rows


def build_prediction_warroom_prediction_widget_source_readiness_preflight_packet() -> dict[str, Any]:
    rows = build_prediction_warroom_prediction_widget_source_readiness_rows()
    failures: list[str] = []
    if [row["widget_family_id"] for row in rows] != list(EXPECTED_WIDGET_FAMILY_ORDER):
        failures.append("widget_family_order_mismatch")
    for row in rows:
        widget_id = str(row.get("widget_family_id") or "")
        for field in ("source_packet_id", "freshness_field", "source_artifact_ref_field", "release_gate_field"):
            if not str(row.get(field) or ""):
                failures.append(f"missing_source_binding_field:{widget_id}:{field}")
        if row.get("actual_source_binding_ready") is not True:
            failures.append(f"binding_not_ready:{widget_id}")
        if row.get("readiness_row_visible_in_warroom") is not True:
            failures.append(f"readiness_row_not_visible:{widget_id}")
        for key in (
            "actual_source_bound",
            "source_artifact_resolution_allowed",
            "source_artifact_resolved",
            "freshness_checked_against_d_hot",
            "real_widget_render_ready",
            "render_allowed",
            "actual_source_read_allowed",
            "d_hot_actual_read_allowed",
            "refresh_invocation_allowed",
            "runtime_artifact_write_allowed",
            "status_artifact_write_allowed",
            "confidence_increase_allowed",
            "parameter_apply_allowed",
            "parameter_staging_write_allowed",
            "ledger_append_allowed",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
        ):
            if row.get(key) is not False:
                failures.append(f"false_boundary_not_false:{widget_id}:{key}")
    unique_source_packet_ids = sorted({str(row.get("source_packet_id") or "") for row in rows})
    return {
        "ok": not failures,
        "panel_version": PREDICTION_WARROOM_SOURCE_READINESS_PREFLIGHT_PANEL_VERSION,
        "source_readiness_preflight_state": "warroom_source_readiness_rows_visible_actual_read_deferred",
        "readiness_row_count": len(rows),
        "unique_source_packet_count": len(unique_source_packet_ids),
        "unique_source_packet_ids": unique_source_packet_ids,
        "readiness_rows": rows,
        "validation_failures": failures,
        "read_only": True,
        "non_executing": True,
        "source_readiness_row_mount_only": True,
        "readiness_row_visible_in_warroom": True,
        "source_binding_contract_ready": True,
        "source_artifact_resolution_allowed": False,
        "actual_source_bound": False,
        "source_artifact_resolved": False,
        "freshness_checked_against_d_hot": False,
        "real_prediction_widget_rendering_allowed": False,
        "warroom_widget_rendering_allowed": False,
        "actual_source_read_allowed": False,
        "d_hot_actual_read_allowed": False,
        "refresh_invocation_allowed": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "confidence_increase_allowed": False,
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
