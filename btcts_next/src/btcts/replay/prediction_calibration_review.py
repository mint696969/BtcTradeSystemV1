# path: ./btcts_next/src/btcts/replay/prediction_calibration_review.py
# desc: Build compact calibration review summaries from prediction calibration hints and evaluation reports.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l4_consumer_models.shared import PredictionCalibrationHint
from btcts.processing.l4_consumer_models.shared._value_utils import safe_float


@dataclass(frozen=True)
class PredictionCalibrationReviewBuildInput:
    calibration_hint: PredictionCalibrationHint | None = None
    evaluation_report: dict[str, Any] | None = None
    diagnostics: dict[str, Any] | None = None


def _safe_int(value: Any) -> int:
    if value is None:
        return 0
    try:
        return int(value)
    except Exception:
        return 0


def _dominant_count_key(counts: dict[str, Any] | None) -> str:
    if not isinstance(counts, dict):
        return "unknown"

    best_key = "unknown"
    best_count = -1
    for key, value in counts.items():
        name = str(key).strip()
        if not name:
            continue
        count = _safe_int(value)
        if count > best_count:
            best_key = name
            best_count = count
    return best_key


def _resolve_review_priority(
    *,
    calibration_hint: PredictionCalibrationHint | None,
    evaluation_report: dict[str, Any],
) -> str:
    high_priority_count = _safe_int(evaluation_report.get("high_priority_count"))
    missed_count = _safe_int(evaluation_report.get("missed_count"))
    partial_count = _safe_int(evaluation_report.get("partial_count"))

    if calibration_hint is not None and calibration_hint.replay_priority == "high":
        return "high"
    if high_priority_count > 0 or missed_count > 0:
        return "high"
    if partial_count > 0:
        return "medium"
    return "normal"


def _resolve_primary_focus(
    *,
    calibration_hint: PredictionCalibrationHint | None,
    evaluation_report: dict[str, Any],
) -> str:
    average_confidence_gap = safe_float(evaluation_report.get("average_confidence_gap"))
    average_caution_gap = safe_float(evaluation_report.get("average_caution_gap"))
    missed_count = _safe_int(evaluation_report.get("missed_count"))

    if calibration_hint is not None:
        if calibration_hint.confidence_bias == "slightly_overstated":
            return "confidence_downside_review"
        if calibration_hint.confidence_bias == "understated":
            return "confidence_upside_review"
        if calibration_hint.caution_bias == "understated":
            return "caution_underestimation_review"
        if calibration_hint.caution_bias == "slightly_overstated":
            return "caution_overestimation_review"

    if average_confidence_gap is not None:
        if average_confidence_gap <= -0.10:
            return "confidence_downside_review"
        if average_confidence_gap >= 0.10:
            return "confidence_upside_review"

    if average_caution_gap is not None:
        if average_caution_gap >= 0.50:
            return "caution_underestimation_review"
        if average_caution_gap <= -0.50:
            return "caution_overestimation_review"

    if missed_count > 0:
        return "scenario_alignment_review"

    return "stability_review"


def _resolve_confidence_review(
    *,
    calibration_hint: PredictionCalibrationHint | None,
    evaluation_report: dict[str, Any],
) -> str:
    average_confidence_gap = safe_float(evaluation_report.get("average_confidence_gap"))

    if calibration_hint is not None:
        if calibration_hint.confidence_bias == "slightly_overstated":
            return "lower_confidence_weight"
        if calibration_hint.confidence_bias == "understated":
            return "raise_confidence_weight"
        if calibration_hint.confidence_bias == "blocked":
            return "hold_confidence_weight"

    if average_confidence_gap is not None:
        if average_confidence_gap <= -0.10:
            return "lower_confidence_weight"
        if average_confidence_gap >= 0.10:
            return "raise_confidence_weight"

    return "keep_confidence_weight"


def _resolve_caution_review(
    *,
    calibration_hint: PredictionCalibrationHint | None,
    evaluation_report: dict[str, Any],
) -> str:
    average_caution_gap = safe_float(evaluation_report.get("average_caution_gap"))

    if calibration_hint is not None:
        if calibration_hint.caution_bias == "understated":
            return "raise_caution_weight"
        if calibration_hint.caution_bias == "slightly_overstated":
            return "lower_caution_weight"
        if calibration_hint.caution_bias == "blocked":
            return "hold_caution_weight"

    if average_caution_gap is not None:
        if average_caution_gap >= 0.50:
            return "raise_caution_weight"
        if average_caution_gap <= -0.50:
            return "lower_caution_weight"

    return "keep_caution_weight"


def _resolve_invalidation_review(
    *,
    calibration_hint: PredictionCalibrationHint | None,
    evaluation_report: dict[str, Any],
) -> str:
    missed_count = _safe_int(evaluation_report.get("missed_count"))
    partial_count = _safe_int(evaluation_report.get("partial_count"))

    if calibration_hint is not None:
        if calibration_hint.invalidation_sensitivity == "fast":
            return "keep_fast_invalidation"
        if calibration_hint.invalidation_sensitivity == "slow":
            if missed_count > 0:
                return "raise_invalidation_sensitivity"
            return "keep_slow_invalidation"

    if missed_count > 0:
        return "raise_invalidation_sensitivity"
    if partial_count > 0:
        return "keep_medium_invalidation"
    return "keep_current_invalidation"


def _resolve_scenario_trace_focus(
    *,
    evaluation_report: dict[str, Any],
) -> str:
    dominant_regime_decision = _dominant_count_key(
        evaluation_report.get("scenario_trace_regime_decision_counts")
    )
    dominant_switch_reason = _dominant_count_key(
        evaluation_report.get("scenario_trace_switch_reason_counts")
    )
    missed_count = _safe_int(evaluation_report.get("missed_count"))

    if missed_count <= 0:
        return "none"

    if dominant_switch_reason in {
        "watch_reversal_path",
        "prepare_reversal_switch",
        "execute_transition_switch",
    }:
        return f"switch_reason:{dominant_switch_reason}"

    if dominant_regime_decision != "unknown":
        return f"regime_decision:{dominant_regime_decision}"

    return "none"


def _build_followup_actions(
    *,
    primary_focus: str,
    review_priority: str,
    confidence_review: str,
    caution_review: str,
    invalidation_review: str,
    scenario_trace_focus: str,
) -> tuple[str, ...]:
    out: list[str] = []

    if review_priority == "high":
        out.append("schedule_replay_review")
    if primary_focus != "stability_review":
        out.append(primary_focus)
    if confidence_review != "keep_confidence_weight":
        out.append(confidence_review)
    if caution_review != "keep_caution_weight":
        out.append(caution_review)
    if invalidation_review not in {
        "keep_current_invalidation",
        "keep_medium_invalidation",
    }:
        out.append(invalidation_review)
    if scenario_trace_focus != "none":
        out.append(f"trace_focus:{scenario_trace_focus}")

    return tuple(out or ["keep_current_course"])


def build_prediction_calibration_review(
    inp: PredictionCalibrationReviewBuildInput,
) -> dict[str, Any]:
    calibration_hint = inp.calibration_hint
    evaluation_report = dict(inp.evaluation_report or {})

    review_priority = _resolve_review_priority(
        calibration_hint=calibration_hint,
        evaluation_report=evaluation_report,
    )
    primary_focus = _resolve_primary_focus(
        calibration_hint=calibration_hint,
        evaluation_report=evaluation_report,
    )
    confidence_review = _resolve_confidence_review(
        calibration_hint=calibration_hint,
        evaluation_report=evaluation_report,
    )
    caution_review = _resolve_caution_review(
        calibration_hint=calibration_hint,
        evaluation_report=evaluation_report,
    )
    invalidation_review = _resolve_invalidation_review(
        calibration_hint=calibration_hint,
        evaluation_report=evaluation_report,
    )
    scenario_trace_focus = _resolve_scenario_trace_focus(
        evaluation_report=evaluation_report,
    )

    return {
        "review_type": "prediction_calibration_review",
        "review_version": "phase3.v1alpha1",
        "review_priority": review_priority,
        "primary_focus": primary_focus,
        "confidence_review": confidence_review,
        "caution_review": caution_review,
        "invalidation_review": invalidation_review,
        "scenario_trace_focus": scenario_trace_focus,
        "followup_actions": _build_followup_actions(
            primary_focus=primary_focus,
            review_priority=review_priority,
            confidence_review=confidence_review,
            caution_review=caution_review,
            invalidation_review=invalidation_review,
            scenario_trace_focus=scenario_trace_focus,
        ),
        "diagnostics": {
            "builder_type": "prediction_calibration_review",
            "calibration_hint_present": calibration_hint is not None,
            "evaluation_report_present": bool(evaluation_report),
            "report_entry_count": _safe_int(evaluation_report.get("entry_count")),
            "dominant_trace_regime_decision": _dominant_count_key(
                evaluation_report.get("scenario_trace_regime_decision_counts")
            ),
            "dominant_trace_switch_reason": _dominant_count_key(
                evaluation_report.get("scenario_trace_switch_reason_counts")
            ),
            **dict(inp.diagnostics or {}),
        },
    }