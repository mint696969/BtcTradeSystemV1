# path: ./btcts_next/src/btcts/replay/experiment_engine.py
# desc: Run replay strategy experiment and determine the best strategy for a replay session.

from __future__ import annotations

from typing import Dict, List, Optional

from .regime_report import build_regime_report
from .strategy_compare import compare_strategies


def _pick_best_strategy(reports: List[Dict]) -> Optional[Dict]:
    if not reports:
        return None

    def sort_key(row: Dict):
        total_pnl = float(row.get("total_pnl") or 0.0)
        wins = int(row.get("wins") or 0)
        trade_count = int(row.get("trade_count") or 0)
        return (total_pnl, wins, trade_count)

    ordered = sorted(reports, key=sort_key, reverse=True)
    return ordered[0]


def run_strategy_experiment(
    *,
    name: str,
    rows: List[Dict],
    strategies: Dict[str, callable],
    size: float = 1.0,
) -> Dict:
    regime_report = build_regime_report(rows)
    comparison = compare_strategies(
        strategies,
        rows,
        size=size,
        regime_report=regime_report,
    )

    best_strategy = _pick_best_strategy(comparison.reports)

    return {
        "name": name,
        "regime_report": regime_report,
        "strategy_reports": comparison.reports,
        "best_strategy": best_strategy,
        "result_count": len(rows),
    }