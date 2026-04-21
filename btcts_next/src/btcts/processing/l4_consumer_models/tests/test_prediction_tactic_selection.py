# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_tactic_selection.py
# desc: Verify Phase 4-A tactic selection policy stays scenario-driven and builder-independent.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared.prediction_system_contract import (  # noqa: E402
    PredictionScenarioOutput,
)
from btcts.processing.l4_consumer_models.shared.prediction_tactic_selection import (  # noqa: E402
    build_candidate_plan,
    build_selection_trace,
    resolve_primary_tactic_key,
    resolve_proposal_state,
)


def main() -> int:
    continuation = PredictionScenarioOutput(
        current_regime_state="continuation",
        current_caution_level="low",
        current_confidence=0.62,
        invalidation_state="stable",
        scenario_switch_hint="hold_primary",
    )
    assert resolve_primary_tactic_key(continuation) == "continuation_follow"
    assert resolve_proposal_state("continuation_follow", continuation) == "proposed"
    assert build_candidate_plan(
        primary_tactic_key="continuation_follow",
        scenario_output=continuation,
    ) == (
        ("continuation_follow", 10, "aligned"),
        ("cautious_probe", 20, "supporting"),
        ("observe_only", 80, "fallback"),
    )

    reversal_watch = PredictionScenarioOutput(
        current_regime_state="reversal_watch",
        current_caution_level="medium",
        current_confidence=0.31,
        invalidation_state="caution_increase",
        scenario_switch_hint="prepare_reversal_switch",
    )
    assert resolve_primary_tactic_key(reversal_watch) == "reversal_prepare"
    assert resolve_proposal_state("reversal_prepare", reversal_watch) == "proposed"
    assert build_candidate_plan(
        primary_tactic_key="reversal_prepare",
        scenario_output=reversal_watch,
    ) == (
        ("reversal_prepare", 10, "aligned"),
        ("observe_only", 80, "fallback"),
    )

    defensive = PredictionScenarioOutput(
        current_regime_state="continuation",
        current_caution_level="high",
        current_confidence=0.41,
        invalidation_state="degraded",
        scenario_switch_hint="hold_primary",
    )
    assert resolve_primary_tactic_key(defensive) == "defensive_reduce_risk"
    assert build_candidate_plan(
        primary_tactic_key="defensive_reduce_risk",
        scenario_output=defensive,
    ) == (
        ("defensive_reduce_risk", 10, "aligned"),
        ("observe_only", 80, "fallback"),
    )

    overlay_probe = PredictionScenarioOutput(
        current_regime_state="continuation",
        current_caution_level="low",
        current_confidence=0.62,
        invalidation_state="stable",
        scenario_switch_hint="hold_primary",
    )
    assert (
        resolve_primary_tactic_key(
            overlay_probe,
            overlay_refs=("prefer_cautious_probe",),
        )
        == "cautious_probe"
    )
    assert build_candidate_plan(
        primary_tactic_key="cautious_probe",
        scenario_output=overlay_probe,
        overlay_refs=("prefer_cautious_probe",),
    ) == (
        ("cautious_probe", 10, "aligned"),
        ("observe_only", 80, "fallback"),
    )
    assert build_selection_trace(
        scenario_output=overlay_probe,
        primary_tactic_key="cautious_probe",
        overlay_refs=("prefer_cautious_probe",),
    ) == {
        "trace_type": "tactic_selection_trace",
        "primary_tactic_key": "cautious_probe",
        "scenario_present": True,
        "profile_kind": None,
        "overlay_refs": ("prefer_cautious_probe",),
        "selection_bias_tags": ("overlay:prefer_cautious_probe",),
        "scenario_switch_hint": "hold_primary",
        "scenario_regime": "continuation",
        "current_caution_level": "low",
        "invalidation_state": "stable",
    }

    defensive_profile = PredictionScenarioOutput(
        current_regime_state="continuation",
        current_caution_level="medium",
        current_confidence=0.48,
        invalidation_state="caution_increase",
        scenario_switch_hint="hold_primary",
    )
    assert (
        resolve_primary_tactic_key(
            defensive_profile,
            profile_kind="defensive",
        )
        == "defensive_reduce_risk"
    )
    assert build_candidate_plan(
        primary_tactic_key="defensive_reduce_risk",
        scenario_output=defensive_profile,
        profile_kind="defensive",
    ) == (
        ("defensive_reduce_risk", 10, "aligned"),
        ("observe_only", 80, "fallback"),
    )
    assert build_selection_trace(
        scenario_output=defensive_profile,
        primary_tactic_key="defensive_reduce_risk",
        profile_kind="defensive",
        overlay_refs=("prefer_cautious_probe",),
    ) == {
        "trace_type": "tactic_selection_trace",
        "primary_tactic_key": "defensive_reduce_risk",
        "scenario_present": True,
        "profile_kind": "defensive",
        "overlay_refs": ("prefer_cautious_probe",),
        "selection_bias_tags": (
            "profile:defensive",
            "overlay:prefer_cautious_probe",
        ),
        "scenario_switch_hint": "hold_primary",
        "scenario_regime": "continuation",
        "current_caution_level": "medium",
        "invalidation_state": "caution_increase",
    }

    tighten_gate_overlay = PredictionScenarioOutput(
        current_regime_state="continuation",
        current_caution_level="medium",
        current_confidence=0.38,
        invalidation_state="stable",
        scenario_switch_hint="hold_primary",
    )
    assert (
        resolve_primary_tactic_key(
            tighten_gate_overlay,
            overlay_refs=("prefer_tighten_entry_gate",),
        )
        == "tighten_entry_gate"
    )
    assert build_candidate_plan(
        primary_tactic_key="tighten_entry_gate",
        scenario_output=tighten_gate_overlay,
        overlay_refs=("prefer_tighten_entry_gate",),
    ) == (
        ("tighten_entry_gate", 10, "aligned"),
        ("observe_only", 80, "fallback"),
    )

    continuation_overlay = PredictionScenarioOutput(
        current_regime_state="continuation",
        current_caution_level="low",
        current_confidence=0.61,
        invalidation_state="stable",
        scenario_switch_hint="hold_primary",
    )
    assert (
        resolve_primary_tactic_key(
            continuation_overlay,
            overlay_refs=("prefer_continuation_follow",),
        )
        == "continuation_follow"
    )
    assert build_candidate_plan(
        primary_tactic_key="continuation_follow",
        scenario_output=continuation_overlay,
        overlay_refs=("prefer_continuation_follow",),
    ) == (
        ("continuation_follow", 10, "aligned"),
        ("cautious_probe", 20, "supporting"),
        ("observe_only", 80, "fallback"),
    )
    assert build_candidate_plan(
        primary_tactic_key="observe_only",
        scenario_output=continuation_overlay,
        overlay_refs=("prefer_continuation_follow",),
    ) == (
        ("observe_only", 10, "aligned"),
        ("continuation_follow", 25, "overlay_support"),
    )
    assert build_candidate_plan(
        primary_tactic_key="observe_only",
        scenario_output=continuation_overlay,
        overlay_refs=(
            "prefer_tighten_entry_gate",
            "prefer_continuation_follow",
            "prefer_cautious_probe",
        ),
    ) == (
        ("observe_only", 10, "aligned"),
        ("tighten_entry_gate", 25, "overlay_support"),
        ("continuation_follow", 25, "overlay_support"),
        ("cautious_probe", 25, "overlay_support"),
    )

    blocked = None
    assert resolve_primary_tactic_key(blocked) == "maintain_no_trade"
    assert resolve_proposal_state("maintain_no_trade", blocked) == "blocked"
    assert build_candidate_plan(
        primary_tactic_key="maintain_no_trade",
        scenario_output=blocked,
    ) == (
        ("maintain_no_trade", 10, "aligned"),
    )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())