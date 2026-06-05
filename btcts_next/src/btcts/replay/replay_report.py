# path: ./btcts_next/src/btcts/replay/replay_report.py
# desc: Build replay summary reports from fusion results.

from __future__ import annotations

from typing import Dict, List

from .prediction_evaluation_report import build_prediction_evaluation_report


def _build_tactic_compare_friendly_summary_line(
    *,
    tactic_key: object,
    comparison_relation: object,
    overlay_influence: object,
    overlay_application_mode: object,
    rollback_target_ref: object,
    adoption_ready: object,
    selected_set_id: object,
) -> str:
    operating_stance = str(tactic_key or "").strip()
    if not operating_stance:
        return ""

    parts: list[str] = [operating_stance]

    normalized_relation = str(comparison_relation or "").strip()
    if normalized_relation:
        parts.append(normalized_relation)

    normalized_overlay = str(overlay_influence or "").strip()
    if normalized_overlay == "overlay_bias":
        parts.append("overlay_bias_present")

    normalized_overlay_mode = str(overlay_application_mode or "").strip()
    if normalized_overlay_mode == "primary_only":
        parts.append("overlay_primary")
    elif normalized_overlay_mode == "primary_and_support":
        parts.append("overlay_primary_plus_support")
    elif normalized_overlay_mode == "support_only":
        parts.append("overlay_support_only")

    normalized_selected_set_id = str(selected_set_id or "").strip()
    if normalized_selected_set_id:
        parts.append(f"selected_set={normalized_selected_set_id}")

    normalized_rollback_target_ref = str(rollback_target_ref or "").strip()
    if normalized_rollback_target_ref:
        parts.append(f"rollback_target={normalized_rollback_target_ref}")

    if adoption_ready is True:
        parts.append("adoption_ready_for_review")

    parts.append("review_only")

    return " | ".join(parts)


def _build_prediction_calibration_review_summary(
    prediction_calibration_reviews: List[Dict] | None,
) -> Dict | None:
    if not prediction_calibration_reviews:
        return None

    latest_review = dict(prediction_calibration_reviews[-1] or {})
    return {
        "review_count": len(prediction_calibration_reviews),
        "latest_review_priority": latest_review.get("review_priority"),
        "latest_primary_focus": latest_review.get("primary_focus"),
        "latest_confidence_review": latest_review.get("confidence_review"),
        "latest_caution_review": latest_review.get("caution_review"),
        "latest_invalidation_review": latest_review.get("invalidation_review"),
    }


def _build_tactic_proposal_summary(
    tactic_proposal_outputs: List[Dict] | None,
) -> Dict | None:
    if not tactic_proposal_outputs:
        return None

    latest_proposal = dict(tactic_proposal_outputs[-1] or {})
    diagnostics = dict(latest_proposal.get("diagnostics", {}) or {})
    parameter_trace = dict(diagnostics.get("parameter_trace", {}) or {})
    selection_trace = dict(diagnostics.get("selection_trace", {}) or {})
    compare_friendly_summary_line = _build_tactic_compare_friendly_summary_line(
        tactic_key=latest_proposal.get("primary_tactic_key"),
        comparison_relation=parameter_trace.get("comparison_relation"),
        overlay_influence=parameter_trace.get("overlay_influence"),
        overlay_application_mode=selection_trace.get("overlay_application_mode"),
        rollback_target_ref=parameter_trace.get("rollback_target_ref"),
        adoption_ready=diagnostics.get("adoption_ready"),
        selected_set_id=diagnostics.get("selected_set_id"),
    )
    return {
        "proposal_count": len(tactic_proposal_outputs),
        "latest_primary_tactic_key": latest_proposal.get("primary_tactic_key"),
        "latest_proposal_state": latest_proposal.get("proposal_state"),
        "latest_scenario_regime": latest_proposal.get("scenario_regime"),
        "latest_profile_kind": parameter_trace.get("profile_kind"),
        "latest_adoption_ready": diagnostics.get("adoption_ready"),
        "latest_selected_set_id": diagnostics.get("selected_set_id"),
        "latest_rollback_target_ref": parameter_trace.get("rollback_target_ref"),
        "latest_comparison_profile_kinds": parameter_trace.get(
            "comparison_profile_kinds"
        ),
        "latest_comparison_active_index": parameter_trace.get(
            "comparison_active_index"
        ),
        "latest_comparison_baseline_available": parameter_trace.get(
            "comparison_baseline_available"
        ),
        "latest_comparison_relation": parameter_trace.get(
            "comparison_relation"
        ),
        "latest_overlay_influence": parameter_trace.get(
            "overlay_influence"
        ),
        "latest_overlay_application_mode": selection_trace.get(
            "overlay_application_mode"
        ),
        "latest_compare_friendly_summary_line": compare_friendly_summary_line,
    }


def _build_tactic_review_record_summary(
    tactic_review_records: List[Dict] | None,
) -> Dict | None:
    if not tactic_review_records:
        return None

    latest_review = dict(tactic_review_records[-1] or {})
    diagnostics = dict(latest_review.get("diagnostics", {}) or {})
    parameter_trace = dict(latest_review.get("parameter_trace", {}) or {})
    selection_trace = dict(latest_review.get("selection_trace", {}) or {})
    compare_friendly_summary_line = _build_tactic_compare_friendly_summary_line(
        tactic_key=latest_review.get("selected_tactic_key"),
        comparison_relation=parameter_trace.get("comparison_relation"),
        overlay_influence=parameter_trace.get("overlay_influence"),
        overlay_application_mode=selection_trace.get("overlay_application_mode"),
        rollback_target_ref=latest_review.get("rollback_target_ref"),
        adoption_ready=diagnostics.get("adoption_ready"),
        selected_set_id=diagnostics.get("selected_set_id"),
    )
    return {
        "review_count": len(tactic_review_records),
        "latest_selected_tactic_key": latest_review.get("selected_tactic_key"),
        "latest_decision_state": latest_review.get("decision_state"),
        "latest_rollback_target_ref": latest_review.get("rollback_target_ref"),
        "latest_adoption_ready": diagnostics.get("adoption_ready"),
        "latest_selected_set_id": diagnostics.get("selected_set_id"),
        "latest_comparison_ref_count": diagnostics.get("comparison_ref_count"),
        "latest_comparison_profile_kinds": parameter_trace.get(
            "comparison_profile_kinds"
        ),
        "latest_comparison_active_index": parameter_trace.get(
            "comparison_active_index"
        ),
        "latest_comparison_baseline_available": parameter_trace.get(
            "comparison_baseline_available"
        ),
        "latest_comparison_relation": parameter_trace.get(
            "comparison_relation"
        ),
        "latest_overlay_influence": parameter_trace.get(
            "overlay_influence"
        ),
        "latest_overlay_application_mode": selection_trace.get(
            "overlay_application_mode"
        ),
        "latest_compare_friendly_summary_line": compare_friendly_summary_line,
    }


def _build_prediction_direction_summary(
    prediction_direction_snapshots: List[Dict] | None,
) -> Dict | None:
    if not prediction_direction_snapshots:
        return None

    latest_snapshot = dict(prediction_direction_snapshots[-1] or {})
    diagnostics = dict(latest_snapshot.get("diagnostics", {}) or {})
    diagnostic_quality = dict(diagnostics.get("diagnostic_quality", {}) or {})
    diagnostic_quality_required_flags = [
        "scenario_ref_present",
        "market_uid_present",
        "event_ts_present",
        "scenario_regime_bias_present",
        "artifact_only_marker_present",
        "read_only_marker_present",
        "runtime_wiring_closed",
        "ui_wiring_closed",
        "market_engine_wiring_closed",
    ]
    diagnostic_quality_passed_count = sum(
        1
        for key in diagnostic_quality_required_flags
        if diagnostic_quality.get(key) is True
    )
    horizon_readings = list(
        latest_snapshot.get("horizon_direction_readings", []) or []
    )
    horizon_count = len(horizon_readings)
    caution_count = 0
    horizon_labels: list[str] = []
    for reading in horizon_readings:
        if not isinstance(reading, dict):
            continue
        horizon = str(reading.get("horizon") or "").strip()
        if horizon:
            horizon_labels.append(horizon)
        if reading.get("caution_flag") is True:
            caution_count += 1

    return {
        "snapshot_count": len(prediction_direction_snapshots),
        "latest_prediction_type": latest_snapshot.get("prediction_type"),
        "latest_source_kind": latest_snapshot.get("source_kind"),
        "latest_market_uid": latest_snapshot.get("market_uid"),
        "latest_event_ts": latest_snapshot.get("event_ts"),
        "latest_scenario_ref": latest_snapshot.get("scenario_ref"),
        "latest_primary_direction_bias": latest_snapshot.get(
            "primary_direction_bias"
        ),
        "latest_horizon_count": horizon_count,
        "latest_horizons": horizon_labels,
        "latest_caution_horizon_count": caution_count,
        "latest_evidence_trace_ref_count": len(
            latest_snapshot.get("evidence_trace_refs", []) or []
        ),
        "latest_artifact_only": diagnostics.get("artifact_only"),
        "latest_read_only_contract": latest_snapshot.get("read_only_contract"),
        "latest_not_runtime_wiring": latest_snapshot.get("not_runtime_wiring"),
        "latest_not_ui_wiring": latest_snapshot.get("not_ui_wiring"),
        "latest_diagnostic_quality_version": diagnostic_quality.get(
            "quality_version"
        ),
        "latest_diagnostic_quality_passed_count": (
            diagnostic_quality_passed_count
        ),
        "latest_diagnostic_quality_required_count": len(
            diagnostic_quality_required_flags
        ),
        "latest_diagnostic_quality_ok": diagnostic_quality_passed_count
        == len(diagnostic_quality_required_flags),
    }


def _summarize_position_review_hint_snapshot(
    prediction_position_review_hint_snapshots: List[Dict] | None,
) -> Dict | None:
    if not prediction_position_review_hint_snapshots:
        return None

    latest_snapshot = dict(prediction_position_review_hint_snapshots[-1] or {})
    diagnostics = dict(latest_snapshot.get("diagnostics", {}) or {})
    return {
        "snapshot_count": len(prediction_position_review_hint_snapshots),
        "latest_prediction_type": latest_snapshot.get("prediction_type"),
        "latest_source_kind": latest_snapshot.get("source_kind"),
        "latest_market_uid": latest_snapshot.get("market_uid"),
        "latest_event_ts": latest_snapshot.get("event_ts"),
        "latest_scenario_ref": latest_snapshot.get("scenario_ref"),
        "latest_direction_ref": latest_snapshot.get("direction_ref"),
        "latest_position_context_ref": latest_snapshot.get("position_context_ref"),
        "latest_position_state_reading": latest_snapshot.get("position_state_reading"),
        "latest_management_hint": latest_snapshot.get("management_hint"),
        "latest_exposure_risk_hint": latest_snapshot.get("exposure_risk_hint"),
        "latest_evidence_trace_ref_count": len(latest_snapshot.get("evidence_trace_refs", []) or []),
        "latest_artifact_only": diagnostics.get("artifact_only"),
        "latest_read_only_contract": latest_snapshot.get("read_only_contract"),
        "latest_not_runtime_wiring": latest_snapshot.get("not_runtime_wiring"),
        "latest_not_ui_wiring": latest_snapshot.get("not_ui_wiring"),
    }


def _summarize_execution_review_hint_snapshot(
    prediction_execution_review_hint_snapshots: List[Dict] | None,
) -> Dict | None:
    if not prediction_execution_review_hint_snapshots:
        return None

    latest_snapshot = dict(prediction_execution_review_hint_snapshots[-1] or {})
    diagnostics = dict(latest_snapshot.get("diagnostics", {}) or {})
    return {
        "snapshot_count": len(prediction_execution_review_hint_snapshots),
        "latest_prediction_type": latest_snapshot.get("prediction_type"),
        "latest_source_kind": latest_snapshot.get("source_kind"),
        "latest_market_uid": latest_snapshot.get("market_uid"),
        "latest_event_ts": latest_snapshot.get("event_ts"),
        "latest_scenario_ref": latest_snapshot.get("scenario_ref"),
        "latest_direction_ref": latest_snapshot.get("direction_ref"),
        "latest_position_ref": latest_snapshot.get("position_ref"),
        "latest_execution_context_ref": latest_snapshot.get("execution_context_ref"),
        "latest_timing_hint": latest_snapshot.get("timing_hint"),
        "latest_urgency_hint": latest_snapshot.get("urgency_hint"),
        "latest_feasibility_hint": latest_snapshot.get("feasibility_hint"),
        "latest_evidence_trace_ref_count": len(latest_snapshot.get("evidence_trace_refs", []) or []),
        "latest_artifact_only": diagnostics.get("artifact_only"),
        "latest_read_only_contract": latest_snapshot.get("read_only_contract"),
        "latest_execution_side_effect_free": latest_snapshot.get("execution_side_effect_free"),
        "latest_broker_link_free": latest_snapshot.get("broker_link_free"),
        "latest_account_side_effect_free": latest_snapshot.get("account_side_effect_free"),
        "latest_not_runtime_wiring": latest_snapshot.get("not_runtime_wiring"),
        "latest_not_ui_wiring": latest_snapshot.get("not_ui_wiring"),
    }


def _build_direction_replay_calibration_review_material(
    prediction_direction_summary: Dict | None,
) -> Dict | None:
    if not prediction_direction_summary:
        return None

    latest_source_kind = prediction_direction_summary.get("latest_source_kind")
    read_only_contract = prediction_direction_summary.get(
        "latest_read_only_contract"
    )
    not_runtime_wiring = prediction_direction_summary.get(
        "latest_not_runtime_wiring"
    )
    not_ui_wiring = prediction_direction_summary.get("latest_not_ui_wiring")
    diagnostic_quality_ok = prediction_direction_summary.get(
        "latest_diagnostic_quality_ok"
    )
    caution_horizon_count = int(
        prediction_direction_summary.get("latest_caution_horizon_count") or 0
    )
    evidence_ref_count = int(
        prediction_direction_summary.get("latest_evidence_trace_ref_count") or 0
    )
    horizon_count = int(
        prediction_direction_summary.get("latest_horizon_count") or 0
    )

    review_flags: list[str] = []
    if latest_source_kind != "replay_artifact_only":
        review_flags.append("unexpected_source_kind")
    if read_only_contract is not True:
        review_flags.append("read_only_contract_missing")
    if not_runtime_wiring is not True:
        review_flags.append("runtime_wiring_not_closed")
    if not_ui_wiring is not True:
        review_flags.append("ui_wiring_not_closed")
    if diagnostic_quality_ok is not True:
        review_flags.append("diagnostic_quality_review_required")
    if caution_horizon_count > 0:
        review_flags.append("caution_horizon_review")
    if evidence_ref_count == 0:
        review_flags.append("evidence_trace_review_required")
    if horizon_count == 0:
        review_flags.append("horizon_coverage_review_required")

    if not review_flags:
        review_flags.append("keep_current_course")

    review_priority = "normal"
    if diagnostic_quality_ok is not True or horizon_count == 0:
        review_priority = "high"
    elif caution_horizon_count > 0 or evidence_ref_count == 0:
        review_priority = "medium"

    return {
        "material_type": "direction_replay_calibration_review_material",
        "material_version": "phase4a.direction_replay_calibration_review.v1",
        "source_kind": "replay_report_prediction_direction_summary",
        "review_only": True,
        "read_only_contract": True,
        "not_runtime_wiring": True,
        "not_ui_wiring": True,
        "not_market_engine_wiring": True,
        "snapshot_count": prediction_direction_summary.get("snapshot_count"),
        "latest_primary_direction_bias": prediction_direction_summary.get(
            "latest_primary_direction_bias"
        ),
        "latest_horizon_count": horizon_count,
        "latest_caution_horizon_count": caution_horizon_count,
        "latest_evidence_trace_ref_count": evidence_ref_count,
        "latest_diagnostic_quality_ok": diagnostic_quality_ok,
        "review_priority": review_priority,
        "review_flags": review_flags,
    }


def _build_tactic_operation_record_summary(
    tactic_operation_records: List[Dict] | None,
) -> Dict | None:
    if not tactic_operation_records:
        return None

    latest_operation = dict(tactic_operation_records[-1] or {})
    diagnostics = dict(latest_operation.get("diagnostics", {}) or {})
    parameter_trace = dict(latest_operation.get("parameter_trace", {}) or {})
    selection_trace = dict(latest_operation.get("selection_trace", {}) or {})
    compare_friendly_summary_line = _build_tactic_compare_friendly_summary_line(
        tactic_key=latest_operation.get("selected_tactic_key"),
        comparison_relation=parameter_trace.get("comparison_relation"),
        overlay_influence=parameter_trace.get("overlay_influence"),
        overlay_application_mode=selection_trace.get("overlay_application_mode"),
        rollback_target_ref=latest_operation.get("rollback_target_ref"),
        adoption_ready=diagnostics.get("adoption_ready"),
        selected_set_id=diagnostics.get("selected_set_id"),
    )
    return {
        "operation_count": len(tactic_operation_records),
        "latest_operation_state": latest_operation.get("operation_state"),
        "latest_selected_tactic_key": latest_operation.get("selected_tactic_key"),
        "latest_rollback_target_ref": latest_operation.get("rollback_target_ref"),
        "latest_adoption_ready": diagnostics.get("adoption_ready"),
        "latest_selected_set_id": diagnostics.get("selected_set_id"),
        "latest_comparison_ref_count": diagnostics.get("comparison_ref_count"),
        "latest_comparison_profile_kinds": parameter_trace.get(
            "comparison_profile_kinds"
        ),
        "latest_comparison_active_index": parameter_trace.get(
            "comparison_active_index"
        ),
        "latest_comparison_baseline_available": parameter_trace.get(
            "comparison_baseline_available"
        ),
        "latest_comparison_relation": parameter_trace.get(
            "comparison_relation"
        ),
        "latest_overlay_influence": parameter_trace.get(
            "overlay_influence"
        ),
        "latest_overlay_application_mode": selection_trace.get(
            "overlay_application_mode"
        ),
        "latest_compare_friendly_summary_line": compare_friendly_summary_line,
    }


def build_replay_report(
    name: str,
    source_paths: List[str],
    results: List[Dict],
    prediction_evaluation_entries: List[Dict] | None = None,
    prediction_calibration_reviews: List[Dict] | None = None,
    tactic_proposal_outputs: List[Dict] | None = None,
    tactic_review_records: List[Dict] | None = None,
    tactic_operation_records: List[Dict] | None = None,
    prediction_direction_snapshots: List[Dict] | None = None,
    prediction_position_review_hint_snapshots: List[Dict] | None = None,
    prediction_execution_review_hint_snapshots: List[Dict] | None = None,
) -> Dict:
    board_count = 0
    trade_count = 0
    microstructure_event_count = 0
    signal_count = 0

    event_name_counts: Dict[str, int] = {}

    prediction_evaluation_summary = None
    if prediction_evaluation_entries:
        prediction_report = build_prediction_evaluation_report(
            name=f"{name}_prediction_evaluation",
            entries=prediction_evaluation_entries,
        )
        prediction_evaluation_summary = {
            "entry_count": prediction_report["entry_count"],
            "matched_count": prediction_report["matched_count"],
            "partial_count": prediction_report["partial_count"],
            "missed_count": prediction_report["missed_count"],
            "high_priority_count": prediction_report["high_priority_count"],
            "average_confidence_gap": prediction_report["average_confidence_gap"],
            "average_caution_gap": prediction_report["average_caution_gap"],
        }

    for row in results:
        kind = row.get("kind")

        if kind == "board":
            board_count += 1
            result = row.get("result")
            if isinstance(result, dict) and result.get("signal") is not None:
                signal_count += 1

                for event in result.get("events", []):
                    event_name = str(event.get("event_name") or "")
                    if event_name:
                        event_name_counts[event_name] = event_name_counts.get(event_name, 0) + 1

        elif kind == "trade":
            trade_count += 1
            for event in row.get("microstructure", []):
                event_name = str(event.get("event_name") or "")
                if event_name:
                    microstructure_event_count += 1
                    event_name_counts[event_name] = event_name_counts.get(event_name, 0) + 1

    prediction_direction_summary = _build_prediction_direction_summary(
        prediction_direction_snapshots
    )
    prediction_position_review_hint_summary = (
        _summarize_position_review_hint_snapshot(
            prediction_position_review_hint_snapshots
        )
    )
    prediction_execution_review_hint_summary = (
        _summarize_execution_review_hint_snapshot(
            prediction_execution_review_hint_snapshots
        )
    )

    return {
        "name": name,
        "source_paths": source_paths,
        "result_count": len(results),
        "board_count": board_count,
        "trade_count": trade_count,
        "signal_count": signal_count,
        "microstructure_event_count": microstructure_event_count,
        "event_name_counts": dict(sorted(event_name_counts.items())),
        "prediction_evaluation_summary": prediction_evaluation_summary,
        "prediction_calibration_review_summary": _build_prediction_calibration_review_summary(
            prediction_calibration_reviews
        ),
        "tactic_proposal_summary": _build_tactic_proposal_summary(
            tactic_proposal_outputs
        ),
        "tactic_review_record_summary": _build_tactic_review_record_summary(
            tactic_review_records
        ),
        "tactic_operation_record_summary": _build_tactic_operation_record_summary(
            tactic_operation_records
        ),
        "prediction_direction_summary": prediction_direction_summary,
        "prediction_position_review_hint_summary": (
            prediction_position_review_hint_summary
        ),
        "prediction_execution_review_hint_summary": (
            prediction_execution_review_hint_summary
        ),
        "direction_replay_calibration_review_material": (
            _build_direction_replay_calibration_review_material(
                prediction_direction_summary
            )
        ),
    }