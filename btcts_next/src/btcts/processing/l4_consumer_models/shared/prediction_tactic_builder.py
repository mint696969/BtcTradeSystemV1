# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_tactic_builder.py
# desc: Thin builder for Phase 4-A scenario-driven tactic proposal output.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l4_consumer_models.shared.prediction_system_contract import (
    PredictionScenarioOutput,
)
from btcts.processing.l4_consumer_models.shared.prediction_tactic_catalog import (
    get_tactic_shape,
)
from btcts.processing.l4_consumer_models.shared.prediction_tactic_contract import (
    ScenarioTacticCandidate,
    ScenarioTacticProposalOutput,
    TacticParameterSetRef,
)
from btcts.processing.l4_consumer_models.shared.prediction_tactic_parameter_sets import (
    resolve_tactic_parameter_set_bundle,
)
from btcts.processing.l4_consumer_models.shared.prediction_tactic_selection import (
    build_candidate_plan,
    build_selection_trace,
    resolve_primary_tactic_key,
    resolve_proposal_state,
)


@dataclass(frozen=True)
class PredictionTacticBuildInput:
    scenario_output: PredictionScenarioOutput | None = None
    active_parameter_set_ref: TacticParameterSetRef | None = None
    comparison_set_refs: tuple[TacticParameterSetRef, ...] | None = None
    diagnostics: dict[str, Any] | None = None


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _resolve_reason_refs(
    scenario_output: PredictionScenarioOutput | None,
    primary_tactic_key: str,
) -> tuple[str, ...]:
    if scenario_output is None:
        return ("scenario_absent",)

    refs: list[str] = [
        f"scenario_regime:{scenario_output.current_regime_state}",
        f"scenario_switch_hint:{scenario_output.scenario_switch_hint}",
        f"invalidation_state:{scenario_output.invalidation_state}",
        f"primary_tactic:{primary_tactic_key}",
    ]

    trace_focus = _safe_str(
        (
            scenario_output.scenario_trace.get("replay_feedback_effect", {})
            or {}
        ).get("scenario_trace_focus")
    )
    if trace_focus is not None:
        refs.append(f"scenario_trace_focus:{trace_focus}")

    return tuple(refs)


def _resolve_caution_flags(
    scenario_output: PredictionScenarioOutput | None,
) -> tuple[str, ...]:
    if scenario_output is None:
        return ("scenario_absent",)

    flags: list[str] = []

    if scenario_output.current_caution_level in {"high", "blocked"}:
        flags.append(f"caution:{scenario_output.current_caution_level}")
    if scenario_output.invalidation_state in {
        "degraded",
        "invalidated",
        "scenario_switch_required",
    }:
        flags.append(f"invalidation:{scenario_output.invalidation_state}")
    if scenario_output.is_stale is True:
        flags.append("scenario_stale")

    return tuple(flags)


def _build_candidate(
    *,
    tactic_key: str,
    priority: int,
    scenario_output: PredictionScenarioOutput | None,
    parameter_set_ref: TacticParameterSetRef,
    switch_alignment: str,
) -> ScenarioTacticCandidate:
    tactic_label, stance_bias, readiness = get_tactic_shape(tactic_key)
    return ScenarioTacticCandidate(
        tactic_key=tactic_key,
        tactic_label=tactic_label,
        stance_bias=stance_bias,
        readiness=readiness,
        priority=priority,
        parameter_set_ref=parameter_set_ref,
        reason_refs=_resolve_reason_refs(scenario_output, tactic_key),
        caution_flags=_resolve_caution_flags(scenario_output),
        invalidation_watch="unknown"
        if scenario_output is None
        else scenario_output.invalidation_state,
        switch_alignment=switch_alignment,
        diagnostics={
            "builder_type": "prediction_tactic_candidate",
            "scenario_switch_hint": None
            if scenario_output is None
            else scenario_output.scenario_switch_hint,
        },
    )


def _build_candidate_tactics(
    *,
    primary_tactic_key: str,
    scenario_output: PredictionScenarioOutput | None,
    parameter_set_ref: TacticParameterSetRef,
) -> tuple[ScenarioTacticCandidate, ...]:
    ordered_keys = build_candidate_plan(
        primary_tactic_key=primary_tactic_key,
        scenario_output=scenario_output,
        profile_kind=parameter_set_ref.profile_kind,
        overlay_refs=parameter_set_ref.overlay_refs,
    )

    seen: set[str] = set()
    out: list[ScenarioTacticCandidate] = []
    for tactic_key, priority, switch_alignment in ordered_keys:
        if tactic_key in seen:
            continue
        seen.add(tactic_key)
        out.append(
            _build_candidate(
                tactic_key=tactic_key,
                priority=priority,
                scenario_output=scenario_output,
                parameter_set_ref=parameter_set_ref,
                switch_alignment=switch_alignment,
            )
        )
    return tuple(out)


def _build_scenario_ref(
    scenario_output: PredictionScenarioOutput | None,
) -> str | None:
    if scenario_output is None:
        return None

    market_uid = _safe_str(scenario_output.market_uid)
    event_ts = _safe_str(scenario_output.event_ts)

    if market_uid and event_ts:
        return f"{market_uid}@{event_ts}"
    return market_uid or event_ts


def _build_explanation_trace(
    *,
    scenario_output: PredictionScenarioOutput | None,
    primary_tactic_key: str,
    candidate_tactics: tuple[ScenarioTacticCandidate, ...],
    selection_trace: dict[str, Any],
) -> dict[str, Any]:
    if scenario_output is None:
        return {
            "trace_type": "scenario_tactic_explanation_trace",
            "primary_tactic_key": primary_tactic_key,
            "candidate_count": len(candidate_tactics),
            "scenario_present": False,
            "selection_trace": selection_trace,
        }

    replay_feedback_effect = dict(
        scenario_output.scenario_trace.get("replay_feedback_effect", {}) or {}
    )

    return {
        "trace_type": "scenario_tactic_explanation_trace",
        "primary_tactic_key": primary_tactic_key,
        "candidate_count": len(candidate_tactics),
        "scenario_present": True,
        "scenario_regime": scenario_output.current_regime_state,
        "hypothesis_health": scenario_output.current_hypothesis_health,
        "current_confidence": scenario_output.current_confidence,
        "current_caution_level": scenario_output.current_caution_level,
        "invalidation_state": scenario_output.invalidation_state,
        "scenario_switch_hint": scenario_output.scenario_switch_hint,
        "scenario_trace_focus": replay_feedback_effect.get("scenario_trace_focus"),
        "selection_trace": selection_trace,
    }


def build_prediction_tactic_proposal_output(
    inp: PredictionTacticBuildInput,
) -> ScenarioTacticProposalOutput:
    scenario_output = inp.scenario_output
    parameter_set_bundle = resolve_tactic_parameter_set_bundle(
        scenario_output=scenario_output,
        active_parameter_set_ref=inp.active_parameter_set_ref,
        comparison_set_refs=inp.comparison_set_refs,
    )
    primary_tactic_key = resolve_primary_tactic_key(
        scenario_output,
        profile_kind=parameter_set_bundle.active_parameter_set_ref.profile_kind,
        overlay_refs=parameter_set_bundle.active_parameter_set_ref.overlay_refs,
    )
    selection_trace = build_selection_trace(
        scenario_output=scenario_output,
        primary_tactic_key=primary_tactic_key,
        profile_kind=parameter_set_bundle.active_parameter_set_ref.profile_kind,
        overlay_refs=parameter_set_bundle.active_parameter_set_ref.overlay_refs,
    )
    candidate_tactics = _build_candidate_tactics(
        primary_tactic_key=primary_tactic_key,
        scenario_output=scenario_output,
        parameter_set_ref=parameter_set_bundle.active_parameter_set_ref,
    )

    parameter_trace = dict(parameter_set_bundle.parameter_trace)
    adoption_ready = bool(parameter_trace.get("adoption_ready"))
    rollback_target_available = bool(parameter_trace.get("rollback_target_ref"))

    return ScenarioTacticProposalOutput(
        source_kind="prediction_scenario_output",
        market_uid=None if scenario_output is None else scenario_output.market_uid,
        event_ts=None if scenario_output is None else scenario_output.event_ts,
        scenario_ref=_build_scenario_ref(scenario_output),
        scenario_regime="unknown"
        if scenario_output is None
        else scenario_output.current_regime_state,
        primary_tactic_key=primary_tactic_key,
        proposal_state=resolve_proposal_state(primary_tactic_key, scenario_output),
        candidate_tactics=candidate_tactics,
        active_parameter_set_ref=parameter_set_bundle.active_parameter_set_ref,
        comparison_set_refs=parameter_set_bundle.comparison_set_refs,
        rollback_ready=parameter_set_bundle.rollback_ready,
        review_needed=True,
        explanation_trace=_build_explanation_trace(
            scenario_output=scenario_output,
            primary_tactic_key=primary_tactic_key,
            candidate_tactics=candidate_tactics,
            selection_trace=selection_trace,
        ),
        diagnostics={
            "builder_type": "prediction_tactic_proposal_output",
            "scenario_present": scenario_output is not None,
            "candidate_count": len(candidate_tactics),
            "comparison_set_count": len(parameter_set_bundle.comparison_set_refs),
            "adoption_ready": adoption_ready,
            "rollback_target_available": rollback_target_available,
            "selected_set_id": parameter_set_bundle.active_parameter_set_ref.set_id,
            "parameter_trace": parameter_trace,
            "selection_trace": dict(selection_trace),
            **dict(inp.diagnostics or {}),
        },
    )