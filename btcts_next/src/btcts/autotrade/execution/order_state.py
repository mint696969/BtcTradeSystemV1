# path: ./btcts_next/src/btcts/autotrade/execution/order_state.py
# desc: AutoTrade paper/replay order state contracts. No broker client here.

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from enum import Enum
from typing import Any, Dict

from .intents import OrderIntent


class PaperOrderStatus(str, Enum):
    NEW = "new"
    ACCEPTED = "accepted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    EXPIRED = "expired"
    REJECTED = "rejected"


TERMINAL_PAPER_ORDER_STATUSES = frozenset(
    {
        PaperOrderStatus.FILLED,
        PaperOrderStatus.CANCELED,
        PaperOrderStatus.EXPIRED,
        PaperOrderStatus.REJECTED,
    }
)


@dataclass(frozen=True)
class PaperOrder:
    order_id: str
    intent: OrderIntent
    status: PaperOrderStatus
    created_at: str
    updated_at: str
    filled_size: float = 0.0
    fill_price: float | None = None
    cancel_reason: str | None = None
    reject_reason: str | None = None

    @property
    def remaining_size(self) -> float:
        return max(float(self.intent.size) - float(self.filled_size), 0.0)

    def accept(self, *, ts: str) -> "PaperOrder":
        if self.status != PaperOrderStatus.NEW:
            return self
        return replace(self, status=PaperOrderStatus.ACCEPTED, updated_at=ts)

    def partial_fill(self, *, ts: str, fill_size: float, fill_price: float | None = None) -> "PaperOrder":
        if self.status in TERMINAL_PAPER_ORDER_STATUSES:
            return self
        if self.status not in {PaperOrderStatus.NEW, PaperOrderStatus.ACCEPTED, PaperOrderStatus.PARTIALLY_FILLED}:
            return self

        fill_qty = max(float(fill_size or 0.0), 0.0)
        if fill_qty <= 0.0:
            return self

        prev_filled = float(self.filled_size or 0.0)
        capped_new_fill = min(fill_qty, max(float(self.intent.size) - prev_filled, 0.0))
        new_filled = min(prev_filled + capped_new_fill, float(self.intent.size))
        if capped_new_fill <= 0.0:
            return self

        effective_price = fill_price if fill_price is not None else self.intent.price
        if effective_price is not None and self.fill_price is not None and new_filled > 0.0:
            avg_price = ((self.fill_price * prev_filled) + (float(effective_price) * capped_new_fill)) / new_filled
        elif effective_price is not None:
            avg_price = float(effective_price)
        else:
            avg_price = self.fill_price

        status = PaperOrderStatus.FILLED if new_filled >= float(self.intent.size) else PaperOrderStatus.PARTIALLY_FILLED
        return replace(
            self,
            status=status,
            updated_at=ts,
            filled_size=new_filled,
            fill_price=avg_price,
        )

    def fill(self, *, ts: str, fill_price: float | None = None) -> "PaperOrder":
        return self.partial_fill(ts=ts, fill_size=self.remaining_size, fill_price=fill_price)

    def cancel(self, *, ts: str, reason: str) -> "PaperOrder":
        if self.status in TERMINAL_PAPER_ORDER_STATUSES:
            return self
        return replace(self, status=PaperOrderStatus.CANCELED, updated_at=ts, cancel_reason=reason)

    def expire(self, *, ts: str) -> "PaperOrder":
        if self.status in TERMINAL_PAPER_ORDER_STATUSES:
            return self
        return replace(self, status=PaperOrderStatus.EXPIRED, updated_at=ts)

    def reject(self, *, ts: str, reason: str) -> "PaperOrder":
        if self.status != PaperOrderStatus.NEW:
            return self
        return replace(self, status=PaperOrderStatus.REJECTED, updated_at=ts, reject_reason=reason)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["intent"] = self.intent.to_dict()
        data["remaining_size"] = self.remaining_size
        return data


def paper_order_id_for_intent(intent: OrderIntent) -> str:
    return f"paper_order_{intent.intent_id.removeprefix('intent_')}"


def create_paper_order(intent: OrderIntent, *, ts: str) -> PaperOrder:
    return PaperOrder(
        order_id=paper_order_id_for_intent(intent),
        intent=intent,
        status=PaperOrderStatus.NEW,
        created_at=ts,
        updated_at=ts,
    )
