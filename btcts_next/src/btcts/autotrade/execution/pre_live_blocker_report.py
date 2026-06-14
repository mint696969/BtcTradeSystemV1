# path: ./btcts_next/src/btcts/autotrade/execution/pre_live_blocker_report.py
# desc: SR-FX pre-live blocker report aggregator. Read-only; no broker calls/no mode changes.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Tuple


@dataclass(frozen=True)
class PreLiveBlockerSection:
    name: str
    ok: bool
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]
    summary: Dict[str, Any]
    read_only: bool = True
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SrFxPreLiveBlockerReport:
    ok: bool
    ready_for_live: bool
    product_code: str
    market_uid: str
    primary_blockers: Tuple[str, ...]
    warnings: Tuple[str, ...]
    sections: Dict[str, PreLiveBlockerSection]
    read_only: bool = True
    would_send_to_broker: bool = False
    mode_changed: bool = False
    contract_version: str = "sr_fx_pre_live_blocker_report.v1"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["sections"] = {name: section.to_dict() for name, section in self.sections.items()}
        return data


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _nested(payload: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    nested = payload.get(key)
    return nested if isinstance(nested, Mapping) else payload


def _bool_at(mapping: Mapping[str, Any], key: str, default: bool = False) -> bool:
    return bool(mapping.get(key, default))


def _list_at(mapping: Mapping[str, Any], key: str) -> list[str]:
    raw = mapping.get(key)
    if isinstance(raw, (list, tuple)):
        return [str(x) for x in raw]
    return []


def _unique(items: list[str]) -> Tuple[str, ...]:
    return tuple(dict.fromkeys(x for x in items if x))


def _section(
    *,
    name: str,
    ok: bool,
    blocked_by: list[str],
    warnings: list[str],
    summary: Dict[str, Any],
    read_only: bool = True,
    would_send_to_broker: bool = False,
) -> PreLiveBlockerSection:
    if would_send_to_broker:
        blocked_by.append("unexpected_broker_send_signal")
    if not read_only:
        blocked_by.append("section_not_read_only")
    return PreLiveBlockerSection(
        name=name,
        ok=bool(ok) and not blocked_by,
        blocked_by=_unique(blocked_by),
        warnings=_unique(warnings),
        summary=summary,
        read_only=bool(read_only),
        would_send_to_broker=bool(would_send_to_broker),
    )


def build_sr_fx_pre_live_blocker_report(
    *,
    public_market_readiness: Mapping[str, Any],
    private_readiness: Mapping[str, Any],
    live_readiness_contract: Mapping[str, Any],
    autotrade_readiness: Mapping[str, Any],
) -> SrFxPreLiveBlockerReport:
    public_market = _nested(_as_mapping(public_market_readiness), "public_market_readiness")
    private_state = _nested(_as_mapping(private_readiness), "readiness")
    live_contract = _nested(_as_mapping(live_readiness_contract), "live_readiness_contract")
    autotrade = _nested(_as_mapping(autotrade_readiness), "readiness")

    product_code = str(
        public_market.get("product_code")
        or private_state.get("product_code")
        or live_contract.get("product_code")
        or ""
    )
    market_uid = str(
        public_market.get("market_uid")
        or private_state.get("market_uid")
        or live_contract.get("market_uid")
        or ""
    )

    sections: Dict[str, PreLiveBlockerSection] = {}

    sections["public_market"] = _section(
        name="public_market",
        ok=_bool_at(public_market, "ok"),
        blocked_by=_list_at(public_market, "blocked_by"),
        warnings=_list_at(public_market, "warnings"),
        summary={
            "product_code": public_market.get("product_code"),
            "market_uid": public_market.get("market_uid"),
            "rest_market_ok": _bool_at(public_market, "rest_market_ok"),
            "ws_market_ok": _bool_at(public_market, "ws_market_ok"),
            "require_ws_ok": _bool_at(public_market, "require_ws_ok", True),
            "contract_version": public_market.get("contract_version"),
        },
        read_only=_bool_at(public_market, "read_only", True),
        would_send_to_broker=_bool_at(public_market, "would_send_to_broker"),
    )

    private_blockers: list[str] = []
    if not _bool_at(private_state, "private_state_known_and_fresh"):
        private_blockers.append("private_state_not_fresh")
    if not _bool_at(private_state, "account_clear_for_new_auto_entry"):
        private_blockers.append("account_not_clear_for_new_auto_entry")
    if _bool_at(private_state, "order_send_allowed"):
        private_blockers.append("private_readiness_unexpected_order_send_allowed")
    private_warnings: list[str] = []
    if _bool_at(private_state, "existing_positions_detected"):
        private_warnings.append("existing_positions_detected")
    if _bool_at(private_state, "existing_open_orders_detected"):
        private_warnings.append("existing_open_orders_detected")
    sections["private_account"] = _section(
        name="private_account",
        ok=not private_blockers,
        blocked_by=private_blockers,
        warnings=private_warnings,
        summary={
            "product_code": private_state.get("product_code"),
            "market_uid": private_state.get("market_uid"),
            "private_state_known_and_fresh": _bool_at(private_state, "private_state_known_and_fresh"),
            "account_clear_for_new_auto_entry": _bool_at(private_state, "account_clear_for_new_auto_entry"),
            "existing_positions_detected": _bool_at(private_state, "existing_positions_detected"),
            "existing_open_orders_detected": _bool_at(private_state, "existing_open_orders_detected"),
            "order_send_allowed": _bool_at(private_state, "order_send_allowed"),
            "reason": private_state.get("reason"),
        },
        read_only=True,
        would_send_to_broker=False,
    )

    sections["live_contract"] = _section(
        name="live_contract",
        ok=_bool_at(live_contract, "ready"),
        blocked_by=_list_at(live_contract, "blocked_by"),
        warnings=_list_at(live_contract, "warnings"),
        summary={
            "ready": _bool_at(live_contract, "ready"),
            "public_market_ok": _bool_at(live_contract, "public_market_ok"),
            "private_state_known_and_fresh": _bool_at(live_contract, "private_state_known_and_fresh"),
            "account_clear_for_new_auto_entry": _bool_at(live_contract, "account_clear_for_new_auto_entry"),
            "reconciliation_ok": _bool_at(live_contract, "reconciliation_ok"),
            "preview_ok": _bool_at(live_contract, "preview_ok"),
            "bitflyer_order_send_enabled": _bool_at(live_contract, "bitflyer_order_send_enabled"),
            "autotrade_live_order_enabled": _bool_at(live_contract, "autotrade_live_order_enabled"),
            "order_sender_implemented": _bool_at(live_contract, "order_sender_implemented"),
            "contract_version": live_contract.get("contract_version"),
        },
        read_only=_bool_at(live_contract, "read_only", True),
        would_send_to_broker=_bool_at(live_contract, "would_send_to_broker"),
    )

    sections["autotrade_readiness"] = _section(
        name="autotrade_readiness",
        ok=_bool_at(autotrade, "ready"),
        blocked_by=_list_at(autotrade, "blocked_by"),
        warnings=_list_at(autotrade, "warnings"),
        summary={
            "ready": _bool_at(autotrade, "ready"),
            "current_mode": autotrade.get("current_mode"),
            "target_mode": autotrade.get("target_mode"),
            "transition_allowed": _bool_at(autotrade, "transition_allowed"),
            "human_confirmation_required": _bool_at(autotrade, "human_confirmation_required"),
            "human_confirmed": _bool_at(autotrade, "human_confirmed"),
            "sr_fx_live_readiness_present": bool(_as_mapping(autotrade.get("sr_fx_live_readiness")).get("present")),
        },
        read_only=_bool_at(autotrade, "read_only", True),
        would_send_to_broker=_bool_at(autotrade, "would_send_to_broker"),
    )

    primary: list[str] = []
    warnings: list[str] = []
    read_only = True
    would_send = False
    for section in sections.values():
        primary.extend(section.blocked_by)
        warnings.extend(section.warnings)
        read_only = read_only and section.read_only
        would_send = would_send or section.would_send_to_broker

    if product_code != "FX_BTC_JPY":
        primary.append("execution_product_code_mismatch")
    if market_uid != "bitflyer.fx.FX_BTC_JPY":
        primary.append("execution_market_uid_mismatch")
    if would_send:
        primary.append("unexpected_broker_send_signal")
    if not read_only:
        primary.append("report_not_read_only")

    primary_tuple = _unique(primary)
    return SrFxPreLiveBlockerReport(
        ok=not primary_tuple,
        ready_for_live=not primary_tuple,
        product_code=product_code,
        market_uid=market_uid,
        primary_blockers=primary_tuple,
        warnings=_unique(warnings),
        sections=sections,
        read_only=read_only,
        would_send_to_broker=would_send,
        mode_changed=False,
    )
