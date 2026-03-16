# path: ./btcts_next/src/btcts/collector_vnext/microstructure/absorption_detector.py
# desc: Detect absorption events using orderbook wall + trade flow.

from __future__ import annotations

from typing import Dict, List, Optional


def detect_absorption(
    signal: Dict,
    trade_metrics: Dict,
) -> Optional[Dict]:

    wall = signal.get("wall", {})
    pressure = signal.get("pressure", {})

    wall_detected = wall.get("wall_detected")
    wall_side = wall.get("strongest_side")

    buy_volume = trade_metrics.get("buy_volume", 0)
    sell_volume = trade_metrics.get("sell_volume", 0)
    delta = trade_metrics.get("trade_delta", 0)

    if not wall_detected:
        return None

    if wall_side == "ask" and delta > 5 and buy_volume > sell_volume:
        return {
            "event_name": "absorption_detected",
            "side": "ask",
            "delta": delta,
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "reason": "buy_pressure_absorbed_by_ask_wall",
        }

    if wall_side == "bid" and delta < -5 and sell_volume > buy_volume:
        return {
            "event_name": "absorption_detected",
            "side": "bid",
            "delta": delta,
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "reason": "sell_pressure_absorbed_by_bid_wall",
        }

    return None