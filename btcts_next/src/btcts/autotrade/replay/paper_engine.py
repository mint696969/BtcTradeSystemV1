# path: ./btcts_next/src/btcts/autotrade/replay/paper_engine.py
# desc: Paper/replay order lifecycle engine. Simulation only; no broker execution.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

from btcts.autotrade.execution.intents import OrderIntent
from btcts.autotrade.execution.order_state import PaperOrder, PaperOrderStatus, create_paper_order


@dataclass
class PaperExecutionEngine:
    orders_by_decision_id: Dict[str, PaperOrder] = field(default_factory=dict)

    def submit_intent(self, intent: OrderIntent, *, ts: str) -> PaperOrder:
        existing = self.orders_by_decision_id.get(intent.decision_id)
        if existing is not None:
            return existing
        order = create_paper_order(intent, ts=ts)
        if not intent.risk_gate_allowed:
            order = order.reject(ts=ts, reason="risk_gate_not_allowed")
        else:
            order = order.accept(ts=ts)
        self.orders_by_decision_id[intent.decision_id] = order
        return order

    def fill(self, decision_id: str, *, ts: str, fill_price: float | None = None) -> PaperOrder | None:
        order = self.orders_by_decision_id.get(decision_id)
        if order is None:
            return None
        order = order.fill(ts=ts, fill_price=fill_price)
        self.orders_by_decision_id[decision_id] = order
        return order

    def cancel(self, decision_id: str, *, ts: str, reason: str) -> PaperOrder | None:
        order = self.orders_by_decision_id.get(decision_id)
        if order is None:
            return None
        order = order.cancel(ts=ts, reason=reason)
        self.orders_by_decision_id[decision_id] = order
        return order

    def expire(self, decision_id: str, *, ts: str) -> PaperOrder | None:
        order = self.orders_by_decision_id.get(decision_id)
        if order is None:
            return None
        order = order.expire(ts=ts)
        self.orders_by_decision_id[decision_id] = order
        return order

    def status_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for order in self.orders_by_decision_id.values():
            counts[order.status.value] = counts.get(order.status.value, 0) + 1
        return counts

    def all_orders(self) -> Tuple[PaperOrder, ...]:
        return tuple(self.orders_by_decision_id.values())


def is_terminal_status(status: PaperOrderStatus) -> bool:
    return status in {
        PaperOrderStatus.FILLED,
        PaperOrderStatus.CANCELED,
        PaperOrderStatus.EXPIRED,
        PaperOrderStatus.REJECTED,
    }
