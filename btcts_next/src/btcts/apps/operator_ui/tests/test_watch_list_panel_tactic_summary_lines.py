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
        ),
    }

    empty = _normalize_watch_item({})
    assert empty == {
        "ts": None,
        "regime": None,
        "action": None,
        "risk": None,
        "tactic_summary_lines": (),
    }

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())