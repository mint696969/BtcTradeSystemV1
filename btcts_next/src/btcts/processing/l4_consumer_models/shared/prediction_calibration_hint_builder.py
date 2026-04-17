# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_calibration_hint_builder.py
# desc: Thin shared builder for PredictionCalibrationHint from prediction input / scenario output.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l4_consumer_models.shared.prediction_system_contract import (
    PredictionCalibrationHint,
    PredictionScenarioOutput,
    PredictionSystemInput,
)


@dataclass(frozen=True)
class PredictionCalibrationBuildInput:
    prediction_input: PredictionSystemInput | None = None
    scenario_output: PredictionScenarioOutput | None = None
    diagnostics: dict[str, Any] | None = None


def _resolve_confidence_bias(
    *,
    prediction_input: PredictionSystemInput | None,
    scenario_output: PredictionScenarioOutput | None,
) -> str:
    if prediction_input is None or scenario_output is None:
        return "unknown"

    evidence_trace = prediction_input.evidence_trace

    if scenario_output.current_caution_level == "blocked":
        return "blocked"

    if (
        scenario_output.current_confidence >= 0.55
        and (
            evidence_trace.caution_flags
            or evidence_trace.missing_families
            or scenario_output.current_caution_level in {"medium", "high"}
        )
    ):
        return "slightly_overstated"

    if scenario_output.current_confidence <= 0.20:
        return "understated"

    return "balanced"


def _resolve_caution_bias(
    *,
    prediction_input: PredictionSystemInput | None,
    scenario_output: PredictionScenarioOutput | None,
) -> str:
    if prediction_input is None or scenario_output is None:
        return "unknown"

    evidence_trace = prediction_input.evidence_trace

    if scenario_output.current_caution_level == "blocked":
        return "blocked"

    if scenario_output.current_caution_level == "low" and evidence_trace.caution_flags:
        return "understated"

    if (
        scenario_output.current_caution_level in {"medium", "high"}
        and not evidence_trace.caution_flags
        and not evidence_trace.missing_families
    ):
        return "slightly_overstated"

    return "balanced"


def _resolve_invalidation_sensitivity(
    *,
    scenario_output: PredictionScenarioOutput | None,
) -> str:
    if scenario_output is None:
        return "unknown"

    if scenario_output.current_caution_level == "blocked":
        return "fast"

    if scenario_output.current_regime_state == "transition":
        return "fast"

    if len(scenario_output.invalidation_signals) >= 3:
        return "fast"

    if scenario_output.current_regime_state == "reversal_watch":
        return "medium"

    if (
        scenario_output.current_regime_state == "continuation"
        and scenario_output.current_hypothesis_health == "stable"
    ):
        return "slow"

    return "medium"


def _resolve_replay_priority(
    *,
    prediction_input: PredictionSystemInput | None,
    scenario_output: PredictionScenarioOutput | None,
) -> str:
    if prediction_input is None or scenario_output is None:
        return "normal"

    evidence_trace = prediction_input.evidence_trace

    if scenario_output.current_caution_level == "blocked":
        return "high"

    if scenario_output.invalidation_state in {
        "scenario_switch_required",
        "invalidated",
    }:
        return "high"

    if evidence_trace.caution_flags or evidence_trace.missing_families:
        return "high"

    if scenario_output.current_regime_state in {"reversal_watch", "transition"}:
        return "high"

    return "normal"


def build_prediction_calibration_hint(
    inp: PredictionCalibrationBuildInput,
) -> PredictionCalibrationHint:
    prediction_input = inp.prediction_input
    scenario_output = inp.scenario_output

    active_family_count = 0
    missing_family_count = 0
    caution_flag_count = 0
    if prediction_input is not None:
        active_family_count = len(prediction_input.evidence_trace.active_families)
        missing_family_count = len(prediction_input.evidence_trace.missing_families)
        caution_flag_count = len(prediction_input.evidence_trace.caution_flags)

    return PredictionCalibrationHint(
        confidence_bias=_resolve_confidence_bias(
            prediction_input=prediction_input,
            scenario_output=scenario_output,
        ),
        caution_bias=_resolve_caution_bias(
            prediction_input=prediction_input,
            scenario_output=scenario_output,
        ),
        invalidation_sensitivity=_resolve_invalidation_sensitivity(
            scenario_output=scenario_output,
        ),
        replay_priority=_resolve_replay_priority(
            prediction_input=prediction_input,
            scenario_output=scenario_output,
        ),
        diagnostics={
            "builder_type": "prediction_calibration_hint",
            "active_family_count": active_family_count,
            "missing_family_count": missing_family_count,
            "caution_flag_count": caution_flag_count,
            **dict(inp.diagnostics or {}),
        },
    )