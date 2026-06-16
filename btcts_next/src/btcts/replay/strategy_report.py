# path: ./btcts_next/src/btcts/replay/strategy_report.py
# desc: Build summary metrics for replay strategy sandbox results.

from __future__ import annotations

from typing import Dict

from .strategy_models import SandboxResult


def build_strategy_report(result: SandboxResult) -> Dict:
    closed = result.closed_trades()

    total_pnl = sum(float(t.pnl or 0.0) for t in closed)
    win_count = sum(1 for t in closed if (t.pnl or 0.0) > 0)
    loss_count = sum(1 for t in closed if (t.pnl or 0.0) < 0)

    avg_pnl = None
    if closed:
        avg_pnl = total_pnl / len(closed)

    return {
        "name": result.name,
        "trade_count": len(result.trades),
        "closed_trade_count": len(closed),
        "win_count": win_count,
        "loss_count": loss_count,
        "total_pnl": total_pnl,
        "avg_pnl": avg_pnl,
    }