# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_ai_operator_support_contract.py
# desc: Verify ai_operator deterministic support contract stays advisory-only and structurally stable.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.ai_operator_support_contract import (  # noqa: E402
    build_operator_support_contract,
)


def main() -> int:
    state = {
        "spread": 1800.0,
        "imbalance": 0.35,
        "delta": 0.28,
        "wall_ratio": 0.31,
        "event_ts": "2026-04-17T01:40:00Z",
        "regime": "trend_up",
        "best_strategy": "microstructure_v2",
        "pressure_bias": "buy_pressure",
    }

    contract = build_operator_support_contract(
        state=state,
        runtime_source="external",
    )

    assert contract["action"] == "long_watch"
    assert contract["risk"] == "low"

    decision_row = contract["decision_row"]
    assert decision_row == {
        "ts": "2026-04-17T01:40:00Z",
        "regime": "trend_up",
        "spread_state": "tight",
        "imbalance_state": "bid_bias",
        "delta_state": "buy_flow",
        "wall_state": "bid_wall",
        "action": "long_watch",
        "risk": "low",
        "runtime_source": "external",
    }

    support_context = contract["support_context"]
    assert support_context == {
        "event_ts": "2026-04-17T01:40:00Z",
        "regime": "trend_up",
        "best_strategy": "microstructure_v2",
        "pressure_bias": "buy_pressure",
        "advisory_action": "long_watch",
        "advisory_risk": "low",
        "runtime_source": "external",
    }

    tactic_contract = build_operator_support_contract(
        state=state,
        runtime_source="external",
        tactic_context={
            "primary_tactic_key": "continuation_follow",
            "proposal_state": "proposed",
            "scenario_regime": "continuation",
            "rollback_ready": True,
            "review_needed": True,
            "diagnostics": {
                "adoption_ready": True,
                "rollback_target_available": True,
                "selected_set_id": "candidate-continuation-follow",
                "parameter_trace": {
                    "profile_kind": "candidate",
                    "rollback_target_ref": "baseline-default",
                    "comparison_relation": "candidate_vs_baseline",
                    "overlay_influence": "none",
                },
                "selection_trace": {
                    "selection_bias_tags": ("profile:candidate",)
                },
            },
        },
    )
    assert tactic_contract["support_context"]["tactic_context"] == {
        "primary_tactic_key": "continuation_follow",
        "proposal_state": "proposed",
        "scenario_regime": "continuation",
        "profile_kind": "candidate",
        "rollback_ready": True,
        "review_needed": True,
        "adoption_ready": True,
        "rollback_target_available": True,
        "selected_set_id": "candidate-continuation-follow",
        "rollback_target_ref": "baseline-default",
        "comparison_relation": "candidate_vs_baseline",
        "overlay_influence": "none",
        "selection_bias_tags": ("profile:candidate",),
    }
    assert tactic_contract["support_context"]["tactic_summary_lines"] == (
        "operating_stance=continuation_follow",
        "scenario_regime=continuation",
        "proposal_state=proposed",
        "profile_kind=candidate",
        "review_needed=true",
        "rollback_ready=true",
        "adoption_ready=true",
        "rollback_target_available=true",
        "selected_set_id=candidate-continuation-follow",
        "rollback_target_ref=baseline-default",
        "comparison_relation=candidate_vs_baseline",
        "selection_bias_tags=profile:candidate",
    )
    assert tactic_contract["support_context"]["tactic_interpretation_lines"] == (
        "current set is being compared as a candidate relative to baseline",
        "rollback review target is available: baseline-default",
        "current set is adoption-ready for review, not an automatic decision",
    )
    assert (
        tactic_contract["support_context"]["primary_tactic_interpretation_line"]
        == "current set is being compared as a candidate relative to baseline"
    )
    assert (
        tactic_contract["support_context"]["tactic_primary_summary_line"]
        == "continuation_follow | "
        "candidate_vs_baseline | "
        "current set is being compared as a candidate relative to baseline | "
        "review_only"
    )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())