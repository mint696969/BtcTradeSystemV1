# path: ./btcts_next/src/btcts/autotrade/execution/order_preview.py
# desc: SR-FX manual/broker order preview builder. No network calls and no order send.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Tuple

from btcts.autotrade.execution.intents import OrderIntent, OrderType, validate_fx_execution_market_intent


@dataclass(frozen=True)
class BitflyerFxOrderRequestPreview:
    product_code: str
    child_order_type: str
    side: str
    size: float
    price: float | None
    minute_to_expire: int
    time_in_force: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OrderPreviewResult:
    ok: bool
    intent_id: str
    decision_id: str
    exchange: str
    product_code: str
    market_uid: str
    mode: str
    request_class: str
    broker_request_preview: BitflyerFxOrderRequestPreview | None
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]
    private_readiness_used: Dict[str, Any]
    would_send_to_broker: bool = False
    send_allowed: bool = False
    order_send_allowed: bool = False
    preview_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["broker_request_preview"] = (
            self.broker_request_preview.to_dict() if self.broker_request_preview is not None else None
        )
        return data


def _readiness_flag(readiness: Mapping[str, Any], name: str, default: bool = False) -> bool:
    value = readiness.get(name, default)
    return bool(value)


def _private_readiness_summary(readiness: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "product_code": readiness.get("product_code"),
        "market_uid": readiness.get("market_uid"),
        "private_state_known_and_fresh": _readiness_flag(readiness, "private_state_known_and_fresh"),
        "account_clear_for_new_auto_entry": _readiness_flag(readiness, "account_clear_for_new_auto_entry"),
        "existing_positions_detected": _readiness_flag(readiness, "existing_positions_detected"),
        "existing_open_orders_detected": _readiness_flag(readiness, "existing_open_orders_detected"),
        "order_send_allowed": _readiness_flag(readiness, "order_send_allowed"),
        "reason": readiness.get("reason"),
    }


def build_bitflyer_fx_order_request_preview(
    intent: OrderIntent,
    *,
    minute_to_expire: int = 1,
    time_in_force: str = "GTC",
) -> BitflyerFxOrderRequestPreview:
    child_order_type = "LIMIT" if intent.order_type == OrderType.LIMIT else "MARKET"
    return BitflyerFxOrderRequestPreview(
        product_code=str(intent.product_code or ""),
        child_order_type=child_order_type,
        side=intent.side.value.upper(),
        size=float(intent.size),
        price=float(intent.price) if intent.price is not None else None,
        minute_to_expire=int(minute_to_expire),
        time_in_force=str(time_in_force or "GTC"),
    )


def build_bitflyer_fx_manual_order_preview(
    intent: OrderIntent,
    *,
    private_readiness: Mapping[str, Any],
    require_account_clear_for_new_auto_entry: bool = True,
    minute_to_expire: int = 1,
    time_in_force: str = "GTC",
) -> OrderPreviewResult:
    blocked: list[str] = []
    warnings: list[str] = []

    blocked.extend(validate_fx_execution_market_intent(intent))

    if not intent.risk_gate_allowed:
        blocked.append("risk_gate_not_allowed")
    if float(intent.size or 0.0) <= 0.0:
        blocked.append("order_size_must_be_positive")
    if intent.order_type == OrderType.LIMIT and intent.price is None:
        blocked.append("limit_price_required")
    if intent.order_type == OrderType.MARKET:
        blocked.append("market_order_disabled_initially")

    private_state_known = _readiness_flag(private_readiness, "private_state_known_and_fresh")
    account_clear = _readiness_flag(private_readiness, "account_clear_for_new_auto_entry")
    if not private_state_known:
        blocked.append("private_state_not_fresh")
    if require_account_clear_for_new_auto_entry and not account_clear:
        blocked.append("account_not_clear_for_new_auto_entry")

    if _readiness_flag(private_readiness, "existing_positions_detected"):
        warnings.append("existing_positions_detected")
    if _readiness_flag(private_readiness, "existing_open_orders_detected"):
        warnings.append("existing_open_orders_detected")

    # S7 is preview-only. Even if all preview checks pass, sending remains disabled.
    warnings.append("preview_only_no_broker_send")
    warnings.append("order_send_disabled_until_later_stage")

    broker_preview = None if blocked else build_bitflyer_fx_order_request_preview(
        intent,
        minute_to_expire=minute_to_expire,
        time_in_force=time_in_force,
    )

    return OrderPreviewResult(
        ok=not blocked,
        intent_id=intent.intent_id,
        decision_id=intent.decision_id,
        exchange=str(intent.exchange or ""),
        product_code=str(intent.product_code or ""),
        market_uid=str(intent.market_uid or ""),
        mode=str(intent.mode),
        request_class="order_send",
        broker_request_preview=broker_preview,
        blocked_by=tuple(dict.fromkeys(blocked)),
        warnings=tuple(dict.fromkeys(warnings)),
        private_readiness_used=_private_readiness_summary(private_readiness),
        would_send_to_broker=False,
        send_allowed=False,
        order_send_allowed=False,
        preview_only=True,
    )
