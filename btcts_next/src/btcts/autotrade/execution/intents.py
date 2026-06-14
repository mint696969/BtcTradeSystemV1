# path: ./btcts_next/src/btcts/autotrade/execution/intents.py
# desc: AutoTrade order intent contracts. No broker execution here.

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Tuple


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"


@dataclass(frozen=True)
class OrderIntent:
    intent_id: str
    decision_id: str
    snapshot_id: str
    forecast_id: str | None
    parameter_set_id: str
    logic_version: str
    side: OrderSide
    order_type: OrderType
    size: float
    price: float | None
    reason_codes: Tuple[str, ...]
    risk_gate_allowed: bool
    mode: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["side"] = self.side.value
        data["order_type"] = self.order_type.value
        return data


def build_order_intent_from_decision(
    *,
    decision_id: str,
    snapshot_id: str,
    forecast_id: str | None,
    parameter_set_id: str,
    logic_version: str,
    side: str,
    size: float,
    price: float | None,
    reason_codes: Tuple[str, ...],
    risk_gate_allowed: bool,
    mode: str,
    order_type: OrderType = OrderType.LIMIT,
) -> OrderIntent:
    side_norm = OrderSide.BUY if side == "buy" else OrderSide.SELL
    return OrderIntent(
        intent_id=f"intent_{decision_id}",
        decision_id=decision_id,
        snapshot_id=snapshot_id,
        forecast_id=forecast_id,
        parameter_set_id=parameter_set_id,
        logic_version=logic_version,
        side=side_norm,
        order_type=order_type,
        size=float(size),
        price=price,
        reason_codes=reason_codes,
        risk_gate_allowed=bool(risk_gate_allowed),
        mode=mode,
    )
