# path: ./btcts_next/src/btcts/replay/prediction_evaluation_entry.py
# desc: Thin replay-side entry for prediction outcome evaluation and calibration review.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l4_consumer_models.shared import (
    PredictionCalibrationHint,
    PredictionScenarioOutput,
)


@dataclass(frozen=True)
class PredictionEvaluationBuildInput:
    scenario_output: PredictionScenarioOutput | None = None
    calibration_hint: PredictionCalibrationHint | None = None
    realized_outcome: dict[str, Any] | None = None
    diagnostics: dict[str, Any] | None = None


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _resolve_regime_alignment(
    predicted_regime_state: str | None,
    realized_regime_state: str | None,
) -> str:
    if predicted_regime_state is None or realized_regime_state is None:
        return "unknown"
    if predicted_regime_state == realized_regime_state:
        return "matched"

    fragile_states = {"reversal_watch", "transition"}
    stable_states = {"continuation", "unstable"}

    if (
        predicted_regime_state in fragile_states
        and realized_regime_state in fragile_states
    ):
        return "partial"

    if (
        predicted_regime_state in stable_states
        and realized_regime_state in stable_states
    ):
        return "partial"

    return "missed"


def _resolve_confidence_gap(
    predicted_confidence: float | None,
    realized_confidence: float | None,
) -> float | None:
    if predicted_confidence is None or realized_confidence is None:
        return None
    return round(realized_confidence - predicted_confidence, 2)


def _resolve_confidence_gap_signal(confidence_gap: float | None) -> str:
    if confidence_gap is None:
        return "unknown"
    if confidence_gap <= -0.15:
        return "overstated_confidence"
    if confidence_gap >= 0.15:
        return "understated_confidence"
    return "balanced"


def _caution_rank(value: str | None) -> int | None:
    if value is None:
        return None
    table = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "blocked": 4,
    }
    return table.get(value)


def _resolve_caution_gap(
    predicted_caution_level: str | None,
    realized_caution_level: str | None,
) -> int | None:
    predicted_rank = _caution_rank(predicted_caution_level)
    realized_rank = _caution_rank(realized_caution_level)
    if predicted_rank is None or realized_rank is None:
        return None
    return realized_rank - predicted_rank


def build_prediction_evaluation_entry(
    inp: PredictionEvaluationBuildInput,
) -> dict[str, Any]:
    scenario_output = inp.scenario_output
    calibration_hint = inp.calibration_hint
    realized_outcome = dict(inp.realized_outcome or {})

    predicted_regime_state = None
    predicted_confidence = None
    predicted_caution_level = None
    predicted_invalidation_state = None
    predicted_scenario_switch_hint = None
    predicted_scenario_trace = {}
    market_uid = None
    event_ts = None

    if scenario_output is not None:
        predicted_regime_state = scenario_output.current_regime_state
        predicted_confidence = scenario_output.current_confidence
        predicted_caution_level = scenario_output.current_caution_level
        predicted_invalidation_state = scenario_output.invalidation_state
        predicted_scenario_switch_hint = scenario_output.scenario_switch_hint
        predicted_scenario_trace = dict(scenario_output.scenario_trace or {})
        market_uid = scenario_output.market_uid
        event_ts = scenario_output.event_ts

    realized_regime_state = _safe_str(realized_outcome.get("realized_regime_state"))
    realized_confidence = _safe_float(realized_outcome.get("realized_confidence"))
    realized_caution_level = _safe_str(realized_outcome.get("realized_caution_level"))
    realized_horizon = _safe_str(realized_outcome.get("realized_horizon"))
    realized_return_bp = _safe_float(realized_outcome.get("realized_return_bp"))
    realized_max_adverse_bp = _safe_float(
        realized_outcome.get("realized_max_adverse_bp")
    )
    realized_max_favorable_bp = _safe_float(
        realized_outcome.get("realized_max_favorable_bp")
    )

    confidence_gap = _resolve_confidence_gap(
        predicted_confidence=predicted_confidence,
        realized_confidence=realized_confidence,
    )

    replay_priority = "normal"
    confidence_bias_hint = "unknown"
    caution_bias_hint = "unknown"
    invalidation_sensitivity = "unknown"

    if calibration_hint is not None:
        replay_priority = calibration_hint.replay_priority
        confidence_bias_hint = calibration_hint.confidence_bias
        caution_bias_hint = calibration_hint.caution_bias
        invalidation_sensitivity = calibration_hint.invalidation_sensitivity

    return {
        "entry_type": "prediction_evaluation_entry",
        "entry_version": "phase3.v1alpha1",
        "market_uid": market_uid,
        "event_ts": event_ts,
        "predicted_regime_state": predicted_regime_state,
        "realized_regime_state": realized_regime_state,
        "realized_horizon": realized_horizon,
        "regime_alignment": _resolve_regime_alignment(
            predicted_regime_state=predicted_regime_state,
            realized_regime_state=realized_regime_state,
        ),
        "predicted_confidence": predicted_confidence,
        "realized_confidence": realized_confidence,
        "realized_return_bp": realized_return_bp,
        "realized_max_adverse_bp": realized_max_adverse_bp,
        "realized_max_favorable_bp": realized_max_favorable_bp,
        "confidence_gap": confidence_gap,
        "confidence_gap_signal": _resolve_confidence_gap_signal(confidence_gap),
        "predicted_caution_level": predicted_caution_level,
        "predicted_invalidation_state": predicted_invalidation_state,
        "predicted_scenario_switch_hint": predicted_scenario_switch_hint,
        "predicted_scenario_trace": predicted_scenario_trace,
        "realized_caution_level": realized_caution_level,
        "caution_gap": _resolve_caution_gap(
            predicted_caution_level=predicted_caution_level,
            realized_caution_level=realized_caution_level,
        ),
        "confidence_bias_hint": confidence_bias_hint,
        "caution_bias_hint": caution_bias_hint,
        "invalidation_sensitivity": invalidation_sensitivity,
        "replay_priority": replay_priority,
        "diagnostics": {
            "builder_type": "prediction_evaluation_entry",
            "scenario_output_present": scenario_output is not None,
            "calibration_hint_present": calibration_hint is not None,
            "realized_outcome_present": bool(realized_outcome),
            **dict(inp.diagnostics or {}),
        },
    }