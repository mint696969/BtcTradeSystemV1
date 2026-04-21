# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_tactic_selection.py
# desc: Scenario-driven tactic selection policy for Phase 4-A operating stance proposals.

from __future__ import annotations

from btcts.processing.l4_consumer_models.shared.prediction_system_contract import (
    PredictionScenarioOutput,
)


def _normalize_overlay_refs(
    overlay_refs: tuple[str, ...] | None,
) -> tuple[str, ...]:
    if not overlay_refs:
        return ()

    out: list[str] = []
    for item in overlay_refs:
        text = str(item).strip().lower()
        if text and text not in out:
            out.append(text)
    return tuple(out)


def _has_any_overlay(
    normalized_overlay_refs: tuple[str, ...],
    *expected_refs: str,
) -> bool:
    for item in expected_refs:
        if item in normalized_overlay_refs:
            return True
    return False


def _can_promote_active_tactic(
    *,
    invalidation_state: str,
    current_caution_level: str,
) -> bool:
    if invalidation_state in {"invalidated", "scenario_switch_required"}:
        return False
    if current_caution_level == "blocked":
        return False
    return True


def _resolve_overlay_primary_tactic_key(
    *,
    normalized_overlay_refs: tuple[str, ...],
    switch_hint: str,
    invalidation_state: str,
    current_regime_state: str,
    current_caution_level: str,
    current_confidence: float,
    can_promote_active_tactic: bool,
) -> str | None:
    if _has_any_overlay(normalized_overlay_refs, "force_observe_only"):
        if switch_hint == "maintain_no_trade":
            return "maintain_no_trade"
        if invalidation_state in {"invalidated", "scenario_switch_required"}:
            return "maintain_no_trade"
        return "observe_only"

    if _has_any_overlay(normalized_overlay_refs, "prefer_defensive_reduce_risk"):
        return "defensive_reduce_risk"

    if (
        _has_any_overlay(normalized_overlay_refs, "prefer_tighten_entry_gate")
        and current_regime_state == "continuation"
        and can_promote_active_tactic
    ):
        return "tighten_entry_gate"

    if (
        _has_any_overlay(normalized_overlay_refs, "prefer_reversal_prepare")
        and current_regime_state != "no_trade"
    ):
        return "reversal_prepare"

    if (
        _has_any_overlay(normalized_overlay_refs, "prefer_continuation_follow")
        and current_regime_state == "continuation"
        and can_promote_active_tactic
        and current_confidence >= 0.45
    ):
        return "continuation_follow"

    if (
        _has_any_overlay(normalized_overlay_refs, "prefer_cautious_probe")
        and current_regime_state == "continuation"
        and can_promote_active_tactic
    ):
        return "cautious_probe"

    return None


def _append_overlay_support_candidates(
    *,
    ordered_keys: list[tuple[str, int, str]],
    primary_tactic_key: str,
    scenario_output: PredictionScenarioOutput | None,
    normalized_overlay_refs: tuple[str, ...],
) -> None:
    if scenario_output is None:
        return

    if (
        _has_any_overlay(normalized_overlay_refs, "prefer_tighten_entry_gate")
        and primary_tactic_key not in {"tighten_entry_gate", "maintain_no_trade"}
        and scenario_output.current_regime_state == "continuation"
    ):
        ordered_keys.append(("tighten_entry_gate", 25, "overlay_support"))

    if (
        _has_any_overlay(normalized_overlay_refs, "prefer_continuation_follow")
        and primary_tactic_key not in {"continuation_follow", "maintain_no_trade"}
        and scenario_output.current_regime_state == "continuation"
    ):
        ordered_keys.append(("continuation_follow", 25, "overlay_support"))

    if (
        _has_any_overlay(normalized_overlay_refs, "prefer_cautious_probe")
        and primary_tactic_key not in {"cautious_probe", "maintain_no_trade"}
    ):
        ordered_keys.append(("cautious_probe", 25, "overlay_support"))

    if (
        _has_any_overlay(normalized_overlay_refs, "prefer_reversal_prepare")
        and primary_tactic_key not in {"reversal_prepare", "maintain_no_trade"}
        and scenario_output.current_regime_state != "no_trade"
    ):
        ordered_keys.append(("reversal_prepare", 25, "overlay_support"))

    if (
        _has_any_overlay(normalized_overlay_refs, "prefer_defensive_reduce_risk")
        and primary_tactic_key != "defensive_reduce_risk"
    ):
        ordered_keys.append(("defensive_reduce_risk", 25, "overlay_support"))


def build_selection_trace(
    *,
    scenario_output: PredictionScenarioOutput | None,
    primary_tactic_key: str,
    profile_kind: str | None = None,
    overlay_refs: tuple[str, ...] | None = None,
) -> dict[str, object]:
    normalized_profile_kind = (profile_kind or "").strip().lower() or None
    normalized_overlay_refs = _normalize_overlay_refs(overlay_refs)

    selection_bias_tags: list[str] = []

    if normalized_profile_kind is not None:
        selection_bias_tags.append(f"profile:{normalized_profile_kind}")

    for item in normalized_overlay_refs:
        selection_bias_tags.append(f"overlay:{item}")

    if scenario_output is not None:
        if scenario_output.current_caution_level in {"high", "blocked"}:
            selection_bias_tags.append(
                f"caution:{scenario_output.current_caution_level}"
            )
        if scenario_output.invalidation_state in {
            "invalidated",
            "scenario_switch_required",
        }:
            selection_bias_tags.append(
                f"invalidation:{scenario_output.invalidation_state}"
            )

    return {
        "trace_type": "tactic_selection_trace",
        "primary_tactic_key": primary_tactic_key,
        "scenario_present": scenario_output is not None,
        "profile_kind": normalized_profile_kind,
        "overlay_refs": normalized_overlay_refs,
        "selection_bias_tags": tuple(selection_bias_tags),
        "scenario_switch_hint": None
        if scenario_output is None
        else scenario_output.scenario_switch_hint,
        "scenario_regime": None
        if scenario_output is None
        else scenario_output.current_regime_state,
        "current_caution_level": None
        if scenario_output is None
        else scenario_output.current_caution_level,
        "invalidation_state": None
        if scenario_output is None
        else scenario_output.invalidation_state,
    }


def resolve_primary_tactic_key(
    scenario_output: PredictionScenarioOutput | None,
    *,
    profile_kind: str | None = None,
    overlay_refs: tuple[str, ...] | None = None,
) -> str:
    if scenario_output is None:
        return "maintain_no_trade"

    normalized_profile_kind = (profile_kind or "").strip().lower() or None
    normalized_overlay_refs = _normalize_overlay_refs(overlay_refs)

    switch_hint = scenario_output.scenario_switch_hint
    invalidation_state = scenario_output.invalidation_state
    current_regime_state = scenario_output.current_regime_state
    current_caution_level = scenario_output.current_caution_level
    current_confidence = float(scenario_output.current_confidence or 0.0)

    can_promote_active_tactic = _can_promote_active_tactic(
        invalidation_state=invalidation_state,
        current_caution_level=current_caution_level,
    )

    if (
        normalized_profile_kind == "defensive"
        and current_regime_state in {"continuation", "reversal_watch"}
        and current_caution_level in {"medium", "high", "blocked"}
    ):
        return "defensive_reduce_risk"

    overlay_primary_tactic_key = _resolve_overlay_primary_tactic_key(
        normalized_overlay_refs=normalized_overlay_refs,
        switch_hint=switch_hint,
        invalidation_state=invalidation_state,
        current_regime_state=current_regime_state,
        current_caution_level=current_caution_level,
        current_confidence=current_confidence,
        can_promote_active_tactic=can_promote_active_tactic,
    )
    if overlay_primary_tactic_key is not None:
        return overlay_primary_tactic_key

    if switch_hint == "maintain_no_trade":
        return "maintain_no_trade"
    if switch_hint == "rebuild_after_instability":
        return "observe_only"
    if switch_hint == "tighten_primary_watch":
        return "tighten_entry_gate"
    if switch_hint in {
        "prepare_alternate_path",
        "prepare_reversal_switch",
        "prepare_transition_switch",
        "execute_transition_switch",
        "watch_reversal_path",
    }:
        return "reversal_prepare"

    if invalidation_state in {"invalidated", "scenario_switch_required"}:
        return "maintain_no_trade"
    if current_regime_state in {"transition", "unstable", "no_trade"}:
        return "observe_only"
    if current_caution_level in {"high", "blocked"}:
        return "defensive_reduce_risk"
    if current_regime_state == "continuation":
        if current_confidence >= 0.45 and current_caution_level == "low":
            return "continuation_follow"
        if current_confidence >= 0.25:
            return "cautious_probe"
        return "observe_only"
    if current_regime_state == "reversal_watch":
        return "reversal_prepare"

    return "observe_only"


def resolve_proposal_state(
    primary_tactic_key: str,
    scenario_output: PredictionScenarioOutput | None,
) -> str:
    if scenario_output is None:
        return "blocked"
    if primary_tactic_key in {"maintain_no_trade", "observe_only"}:
        return "hold"
    return "proposed"


def build_candidate_plan(
    *,
    primary_tactic_key: str,
    scenario_output: PredictionScenarioOutput | None,
    profile_kind: str | None = None,
    overlay_refs: tuple[str, ...] | None = None,
) -> tuple[tuple[str, int, str], ...]:
    normalized_profile_kind = (profile_kind or "").strip().lower() or None
    normalized_overlay_refs = _normalize_overlay_refs(overlay_refs)

    ordered_keys: list[tuple[str, int, str]] = [
        (primary_tactic_key, 10, "aligned"),
    ]

    if primary_tactic_key == "continuation_follow":
        ordered_keys.append(("cautious_probe", 20, "supporting"))
    if primary_tactic_key not in {"observe_only", "maintain_no_trade"}:
        ordered_keys.append(("observe_only", 80, "fallback"))

    if (
        normalized_profile_kind == "defensive"
        and primary_tactic_key != "defensive_reduce_risk"
    ):
        ordered_keys.append(("defensive_reduce_risk", 25, "profile_support"))

    _append_overlay_support_candidates(
        ordered_keys=ordered_keys,
        primary_tactic_key=primary_tactic_key,
        scenario_output=scenario_output,
        normalized_overlay_refs=normalized_overlay_refs,
    )

    if (
        scenario_output is not None
        and scenario_output.current_caution_level in {"high", "blocked"}
        and primary_tactic_key != "defensive_reduce_risk"
    ):
        ordered_keys.append(("defensive_reduce_risk", 30, "supporting"))

    if (
        scenario_output is not None
        and scenario_output.invalidation_state
        in {"invalidated", "scenario_switch_required"}
        and primary_tactic_key != "maintain_no_trade"
    ):
        ordered_keys.append(("maintain_no_trade", 40, "supporting"))

    return tuple(ordered_keys)