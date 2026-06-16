# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_tactic_primary_review_display_lines.py
# desc: Verify primary tactic review display lines are aligned across UI consumers.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.ai_operator_tactic_presenter import (  # noqa: E402
    build_tactic_primary_review_display_lines,
)


def main() -> int:
    lines = build_tactic_primary_review_display_lines(
        tactic_primary_summary_line=(
            "cautious_probe | candidate_vs_baseline | overlay_support_only | "
            "current set is being compared as a candidate relative to baseline | "
            "review_only"
        ),
        primary_tactic_interpretation_line=(
            "current set is being compared as a candidate relative to baseline"
        ),
        lang="en",
    )
    assert lines == (
        "★ cautious_probe | candidate_vs_baseline | overlay_support_only | "
        "current set is being compared as a candidate relative to baseline | "
        "review_only",
        "★ Interpretation: current set is being compared as a candidate relative to baseline",
    )

    summary_only = build_tactic_primary_review_display_lines(
        tactic_primary_summary_line="maintain_no_trade | baseline_self_reference | review_only",
        primary_tactic_interpretation_line="",
        lang="en",
    )
    assert summary_only == (
        "★ maintain_no_trade | baseline_self_reference | review_only",
    )

    empty = build_tactic_primary_review_display_lines(
        tactic_primary_summary_line="",
        primary_tactic_interpretation_line="",
        lang="en",
    )
    assert empty == ()

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())