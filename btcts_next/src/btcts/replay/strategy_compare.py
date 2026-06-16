# path: ./btcts_next/src/btcts/replay/strategy_compare.py
# desc: Compare multiple strategy sandbox runs.

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .regime_report import build_regime_report
from .strategy_report import build_strategy_report
from .strategy_sandbox import run_strategy_sandbox


@dataclass
class StrategyComparison:
    name: str
    reports: List[Dict]


def compare_strategies(
    strategies: Dict[str, callable],
    results: list,
    size: float = 1.0,
    regime_report: Optional[Dict] = None,
) -> StrategyComparison:
    reports = []

    if regime_report is None:
        regime_report = build_regime_report(results)

    for name, fn in strategies.items():
        sandbox = run_strategy_sandbox(
            name,
            results,
            size=size,
            strategy_fn=fn,
            strategy_context={
                "regime_report": regime_report,
            },
        )

        report = build_strategy_report(sandbox)

        reports.append(
            {
                "strategy": name,
                "regime": regime_report.get("regime"),
                "trade_count": report["trade_count"],
                "closed_trade_count": report["closed_trade_count"],
                "wins": report["win_count"],
                "losses": report["loss_count"],
                "total_pnl": report["total_pnl"],
                "avg_pnl": report["avg_pnl"],
            }
        )

    return StrategyComparison(
        name="strategy_comparison",
        reports=reports,
    )