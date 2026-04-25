# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_summary_active_event_compact_reading.py
# desc: Verify market summary presenter exposes a compact active-event reading line.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.market_summary_presenter import (  # noqa: E402
    active_event_compact_reading_line,
)


def main() -> int:
    line = active_event_compact_reading_line(
        {
            "orderbook_active_event_contracts": [
                {
                    "event_name": "near_wall_continued",
                    "event_family": "wall",
                    "usage_grade": "strong",
                    "actionability": "review",
                    "forecast_horizon_hint": "short",
                    "half_life_sec": 30,
                    "side": "bid",
                },
                {
                    "event_name": "support_continued",
                    "event_family": "support_resistance",
                    "usage_grade": "watch",
                    "actionability": "review",
                    "forecast_horizon_hint": "short",
                    "half_life_sec": 30,
                    "side": "bid",
                },
            ]
        }
    )
    assert (
        line
        == "near_wall_continued (wall / strong / review / short / half_life=30 / bid) +1 more"
    )

    fallback = active_event_compact_reading_line(
        {
            "orderbook_active_event_names": [
                "near_wall_continued",
                "support_continued",
            ]
        }
    )
    assert fallback == "near_wall_continued +1 more"

    empty = active_event_compact_reading_line(None)
    assert empty == "active_event_reading unavailable"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())