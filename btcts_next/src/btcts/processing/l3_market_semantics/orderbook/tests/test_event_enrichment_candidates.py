# path: ./btcts_next/src/btcts/processing/l3_market_semantics/orderbook/tests/test_event_enrichment_candidates.py
# desc: Behavior test for candidate event enrichment using richer wall/pull signals.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[5]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l3_market_semantics.orderbook.event_enrichment import candidate_events


def _signal_payload() -> dict:
    return {
        "pressure": {
            "bias": "buy_pressure",
        },
        "summary": {
            "imbalance": 0.35,
            "spread": 120.0,
        },
        "wall": {
            "wall_detected": True,
            "strongest_side": "ask",
            "strongest_is_near": True,
            "strongest_rank": 2,
            "near_wall_detected": True,
            "near_strongest_side": "ask",
            "near_strongest_rank": 2,
            "near_strongest_ratio": 0.41,
        },
        "bid_pull": {
            "detected": False,
            "pull_strength": "none",
            "near_removed_ratio": None,
        },
        "ask_pull": {
            "detected": True,
            "pull_strength": "strong",
            "near_removed_ratio": 0.42,
        },
    }


def main() -> int:
    payload = _signal_payload()
    events = candidate_events(payload)

    absorption = next(
        event for event in events if event.get("event_name") == "absorption_candidate"
    )
    assert absorption["side"] == "ask"
    assert absorption["reason"] == "buy_pressure_against_near_ask_wall"
    assert absorption["wall_is_near"] is True
    assert absorption["wall_rank"] == 2

    sweep = next(
        event for event in events if event.get("event_name") == "sweep_candidate"
    )
    assert sweep["side"] == "ask"
    assert sweep["reason"] == "strong_ask_liquidity_pulled_under_buy_pressure"
    assert sweep["pull_strength"] == "strong"
    assert sweep["near_removed_ratio"] == 0.42

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())