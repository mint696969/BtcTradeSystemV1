# path: ./btcts_next/src/btcts/collector_vnext/transforms/trade_structural_hints.py
# desc: Trade canonical payload に L2 structural metadata hints を付与する Collector runtime adapter helper。

from __future__ import annotations

from typing import Any, Dict


def _instrument_id(exchange: str, symbol: str) -> str:
    return f"{exchange}.spot.{symbol}"


def apply_trade_structural_hints(
    trade: Dict[str, Any],
    *,
    exchange: str,
    symbol: str,
    channel: str,
    provider: str,
    transport: str,
    transport_role: str,
    origin_role: str,
    collector_id: str,
    stream_session_id: str,
    seen_in_rest: bool,
    seen_in_ws: bool,
    description: str,
) -> Dict[str, Any]:
    """Attach structural integration/dedupe/completeness/origin hints.

    This helper belongs to the collector runtime adapter layer.
    It must not decide market meaning. L3 remains the semantic owner.
    """

    instrument_id = _instrument_id(exchange, symbol)
    trade_id = trade.get("trade_id")
    source_event_id = str(trade_id) if trade_id is not None else None

    trade["integration_hint"] = {
        "integration_domain": "trade_native_id",
        "transport_role": transport_role,
        "unified_key_hint": source_event_id,
        "dedupe_domain": "trade_native_id",
        "unified_view_policy": "event_dedupe_by_native_id",
    }

    trade["dedupe_hint"] = {
        "entity_kind": "trade",
        "unified_key": {
            "exchange": exchange,
            "instrument_id": instrument_id,
            "source_event_id": source_event_id,
        },
        "native_id_required": True,
        "fallback_key_enabled": False,
        "provenance_policy": {
            "seen_in_rest": bool(seen_in_rest),
            "seen_in_ws": bool(seen_in_ws),
        },
    }

    trade["completeness_hint"] = {
        "evaluation_unit": "trade_event",
        "completeness": "mostly_complete",
        "confidence_hint": "medium_high",
        "completeness_basis": {
            "exchange_present": True,
            "instrument_id_present": True,
            "source_event_id_present": trade_id is not None,
            "price_present": trade.get("price") is not None,
            "size_present": trade.get("size") is not None,
            "side_present": trade.get("side") is not None,
            "event_ts_present": trade.get("trade_ts") is not None,
            "seen_in_rest": bool(seen_in_rest),
            "seen_in_ws": bool(seen_in_ws),
        },
        "policy_note": "native trade id exists and core fields are present, but provenance is single-sided",
    }

    trade["origin_hint"] = {
        "source_layer": "collector",
        "provider": provider,
        "transport": transport,
        "endpoint_or_channel": channel,
        "origin_role": origin_role,
        "collector_id": collector_id,
        "stream_session_id": stream_session_id,
        "description": description,
    }

    return trade