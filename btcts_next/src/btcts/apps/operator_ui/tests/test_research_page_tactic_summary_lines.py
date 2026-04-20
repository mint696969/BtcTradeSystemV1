# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_research_page_tactic_summary_lines.py
# desc: Verify research_page can read ordered tactic summary lines from replay context.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.views.research_page import (  # noqa: E402
    _replay_context_tactic_summary_lines,
)


def main() -> int:
    replay_ctx = {
        "session_name": "watch_list",
        "tactic_summary_lines": (
            "operating_stance=reversal_prepare",
            "scenario_regime=reversal_watch",
            "proposal_state=proposed",
        ),
    }
    assert _replay_context_tactic_summary_lines(replay_ctx) == (
        "operating_stance=reversal_prepare",
        "scenario_regime=reversal_watch",
        "proposal_state=proposed",
    )

    assert _replay_context_tactic_summary_lines(None) == ()
    assert _replay_context_tactic_summary_lines({}) == ()

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())