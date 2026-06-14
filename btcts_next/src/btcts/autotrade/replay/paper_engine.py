# path: ./btcts_next/src/btcts/autotrade/replay/paper_engine.py
# desc: Paper/replay order lifecycle engine. Simulation only; no broker execution.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

from btcts.autotrade.execution.intents import OrderIntent, validate_fx_execution_market_intent
from btcts.autotrade.execution.order_state import (
    PaperOrder,
    PaperOrderStatus,
    TERMINAL_PAPER_ORDER_STATUSES,
    create_paper_order,
)


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

    def submit_fx_execution_intent(
        self,
        intent: OrderIntent,
        *,
        ts: str,
        required_exchange: str = "bitflyer",
        required_product_code: str = "FX_BTC_JPY",
        required_market_type: str = "fx",
        required_market_uid: str = "bitflyer.fx.FX_BTC_JPY",
    ) -> PaperOrder:
        existing = self.orders_by_decision_id.get(intent.decision_id)
        if existing is not None:
            return existing

        blocked = validate_fx_execution_market_intent(
            intent,
            required_exchange=required_exchange,
            required_product_code=required_product_code,
            required_market_type=required_market_type,
            required_market_uid=required_market_uid,
        )
        if blocked:
            order = create_paper_order(intent, ts=ts).reject(ts=ts, reason=";".join(blocked))
            self.orders_by_decision_id[intent.decision_id] = order
            return order

        return self.submit_intent(intent, ts=ts)

    def partial_fill(
        self,
        decision_id: str,
        *,
        ts: str,
        fill_size: float,
        fill_price: float | None = None,
    ) -> PaperOrder | None:
        order = self.orders_by_decision_id.get(decision_id)
        if order is None:
            return None
        order = order.partial_fill(ts=ts, fill_size=fill_size, fill_price=fill_price)
        self.orders_by_decision_id[decision_id] = order
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
    return status in TERMINAL_PAPER_ORDER_STATUSES
