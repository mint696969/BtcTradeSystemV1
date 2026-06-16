# path: ./btcts_next/src/btcts/replay/regime_report.py
# desc: Build replay regime report for UI/research consumption.

from __future__ import annotations

from typing import Dict, List

from .regime_engine import detect_market_regime


def build_regime_report(rows: List[Dict]) -> Dict:
    regime = detect_market_regime(rows)

    return {
        "regime": regime.get("regime"),
        "reason": regime.get("reason"),
        "spread_state": regime.get("spread_state"),
        "pressure_state": regime.get("pressure_state"),
        "board_count": regime.get("board_count"),
        "avg_spread": regime.get("avg_spread"),
        "first_mid": regime.get("first_mid"),
        "last_mid": regime.get("last_mid"),
        "price_change": regime.get("price_change"),
        "price_change_pct": regime.get("price_change_pct"),
        "absorption_count": regime.get("absorption_count"),
        "sweep_count": regime.get("sweep_count"),
        "bias_counts": regime.get("bias_counts"),
        "event_name_counts": regime.get("event_name_counts"),
    }