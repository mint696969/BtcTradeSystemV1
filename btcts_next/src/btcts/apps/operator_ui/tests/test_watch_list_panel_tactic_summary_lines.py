# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_watch_list_panel_tactic_summary_lines.py
# desc: Verify watch_list_panel keeps tactic_summary_lines when lowering watch items.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.watch_list_panel import (  # noqa: E402
    _normalize_watch_item,
)


def main() -> int:
    item = _normalize_watch_item(
        {
            "ts": "2026-04-20T12:01:00Z",
            "regime": "continuation",
            "action": "long_watch",
            "risk": "low",
            "tactic_summary_lines": (
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
            ),
            "tactic_interpretation_lines": (
                "current set is being compared as a candidate relative to baseline",
                "rollback review target is available: baseline-default",
                "current set is adoption-ready for review, not an automatic decision",
            ),
            "primary_tactic_interpretation_line": (
                "current set is being compared as a candidate relative to baseline"
            ),
            "tactic_primary_summary_line": (
                "continuation_follow | "
                "candidate_vs_baseline | "
                "current set is being compared as a candidate relative to baseline | "
                "review_only"
            ),
        }
    )
    assert item == {
        "ts": "2026-04-20T12:01:00Z",
        "regime": "continuation",
        "action": "long_watch",
        "risk": "low",
        "tactic_summary_lines": (
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
        ),
        "tactic_interpretation_lines": (
            "current set is being compared as a candidate relative to baseline",
            "rollback review target is available: baseline-default",
            "current set is adoption-ready for review, not an automatic decision",
        ),
        "primary_tactic_interpretation_line": (
            "current set is being compared as a candidate relative to baseline"
        ),
        "tactic_primary_summary_line": (
            "continuation_follow | "
            "candidate_vs_baseline | "
            "current set is being compared as a candidate relative to baseline | "
            "review_only"
        ),
    }

    empty = _normalize_watch_item({})
    assert empty == {
        "ts": None,
        "regime": None,
        "action": None,
        "risk": None,
        "tactic_summary_lines": (),
        "tactic_interpretation_lines": (),
        "primary_tactic_interpretation_line": "",
        "tactic_primary_summary_line": "",
    }

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())