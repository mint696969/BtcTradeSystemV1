# path: ./btcts_next/src/btcts/market_engine/market_state/orderbook_semantics_contract.py
# desc: Canonical outward contract helpers for live orderbook semantics summary.

from __future__ import annotations

from typing import Any


def empty_orderbook_semantics_summary() -> dict[str, Any]:
    return {
        "near_wall": None,
        "support": None,
        "resistance": None,
        "persistence": None,
    }