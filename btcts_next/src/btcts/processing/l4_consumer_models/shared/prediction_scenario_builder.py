# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_scenario_builder.py
# desc: Thin skeleton builder for PredictionScenarioOutput from PredictionSystemInput.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l4_consumer_models.shared._value_utils import (
    safe_float,
    safe_str,
)
from btcts.processing.l4_consumer_models.shared.prediction_system_contract import (
    PredictionScenarioHorizonOutput,
    PredictionScenarioOutput,
    PredictionSystemInput,
)


@dataclass(frozen=True)
class PredictionScenarioBuildInput:
    prediction_input: PredictionSystemInput | None = None
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


def _clamp_confidence(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 0.75:
        return 0.75
    return round(value, 2)


def _caution_level_to_rank(value: str) -> int:
    table = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "blocked": 4,
    }
    return table.get(value, 4)


def _rank_to_caution_level(value: int) -> str:
    if value <= 1:
        return "low"
    if value == 2:
        return "medium"
    if value == 3:
        return "high"
    return "blocked"


def _resolve_base_current_caution_level(
    prediction_input: PredictionSystemInput | None,
) -> str:
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
        digest_bucket = safe_str(market_runtime.get("interpretation_bucket"))
        if digest_bucket == "reanchor_required":
            return "blocked"
        if digest_bucket == "observe_only":
            return "medium"

        semantic_usage = dict(health_digest.semantic_usage or {})
        observer_status = safe_str(semantic_usage.get("observer_status"))
        if observer_status in {"broken", "unknown"}:
            return "high"
        if observer_status == "caution":
            return "medium"

    return "low"


def _resolve_replay_feedback_caution_signal(
    prediction_input: PredictionSystemInput | None,
) -> int:
    if prediction_input is None:
        return 0

    replay_feedback = dict(
        prediction_input.evidence_bundle.external_context.get("replay_feedback") or {}
    )
    if not replay_feedback:
        return 0

    average_caution_gap = safe_float(replay_feedback.get("average_caution_gap"))
    caution_review = safe_str(replay_feedback.get("caution_review"))

    if caution_review == "raise_caution_weight":
        return 1
    if caution_review == "lower_caution_weight":
        return -1

    if average_caution_gap is not None:
        if average_caution_gap >= 1.0:
            return 1
        if average_caution_gap <= -1.0:
            return -1

    return 0


def _resolve_replay_feedback_caution_adjustment(
    *,
    prediction_input: PredictionSystemInput | None,
    current_regime_state: str,
    base_caution_level: str,
) -> tuple[int, str]:
    raw_signal = _resolve_replay_feedback_caution_signal(prediction_input)
    if raw_signal == 0:
        return (0, "none")

    replay_feedback = {}
    if prediction_input is not None:
        replay_feedback = dict(
            prediction_input.evidence_bundle.external_context.get("replay_feedback")
            or {}
        )
    review_priority = safe_str(replay_feedback.get("review_priority"))

    if raw_signal < 0:
        if base_caution_level != "medium":
            return (0, "gated_non_relaxable_base")
        if current_regime_state in {"transition", "reversal_watch"}:
            return (0, "gated_fragile_regime")
        if review_priority == "high":
            return (0, "gated_high_priority")
        return (-1, "lower_once")

    if review_priority == "high":
        return (1, "raise_once_high_priority")
    return (1, "raise_once")


def _resolve_replay_feedback_invalidation_profile(
    prediction_input: PredictionSystemInput | None,
) -> dict[str, float]:
    defaults = {
        "minimum_entry_count": 2.0,
        "raise_review_score": 1.0,
        "lower_review_score": -1.0,
        "missed_ratio_medium": 0.34,
        "missed_ratio_high": 0.60,
        "missed_ratio_medium_score": 1.0,
        "missed_ratio_high_score": 2.0,
        "high_priority_ratio_trigger": 0.50,
        "high_priority_ratio_score": 1.0,
        "trace_focus_switch_bias_score": 0.5,
        "trace_focus_fragility_bias_score": 0.35,
        "trace_focus_watch_bias_score": 0.2,
        "trace_focus_context_bias_score": 0.1,
    }

    if prediction_input is None:
        return defaults

    replay_feedback = dict(
        prediction_input.evidence_bundle.external_context.get("replay_feedback") or {}
    )
    profile = replay_feedback.get("invalidation_profile")
    if not isinstance(profile, dict):
        return defaults

    merged = dict(defaults)
    for key in defaults:
        parsed = safe_float(profile.get(key))
        if parsed is not None:
            merged[key] = parsed
    return merged


def _resolve_replay_feedback_trace_focus_material(
    prediction_input: PredictionSystemInput | None,
) -> dict[str, Any]:
    defaults = {
        "focus": "unknown",
        "kind": "none",
        "direction": "neutral",
        "strength": 0.0,
    }

    if prediction_input is None:
        return defaults

    replay_feedback = dict(
        prediction_input.evidence_bundle.external_context.get("replay_feedback") or {}
    )
    focus = safe_str(replay_feedback.get("scenario_trace_focus")) or "unknown"
    if focus in {"unknown", "none"}:
        return {
            "focus": focus,
            "kind": "none",
            "direction": "neutral",
            "strength": 0.0,
        }

    if focus.startswith("switch_reason:"):
        focus_value = focus.split(":", 1)[1]
        if focus_value in {
            "watch_reversal_path",
            "prepare_reversal_switch",
            "prepare_transition_switch",
            "execute_transition_switch",
        }:
            return {
                "focus": focus,
                "kind": "switch_reason",
                "direction": "switch_bias",
                "strength": 1.0,
            }
        return {
            "focus": focus,
            "kind": "switch_reason",
            "direction": "watch_bias",
            "strength": 0.5,
        }

    if focus.startswith("regime_decision:"):
        focus_value = focus.split(":", 1)[1]
        if "weakening" in focus_value or "reanchor" in focus_value:
            return {
                "focus": focus,
                "kind": "regime_decision",
                "direction": "fragility_bias",
                "strength": 0.75,
            }
        return {
            "focus": focus,
            "kind": "regime_decision",
            "direction": "context_bias",
            "strength": 0.5,
        }

    return {
        "focus": focus,
        "kind": "other",
        "direction": "neutral",
        "strength": 0.25,
    }


def _resolve_replay_feedback_invalidation_adjustment(
    prediction_input: PredictionSystemInput | None,
) -> tuple[int, str, float]:
    if prediction_input is None:
        return (0, "none", 0.0)

    replay_feedback = dict(
        prediction_input.evidence_bundle.external_context.get("replay_feedback") or {}
    )
    if not replay_feedback:
        return (0, "none", 0.0)

    profile = _resolve_replay_feedback_invalidation_profile(prediction_input)

    entry_count = float(_safe_int(replay_feedback.get("entry_count")) or 0)
    if entry_count < profile["minimum_entry_count"]:
        return (0, "insufficient_entries", 0.0)

    missed_count = float(_safe_int(replay_feedback.get("missed_count")) or 0)
    high_priority_count = float(_safe_int(replay_feedback.get("high_priority_count")) or 0)
    invalidation_review = safe_str(replay_feedback.get("invalidation_review"))
    trace_focus_material = _resolve_replay_feedback_trace_focus_material(
        prediction_input
    )

    score = 0.0

    if invalidation_review == "raise_invalidation_sensitivity":
        score += profile["raise_review_score"]
    elif invalidation_review == "lower_invalidation_sensitivity":
        score += profile["lower_review_score"]

    missed_ratio = missed_count / entry_count if entry_count > 0 else 0.0
    high_priority_ratio = high_priority_count / entry_count if entry_count > 0 else 0.0

    if missed_ratio >= profile["missed_ratio_high"]:
        score += profile["missed_ratio_high_score"]
    elif missed_ratio >= profile["missed_ratio_medium"]:
        score += profile["missed_ratio_medium_score"]

    if high_priority_ratio >= profile["high_priority_ratio_trigger"]:
        score += profile["high_priority_ratio_score"]

    trace_focus_direction = safe_str(trace_focus_material.get("direction")) or "neutral"
    if trace_focus_direction == "switch_bias":
        score += profile["trace_focus_switch_bias_score"]
    elif trace_focus_direction == "fragility_bias":
        score += profile["trace_focus_fragility_bias_score"]
    elif trace_focus_direction == "watch_bias":
        score += profile["trace_focus_watch_bias_score"]
    elif trace_focus_direction == "context_bias":
        score += profile["trace_focus_context_bias_score"]

    rounded_score = round(score, 2)

    if rounded_score >= 3.0:
        return (2, "raise_twice", rounded_score)
    if rounded_score >= 1.0:
        return (1, "raise_once", rounded_score)
    if rounded_score <= -1.0:
        return (-1, "lower_once", rounded_score)
    return (0, "none", rounded_score)


def _apply_caution_adjustment(
    *,
    base_level: str,
    caution_rank_adjustment: int,
) -> str:
    return _rank_to_caution_level(
        _caution_level_to_rank(base_level) + caution_rank_adjustment
    )


def _resolve_current_caution_level(
    *,
    prediction_input: PredictionSystemInput | None,
    current_regime_state: str,
) -> str:
    base_caution_level = _resolve_base_current_caution_level(prediction_input)
    caution_rank_adjustment, _ = _resolve_replay_feedback_caution_adjustment(
        prediction_input=prediction_input,
        current_regime_state=current_regime_state,
        base_caution_level=base_caution_level,
    )
    return _apply_caution_adjustment(
        base_level=base_caution_level,
        caution_rank_adjustment=caution_rank_adjustment,
    )


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

    transition_sign = safe_str(regime_turning_point.get("transition_sign"))
    turning_point_risk = safe_str(regime_turning_point.get("turning_point_risk"))

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


def _resolve_replay_feedback_confidence_adjustment(
    prediction_input: PredictionSystemInput | None,
) -> float:
    if prediction_input is None:
        return 0.0

    replay_feedback = dict(
        prediction_input.evidence_bundle.external_context.get("replay_feedback") or {}
    )
    if not replay_feedback:
        return 0.0

    average_confidence_gap = safe_float(
        replay_feedback.get("average_confidence_gap")
    )
    review_priority = safe_str(replay_feedback.get("review_priority"))
    confidence_review = safe_str(replay_feedback.get("confidence_review"))

    adjustment = 0.0

    if average_confidence_gap is not None:
        if average_confidence_gap <= -0.20:
            adjustment -= 0.08
        elif average_confidence_gap <= -0.10:
            adjustment -= 0.05
        elif average_confidence_gap >= 0.20:
            adjustment += 0.05
        elif average_confidence_gap >= 0.10:
            adjustment += 0.03

    if confidence_review == "lower_confidence_weight":
        adjustment -= 0.04
    elif confidence_review == "raise_confidence_weight":
        adjustment += 0.04

    if review_priority == "high":
        if adjustment < 0.0:
            adjustment -= 0.02
        elif adjustment > 0.0:
            adjustment += 0.01

    return round(adjustment, 2)


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

    base += _resolve_replay_feedback_confidence_adjustment(prediction_input)

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
    turning_point_risk = safe_str(regime_turning_point.get("turning_point_risk")) or "low"

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
    *,
    replay_feedback_invalidation_adjustment: int = 0,
    replay_feedback_invalidation_policy: str = "none",
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

    transition_sign = safe_str(regime_turning_point.get("transition_sign"))
    if transition_sign is not None:
        out.append(f"transition_sign:{transition_sign}")

    turning_point_risk = safe_str(regime_turning_point.get("turning_point_risk"))
    if turning_point_risk in {"medium", "high"}:
        out.append(f"turning_point_risk:{turning_point_risk}")

    if replay_feedback_invalidation_adjustment != 0:
        out.append(
            f"replay_feedback_invalidation:{replay_feedback_invalidation_policy}"
        )

    for family in prediction_input.evidence_trace.missing_families:
        if family != "market_summary_anchor":
            out.append(f"missing:{family}")

    return tuple(out)


def _resolve_invalidation_state(
    *,
    current_regime_state: str,
    current_hypothesis_health: str,
    replay_feedback_invalidation_adjustment: int,
) -> str:
    if current_hypothesis_health in {
        "stable",
        "caution_increase",
        "degraded",
        "invalidated",
        "scenario_switch_required",
    }:
        base_state = current_hypothesis_health
    elif current_regime_state == "transition":
        base_state = "scenario_switch_required"
    elif current_regime_state == "reversal_watch":
        base_state = "caution_increase"
    elif current_regime_state == "unstable":
        base_state = "degraded"
    elif current_regime_state == "no_trade":
        base_state = "invalidated"
    else:
        base_state = "unknown"

    if replay_feedback_invalidation_adjustment <= 0:
        return base_state

    if base_state == "stable":
        return "caution_increase"
    if (
        base_state == "caution_increase"
        and replay_feedback_invalidation_adjustment >= 2
    ):
        return "degraded"
    return base_state


def _resolve_scenario_switch_hint(
    *,
    current_regime_state: str,
    current_hypothesis_health: str,
    invalidation_state: str,
    replay_feedback_invalidation_adjustment: int,
) -> str:
    if current_regime_state == "continuation":
        if invalidation_state == "stable":
            return "hold_primary"
        if invalidation_state == "caution_increase":
            if replay_feedback_invalidation_adjustment > 0:
                return "tighten_primary_watch"
            return "hold_primary"
        if invalidation_state == "degraded":
            return "prepare_alternate_path"
        if invalidation_state in {"invalidated", "scenario_switch_required"}:
            return "exit_primary_bias"
        return "hold_primary"

    if current_regime_state == "reversal_watch":
        if invalidation_state in {"degraded", "invalidated", "scenario_switch_required"}:
            return "prepare_reversal_switch"
        return "watch_reversal_path"

    if current_regime_state == "transition":
        if invalidation_state == "scenario_switch_required":
            return "execute_transition_switch"
        return "prepare_transition_switch"

    if current_regime_state == "unstable":
        if invalidation_state in {"invalidated", "scenario_switch_required"}:
            return "rebuild_after_instability"
        if current_hypothesis_health == "degraded":
            return "reduce_participation"
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


def _build_evidence_weighting_trace(
    prediction_input: PredictionSystemInput | None,
) -> dict[str, Any]:
    if prediction_input is None:
        return {
            "trace_type": "prediction_evidence_weighting_trace",
            "trace_version": "phase3.v1alpha1",
            "family_weight_rows": (),
            "family_count": 0,
            "active_weight_total": 0.0,
            "missing_weight_total": 0.0,
            "caution_family_count": 0,
            "primary_family": None,
        }

    bundle = prediction_input.evidence_bundle
    evidence_trace = prediction_input.evidence_trace
    replay_feedback = dict(bundle.external_context.get("replay_feedback") or {})

    family_specs: tuple[tuple[str, float, bool, bool, tuple[str, ...]], ...] = (
        (
            "market_summary_anchor",
            0.40,
            bundle.market_summary is not None,
            True,
            (
                "market_summary_present"
                if bundle.market_summary is not None
                else "market_summary_absent",
            ),
        ),
        (
            "liquidity_board_history",
            0.20,
            bool(bundle.liquidity_board_history),
            True,
            (
                "liquidity_board_history_present"
                if bundle.liquidity_board_history
                else "liquidity_board_history_absent",
            ),
        ),
        (
            "regime_turning_point",
            0.25,
            bool(bundle.regime_turning_point),
            True,
            (
                "regime_turning_point_present"
                if bundle.regime_turning_point
                else "regime_turning_point_absent",
            ),
        ),
        (
            "health_digest_caution",
            0.10,
            bundle.health_digest is not None,
            False,
            (
                "health_digest_present"
                if bundle.health_digest is not None
                else "health_digest_absent_optional",
            ),
        ),
        (
            "replay_feedback",
            0.05,
            bool(replay_feedback),
            False,
            (
                "replay_feedback_present"
                if replay_feedback
                else "replay_feedback_absent_optional",
            ),
        ),
    )

    rows: list[dict[str, Any]] = []
    active_weight_total = 0.0
    missing_weight_total = 0.0
    caution_family_count = 0

    for family, configured_weight, present, required, reason_refs in family_specs:
        caution_refs = tuple(
            flag
            for flag in evidence_trace.caution_flags
            if flag.startswith(family) or family.split("_", 1)[0] in flag
        )
        if present:
            state = "active_caution" if caution_refs else "active"
            active_weight_total += configured_weight
        elif required:
            state = "missing"
            missing_weight_total += configured_weight
        else:
            state = "inactive_optional"

        if caution_refs:
            caution_family_count += 1

        rows.append(
            {
                "family": family,
                "configured_weight": configured_weight,
                "state": state,
                "required": required,
                "reason_refs": reason_refs,
                "caution_refs": caution_refs,
            }
        )

    active_rows = [row for row in rows if str(row["state"]).startswith("active")]
    primary_family = None
    if active_rows:
        primary_family = max(
            active_rows,
            key=lambda row: float(row["configured_weight"]),
        )["family"]

    return {
        "trace_type": "prediction_evidence_weighting_trace",
        "trace_version": "phase3.v1alpha1",
        "family_weight_rows": tuple(rows),
        "family_count": len(rows),
        "active_weight_total": round(active_weight_total, 2),
        "missing_weight_total": round(missing_weight_total, 2),
        "caution_family_count": caution_family_count,
        "primary_family": primary_family,
    }


def _build_evidence_weighting_summary(
    evidence_weighting_trace: dict[str, Any],
) -> dict[str, Any]:
    return {
        "family_count": evidence_weighting_trace.get("family_count", 0),
        "active_weight_total": evidence_weighting_trace.get(
            "active_weight_total",
            0.0,
        ),
        "missing_weight_total": evidence_weighting_trace.get(
            "missing_weight_total",
            0.0,
        ),
        "caution_family_count": evidence_weighting_trace.get(
            "caution_family_count",
            0,
        ),
        "primary_family": evidence_weighting_trace.get("primary_family"),
    }


def _resolve_rewrite_state(invalidation_state: str) -> str:
    if invalidation_state in {"invalidated", "scenario_switch_required"}:
        return "rewrite_required"
    if invalidation_state == "degraded":
        return "rewrite_prepared"
    if invalidation_state == "caution_increase":
        return "rewrite_watch"
    if invalidation_state == "stable":
        return "rewrite_not_required"
    return "unknown"


def _resolve_rewrite_priority(
    *,
    invalidation_state: str,
    scenario_switch_hint: str,
) -> str:
    if invalidation_state in {"invalidated", "scenario_switch_required"}:
        return "high"
    if scenario_switch_hint in {
        "execute_transition_switch",
        "prepare_reversal_switch",
        "rebuild_after_instability",
        "exit_primary_bias",
    }:
        return "high"
    if invalidation_state in {"degraded", "caution_increase"}:
        return "medium"
    if scenario_switch_hint in {
        "tighten_primary_watch",
        "watch_reversal_path",
        "prepare_transition_switch",
        "reduce_participation",
    }:
        return "medium"
    if invalidation_state == "stable":
        return "normal"
    return "unknown"


def _resolve_evidence_weighting_state(
    evidence_weighting_summary: dict[str, Any],
) -> str:
    active_weight_total = safe_float(
        evidence_weighting_summary.get("active_weight_total")
    )
    missing_weight_total = safe_float(
        evidence_weighting_summary.get("missing_weight_total")
    )
    caution_family_count = _safe_int(
        evidence_weighting_summary.get("caution_family_count")
    )

    active_weight_total = active_weight_total if active_weight_total is not None else 0.0
    missing_weight_total = (
        missing_weight_total if missing_weight_total is not None else 0.0
    )
    caution_family_count = caution_family_count if caution_family_count is not None else 0

    if active_weight_total < 0.60 or missing_weight_total >= 0.25:
        return "weak_evidence"
    if caution_family_count > 0:
        return "caution_evidence"
    if active_weight_total < 0.80 or missing_weight_total > 0.0:
        return "partial_evidence"
    return "sufficient_evidence"


def _resolve_replay_feedback_rewrite_effect(
    replay_feedback_invalidation_adjustment: int,
) -> str:
    if replay_feedback_invalidation_adjustment > 0:
        return "raise_rewrite_sensitivity"
    if replay_feedback_invalidation_adjustment < 0:
        return "lower_rewrite_sensitivity"
    return "neutral"


def _resolve_trace_focus_rewrite_action(
    replay_feedback_trace_focus_material: dict[str, Any],
) -> str:
    direction = safe_str(
        replay_feedback_trace_focus_material.get("direction")
    ) or "neutral"
    if direction == "switch_bias":
        return "prioritize_switch_reason_review"
    if direction == "fragility_bias":
        return "prioritize_fragility_rewrite_review"
    if direction == "watch_bias":
        return "prioritize_watch_path_review"
    if direction == "context_bias":
        return "include_context_in_rewrite_review"
    return "none"


def _build_invalidation_rewrite_trace(
    *,
    current_regime_state: str,
    current_hypothesis_health: str,
    invalidation_state: str,
    invalidation_signals: tuple[str, ...],
    scenario_switch_hint: str,
    evidence_weighting_summary: dict[str, Any],
    replay_feedback_invalidation_adjustment: int,
    replay_feedback_invalidation_policy: str,
    replay_feedback_invalidation_score: float,
    replay_feedback_trace_focus_material: dict[str, Any],
) -> dict[str, Any]:
    rewrite_state = _resolve_rewrite_state(invalidation_state)
    rewrite_priority = _resolve_rewrite_priority(
        invalidation_state=invalidation_state,
        scenario_switch_hint=scenario_switch_hint,
    )
    evidence_weighting_state = _resolve_evidence_weighting_state(
        evidence_weighting_summary
    )

    return {
        "trace_type": "prediction_invalidation_rewrite_trace",
        "trace_version": "phase3.v1alpha1",
        "current_regime_state": current_regime_state,
        "current_hypothesis_health": current_hypothesis_health,
        "invalidation_state": invalidation_state,
        "invalidation_signal_count": len(invalidation_signals),
        "invalidation_signals": invalidation_signals,
        "rewrite_state": rewrite_state,
        "rewrite_priority": rewrite_priority,
        "rewrite_reason": scenario_switch_hint,
        "evidence_weighting_state": evidence_weighting_state,
        "evidence_weighting_summary": dict(evidence_weighting_summary),
        "replay_feedback_rewrite_effect": (
            _resolve_replay_feedback_rewrite_effect(
                replay_feedback_invalidation_adjustment
            )
        ),
        "replay_feedback_invalidation_adjustment": (
            replay_feedback_invalidation_adjustment
        ),
        "replay_feedback_invalidation_policy": (
            replay_feedback_invalidation_policy
        ),
        "replay_feedback_invalidation_score": replay_feedback_invalidation_score,
        "trace_focus_rewrite_action": _resolve_trace_focus_rewrite_action(
            replay_feedback_trace_focus_material
        ),
        "trace_focus_material": dict(replay_feedback_trace_focus_material),
    }


def _resolve_switch_action_family(scenario_switch_hint: str) -> str:
    if scenario_switch_hint in {"hold_primary", "maintain_no_trade"}:
        return "hold"
    if scenario_switch_hint in {"tighten_primary_watch", "watch_reversal_path"}:
        return "watch"
    if scenario_switch_hint in {
        "prepare_alternate_path",
        "prepare_reversal_switch",
        "prepare_transition_switch",
    }:
        return "prepare"
    if scenario_switch_hint == "execute_transition_switch":
        return "execute"
    if scenario_switch_hint == "exit_primary_bias":
        return "exit"
    if scenario_switch_hint == "rebuild_after_instability":
        return "rebuild"
    if scenario_switch_hint == "reduce_participation":
        return "reduce"
    return "unknown"


def _resolve_switch_urgency(
    *,
    scenario_switch_hint: str,
    invalidation_rewrite_trace: dict[str, Any],
) -> str:
    rewrite_priority = safe_str(
        invalidation_rewrite_trace.get("rewrite_priority")
    ) or "unknown"
    if scenario_switch_hint in {
        "execute_transition_switch",
        "prepare_reversal_switch",
        "rebuild_after_instability",
        "exit_primary_bias",
    }:
        return "high"
    if rewrite_priority == "high":
        return "high"
    if scenario_switch_hint in {
        "tighten_primary_watch",
        "watch_reversal_path",
        "prepare_alternate_path",
        "prepare_transition_switch",
        "reduce_participation",
    }:
        return "medium"
    if rewrite_priority == "medium":
        return "medium"
    if scenario_switch_hint in {"hold_primary", "maintain_no_trade"}:
        return "normal"
    return "unknown"


def _resolve_trace_focus_switch_alignment(
    *,
    scenario_switch_hint: str,
    replay_feedback_trace_focus_material: dict[str, Any],
) -> str:
    focus = safe_str(replay_feedback_trace_focus_material.get("focus")) or "unknown"
    kind = safe_str(replay_feedback_trace_focus_material.get("kind")) or "none"
    if kind == "none" or focus in {"unknown", "none"}:
        return "no_focus"
    if kind != "switch_reason":
        return "context_focus"
    expected_focus = f"switch_reason:{scenario_switch_hint}"
    if focus == expected_focus:
        return "aligned"
    return "different_switch_focus"


def _build_scenario_switch_trace(
    *,
    current_regime_state: str,
    current_hypothesis_health: str,
    invalidation_state: str,
    scenario_switch_hint: str,
    evidence_weighting_summary: dict[str, Any],
    invalidation_rewrite_trace: dict[str, Any],
    replay_feedback_trace_focus_material: dict[str, Any],
) -> dict[str, Any]:
    switch_action_family = _resolve_switch_action_family(scenario_switch_hint)
    switch_urgency = _resolve_switch_urgency(
        scenario_switch_hint=scenario_switch_hint,
        invalidation_rewrite_trace=invalidation_rewrite_trace,
    )
    focus_alignment = _resolve_trace_focus_switch_alignment(
        scenario_switch_hint=scenario_switch_hint,
        replay_feedback_trace_focus_material=replay_feedback_trace_focus_material,
    )

    return {
        "trace_type": "prediction_scenario_switch_trace",
        "trace_version": "phase3.v1alpha1",
        "switch_hint": scenario_switch_hint,
        "switch_action_family": switch_action_family,
        "switch_urgency": switch_urgency,
        "switch_reason_path": (
            f"regime:{current_regime_state}",
            f"hypothesis:{current_hypothesis_health}",
            f"invalidation:{invalidation_state}",
            f"rewrite:{invalidation_rewrite_trace.get('rewrite_state')}",
            f"evidence:{invalidation_rewrite_trace.get('evidence_weighting_state')}",
        ),
        "current_regime_state": current_regime_state,
        "current_hypothesis_health": current_hypothesis_health,
        "invalidation_state": invalidation_state,
        "evidence_weighting_state": invalidation_rewrite_trace.get(
            "evidence_weighting_state"
        ),
        "evidence_weighting_summary": dict(evidence_weighting_summary),
        "rewrite_state": invalidation_rewrite_trace.get("rewrite_state"),
        "rewrite_priority": invalidation_rewrite_trace.get("rewrite_priority"),
        "trace_focus_switch_alignment": focus_alignment,
        "trace_focus_material": dict(replay_feedback_trace_focus_material),
    }


def _build_scenario_trace(
    *,
    prediction_input: PredictionSystemInput | None,
    current_regime_state: str,
    current_hypothesis_health: str,
    current_caution_level: str,
    invalidation_state: str,
    scenario_switch_hint: str,
    evidence_weighting_trace: dict[str, Any],
    invalidation_rewrite_trace: dict[str, Any],
    scenario_switch_trace: dict[str, Any],
    replay_feedback_caution_adjustment: int,
    replay_feedback_caution_adjustment_policy: str,
    replay_feedback_invalidation_adjustment: int,
    replay_feedback_invalidation_policy: str,
    replay_feedback_invalidation_score: float,
    replay_feedback_scenario_trace_focus: str,
    replay_feedback_trace_focus_material: dict[str, Any],
) -> dict[str, Any]:
    if prediction_input is None:
        return {
            "trace_type": "prediction_scenario_trace",
            "trace_version": "phase3.v1alpha1",
            "regime_decision": "prediction_input_absent",
            "hypothesis_health_path": current_hypothesis_health,
            "caution_path": current_caution_level,
            "invalidation_path": invalidation_state,
            "switch_reason": scenario_switch_hint,
            "evidence_weighting_trace": dict(evidence_weighting_trace),
            "invalidation_rewrite_trace": dict(invalidation_rewrite_trace),
            "scenario_switch_trace": dict(scenario_switch_trace),
            "replay_feedback_effect": {
                "caution_adjustment": replay_feedback_caution_adjustment,
                "caution_policy": replay_feedback_caution_adjustment_policy,
                "invalidation_adjustment": replay_feedback_invalidation_adjustment,
                "invalidation_policy": replay_feedback_invalidation_policy,
                "invalidation_score": replay_feedback_invalidation_score,
                "scenario_trace_focus": replay_feedback_scenario_trace_focus,
                "trace_focus_material": dict(replay_feedback_trace_focus_material),
            },
        }

    bundle = prediction_input.evidence_bundle
    summary = bundle.market_summary
    regime_turning_point = dict(bundle.regime_turning_point or {})

    if summary is None:
        regime_decision = "market_summary_absent"
    elif summary.interpretation_bucket == "reanchor_required":
        regime_decision = "summary_reanchor_required"
    elif summary.interpretation_bucket == "observe_only":
        regime_decision = "summary_observe_only"
    elif summary.continuity_state == "resynced":
        regime_decision = "continuity_resynced"
    else:
        transition_sign = safe_str(regime_turning_point.get("transition_sign"))
        turning_point_risk = safe_str(regime_turning_point.get("turning_point_risk"))
        regime_decision = (
            f"transition_sign:{transition_sign}"
            if transition_sign is not None
            else f"turning_point_risk:{turning_point_risk or 'low'}"
        )

    return {
        "trace_type": "prediction_scenario_trace",
        "trace_version": "phase3.v1alpha1",
        "regime_decision": regime_decision,
        "hypothesis_health_path": current_hypothesis_health,
        "caution_path": current_caution_level,
        "invalidation_path": invalidation_state,
        "switch_reason": scenario_switch_hint,
        "evidence_weighting_trace": dict(evidence_weighting_trace),
        "invalidation_rewrite_trace": dict(invalidation_rewrite_trace),
        "scenario_switch_trace": dict(scenario_switch_trace),
        "replay_feedback_effect": {
            "caution_adjustment": replay_feedback_caution_adjustment,
            "caution_policy": replay_feedback_caution_adjustment_policy,
            "invalidation_adjustment": replay_feedback_invalidation_adjustment,
            "invalidation_policy": replay_feedback_invalidation_policy,
            "invalidation_score": replay_feedback_invalidation_score,
            "scenario_trace_focus": replay_feedback_scenario_trace_focus,
            "trace_focus_material": dict(replay_feedback_trace_focus_material),
        },
    }


def _build_replay_feedback_summary(
    prediction_input: PredictionSystemInput | None,
) -> dict[str, Any] | None:
    if prediction_input is None:
        return None

    replay_feedback = dict(
        prediction_input.evidence_bundle.external_context.get("replay_feedback") or {}
    )
    if not replay_feedback:
        return None

    return {
        "review_priority": safe_str(replay_feedback.get("review_priority")),
        "primary_focus": safe_str(replay_feedback.get("primary_focus")),
        "invalidation_review": safe_str(replay_feedback.get("invalidation_review")),
        "scenario_trace_focus": safe_str(
            replay_feedback.get("scenario_trace_focus")
        ),
        "entry_count": replay_feedback.get("entry_count"),
        "missed_count": replay_feedback.get("missed_count"),
        "high_priority_count": replay_feedback.get("high_priority_count"),
        "average_confidence_gap": replay_feedback.get("average_confidence_gap"),
        "average_caution_gap": replay_feedback.get("average_caution_gap"),
    }


def _build_evidence(prediction_input: PredictionSystemInput | None) -> dict[str, Any]:
    evidence_weighting_trace = _build_evidence_weighting_trace(prediction_input)
    evidence_weighting_summary = _build_evidence_weighting_summary(
        evidence_weighting_trace
    )
    if prediction_input is None:
        return {
            "market_summary_present": False,
            "health_digest_present": False,
            "liquidity_board_history_present": False,
            "regime_turning_point_present": False,
            "replay_feedback_present": False,
            "replay_feedback_summary": None,
            "evidence_trace_summary": _build_evidence_trace_summary(prediction_input),
            "evidence_weighting_summary": evidence_weighting_summary,
        }

    bundle = prediction_input.evidence_bundle
    summary = bundle.market_summary
    regime_turning_point = dict(bundle.regime_turning_point or {})
    replay_feedback = dict(bundle.external_context.get("replay_feedback") or {})

    return {
        "market_summary_present": summary is not None,
        "health_digest_present": bundle.health_digest is not None,
        "liquidity_board_history_present": bool(bundle.liquidity_board_history),
        "regime_turning_point_present": bool(bundle.regime_turning_point),
        "replay_feedback_present": bool(replay_feedback),
        "replay_feedback_summary": _build_replay_feedback_summary(prediction_input),
        "summary_interpretation_bucket": None if summary is None else summary.interpretation_bucket,
        "summary_trust_state": None if summary is None else summary.trust_state,
        "summary_continuity_state": None if summary is None else summary.continuity_state,
        "semantic_active_event_count": None
        if summary is None
        else summary.semantic_active_event_count,
        "orderbook_active_event_count": None
        if summary is None
        else summary.orderbook_active_event_count,
        "transition_sign": safe_str(regime_turning_point.get("transition_sign")),
        "turning_point_risk": safe_str(regime_turning_point.get("turning_point_risk")),
        "evidence_trace_summary": _build_evidence_trace_summary(prediction_input),
        "evidence_weighting_summary": evidence_weighting_summary,
    }


def build_prediction_scenario_output(
    inp: PredictionScenarioBuildInput,
) -> PredictionScenarioOutput:
    prediction_input = inp.prediction_input
    current_regime_state = _resolve_current_regime_state(prediction_input)
    base_current_caution_level = _resolve_base_current_caution_level(prediction_input)
    (
        replay_feedback_caution_adjustment,
        replay_feedback_caution_adjustment_policy,
    ) = _resolve_replay_feedback_caution_adjustment(
        prediction_input=prediction_input,
        current_regime_state=current_regime_state,
        base_caution_level=base_current_caution_level,
    )
    current_caution_level = _apply_caution_adjustment(
        base_level=base_current_caution_level,
        caution_rank_adjustment=replay_feedback_caution_adjustment,
    )
    current_hypothesis_health = _resolve_current_hypothesis_health(
        current_regime_state=current_regime_state,
        current_caution_level=current_caution_level,
    )
    (
        replay_feedback_invalidation_adjustment,
        replay_feedback_invalidation_policy,
        replay_feedback_invalidation_score,
    ) = _resolve_replay_feedback_invalidation_adjustment(prediction_input)
    replay_feedback = {}
    if prediction_input is not None:
        replay_feedback = dict(
            prediction_input.evidence_bundle.external_context.get("replay_feedback")
            or {}
        )
    replay_feedback_scenario_trace_focus = (
        safe_str(replay_feedback.get("scenario_trace_focus")) or "unknown"
    )
    replay_feedback_trace_focus_material = (
        _resolve_replay_feedback_trace_focus_material(prediction_input)
    )
    evidence_weighting_trace = _build_evidence_weighting_trace(prediction_input)
    evidence_weighting_summary = _build_evidence_weighting_summary(
        evidence_weighting_trace
    )

    current_confidence = _resolve_current_confidence(
        prediction_input=prediction_input,
        current_regime_state=current_regime_state,
        current_caution_level=current_caution_level,
    )
    invalidation_signals = _build_invalidation_signals(
        prediction_input,
        replay_feedback_invalidation_adjustment=replay_feedback_invalidation_adjustment,
        replay_feedback_invalidation_policy=replay_feedback_invalidation_policy,
    )
    invalidation_state = _resolve_invalidation_state(
        current_regime_state=current_regime_state,
        current_hypothesis_health=current_hypothesis_health,
        replay_feedback_invalidation_adjustment=replay_feedback_invalidation_adjustment,
    )
    scenario_switch_hint = _resolve_scenario_switch_hint(
        current_regime_state=current_regime_state,
        current_hypothesis_health=current_hypothesis_health,
        invalidation_state=invalidation_state,
        replay_feedback_invalidation_adjustment=replay_feedback_invalidation_adjustment,
    )
    invalidation_rewrite_trace = _build_invalidation_rewrite_trace(
        current_regime_state=current_regime_state,
        current_hypothesis_health=current_hypothesis_health,
        invalidation_state=invalidation_state,
        invalidation_signals=invalidation_signals,
        scenario_switch_hint=scenario_switch_hint,
        evidence_weighting_summary=evidence_weighting_summary,
        replay_feedback_invalidation_adjustment=(
            replay_feedback_invalidation_adjustment
        ),
        replay_feedback_invalidation_policy=replay_feedback_invalidation_policy,
        replay_feedback_invalidation_score=replay_feedback_invalidation_score,
        replay_feedback_trace_focus_material=replay_feedback_trace_focus_material,
    )
    scenario_switch_trace = _build_scenario_switch_trace(
        current_regime_state=current_regime_state,
        current_hypothesis_health=current_hypothesis_health,
        invalidation_state=invalidation_state,
        scenario_switch_hint=scenario_switch_hint,
        evidence_weighting_summary=evidence_weighting_summary,
        invalidation_rewrite_trace=invalidation_rewrite_trace,
        replay_feedback_trace_focus_material=replay_feedback_trace_focus_material,
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
            scenario_trace=_build_scenario_trace(
                prediction_input=prediction_input,
                current_regime_state=current_regime_state,
                current_hypothesis_health=current_hypothesis_health,
                current_caution_level=current_caution_level,
                invalidation_state=invalidation_state,
                scenario_switch_hint=scenario_switch_hint,
                evidence_weighting_trace=evidence_weighting_trace,
                invalidation_rewrite_trace=invalidation_rewrite_trace,
                scenario_switch_trace=scenario_switch_trace,
                replay_feedback_caution_adjustment=replay_feedback_caution_adjustment,
                replay_feedback_caution_adjustment_policy=replay_feedback_caution_adjustment_policy,
                replay_feedback_invalidation_adjustment=replay_feedback_invalidation_adjustment,
                replay_feedback_invalidation_policy=replay_feedback_invalidation_policy,
                replay_feedback_invalidation_score=replay_feedback_invalidation_score,
                replay_feedback_scenario_trace_focus=replay_feedback_scenario_trace_focus,
                replay_feedback_trace_focus_material=replay_feedback_trace_focus_material,
            ),
            evidence=_build_evidence(prediction_input),
            diagnostics={
                "builder_type": "prediction_scenario_output",
                "active_family_count": 0,
                "missing_family_count": 0,
                "caution_flag_count": 0,
                "replay_feedback_invalidation_adjustment": replay_feedback_invalidation_adjustment,
                "replay_feedback_invalidation_adjustment_policy": replay_feedback_invalidation_policy,
                "replay_feedback_invalidation_score": replay_feedback_invalidation_score,
                "evidence_weighting_active_weight_total": evidence_weighting_summary[
                    "active_weight_total"
                ],
                "evidence_weighting_missing_weight_total": evidence_weighting_summary[
                    "missing_weight_total"
                ],
                "evidence_weighting_primary_family": evidence_weighting_summary[
                    "primary_family"
                ],
                "invalidation_rewrite_state": invalidation_rewrite_trace[
                    "rewrite_state"
                ],
                "invalidation_rewrite_priority": invalidation_rewrite_trace[
                    "rewrite_priority"
                ],
                "invalidation_rewrite_evidence_weighting_state": (
                    invalidation_rewrite_trace["evidence_weighting_state"]
                ),
                "scenario_switch_action_family": scenario_switch_trace[
                    "switch_action_family"
                ],
                "scenario_switch_urgency": scenario_switch_trace[
                    "switch_urgency"
                ],
                "scenario_switch_trace_focus_alignment": scenario_switch_trace[
                    "trace_focus_switch_alignment"
                ],
                "replay_feedback_scenario_trace_focus": replay_feedback_scenario_trace_focus,
                "replay_feedback_trace_focus_kind": replay_feedback_trace_focus_material["kind"],
                "replay_feedback_trace_focus_direction": replay_feedback_trace_focus_material["direction"],
                "replay_feedback_trace_focus_strength": replay_feedback_trace_focus_material["strength"],
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
        scenario_trace=_build_scenario_trace(
            prediction_input=prediction_input,
            current_regime_state=current_regime_state,
            current_hypothesis_health=current_hypothesis_health,
            current_caution_level=current_caution_level,
            invalidation_state=invalidation_state,
            scenario_switch_hint=scenario_switch_hint,
            evidence_weighting_trace=evidence_weighting_trace,
            invalidation_rewrite_trace=invalidation_rewrite_trace,
            scenario_switch_trace=scenario_switch_trace,
            replay_feedback_caution_adjustment=replay_feedback_caution_adjustment,
            replay_feedback_caution_adjustment_policy=replay_feedback_caution_adjustment_policy,
            replay_feedback_invalidation_adjustment=replay_feedback_invalidation_adjustment,
            replay_feedback_invalidation_policy=replay_feedback_invalidation_policy,
            replay_feedback_invalidation_score=replay_feedback_invalidation_score,
            replay_feedback_scenario_trace_focus=replay_feedback_scenario_trace_focus,
            replay_feedback_trace_focus_material=replay_feedback_trace_focus_material,
        ),
        evidence=_build_evidence(prediction_input),
        evidence_trace=prediction_input.evidence_trace,
        diagnostics={
            "builder_type": "prediction_scenario_output",
            "requested_horizons_count": len(prediction_input.requested_horizons),
            "active_family_count": len(prediction_input.evidence_trace.active_families),
            "missing_family_count": len(prediction_input.evidence_trace.missing_families),
            "caution_flag_count": len(prediction_input.evidence_trace.caution_flags),
            "replay_feedback_present": bool(
                prediction_input.evidence_bundle.external_context.get("replay_feedback")
            ),
            "replay_feedback_confidence_adjustment": _resolve_replay_feedback_confidence_adjustment(
                prediction_input
            ),
            "replay_feedback_caution_adjustment": replay_feedback_caution_adjustment,
            "replay_feedback_caution_adjustment_policy": replay_feedback_caution_adjustment_policy,
            "replay_feedback_invalidation_adjustment": replay_feedback_invalidation_adjustment,
            "replay_feedback_invalidation_adjustment_policy": replay_feedback_invalidation_policy,
            "replay_feedback_invalidation_score": replay_feedback_invalidation_score,
            "evidence_weighting_active_weight_total": evidence_weighting_summary[
                "active_weight_total"
            ],
            "evidence_weighting_missing_weight_total": evidence_weighting_summary[
                "missing_weight_total"
            ],
            "evidence_weighting_primary_family": evidence_weighting_summary[
                "primary_family"
            ],
            "invalidation_rewrite_state": invalidation_rewrite_trace[
                "rewrite_state"
            ],
            "invalidation_rewrite_priority": invalidation_rewrite_trace[
                "rewrite_priority"
            ],
            "invalidation_rewrite_evidence_weighting_state": (
                invalidation_rewrite_trace["evidence_weighting_state"]
            ),
            "scenario_switch_action_family": scenario_switch_trace[
                "switch_action_family"
            ],
            "scenario_switch_urgency": scenario_switch_trace[
                "switch_urgency"
            ],
            "scenario_switch_trace_focus_alignment": scenario_switch_trace[
                "trace_focus_switch_alignment"
            ],
            "replay_feedback_scenario_trace_focus": replay_feedback_scenario_trace_focus,
            "replay_feedback_trace_focus_kind": replay_feedback_trace_focus_material["kind"],
            "replay_feedback_trace_focus_direction": replay_feedback_trace_focus_material["direction"],
            "replay_feedback_trace_focus_strength": replay_feedback_trace_focus_material["strength"],
            **dict(inp.diagnostics or {}),
        },
    )