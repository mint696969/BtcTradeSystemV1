# path: ./btcts_next/src/btcts/processing/l3_market_semantics/microstructure/sweep_detector.py
# desc: Detect liquidity sweep events using liquidity pull + aggressive trade flow.

from __future__ import annotations

from typing import Dict, Optional


def detect_sweep(
    signal: Dict,
    trade_metrics: Dict,
) -> Optional[Dict]:
    bid_pull = signal.get("bid_pull", {})
    ask_pull = signal.get("ask_pull", {})

    delta = trade_metrics.get("trade_delta", 0)
    buy_volume = trade_metrics.get("buy_volume", 0)
    sell_volume = trade_metrics.get("sell_volume", 0)

    if ask_pull.get("detected") and delta > 5:
        return {
            "event_name": "liquidity_sweep",
            "side": "ask",
            "delta": delta,
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "reason": "ask_liquidity_removed_under_buy_pressure",
        }

    if bid_pull.get("detected") and delta < -5:
        return {
            "event_name": "liquidity_sweep",
            "side": "bid",
            "delta": delta,
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "reason": "bid_liquidity_removed_under_sell_pressure",
        }

    return None