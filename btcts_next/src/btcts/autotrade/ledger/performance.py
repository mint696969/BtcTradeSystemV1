# path: ./btcts_next/src/btcts/autotrade/ledger/performance.py
# desc: AutoTrade expectancy-first performance ledger models and summaries.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, Tuple


@dataclass(frozen=True)
class DecisionOutcomeRecord:
    decision_id: str
    parameter_set_id: str
    logic_version: str
    action: str
    side: str | None
    base_ground_direction: str
    base_ground_confidence: str
    forecast_direction: str | None
    forecast_confidence: str | None
    strategy_profile: str
    entry_quality: int
    reason_codes: Tuple[str, ...]
    blocked_by: Tuple[str, ...]
    realized_pnl: float | None = None
    fees: float = 0.0
    slippage: float = 0.0
    hold_sec: float | None = None
    outcome_label: str = "unresolved"

    def cost_adjusted_pnl(self) -> float | None:
        if self.realized_pnl is None:
            return None
        return float(self.realized_pnl) - float(self.fees) - float(self.slippage)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["cost_adjusted_pnl"] = self.cost_adjusted_pnl()
        return data


@dataclass(frozen=True)
class PerformanceSummary:
    group_key: str
    decision_count: int
    resolved_trade_count: int
    win_count: int
    loss_count: int
    win_rate: float | None
    average_win: float | None
    average_loss: float | None
    profit_factor: float | None
    expectancy: float | None
    realized_pnl: float
    max_drawdown: float | None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def summarize_outcomes(records: Iterable[DecisionOutcomeRecord], *, group_key: str = "all") -> PerformanceSummary:
    rows = list(records)
    pnl_values = [r.cost_adjusted_pnl() for r in rows if r.cost_adjusted_pnl() is not None]
    wins = [p for p in pnl_values if p is not None and p > 0]
    losses = [p for p in pnl_values if p is not None and p < 0]
    resolved = len(pnl_values)

    win_rate = (len(wins) / resolved) if resolved else None
    avg_win = (sum(wins) / len(wins)) if wins else None
    avg_loss = (sum(losses) / len(losses)) if losses else None
    gross_win = sum(wins)
    gross_loss_abs = abs(sum(losses))
    profit_factor = (gross_win / gross_loss_abs) if gross_loss_abs > 0 else (None if gross_win == 0 else float("inf"))

    if resolved and avg_win is not None and avg_loss is not None:
        loss_rate = 1.0 - (win_rate or 0.0)
        expectancy = (win_rate or 0.0) * avg_win + loss_rate * avg_loss
    elif resolved:
        expectancy = sum(pnl_values) / resolved
    else:
        expectancy = None

    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for pnl in pnl_values:
        equity += pnl or 0.0
        peak = max(peak, equity)
        max_dd = min(max_dd, equity - peak)

    return PerformanceSummary(
        group_key=group_key,
        decision_count=len(rows),
        resolved_trade_count=resolved,
        win_count=len(wins),
        loss_count=len(losses),
        win_rate=win_rate,
        average_win=avg_win,
        average_loss=avg_loss,
        profit_factor=profit_factor,
        expectancy=expectancy,
        realized_pnl=sum(pnl_values),
        max_drawdown=max_dd if resolved else None,
    )


def group_by_parameter_set(records: Iterable[DecisionOutcomeRecord]) -> Dict[str, PerformanceSummary]:
    groups: dict[str, list[DecisionOutcomeRecord]] = {}
    for record in records:
        groups.setdefault(record.parameter_set_id, []).append(record)
    return {key: summarize_outcomes(value, group_key=f"parameter_set:{key}") for key, value in groups.items()}


def group_by_ground(records: Iterable[DecisionOutcomeRecord]) -> Dict[str, PerformanceSummary]:
    groups: dict[str, list[DecisionOutcomeRecord]] = {}
    for record in records:
        key = f"ground:{record.base_ground_direction}:{record.base_ground_confidence}"
        groups.setdefault(key, []).append(record)
    return {key: summarize_outcomes(value, group_key=key) for key, value in groups.items()}


def group_by_reason_code(records: Iterable[DecisionOutcomeRecord]) -> Dict[str, PerformanceSummary]:
    groups: dict[str, list[DecisionOutcomeRecord]] = {}
    for record in records:
        for reason in record.reason_codes or ("no_reason_code",):
            groups.setdefault(reason, []).append(record)
    return {key: summarize_outcomes(value, group_key=f"reason:{key}") for key, value in groups.items()}
