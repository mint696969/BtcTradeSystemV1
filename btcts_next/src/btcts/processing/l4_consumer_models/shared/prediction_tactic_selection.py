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

    if "force_observe_only" in normalized_overlay_refs:
        if switch_hint == "maintain_no_trade":
            return "maintain_no_trade"
        if invalidation_state in {"invalidated", "scenario_switch_required"}:
            return "maintain_no_trade"
        return "observe_only"

    if "prefer_defensive_reduce_risk" in normalized_overlay_refs:
        return "defensive_reduce_risk"

    if (
        normalized_profile_kind == "defensive"
        and current_regime_state in {"continuation", "reversal_watch"}
        and current_caution_level in {"medium", "high", "blocked"}
    ):
        return "defensive_reduce_risk"

    if (
        "prefer_reversal_prepare" in normalized_overlay_refs
        and current_regime_state != "no_trade"
    ):
        return "reversal_prepare"

    if (
        "prefer_cautious_probe" in normalized_overlay_refs
        and current_regime_state == "continuation"
        and invalidation_state not in {"invalidated", "scenario_switch_required"}
        and current_caution_level != "blocked"
    ):
        return "cautious_probe"

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

    if (
        "prefer_cautious_probe" in normalized_overlay_refs
        and scenario_output is not None
        and primary_tactic_key not in {"cautious_probe", "maintain_no_trade"}
    ):
        ordered_keys.append(("cautious_probe", 25, "overlay_support"))

    if (
        "prefer_reversal_prepare" in normalized_overlay_refs
        and scenario_output is not None
        and primary_tactic_key not in {"reversal_prepare", "maintain_no_trade"}
        and scenario_output.current_regime_state != "no_trade"
    ):
        ordered_keys.append(("reversal_prepare", 25, "overlay_support"))

    if (
        "prefer_defensive_reduce_risk" in normalized_overlay_refs
        and scenario_output is not None
        and primary_tactic_key != "defensive_reduce_risk"
    ):
        ordered_keys.append(("defensive_reduce_risk", 25, "overlay_support"))

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