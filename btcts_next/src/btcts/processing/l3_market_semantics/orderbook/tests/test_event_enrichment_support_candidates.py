# path: ./btcts_next/src/btcts/processing/l3_market_semantics/orderbook/tests/test_event_enrichment_support_candidates.py
# desc: Behavior test for near-wall support / resistance candidates.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[5]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l3_market_semantics.orderbook.event_enrichment import candidate_events


def _bid_support_payload() -> dict:
    return {
        "pressure": {
            "bias": "buy_pressure",
        },
        "summary": {
            "imbalance": 0.29,
            "spread": 110.0,
        },
        "wall": {
            "wall_detected": True,
            "strongest_side": "bid",
            "strongest_is_near": False,
            "strongest_rank": 12,
            "near_wall_detected": True,
            "near_strongest_side": "bid",
            "near_strongest_rank": 5,
            "near_strongest_ratio": 0.28,
        },
        "bid_pull": {
            "detected": False,
            "pull_strength": "none",
            "near_removed_ratio": None,
        },
        "ask_pull": {
            "detected": False,
            "pull_strength": "none",
            "near_removed_ratio": None,
        },
    }


def _ask_resistance_payload() -> dict:
    return {
        "pressure": {
            "bias": "sell_pressure",
        },
        "summary": {
            "imbalance": -0.27,
            "spread": 105.0,
        },
        "wall": {
            "wall_detected": True,
            "strongest_side": "ask",
            "strongest_is_near": False,
            "strongest_rank": 14,
            "near_wall_detected": True,
            "near_strongest_side": "ask",
            "near_strongest_rank": 6,
            "near_strongest_ratio": 0.31,
        },
        "bid_pull": {
            "detected": False,
            "pull_strength": "none",
            "near_removed_ratio": None,
        },
        "ask_pull": {
            "detected": False,
            "pull_strength": "none",
            "near_removed_ratio": None,
        },
    }


def main() -> int:
    bid_events = candidate_events(_bid_support_payload())
    bid_support = next(
        event for event in bid_events if event.get("event_name") == "support_candidate"
    )
    assert bid_support["side"] == "bid"
    assert bid_support["reason"] == "buy_pressure_supported_by_near_bid_wall"
    assert bid_support["wall_scope"] == "near"
    assert bid_support["wall_is_near"] is True
    assert bid_support["wall_rank"] == 5

    ask_events = candidate_events(_ask_resistance_payload())
    ask_resistance = next(
        event for event in ask_events if event.get("event_name") == "resistance_candidate"
    )
    assert ask_resistance["side"] == "ask"
    assert ask_resistance["reason"] == "sell_pressure_resisted_by_near_ask_wall"
    assert ask_resistance["wall_scope"] == "near"
    assert ask_resistance["wall_is_near"] is True
    assert ask_resistance["wall_rank"] == 6

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())