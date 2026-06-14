# path: ./btcts_next/src/btcts/autotrade/execution/safety_harness.py
# desc: SR-FX execution safety harness scaffolding. Read-only; no broker calls/no order send.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Tuple

LIVE_CAPABLE_MODES = frozenset({"LIVE_MIN_SIZE", "LIVE_CONTROLLED"})


@dataclass(frozen=True)
class SrFxExecutionSafetyHarnessResult:
    ok: bool
    target_mode: str
    product_code: str
    market_uid: str
    public_market_ok: bool
    private_state_known_and_fresh: bool
    account_clear_for_new_auto_entry: bool
    live_readiness_ready: bool
    autotrade_readiness_ready: bool
    active_paper_order_count: int
    paper_position_size: float
    paper_position_side: str
    kill_switch_active: bool
    order_sender_implemented: bool
    bitflyer_order_send_enabled: bool
    autotrade_live_order_enabled: bool
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]
    read_only: bool = True
    would_send_to_broker: bool = False
    mode_changed: bool = False
    contract_version: str = "sr_fx_execution_safety_harness.v1"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _nested(payload: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    nested = payload.get(key)
    return nested if isinstance(nested, Mapping) else payload


def _bool_at(mapping: Mapping[str, Any], key: str, default: bool = False) -> bool:
    return bool(mapping.get(key, default))


def _int_at(mapping: Mapping[str, Any], key: str, default: int = 0) -> int:
    try:
        return max(int(mapping.get(key, default) or 0), 0)
    except Exception:
        return default


def _float_at(mapping: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float(mapping.get(key, default) or 0.0)
    except Exception:
        return default


def _list_at(mapping: Mapping[str, Any], key: str) -> list[str]:
    raw = mapping.get(key)
    if isinstance(raw, (list, tuple)):
        return [str(x) for x in raw if str(x)]
    return []


def _unique(items: list[str]) -> Tuple[str, ...]:
    return tuple(dict.fromkeys(x for x in items if x))


def evaluate_sr_fx_execution_safety_harness(
    *,
    public_market_readiness: Mapping[str, Any],
    private_readiness: Mapping[str, Any],
    live_readiness_contract: Mapping[str, Any],
    autotrade_readiness: Mapping[str, Any],
    target_mode: str = "LIVE_MIN_SIZE",
    kill_switch_active: bool = False,
    kill_switch_reason: str | None = None,
) -> SrFxExecutionSafetyHarnessResult:
    """Evaluate the final read-only SR-FX pre-live safety harness.

    This is scaffolding only: it never sends broker orders, never changes mode,
    and treats any would-send or non-read-only input as a hard blocker.
    """
    public_market = _nested(_as_mapping(public_market_readiness), "public_market_readiness")
    private_state = _nested(_as_mapping(private_readiness), "readiness")
    live_contract = _nested(_as_mapping(live_readiness_contract), "live_readiness_contract")
    autotrade = _nested(_as_mapping(autotrade_readiness), "readiness")

    target = str(target_mode or "").strip().upper()
    product_code = str(
        live_contract.get("product_code")
        or public_market.get("product_code")
        or private_state.get("product_code")
        or ""
    )
    market_uid = str(
        live_contract.get("market_uid")
        or public_market.get("market_uid")
        or private_state.get("market_uid")
        or ""
    )

    blocked: list[str] = []
    warnings: list[str] = []

    if target not in LIVE_CAPABLE_MODES:
        blocked.append("target_mode_not_live_capable")
    if product_code != "FX_BTC_JPY":
        blocked.append("execution_product_code_mismatch")
    if market_uid != "bitflyer.fx.FX_BTC_JPY":
        blocked.append("execution_market_uid_mismatch")

    public_ok = _bool_at(public_market, "ok")
    private_fresh = _bool_at(private_state, "private_state_known_and_fresh")
    account_clear = _bool_at(private_state, "account_clear_for_new_auto_entry")
    live_ready = _bool_at(live_contract, "ready")
    autotrade_ready = _bool_at(autotrade, "ready")

    if not public_ok:
        blocked.append("public_market_not_ready")
        blocked.extend(_list_at(public_market, "blocked_by"))
    if not private_fresh:
        blocked.append("private_state_not_fresh")
    if not account_clear:
        blocked.append("account_not_clear_for_new_auto_entry")
    if not live_ready:
        blocked.append("sr_fx_live_readiness_not_ready")
        blocked.extend(_list_at(live_contract, "blocked_by"))
    if not autotrade_ready:
        blocked.append("autotrade_readiness_not_ready")
        blocked.extend(_list_at(autotrade, "blocked_by"))

    active_paper_orders = _int_at(live_contract, "active_paper_order_count")
    paper_position_size = _float_at(live_contract, "paper_position_size")
    paper_position_side = str(live_contract.get("paper_position_side") or "flat")
    if active_paper_orders > 0:
        blocked.append("active_paper_orders_present")
    if abs(paper_position_size) > 0.0:
        blocked.append("paper_position_open")

    order_sender_implemented = _bool_at(live_contract, "order_sender_implemented")
    bitflyer_order_send_enabled = _bool_at(live_contract, "bitflyer_order_send_enabled")
    autotrade_live_order_enabled = _bool_at(live_contract, "autotrade_live_order_enabled")
    if not order_sender_implemented:
        blocked.append("order_sender_not_implemented")
    if not bitflyer_order_send_enabled:
        blocked.append("bitflyer_order_send_flag_disabled")
    if not autotrade_live_order_enabled:
        blocked.append("autotrade_live_order_flag_disabled")

    if kill_switch_active:
        blocked.append("kill_switch_active")
        if kill_switch_reason:
            warnings.append(f"kill_switch_reason:{kill_switch_reason}")

    for name, section in (
        ("public_market", public_market),
        ("private_account", private_state),
        ("live_contract", live_contract),
        ("autotrade_readiness", autotrade),
    ):
        if _bool_at(section, "would_send_to_broker"):
            blocked.append(f"{name}_attempted_broker_send")
        if not _bool_at(section, "read_only", True):
            blocked.append(f"{name}_not_read_only")
        warnings.extend(_list_at(section, "warnings"))

    warnings.append("execution_safety_harness_read_only")
    blocked_tuple = _unique(blocked)
    return SrFxExecutionSafetyHarnessResult(
        ok=not blocked_tuple,
        target_mode=target,
        product_code=product_code,
        market_uid=market_uid,
        public_market_ok=public_ok,
        private_state_known_and_fresh=private_fresh,
        account_clear_for_new_auto_entry=account_clear,
        live_readiness_ready=live_ready,
        autotrade_readiness_ready=autotrade_ready,
        active_paper_order_count=active_paper_orders,
        paper_position_size=paper_position_size,
        paper_position_side=paper_position_side,
        kill_switch_active=bool(kill_switch_active),
        order_sender_implemented=order_sender_implemented,
        bitflyer_order_send_enabled=bitflyer_order_send_enabled,
        autotrade_live_order_enabled=autotrade_live_order_enabled,
        blocked_by=blocked_tuple,
        warnings=_unique(warnings),
        read_only=True,
        would_send_to_broker=False,
        mode_changed=False,
    )
