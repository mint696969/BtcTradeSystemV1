# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_replay_feedback.py
# desc: Thin shared builder that normalizes replay-side calibration feedback for Scenario Core input lanes.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l4_consumer_models.shared._value_utils import (
    safe_float,
    safe_str,
)


@dataclass(frozen=True)
class PredictionReplayFeedbackBuildInput:
    calibration_review: dict[str, Any] | None = None
    evaluation_report: dict[str, Any] | None = None
    source_kind: str | None = None
    diagnostics: dict[str, Any] | None = None


def _safe_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:
        parsed = safe_float(value)
        if parsed is None:
            return None
        return int(parsed)


def _round_optional(value: Any) -> float | None:
    parsed = safe_float(value)
    if parsed is None:
        return None
    return round(parsed, 2)


def _normalize_followup_actions(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()

    out: list[str] = []
    for item in value:
        normalized = safe_str(item)
        if normalized is None:
            continue
        out.append(normalized)
    return tuple(out)


def _resolve_source_kind(value: Any) -> str:
    return safe_str(value) or "replay_prediction_calibration"


def build_prediction_replay_feedback(
    inp: PredictionReplayFeedbackBuildInput,
) -> dict[str, Any]:
    calibration_review = dict(inp.calibration_review or {})
    evaluation_report = dict(inp.evaluation_report or {})

    return {
        "feedback_type": "prediction_replay_feedback",
        "feedback_version": "phase3.v1alpha1",
        "source_kind": _resolve_source_kind(inp.source_kind),
        "review_priority": safe_str(calibration_review.get("review_priority")) or "normal",
        "primary_focus": safe_str(calibration_review.get("primary_focus")) or "unknown",
        "confidence_review": safe_str(calibration_review.get("confidence_review")) or "unknown",
        "caution_review": safe_str(calibration_review.get("caution_review")) or "unknown",
        "invalidation_review": safe_str(calibration_review.get("invalidation_review")) or "unknown",
        "scenario_trace_focus": safe_str(
            calibration_review.get("scenario_trace_focus")
        ) or "unknown",
        "followup_actions": _normalize_followup_actions(
            calibration_review.get("followup_actions")
        ),
        "entry_count": _safe_int(evaluation_report.get("entry_count")) or 0,
        "matched_count": _safe_int(evaluation_report.get("matched_count")) or 0,
        "partial_count": _safe_int(evaluation_report.get("partial_count")) or 0,
        "missed_count": _safe_int(evaluation_report.get("missed_count")) or 0,
        "high_priority_count": _safe_int(evaluation_report.get("high_priority_count")) or 0,
        "average_confidence_gap": _round_optional(
            evaluation_report.get("average_confidence_gap")
        ),
        "average_caution_gap": _round_optional(
            evaluation_report.get("average_caution_gap")
        ),
        "diagnostics": {
            "builder_type": "prediction_replay_feedback",
            "calibration_review_present": bool(calibration_review),
            "evaluation_report_present": bool(evaluation_report),
            **dict(inp.diagnostics or {}),
        },
    }