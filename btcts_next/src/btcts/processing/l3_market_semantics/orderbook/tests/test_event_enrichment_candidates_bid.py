# path: ./btcts_next/src/btcts/processing/l3_market_semantics/orderbook/tests/test_event_enrichment_candidates_bid.py
# desc: Behavior test for bid-side candidate event enrichment using richer wall/pull signals.

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
            "bias": "sell_pressure",
        },
        "summary": {
            "imbalance": -0.31,
            "spread": 95.0,
        },
        "wall": {
            "wall_detected": True,
            "strongest_side": "bid",
            "strongest_is_near": True,
            "strongest_rank": 1,
            "near_wall_detected": True,
            "near_strongest_side": "bid",
            "near_strongest_rank": 1,
            "near_strongest_ratio": 0.44,
        },
        "bid_pull": {
            "detected": True,
            "pull_strength": "moderate",
            "near_removed_ratio": 0.36,
        },
        "ask_pull": {
            "detected": False,
            "pull_strength": "none",
            "near_removed_ratio": None,
        },
    }


def main() -> int:
    payload = _signal_payload()
    events = candidate_events(payload)

    absorption = next(
        event for event in events if event.get("event_name") == "absorption_candidate"
    )
    assert absorption["side"] == "bid"
    assert absorption["reason"] == "sell_pressure_against_near_bid_wall"
    assert absorption["wall_is_near"] is True
    assert absorption["wall_rank"] == 1

    sweep = next(
        event for event in events if event.get("event_name") == "sweep_candidate"
    )
    assert sweep["side"] == "bid"
    assert sweep["reason"] == "near_bid_liquidity_pulled_under_sell_pressure"
    assert sweep["pull_strength"] == "moderate"
    assert sweep["near_removed_ratio"] == 0.36

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())