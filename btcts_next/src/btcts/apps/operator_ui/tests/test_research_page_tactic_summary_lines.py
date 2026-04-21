# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_research_page_tactic_summary_lines.py
# desc: Verify research_page can read ordered tactic summary lines from replay context.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.views.research_page import (  # noqa: E402
    _replay_context_primary_tactic_interpretation_line,
    _replay_context_tactic_interpretation_lines,
    _replay_context_tactic_primary_summary_line,
    _replay_context_tactic_summary_lines,
)


def main() -> int:
    replay_ctx = {
        "session_name": "watch_list",
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
    assert _replay_context_tactic_summary_lines(replay_ctx) == (
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
    )
    assert _replay_context_tactic_interpretation_lines(replay_ctx) == (
        "current set is being compared as a candidate relative to baseline",
        "overlay influence is present, so the stance should be read as context-shaped",
        "rollback review target is available: baseline-default",
        "current set is adoption-ready for review, not an automatic decision",
    )
    assert _replay_context_primary_tactic_interpretation_line(replay_ctx) == (
        "overlay influence is present, so the stance should be read as context-shaped"
    )
    assert _replay_context_tactic_primary_summary_line(replay_ctx) == (
        "reversal_prepare | "
        "candidate_vs_baseline | "
        "overlay influence is present, so the stance should be read as context-shaped | "
        "review_only"
    )

    assert _replay_context_tactic_summary_lines(None) == ()
    assert _replay_context_tactic_interpretation_lines(None) == ()
    assert _replay_context_primary_tactic_interpretation_line(None) == ""
    assert _replay_context_tactic_primary_summary_line(None) == ""
    assert _replay_context_tactic_summary_lines({}) == ()
    assert _replay_context_tactic_interpretation_lines({}) == ()
    assert _replay_context_primary_tactic_interpretation_line({}) == ""
    assert _replay_context_tactic_primary_summary_line({}) == ""

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())