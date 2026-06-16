# path: ./btcts_next/src/btcts/autotrade/execution/paper_intent.py
# desc: Build SR-FX paper order intents from read-only execution-market service inputs. No broker calls.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Tuple

from btcts.autotrade.execution.intents import (
    OrderIntent,
    OrderType,
    attach_execution_market,
    build_order_intent_from_decision,
    validate_fx_execution_market_intent,
)

REQUIRED_EXCHANGE = "bitflyer"
REQUIRED_PRODUCT_CODE = "FX_BTC_JPY"
REQUIRED_MARKET_TYPE = "fx"
REQUIRED_MARKET_UID = "bitflyer.fx.FX_BTC_JPY"
REQUIRED_SERVICE_INPUT_ROLE = "execution_market"
REQUIRED_MARKET_ROLE = "execution"
REQUIRED_CONTRACT_TYPE = "execution_market_service_input"


@dataclass(frozen=True)
class PaperOrderIntentBuildResult:
    ok: bool
    intent: OrderIntent | None
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]
    service_input_used: dict[str, Any]
    read_only: bool = True
    would_send_to_broker: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["intent"] = self.intent.to_dict() if self.intent is not None else None
        return data


def _str_at(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    return "" if value is None else str(value)


def _bool_at(mapping: Mapping[str, Any], key: str, default: bool = False) -> bool:
    value = mapping.get(key, default)
    return bool(value)


def _list_at(mapping: Mapping[str, Any], key: str) -> list[Any]:
    value = mapping.get(key)
    return list(value) if isinstance(value, (list, tuple)) else []


def validate_execution_market_service_input_for_paper(service_input: Mapping[str, Any]) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    blocked: list[str] = []
    warnings: list[str] = []

    if _str_at(service_input, "contract_type") != REQUIRED_CONTRACT_TYPE:
        blocked.append("service_input_contract_type_mismatch")
    if _str_at(service_input, "service_input_role") != REQUIRED_SERVICE_INPUT_ROLE:
        blocked.append("service_input_role_not_execution_market")
    if _str_at(service_input, "exchange") != REQUIRED_EXCHANGE:
        blocked.append("execution_exchange_mismatch")
    if _str_at(service_input, "symbol_raw") != REQUIRED_PRODUCT_CODE:
        blocked.append("execution_product_code_mismatch")
    if _str_at(service_input, "market_uid") != REQUIRED_MARKET_UID:
        blocked.append("execution_market_uid_mismatch")
    if ".spot." in _str_at(service_input, "market_uid").lower() or _str_at(service_input, "symbol_raw") == "BTC_JPY":
        blocked.append("spot_identity_forbidden_for_execution")

    if _str_at(service_input, "freshness") == "STALE" or _bool_at(service_input, "is_stale"):
        blocked.append("service_input_stale")
    if _str_at(service_input, "trust_state") not in {"", "trusted"}:
        blocked.append("service_input_not_trusted")
    if _str_at(service_input, "interpretation_bucket") not in {"", "allow_structural_use"}:
        blocked.append("service_input_not_structural_use")

    service_blockers = [str(item) for item in _list_at(service_input, "blocked_by") if str(item)]
    if service_blockers:
        blocked.append("service_input_has_blockers")
        blocked.extend(service_blockers)

    consumer_allowed = {str(item) for item in _list_at(service_input, "consumer_allowed")}
    if "autotrade" not in consumer_allowed:
        blocked.append("autotrade_not_allowed_consumer")

    if not _bool_at(service_input, "read_only", default=False):
        blocked.append("service_input_not_read_only")
    if _bool_at(service_input, "would_send_to_broker", default=False):
        blocked.append("service_input_would_send_to_broker")

    if _str_at(service_input, "continuity_state") == "rest_baseline_snapshot":
        warnings.append("paper_intent_from_rest_baseline_not_continuous_ws_series")
    for warning in _list_at(service_input, "warnings"):
        if str(warning):
            warnings.append(str(warning))

    return tuple(dict.fromkeys(blocked)), tuple(dict.fromkeys(warnings))


def build_fx_paper_order_intent_from_service_input(
    service_input: Mapping[str, Any],
    *,
    decision_id: str,
    snapshot_id: str,
    forecast_id: str | None,
    parameter_set_id: str,
    logic_version: str,
    side: str,
    size: float,
    price: float | None,
    reason_codes: Tuple[str, ...] = ("sr_fx_paper_order_intent",),
    risk_gate_allowed: bool = True,
    mode: str = "PAPER_OR_REPLAY",
    order_type: OrderType = OrderType.LIMIT,
) -> PaperOrderIntentBuildResult:
    blocked, warnings = validate_execution_market_service_input_for_paper(service_input)
    blocked_list = list(blocked)
    warning_list = list(warnings)

    side_norm = str(side or "").lower().strip()
    if side_norm not in {"buy", "sell"}:
        blocked_list.append("paper_intent_side_invalid")
        side_norm = "buy"
    try:
        size_f = float(size)
    except Exception:
        size_f = 0.0
    if size_f <= 0.0:
        blocked_list.append("paper_intent_size_must_be_positive")
    if order_type == OrderType.MARKET:
        blocked_list.append("market_order_disabled_initially")
    if order_type == OrderType.LIMIT and price is None:
        blocked_list.append("limit_price_required")
    if str(mode) != "PAPER_OR_REPLAY":
        blocked_list.append("paper_intent_mode_must_be_paper_or_replay")
    if not risk_gate_allowed:
        blocked_list.append("risk_gate_not_allowed")

    intent = attach_execution_market(
        build_order_intent_from_decision(
            decision_id=decision_id,
            snapshot_id=snapshot_id,
            forecast_id=forecast_id,
            parameter_set_id=parameter_set_id,
            logic_version=logic_version,
            side=side_norm,
            size=size_f,
            price=price,
            reason_codes=tuple(dict.fromkeys(tuple(reason_codes) + ("execution_market_service_input",))),
            risk_gate_allowed=bool(risk_gate_allowed),
            mode=str(mode),
            order_type=order_type,
        ),
        exchange=REQUIRED_EXCHANGE,
        product_code=REQUIRED_PRODUCT_CODE,
        market_type=REQUIRED_MARKET_TYPE,
        market_uid=REQUIRED_MARKET_UID,
        market_role=REQUIRED_MARKET_ROLE,
    )
    blocked_list.extend(validate_fx_execution_market_intent(intent))
    final_blocked = tuple(dict.fromkeys(blocked_list))

    return PaperOrderIntentBuildResult(
        ok=not final_blocked,
        intent=None if final_blocked else intent,
        blocked_by=final_blocked,
        warnings=tuple(dict.fromkeys(warning_list)),
        service_input_used=dict(service_input),
        read_only=True,
        would_send_to_broker=False,
    )
