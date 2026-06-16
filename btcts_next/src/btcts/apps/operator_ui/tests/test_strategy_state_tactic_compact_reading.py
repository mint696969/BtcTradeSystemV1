# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_strategy_state_tactic_compact_reading.py
# desc: Verify strategy_state_panel exposes a compact tactic reading line.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.ai_operator_tactic_presenter import (  # noqa: E402
    build_tactic_compact_reading_line,
)


def main() -> int:
    line = build_tactic_compact_reading_line(
        {
            "primary_tactic_key": "cautious_probe",
            "tactic_primary_summary_line": (
                "cautious_probe | "
                "candidate_vs_baseline | "
                "overlay_support_only | "
                "current set is being compared as a candidate relative to baseline | "
                "review_only"
            ),
            "primary_tactic_interpretation_line": (
                "current set is being compared as a candidate relative to baseline"
            ),
        }
    )
    assert line == (
        "tactic_reading=cautious_probe | "
        "candidate_vs_baseline | "
        "overlay_support_only | "
        "current set is being compared as a candidate relative to baseline | "
        "review_only"
    )

    fallback = build_tactic_compact_reading_line(
        {
            "primary_tactic_key": "reversal_prepare",
            "primary_tactic_interpretation_line": (
                "current set is being compared as a candidate relative to baseline"
            ),
        }
    )
    assert fallback == (
        "tactic_reading=reversal_prepare / "
        "current set is being compared as a candidate relative to baseline"
    )

    minimal = build_tactic_compact_reading_line(
        {
            "primary_tactic_key": "maintain_no_trade",
        }
    )
    assert minimal == "tactic_reading=maintain_no_trade"

    empty = build_tactic_compact_reading_line(None)
    assert empty == "tactic_reading unavailable"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())