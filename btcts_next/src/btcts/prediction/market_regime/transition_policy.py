# path: ./btcts_next/src/btcts/prediction/market_regime/transition_policy.py
# desc: MR-F4 pure transition and persistence policy evaluator. No reads, writes, scheduler, UI, broker, AutoTrade, or order behavior.

from __future__ import annotations

from typing import Any, Mapping

MR_F4_TRANSITION_POLICY_VERSION = "prediction.market_regime.transition_policy.mr_f4.v1"

_VALID_CODES = {
    "UNKNOWN",
    "RANGE",
    "LOW_VOL_COMPRESSION",
    "UP_TREND",
    "DOWN_TREND",
    "HIGH_VOL_CHOP",
    "BREAKOUT",
    "REVERSAL_WATCH",
    "PANIC_SPIKE",
}

_DEFAULT_ALLOWED_TRANSITIONS = {
    "UNKNOWN": tuple(sorted(_VALID_CODES - {"UNKNOWN"})),
    "RANGE": ("RANGE", "LOW_VOL_COMPRESSION", "BREAKOUT", "HIGH_VOL_CHOP"),
    "LOW_VOL_COMPRESSION": ("LOW_VOL_COMPRESSION", "RANGE", "BREAKOUT"),
    "BREAKOUT": ("BREAKOUT", "UP_TREND", "DOWN_TREND", "HIGH_VOL_CHOP", "RANGE"),
    "UP_TREND": ("UP_TREND", "REVERSAL_WATCH", "HIGH_VOL_CHOP", "RANGE"),
    "DOWN_TREND": ("DOWN_TREND", "REVERSAL_WATCH", "HIGH_VOL_CHOP", "RANGE"),
    "REVERSAL_WATCH": ("REVERSAL_WATCH", "RANGE", "UP_TREND", "DOWN_TREND", "HIGH_VOL_CHOP"),
    "HIGH_VOL_CHOP": ("HIGH_VOL_CHOP", "RANGE", "UP_TREND", "DOWN_TREND", "PANIC_SPIKE"),
    "PANIC_SPIKE": ("PANIC_SPIKE", "HIGH_VOL_CHOP", "RANGE"),
}


def _clamp01(value: Any) -> float:
    try:
        number = float(value)
    except Exception:
        return 0.0
    return max(0.0, min(number, 1.0))


def _normalize(code: Any) -> str:
    value = str(code or "UNKNOWN").strip().upper() or "UNKNOWN"
    return value if value in _VALID_CODES else "UNKNOWN"


def _transition_settings(parameter_set: Any | None) -> Mapping[str, Any]:
    thresholds = getattr(parameter_set, "thresholds", {}) if parameter_set is not None else {}
    if not isinstance(thresholds, Mapping):
        return {}
    value = thresholds.get("transition_and_persistence", {})
    return value if isinstance(value, Mapping) else {}


def _allowed_transitions(settings: Mapping[str, Any]) -> dict[str, tuple[str, ...]]:
    raw = settings.get("allowed_transitions")
    if not isinstance(raw, Mapping):
        return dict(_DEFAULT_ALLOWED_TRANSITIONS)
    result: dict[str, tuple[str, ...]] = {}
    for source, targets in raw.items():
        normalized_source = _normalize(source)
        if not isinstance(targets, (list, tuple)):
            continue
        normalized_targets = tuple(dict.fromkeys(_normalize(item) for item in targets))
        result[normalized_source] = normalized_targets
    return result or dict(_DEFAULT_ALLOWED_TRANSITIONS)


def evaluate_market_regime_transition(
    *,
    previous_regime: str,
    candidate_regime: str,
    previous_state_age_sec: int | None,
    candidate_score: float | None,
    runner_up_score: float | None,
    change_point_evidence_score: float | None,
    parameter_set: Any | None = None,
) -> dict[str, Any]:
    settings = _transition_settings(parameter_set)
    previous = _normalize(previous_regime)
    candidate = _normalize(candidate_regime)

    minimum_dwell_sec = max(0, int(settings.get("minimum_dwell_sec", 300)))
    hysteresis_margin_min = _clamp01(settings.get("hysteresis_margin_min", 0.10))
    change_point_override_min = _clamp01(settings.get("change_point_override_min", 0.80))
    transition_penalty = _clamp01(settings.get("transition_penalty", 0.12))
    allowed = _allowed_transitions(settings)

    score = None if candidate_score is None else _clamp01(candidate_score)
    runner = None if runner_up_score is None else _clamp01(runner_up_score)
    margin = None if score is None or runner is None else round(score - runner, 4)
    change_point = _clamp01(change_point_evidence_score)
    age = previous_state_age_sec if isinstance(previous_state_age_sec, int) and previous_state_age_sec >= 0 else None

    same_state = previous == candidate and candidate != "UNKNOWN"
    dwell_satisfied = previous == "UNKNOWN" or (age is not None and age >= minimum_dwell_sec)
    change_point_override = change_point >= change_point_override_min
    hysteresis_satisfied = same_state or (margin is not None and margin >= hysteresis_margin_min)
    transition_allowed = candidate in allowed.get(previous, ())

    blockers: list[str] = []
    if candidate == "UNKNOWN":
        blockers.append("candidate_regime_unknown")
    if previous != "UNKNOWN" and not same_state and not transition_allowed:
        blockers.append("invalid_transition")
    if previous != "UNKNOWN" and not same_state and not dwell_satisfied and not change_point_override:
        blockers.append("minimum_dwell_not_satisfied")
    if previous != "UNKNOWN" and not same_state and not hysteresis_satisfied and not change_point_override:
        blockers.append("hysteresis_margin_not_satisfied")

    if candidate == "UNKNOWN":
        decision = "unknown"
        accepted_regime = "UNKNOWN"
    elif same_state:
        decision = "continued"
        accepted_regime = candidate
    elif blockers:
        decision = "held"
        accepted_regime = previous if previous != "UNKNOWN" else "UNKNOWN"
    else:
        decision = "transitioned" if previous != "UNKNOWN" else "started"
        accepted_regime = candidate

    score_support = score if score is not None else 0.0
    age_support = 1.0 if minimum_dwell_sec == 0 else min(1.0, float(age or 0) / float(minimum_dwell_sec))
    continuity_bonus = 0.20 if same_state else 0.0
    persistence_probability = _clamp01(
        0.45 * score_support
        + 0.25 * age_support
        + 0.20 * (1.0 - change_point)
        + continuity_bonus
        - (0.0 if same_state else transition_penalty)
    )

    return {
        "logic_version": MR_F4_TRANSITION_POLICY_VERSION,
        "previous_regime": previous,
        "candidate_regime": candidate,
        "accepted_regime": accepted_regime,
        "decision": decision,
        "same_state": same_state,
        "minimum_dwell_sec": minimum_dwell_sec,
        "previous_state_age_sec": age,
        "dwell_satisfied": dwell_satisfied,
        "hysteresis_margin_min": hysteresis_margin_min,
        "candidate_margin": margin,
        "hysteresis_satisfied": hysteresis_satisfied,
        "change_point_evidence_score": change_point,
        "change_point_override_min": change_point_override_min,
        "change_point_override_applied": change_point_override and not same_state,
        "transition_penalty": transition_penalty,
        "transition_allowed": transition_allowed,
        "persistence_probability": round(persistence_probability, 4),
        "persistence_probability_calibrated": False,
        "blockers": blockers,
        "read_only": True,
        "non_executing": True,
        "label_selection_applied": False,
        "would_send_to_broker": False,
    }
