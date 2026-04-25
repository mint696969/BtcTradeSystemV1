# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_ai_operator_action_payloads.py
# desc: Verify ai_operator support context can be lowered into research/watch payloads safely.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.ai_operator_action_payloads import (  # noqa: E402
    build_research_context_base,
    build_research_replay_context,
    build_watch_item,
    normalize_watch_item_payload,
)


def main() -> int:
    support_context = {
        "event_ts": "2026-04-17T01:45:00Z",
        "regime": "transition",
        "best_strategy": "scenario_prediction_core",
        "pressure_bias": "sell_pressure",
        "advisory_action": "trap_caution",
        "advisory_risk": "high",
        "runtime_source": "fallback-local",
        "tactic_summary_lines": (
            "operating_stance=reversal_prepare",
            "scenario_regime=reversal_watch",
            "proposal_state=proposed",
            "profile_kind=candidate",
            "review_needed=true",
            "rollback_ready=true",
            "adoption_ready=true",
            "rollback_target_available=true",
            "selected_set_id=candidate-reversal-watch",
            "rollback_target_ref=baseline-default",
            "comparison_relation=candidate_vs_baseline",
            "overlay_influence=overlay_bias",
        ),
        "tactic_interpretation_lines": (
            "current set is being compared as a candidate relative to baseline",
            "overlay influence is present, so the stance should be read as context-shaped",
            "rollback review target is available: baseline-default",
            "current set is adoption-ready for review, not an automatic decision",
        ),
        "primary_tactic_interpretation_line": (
            "overlay influence is present, so the stance should be read as context-shaped"
        ),
        "tactic_primary_summary_line": (
            "reversal_prepare | "
            "candidate_vs_baseline | "
            "overlay influence is present, so the stance should be read as context-shaped | "
            "review_only"
        ),
    }

    research_replay_context = build_research_replay_context(support_context)
    assert research_replay_context == {
        "session_name": "warroom_ai_operator",
        "start_ts": "",
        "end_ts": "",
        "jump_ts": "2026-04-17T01:45:00Z",
        "kind_filter": "all",
        "event_filter": "sell_pressure",
        "filtered_rows": 1,
        "tactic_summary_lines": (
            "operating_stance=reversal_prepare",
            "scenario_regime=reversal_watch",
            "proposal_state=proposed",
            "profile_kind=candidate",
            "review_needed=true",
            "rollback_ready=true",
            "adoption_ready=true",
            "rollback_target_available=true",
            "selected_set_id=candidate-reversal-watch",
            "rollback_target_ref=baseline-default",
            "comparison_relation=candidate_vs_baseline",
            "overlay_influence=overlay_bias",
        ),
        "tactic_interpretation_lines": (
            "current set is being compared as a candidate relative to baseline",
            "overlay influence is present, so the stance should be read as context-shaped",
            "rollback review target is available: baseline-default",
            "current set is adoption-ready for review, not an automatic decision",
        ),
        "primary_tactic_interpretation_line": (
            "overlay influence is present, so the stance should be read as context-shaped"
        ),
        "tactic_primary_summary_line": (
            "reversal_prepare | "
            "candidate_vs_baseline | "
            "overlay influence is present, so the stance should be read as context-shaped | "
            "review_only"
        ),
    }

    watch_item = build_watch_item(support_context)
    assert watch_item == {
        "ts": "2026-04-17T01:45:00Z",
        "regime": "transition",
        "action": "trap_caution",
        "risk": "high",
        "tactic_summary_lines": (
            "operating_stance=reversal_prepare",
            "scenario_regime=reversal_watch",
            "proposal_state=proposed",
            "profile_kind=candidate",
            "review_needed=true",
            "rollback_ready=true",
            "adoption_ready=true",
            "rollback_target_available=true",
            "selected_set_id=candidate-reversal-watch",
            "rollback_target_ref=baseline-default",
            "comparison_relation=candidate_vs_baseline",
            "overlay_influence=overlay_bias",
        ),
        "tactic_interpretation_lines": (
            "current set is being compared as a candidate relative to baseline",
            "overlay influence is present, so the stance should be read as context-shaped",
            "rollback review target is available: baseline-default",
            "current set is adoption-ready for review, not an automatic decision",
        ),
        "primary_tactic_interpretation_line": (
            "overlay influence is present, so the stance should be read as context-shaped"
        ),
        "tactic_primary_summary_line": (
            "reversal_prepare | "
            "candidate_vs_baseline | "
            "overlay influence is present, so the stance should be read as context-shaped | "
            "review_only"
        ),
    }

    assert build_research_context_base(
        session_name="watch_list",
        start_ts="",
        end_ts="",
        jump_ts="2026-04-23T10:00:00Z",
        kind_filter="all",
        event_filter="observe",
        filtered_rows=1,
    ) == {
        "session_name": "watch_list",
        "start_ts": "",
        "end_ts": "",
        "jump_ts": "2026-04-23T10:00:00Z",
        "kind_filter": "all",
        "event_filter": "observe",
        "filtered_rows": 1,
    }

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
