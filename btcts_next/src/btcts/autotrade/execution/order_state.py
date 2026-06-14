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
    FILLED = "filled"
    CANCELED = "canceled"
    EXPIRED = "expired"
    REJECTED = "rejected"


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

    def accept(self, *, ts: str) -> "PaperOrder":
        if self.status != PaperOrderStatus.NEW:
            return self
        return replace(self, status=PaperOrderStatus.ACCEPTED, updated_at=ts)

    def fill(self, *, ts: str, fill_price: float | None = None) -> "PaperOrder":
        if self.status not in {PaperOrderStatus.NEW, PaperOrderStatus.ACCEPTED}:
            return self
        return replace(
            self,
            status=PaperOrderStatus.FILLED,
            updated_at=ts,
            filled_size=self.intent.size,
            fill_price=fill_price if fill_price is not None else self.intent.price,
        )

    def cancel(self, *, ts: str, reason: str) -> "PaperOrder":
        if self.status in {PaperOrderStatus.FILLED, PaperOrderStatus.CANCELED, PaperOrderStatus.EXPIRED, PaperOrderStatus.REJECTED}:
            return self
        return replace(self, status=PaperOrderStatus.CANCELED, updated_at=ts, cancel_reason=reason)

    def expire(self, *, ts: str) -> "PaperOrder":
        if self.status in {PaperOrderStatus.FILLED, PaperOrderStatus.CANCELED, PaperOrderStatus.EXPIRED, PaperOrderStatus.REJECTED}:
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
