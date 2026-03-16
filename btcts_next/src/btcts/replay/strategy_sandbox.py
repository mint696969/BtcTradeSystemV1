# path: ./btcts_next/src/btcts/replay/strategy_sandbox.py
# desc: Minimal replay strategy sandbox that simulates entries/exits on replay rows.

from __future__ import annotations

from typing import Dict, List, Optional

from .strategy_models import SandboxPosition, SandboxResult, SandboxTrade
from .strategy_rules import decide_entry, decide_exit


def _row_price(row: Dict) -> Optional[float]:
    tradeflow = row.get("tradeflow")
    if isinstance(tradeflow, dict):
        avg_price = tradeflow.get("avg_price")
        if avg_price is not None:
            return float(avg_price)

    result = row.get("result")
    if isinstance(result, dict):
        signal = result.get("signal")
        if isinstance(signal, dict):
            mid = signal.get("mid")
            if mid is not None:
                return float(mid)

        best_bid = result.get("best_bid")
        best_ask = result.get("best_ask")
        if best_bid is not None and best_ask is not None:
            return (float(best_bid) + float(best_ask)) / 2.0

    return None


def _close_trade(position: SandboxPosition, row: Dict, exit_reason: str) -> Optional[SandboxTrade]:
    price = _row_price(row)
    if price is None:
        return None

    pnl = 0.0
    if position.side == "long":
        pnl = (price - position.entry_price) * position.size
    elif position.side == "short":
        pnl = (position.entry_price - price) * position.size

    return SandboxTrade(
        side=position.side,
        entry_ts=position.entry_ts,
        entry_price=position.entry_price,
        size=position.size,
        reason=position.reason,
        exit_ts=str(row.get("event_ts") or ""),
        exit_price=price,
        exit_reason=exit_reason,
        pnl=pnl,
    )


def _call_strategy_fn(strategy_fn, row: Dict, position, strategy_context: Optional[Dict]):
    if strategy_context is not None:
        try:
            return strategy_fn(row, position, strategy_context)
        except TypeError:
            pass

    return strategy_fn(row, position)


def run_strategy_sandbox(
    name: str,
    rows: List[Dict],
    *,
    size: float = 1.0,
    strategy_fn=None,
    strategy_context: Optional[Dict] = None,
) -> SandboxResult:
    result = SandboxResult(name=name)
    position: Optional[SandboxPosition] = None

    for row in rows:
        event_ts = str(row.get("event_ts") or "")
        price = _row_price(row)

        if position is None:
            if strategy_fn is None:
                decision = decide_entry(row)
            else:
                decision = _call_strategy_fn(strategy_fn, row, None, strategy_context)

            if decision is None or price is None:
                continue

            action = decision.get("action")
            if action == "enter_long":
                position = SandboxPosition(
                    side="long",
                    entry_ts=event_ts,
                    entry_price=price,
                    size=size,
                    reason=str(decision.get("reason") or "enter_long"),
                )
            elif action == "enter_short":
                position = SandboxPosition(
                    side="short",
                    entry_ts=event_ts,
                    entry_price=price,
                    size=size,
                    reason=str(decision.get("reason") or "enter_short"),
                )
            continue

        if strategy_fn is None:
            exit_decision = decide_exit(row, position.side)
        else:
            exit_decision = _call_strategy_fn(strategy_fn, row, position, strategy_context)

        if exit_decision is None:
            continue

        trade = _close_trade(position, row, str(exit_decision.get("reason") or "exit"))
        if trade is not None:
            result.trades.append(trade)
            position = None

    return result