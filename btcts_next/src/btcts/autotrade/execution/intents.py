# path: ./btcts_next/src/btcts/autotrade/execution/intents.py
# desc: AutoTrade order intent contracts. No broker execution here.

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
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
    exchange: str | None = None
    product_code: str | None = None
    market_type: str | None = None
    market_uid: str | None = None
    market_role: str | None = None

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
    exchange: str | None = None,
    product_code: str | None = None,
    market_type: str | None = None,
    market_uid: str | None = None,
    market_role: str | None = None,
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
        exchange=exchange,
        product_code=product_code,
        market_type=market_type,
        market_uid=market_uid,
        market_role=market_role,
    )


def attach_execution_market(
    intent: OrderIntent,
    *,
    exchange: str,
    product_code: str,
    market_type: str,
    market_uid: str,
    market_role: str = "execution",
) -> OrderIntent:
    return replace(
        intent,
        exchange=exchange,
        product_code=product_code,
        market_type=market_type,
        market_uid=market_uid,
        market_role=market_role,
    )


def validate_fx_execution_market_intent(
    intent: OrderIntent,
    *,
    required_exchange: str = "bitflyer",
    required_product_code: str = "FX_BTC_JPY",
    required_market_type: str = "fx",
    required_market_uid: str = "bitflyer.fx.FX_BTC_JPY",
) -> Tuple[str, ...]:
    blocked: list[str] = []

    if (intent.exchange or "").lower() != required_exchange.lower():
        blocked.append("execution_exchange_mismatch")
    if intent.product_code != required_product_code:
        blocked.append("execution_product_code_mismatch")
    if (intent.market_type or "").lower() != required_market_type.lower():
        blocked.append("execution_market_type_mismatch")
    if intent.market_uid != required_market_uid:
        blocked.append("execution_market_uid_mismatch")
    if (intent.market_role or "").lower() != "execution":
        blocked.append("execution_market_role_mismatch")
    if (intent.market_type or "").lower() == "spot" or ".spot." in str(intent.market_uid or "").lower():
        blocked.append("spot_identity_forbidden_for_execution")

    return tuple(dict.fromkeys(blocked))
