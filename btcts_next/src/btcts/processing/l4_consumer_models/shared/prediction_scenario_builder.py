# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_scenario_builder.py
# desc: Thin skeleton builder for PredictionScenarioOutput from PredictionSystemInput.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l4_consumer_models.shared.prediction_system_contract import (
    PredictionScenarioHorizonOutput,
    PredictionScenarioOutput,
    PredictionSystemInput,
)


@dataclass(frozen=True)
class PredictionScenarioBuildInput:
    prediction_input: PredictionSystemInput | None = None
    diagnostics: dict[str, Any] | None = None


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clamp_confidence(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 0.75:
        return 0.75
    return round(value, 2)


def _resolve_current_caution_level(prediction_input: PredictionSystemInput | None) -> str:
    if prediction_input is None:
        return "blocked"

    bundle = prediction_input.evidence_bundle
    summary = bundle.market_summary
    health_digest = bundle.health_digest

    if summary is None:
        return "blocked"
    if summary.interpretation_bucket == "reanchor_required":
        return "blocked"
    if summary.is_stale is True:
        return "high"
    if summary.trust_state not in {None, "trusted"}:
        return "high"
    if summary.interpretation_bucket == "observe_only":
        return "medium"

    if health_digest is not None:
        if health_digest.is_stale is True:
            return "high"

        market_runtime = dict(health_digest.market_runtime or {})
        digest_bucket = _safe_str(market_runtime.get("interpretation_bucket"))
        if digest_bucket == "reanchor_required":
            return "blocked"
        if digest_bucket == "observe_only":
            return "medium"

        semantic_usage = dict(health_digest.semantic_usage or {})
        observer_status = _safe_str(semantic_usage.get("observer_status"))
        if observer_status in {"broken", "unknown"}:
            return "high"
        if observer_status == "caution":
            return "medium"

    return "low"


def _resolve_current_regime_state(prediction_input: PredictionSystemInput | None) -> str:
    if prediction_input is None:
        return "no_trade"

    bundle = prediction_input.evidence_bundle
    summary = bundle.market_summary
    regime_turning_point = dict(bundle.regime_turning_point or {})

    if summary is None:
        return "no_trade"
    if summary.interpretation_bucket == "reanchor_required":
        return "transition"
    if summary.interpretation_bucket == "observe_only":
        return "unstable"
    if summary.continuity_state == "resynced":
        return "transition"

    transition_sign = _safe_str(regime_turning_point.get("transition_sign"))
    turning_point_risk = _safe_str(regime_turning_point.get("turning_point_risk"))

    if transition_sign in {"transition_underway", "active_transition"}:
        return "transition"
    if transition_sign in {"weakening_continuation", "reversal_watch"}:
        return "reversal_watch"
    if turning_point_risk == "high":
        return "reversal_watch"

    return "continuation"


def _resolve_current_hypothesis_health(
    *,
    current_regime_state: str,
    current_caution_level: str,
) -> str:
    if current_caution_level == "blocked":
        return "scenario_switch_required"
    if current_regime_state == "continuation":
        return "stable" if current_caution_level == "low" else "caution_increase"
    if current_regime_state == "reversal_watch":
        return "caution_increase"
    if current_regime_state == "transition":
        return "scenario_switch_required"
    if current_regime_state == "unstable":
        return "degraded"
    if current_regime_state == "no_trade":
        return "invalidated"
    return "unknown"


def _resolve_current_confidence(
    *,
    prediction_input: PredictionSystemInput | None,
    current_regime_state: str,
    current_caution_level: str,
) -> float:
    if prediction_input is None or prediction_input.evidence_bundle.market_summary is None:
        return 0.0
    if current_caution_level == "blocked":
        return 0.0

    base = 0.45
    if current_regime_state == "continuation":
        base = 0.62
    elif current_regime_state == "reversal_watch":
        base = 0.46
    elif current_regime_state == "transition":
        base = 0.32
    elif current_regime_state == "unstable":
        base = 0.25
    elif current_regime_state == "no_trade":
        base = 0.15

    if current_caution_level == "medium":
        base -= 0.07
    elif current_caution_level == "high":
        base -= 0.17

    return _clamp_confidence(base)


def _resolve_horizon_shape(
    *,
    current_regime_state: str,
    turning_point_risk: str,
) -> tuple[str, str, str]:
    if current_regime_state == "continuation":
        return ("continuation", "high", turning_point_risk)
    if current_regime_state == "reversal_watch":
        reversal_likelihood = "medium"
        if turning_point_risk == "high":
            reversal_likelihood = "high"
        return ("reversal_watch", "medium", reversal_likelihood)
    if current_regime_state == "transition":
        return ("transition", "low", "high")
    if current_regime_state == "unstable":
        return ("unstable", "low", "medium")
    if current_regime_state == "no_trade":
        return ("no_trade", "unknown", "unknown")
    return ("unknown", "unknown", "unknown")


def _build_outlooks(
    *,
    prediction_input: PredictionSystemInput | None,
    current_regime_state: str,
    current_confidence: float,
    current_caution_level: str,
) -> tuple[PredictionScenarioHorizonOutput, ...]:
    if prediction_input is None:
        return ()

    regime_turning_point = dict(prediction_input.evidence_bundle.regime_turning_point or {})
    turning_point_risk = _safe_str(regime_turning_point.get("turning_point_risk")) or "low"

    regime_bias, continuation_likelihood, reversal_likelihood = _resolve_horizon_shape(
        current_regime_state=current_regime_state,
        turning_point_risk=turning_point_risk,
    )

    horizon_penalty = {
        "5m": 0.00,
        "10m": 0.08,
        "30m": 0.16,
    }

    out: list[PredictionScenarioHorizonOutput] = []
    for horizon in prediction_input.requested_horizons:
        confidence = _clamp_confidence(
            current_confidence - horizon_penalty.get(horizon, 0.0)
        )
        out.append(
            PredictionScenarioHorizonOutput(
                horizon=horizon,
                regime_bias=regime_bias,
                continuation_likelihood=continuation_likelihood,
                reversal_likelihood=reversal_likelihood,
                turning_point_risk=turning_point_risk,
                confidence=confidence,
                caution_level=current_caution_level,
            )
        )

    return tuple(out)


def _build_invalidation_signals(
    prediction_input: PredictionSystemInput | None,
) -> tuple[str, ...]:
    if prediction_input is None:
        return ("prediction_input_absent",)

    bundle = prediction_input.evidence_bundle
    summary = bundle.market_summary
    health_digest = bundle.health_digest
    regime_turning_point = dict(bundle.regime_turning_point or {})

    out: list[str] = []

    if summary is None:
        out.append("market_summary_absent")
    else:
        if summary.is_stale is True:
            out.append("market_summary_stale")
        if summary.trust_state not in {None, "trusted"}:
            out.append("trust_not_trusted")
        if summary.interpretation_bucket == "observe_only":
            out.append("interpretation_observe_only")
        elif summary.interpretation_bucket == "reanchor_required":
            out.append("interpretation_reanchor_required")
        if summary.continuity_state == "resynced":
            out.append("continuity_resynced")

    if health_digest is not None and health_digest.is_stale is True:
        out.append("health_digest_stale")

    transition_sign = _safe_str(regime_turning_point.get("transition_sign"))
    if transition_sign is not None:
        out.append(f"transition_sign:{transition_sign}")

    turning_point_risk = _safe_str(regime_turning_point.get("turning_point_risk"))
    if turning_point_risk in {"medium", "high"}:
        out.append(f"turning_point_risk:{turning_point_risk}")

    for family in prediction_input.evidence_trace.missing_families:
        if family != "market_summary_anchor":
            out.append(f"missing:{family}")

    return tuple(out)


def _resolve_invalidation_state(
    *,
    current_regime_state: str,
    current_hypothesis_health: str,
) -> str:
    if current_hypothesis_health in {
        "stable",
        "caution_increase",
        "degraded",
        "invalidated",
        "scenario_switch_required",
    }:
        return current_hypothesis_health

    if current_regime_state == "transition":
        return "scenario_switch_required"
    if current_regime_state == "reversal_watch":
        return "caution_increase"
    if current_regime_state == "unstable":
        return "degraded"
    if current_regime_state == "no_trade":
        return "invalidated"
    return "unknown"


def _resolve_scenario_switch_hint(
    *,
    current_regime_state: str,
    current_hypothesis_health: str,
) -> str:
    if current_regime_state == "continuation" and current_hypothesis_health == "stable":
        return "hold_primary"
    if current_regime_state == "reversal_watch":
        return "watch_reversal_path"
    if current_regime_state == "transition":
        return "prepare_transition_switch"
    if current_regime_state == "unstable":
        return "reduce_participation"
    if current_regime_state == "no_trade":
        return "maintain_no_trade"
    return "unknown"


def _build_evidence_trace_summary(
    prediction_input: PredictionSystemInput | None,
) -> dict[str, Any]:
    if prediction_input is None:
        return {
            "active_family_count": 0,
            "missing_family_count": 0,
            "caution_flag_count": 0,
            "active_families": (),
            "missing_families": (),
            "caution_flags": (),
            "market_summary_anchor_present": False,
        }

    evidence_trace = prediction_input.evidence_trace
    return {
        "active_family_count": len(evidence_trace.active_families),
        "missing_family_count": len(evidence_trace.missing_families),
        "caution_flag_count": len(evidence_trace.caution_flags),
        "active_families": evidence_trace.active_families,
        "missing_families": evidence_trace.missing_families,
        "caution_flags": evidence_trace.caution_flags,
        "market_summary_anchor_present": "market_summary_anchor"
        in evidence_trace.active_families,
    }


def _build_evidence(prediction_input: PredictionSystemInput | None) -> dict[str, Any]:
    if prediction_input is None:
        return {
            "market_summary_present": False,
            "health_digest_present": False,
            "liquidity_board_history_present": False,
            "regime_turning_point_present": False,
            "evidence_trace_summary": _build_evidence_trace_summary(prediction_input),
        }

    bundle = prediction_input.evidence_bundle
    summary = bundle.market_summary
    regime_turning_point = dict(bundle.regime_turning_point or {})

    return {
        "market_summary_present": summary is not None,
        "health_digest_present": bundle.health_digest is not None,
        "liquidity_board_history_present": bool(bundle.liquidity_board_history),
        "regime_turning_point_present": bool(bundle.regime_turning_point),
        "summary_interpretation_bucket": None if summary is None else summary.interpretation_bucket,
        "summary_trust_state": None if summary is None else summary.trust_state,
        "summary_continuity_state": None if summary is None else summary.continuity_state,
        "semantic_active_event_count": None
        if summary is None
        else summary.semantic_active_event_count,
        "orderbook_active_event_count": None
        if summary is None
        else summary.orderbook_active_event_count,
        "transition_sign": _safe_str(regime_turning_point.get("transition_sign")),
        "turning_point_risk": _safe_str(regime_turning_point.get("turning_point_risk")),
        "evidence_trace_summary": _build_evidence_trace_summary(prediction_input),
    }


def build_prediction_scenario_output(
    inp: PredictionScenarioBuildInput,
) -> PredictionScenarioOutput:
    prediction_input = inp.prediction_input
    current_caution_level = _resolve_current_caution_level(prediction_input)
    current_regime_state = _resolve_current_regime_state(prediction_input)
    current_hypothesis_health = _resolve_current_hypothesis_health(
        current_regime_state=current_regime_state,
        current_caution_level=current_caution_level,
    )
    current_confidence = _resolve_current_confidence(
        prediction_input=prediction_input,
        current_regime_state=current_regime_state,
        current_caution_level=current_caution_level,
    )
    invalidation_signals = _build_invalidation_signals(prediction_input)
    invalidation_state = _resolve_invalidation_state(
        current_regime_state=current_regime_state,
        current_hypothesis_health=current_hypothesis_health,
    )
    scenario_switch_hint = _resolve_scenario_switch_hint(
        current_regime_state=current_regime_state,
        current_hypothesis_health=current_hypothesis_health,
    )

    if prediction_input is None:
        return PredictionScenarioOutput(
            current_regime_state=current_regime_state,
            current_hypothesis_health=current_hypothesis_health,
            current_confidence=current_confidence,
            current_caution_level=current_caution_level,
            outlooks=(),
            invalidation_state=invalidation_state,
            invalidation_signals=invalidation_signals,
            scenario_switch_hint=scenario_switch_hint,
            evidence=_build_evidence(prediction_input),
            diagnostics={
                "builder_type": "prediction_scenario_output",
                "active_family_count": 0,
                "missing_family_count": 0,
                "caution_flag_count": 0,
                **dict(inp.diagnostics or {}),
            },
        )

    return PredictionScenarioOutput(
        source_kind=prediction_input.system_type,
        market_uid=prediction_input.market_uid,
        event_ts=prediction_input.event_ts,
        freshness=prediction_input.freshness,
        is_stale=prediction_input.is_stale,
        current_regime_state=current_regime_state,
        current_hypothesis_health=current_hypothesis_health,
        current_confidence=current_confidence,
        current_caution_level=current_caution_level,
        outlooks=_build_outlooks(
            prediction_input=prediction_input,
            current_regime_state=current_regime_state,
            current_confidence=current_confidence,
            current_caution_level=current_caution_level,
        ),
        invalidation_state=invalidation_state,
        invalidation_signals=invalidation_signals,
        scenario_switch_hint=scenario_switch_hint,
        evidence=_build_evidence(prediction_input),
        evidence_trace=prediction_input.evidence_trace,
        diagnostics={
            "builder_type": "prediction_scenario_output",
            "requested_horizons_count": len(prediction_input.requested_horizons),
            "active_family_count": len(prediction_input.evidence_trace.active_families),
            "missing_family_count": len(prediction_input.evidence_trace.missing_families),
            "caution_flag_count": len(prediction_input.evidence_trace.caution_flags),
            **dict(inp.diagnostics or {}),
        },
    )