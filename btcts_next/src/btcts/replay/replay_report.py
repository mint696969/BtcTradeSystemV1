# path: ./btcts_next/src/btcts/replay/replay_report.py
# desc: Build replay summary reports from fusion results.

from __future__ import annotations

from typing import Dict, List

from .prediction_evaluation_report import build_prediction_evaluation_report


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
    parameter_trace = dict(latest_proposal.get("diagnostics", {}).get("parameter_trace", {}) or {})
    return {
        "proposal_count": len(tactic_proposal_outputs),
        "latest_primary_tactic_key": latest_proposal.get("primary_tactic_key"),
        "latest_proposal_state": latest_proposal.get("proposal_state"),
        "latest_scenario_regime": latest_proposal.get("scenario_regime"),
        "latest_profile_kind": parameter_trace.get("profile_kind"),
    }


def _build_tactic_review_record_summary(
    tactic_review_records: List[Dict] | None,
) -> Dict | None:
    if not tactic_review_records:
        return None

    latest_review = dict(tactic_review_records[-1] or {})
    return {
        "review_count": len(tactic_review_records),
        "latest_selected_tactic_key": latest_review.get("selected_tactic_key"),
        "latest_decision_state": latest_review.get("decision_state"),
        "latest_rollback_target_ref": latest_review.get("rollback_target_ref"),
    }


def _build_tactic_operation_record_summary(
    tactic_operation_records: List[Dict] | None,
) -> Dict | None:
    if not tactic_operation_records:
        return None

    latest_operation = dict(tactic_operation_records[-1] or {})
    return {
        "operation_count": len(tactic_operation_records),
        "latest_operation_state": latest_operation.get("operation_state"),
        "latest_selected_tactic_key": latest_operation.get("selected_tactic_key"),
        "latest_rollback_target_ref": latest_operation.get("rollback_target_ref"),
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
    }