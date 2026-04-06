# path: ./btcts_next/src/btcts/processing/l3_market_semantics/orderbook/tests/test_signal_events_near_wall_persistence.py
# desc: Behavior test for near-wall and support persistence events.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[5]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l3_market_semantics.orderbook.signal_events import build_signal_events


def _prev_signal() -> dict:
    return {
        "pressure": {"bias": "buy_pressure"},
        "summary": {"imbalance": 0.22, "spread": 100.0},
        "wall": {
            "wall_detected": True,
            "strongest_side": "bid",
            "strongest_rank": 10,
            "near_wall_detected": True,
            "near_strongest_side": "bid",
            "near_strongest_rank": 5,
            "near_strongest_ratio": 0.27,
        },
        "bid_pull": {"detected": False},
        "ask_pull": {"detected": False},
    }


def _curr_signal() -> dict:
    return {
        "pressure": {"bias": "buy_pressure"},
        "summary": {"imbalance": 0.24, "spread": 98.0},
        "wall": {
            "wall_detected": True,
            "strongest_side": "bid",
            "strongest_rank": 9,
            "near_wall_detected": True,
            "near_strongest_side": "bid",
            "near_strongest_rank": 4,
            "near_strongest_ratio": 0.29,
        },
        "bid_pull": {"detected": False},
        "ask_pull": {"detected": False},
    }


def main() -> int:
    events = build_signal_events(_prev_signal(), _curr_signal())

    names = [event.get("event_name") for event in events]
    assert "near_wall_continued" in names
    assert "support_continued" in names
    assert "resistance_continued" not in names

    near_wall = next(event for event in events if event.get("event_name") == "near_wall_continued")
    assert near_wall["side"] == "bid"

    support = next(event for event in events if event.get("event_name") == "support_continued")
    assert support["side"] == "bid"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())