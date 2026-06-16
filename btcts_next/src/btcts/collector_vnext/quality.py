# path: ./btcts_next/src/btcts/collector_vnext/quality.py
# desc: Minimal quality flag helpers for Collector vNext.

from __future__ import annotations

from typing import Any, Dict, List


def flags_for_missing_exchange_ts(exchange_ts: str | None) -> List[str]:
    if exchange_ts:
        return []
    return ["missing_exchange_ts"]


def confidence_from_flags(flags: List[str]) -> float:
    if not flags:
        return 1.0
    if flags == ["missing_exchange_ts"]:
        return 0.95
    return 0.80


def validate_board_payload(payload: Dict[str, Any]) -> List[str]:
    flags: List[str] = []
    if not isinstance(payload, dict):
        return ["invalid_payload_type"]

    bids = payload.get("bids")
    asks = payload.get("asks")

    if not isinstance(bids, list):
        flags.append("invalid_bids")
    if not isinstance(asks, list):
        flags.append("invalid_asks")

    return flags