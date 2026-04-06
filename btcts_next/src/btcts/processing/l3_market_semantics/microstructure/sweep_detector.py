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

    ask_near_ratio = ask_pull.get("near_removed_ratio")
    bid_near_ratio = bid_pull.get("near_removed_ratio")

    ask_pull_strength = str(ask_pull.get("pull_strength") or "none")
    bid_pull_strength = str(bid_pull.get("pull_strength") or "none")

    if ask_pull.get("detected") and delta > 5:
        reason = "ask_liquidity_removed_under_buy_pressure"
        if ask_pull_strength == "strong":
            reason = "strong_ask_liquidity_removed_under_buy_pressure"
        elif ask_near_ratio is not None and float(ask_near_ratio) >= 0.30:
            reason = "near_ask_liquidity_removed_under_buy_pressure"

        return {
            "event_name": "liquidity_sweep",
            "side": "ask",
            "delta": delta,
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "pull_strength": ask_pull_strength,
            "near_removed_ratio": ask_near_ratio,
            "best_price_changed": ask_pull.get("best_price_changed"),
            "reason": reason,
        }

    if bid_pull.get("detected") and delta < -5:
        reason = "bid_liquidity_removed_under_sell_pressure"
        if bid_pull_strength == "strong":
            reason = "strong_bid_liquidity_removed_under_sell_pressure"
        elif bid_near_ratio is not None and float(bid_near_ratio) >= 0.30:
            reason = "near_bid_liquidity_removed_under_sell_pressure"

        return {
            "event_name": "liquidity_sweep",
            "side": "bid",
            "delta": delta,
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "pull_strength": bid_pull_strength,
            "near_removed_ratio": bid_near_ratio,
            "best_price_changed": bid_pull.get("best_price_changed"),
            "reason": reason,
        }

    return None