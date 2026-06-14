# path: ./btcts_next/src/btcts/autotrade/execution/live_readiness_contract.py
# desc: SR-FX live readiness contract. Fail-closed; no broker calls and no order send.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Tuple

from btcts.autotrade.execution.order_preview import OrderPreviewResult
from btcts.autotrade.execution.reconciliation import FxReconciliationResult

LIVE_CAPABLE_MODES = frozenset({"LIVE_MIN_SIZE", "LIVE_CONTROLLED"})


@dataclass(frozen=True)
class FxLiveReadinessContractResult:
    ready: bool
    target_mode: str
    product_code: str
    market_uid: str
    public_market_ok: bool
    private_state_known_and_fresh: bool
    account_clear_for_new_auto_entry: bool
    reconciliation_ok: bool
    preview_ok: bool
    bitflyer_order_send_enabled: bool
    autotrade_live_order_enabled: bool
    order_sender_implemented: bool
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]
    public_market_readiness_used: Dict[str, Any] | None = None
    would_send_to_broker: bool = False
    read_only: bool = True
    contract_version: str = "sr_fx_live_readiness_contract.v1"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _bool_at(mapping: Mapping[str, Any], key: str, default: bool = False) -> bool:
    return bool(mapping.get(key, default))


def _public_market_summary(public_market_readiness: Mapping[str, Any] | None) -> Dict[str, Any] | None:
    if public_market_readiness is None:
        return None
    return {
        "ok": bool(public_market_readiness.get("ok", False)),
        "product_code": public_market_readiness.get("product_code"),
        "market_uid": public_market_readiness.get("market_uid"),
        "market_role": public_market_readiness.get("market_role"),
        "rest_market_ok": bool(public_market_readiness.get("rest_market_ok", False)),
        "ws_market_ok": bool(public_market_readiness.get("ws_market_ok", False)),
        "require_ws_ok": bool(public_market_readiness.get("require_ws_ok", True)),
        "blocked_by": list(public_market_readiness.get("blocked_by") or ()),
        "warnings": list(public_market_readiness.get("warnings") or ()),
        "would_send_to_broker": bool(public_market_readiness.get("would_send_to_broker", False)),
        "read_only": bool(public_market_readiness.get("read_only", True)),
        "contract_version": public_market_readiness.get("contract_version"),
    }


def evaluate_fx_live_readiness_contract(
    *,
    private_readiness: Mapping[str, Any],
    reconciliation: FxReconciliationResult,
    order_preview: OrderPreviewResult,
    public_market_readiness: Mapping[str, Any] | None = None,
    target_mode: str = "LIVE_MIN_SIZE",
    bitflyer_order_send_enabled: bool = False,
    autotrade_live_order_enabled: bool = False,
    order_sender_implemented: bool = False,
) -> FxLiveReadinessContractResult:
    blocked: list[str] = []
    warnings: list[str] = []

    target = str(target_mode or "").strip().upper()
    product_code = str(private_readiness.get("product_code") or "")
    market_uid = str(private_readiness.get("market_uid") or "")
    private_fresh = _bool_at(private_readiness, "private_state_known_and_fresh")
    account_clear = _bool_at(private_readiness, "account_clear_for_new_auto_entry")
    public_summary = _public_market_summary(public_market_readiness)
    public_ok = bool(public_summary and public_summary.get("ok"))

    if target not in LIVE_CAPABLE_MODES:
        blocked.append("target_mode_not_live_capable")
    if product_code != "FX_BTC_JPY":
        blocked.append("execution_product_code_mismatch")
    if market_uid != "bitflyer.fx.FX_BTC_JPY":
        blocked.append("execution_market_uid_mismatch")
    if public_summary is None:
        blocked.append("public_market_readiness_missing")
    elif not public_ok:
        blocked.append("public_market_not_ready")
        blocked.extend(str(x) for x in public_summary.get("blocked_by") or ())
    if public_summary is not None and public_summary.get("would_send_to_broker"):
        blocked.append("public_market_readiness_attempted_broker_send")
    if public_summary is not None:
        warnings.extend(str(x) for x in public_summary.get("warnings") or ())
    if not private_fresh:
        blocked.append("private_state_not_fresh")
    if not account_clear:
        blocked.append("account_not_clear_for_new_auto_entry")
    if not reconciliation.ok:
        blocked.append("reconciliation_not_clean")
        blocked.extend(reconciliation.blocked_by)
    if not order_preview.ok:
        blocked.append("order_preview_not_ok")
        blocked.extend(order_preview.blocked_by)
    if order_preview.would_send_to_broker:
        blocked.append("preview_attempted_broker_send")
    if not bitflyer_order_send_enabled:
        blocked.append("bitflyer_order_send_flag_disabled")
    if not autotrade_live_order_enabled:
        blocked.append("autotrade_live_order_flag_disabled")
    if not order_sender_implemented:
        blocked.append("order_sender_not_implemented")

    warnings.extend(reconciliation.warnings)
    warnings.extend(order_preview.warnings)
    warnings.append("live_readiness_contract_read_only")

    return FxLiveReadinessContractResult(
        ready=not blocked,
        target_mode=target,
        product_code=product_code,
        market_uid=market_uid,
        public_market_ok=public_ok,
        private_state_known_and_fresh=private_fresh,
        account_clear_for_new_auto_entry=account_clear,
        reconciliation_ok=bool(reconciliation.ok),
        preview_ok=bool(order_preview.ok),
        bitflyer_order_send_enabled=bool(bitflyer_order_send_enabled),
        autotrade_live_order_enabled=bool(autotrade_live_order_enabled),
        order_sender_implemented=bool(order_sender_implemented),
        blocked_by=tuple(dict.fromkeys(blocked)),
        warnings=tuple(dict.fromkeys(warnings)),
        public_market_readiness_used=public_summary,
        would_send_to_broker=False,
        read_only=True,
    )
