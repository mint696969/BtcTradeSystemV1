# path: ./btcts_next/src/btcts/processing/l3_market_semantics/orderbook/signal_events.py
# desc: Compare consecutive liquidity signal payloads and emit market microstructure events.

from __future__ import annotations

from typing import Dict, List, Optional

from ..event_usage_policy import enrich_event_contracts
from .event_enrichment import (
    candidate_events,
    liquidity_depth_change_events,
    spread_change_events,
    wall_strength_events,
)


def _safe_get(payload: Optional[Dict], *path, default=None):
    cur = payload
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default

def _near_defense_state(signal: Optional[Dict]) -> tuple[Optional[str], Optional[str]]:
    near_wall_detected = bool(_safe_get(signal, "wall", "near_wall_detected", default=False))
    near_wall_side = _safe_get(signal, "wall", "near_strongest_side")
    pressure_bias = _safe_get(signal, "pressure", "bias")

    if near_wall_detected and near_wall_side == "bid" and pressure_bias == "buy_pressure":
        return "support", "bid"
    if near_wall_detected and near_wall_side == "ask" and pressure_bias == "sell_pressure":
        return "resistance", "ask"

    return None, None

def build_signal_events(prev_signal: Optional[Dict], curr_signal: Dict) -> List[Dict]:
    events: List[Dict] = []

    prev_pressure_bias = _safe_get(prev_signal, "pressure", "bias")
    curr_pressure_bias = _safe_get(curr_signal, "pressure", "bias")

    prev_imbalance = _safe_get(prev_signal, "summary", "imbalance")
    curr_imbalance = _safe_get(curr_signal, "summary", "imbalance")

    prev_wall_detected = bool(_safe_get(prev_signal, "wall", "wall_detected", default=False))
    curr_wall_detected = bool(_safe_get(curr_signal, "wall", "wall_detected", default=False))

    prev_wall_side = _safe_get(prev_signal, "wall", "strongest_side")
    curr_wall_side = _safe_get(curr_signal, "wall", "strongest_side")

    prev_near_wall_detected = bool(_safe_get(prev_signal, "wall", "near_wall_detected", default=False))
    curr_near_wall_detected = bool(_safe_get(curr_signal, "wall", "near_wall_detected", default=False))

    prev_near_wall_side = _safe_get(prev_signal, "wall", "near_strongest_side")
    curr_near_wall_side = _safe_get(curr_signal, "wall", "near_strongest_side")

    prev_defense_kind, prev_defense_side = _near_defense_state(prev_signal)
    curr_defense_kind, curr_defense_side = _near_defense_state(curr_signal)

    bid_pull_detected = bool(_safe_get(curr_signal, "bid_pull", "detected", default=False))
    ask_pull_detected = bool(_safe_get(curr_signal, "ask_pull", "detected", default=False))

    if prev_pressure_bias is not None and curr_pressure_bias is not None and prev_pressure_bias != curr_pressure_bias:
        events.append(
            {
                "event_name": "pressure_shift",
                "prev_bias": prev_pressure_bias,
                "curr_bias": curr_pressure_bias,
            }
        )

    if prev_imbalance is not None and curr_imbalance is not None:
        if prev_imbalance < 0 <= curr_imbalance:
            events.append(
                {
                    "event_name": "imbalance_flip_to_bid",
                    "prev_imbalance": prev_imbalance,
                    "curr_imbalance": curr_imbalance,
                }
            )
        elif prev_imbalance > 0 >= curr_imbalance:
            events.append(
                {
                    "event_name": "imbalance_flip_to_ask",
                    "prev_imbalance": prev_imbalance,
                    "curr_imbalance": curr_imbalance,
                }
            )

    if not prev_wall_detected and curr_wall_detected:
        events.append(
            {
                "event_name": "wall_created",
                "side": curr_wall_side,
            }
        )

    if prev_wall_detected and not curr_wall_detected:
        events.append(
            {
                "event_name": "wall_removed",
                "side": prev_wall_side,
            }
        )

    if prev_wall_detected and curr_wall_detected and prev_wall_side != curr_wall_side:
        events.append(
            {
                "event_name": "wall_side_shift",
                "prev_side": prev_wall_side,
                "curr_side": curr_wall_side,
            }
        )

    if not prev_near_wall_detected and curr_near_wall_detected:
        events.append(
            {
                "event_name": "near_wall_created",
                "side": curr_near_wall_side,
            }
        )

    if prev_near_wall_detected and not curr_near_wall_detected:
        events.append(
            {
                "event_name": "near_wall_removed",
                "side": prev_near_wall_side,
            }
        )

    if (
        prev_near_wall_detected
        and curr_near_wall_detected
        and prev_near_wall_side == curr_near_wall_side
    ):
        events.append(
            {
                "event_name": "near_wall_continued",
                "side": curr_near_wall_side,
            }
        )

    if (
        prev_defense_kind is not None
        and curr_defense_kind is not None
        and prev_defense_kind == curr_defense_kind
        and prev_defense_side == curr_defense_side
    ):
        event_name = "support_continued"
        if curr_defense_kind == "resistance":
            event_name = "resistance_continued"

        events.append(
            {
                "event_name": event_name,
                "side": curr_defense_side,
            }
        )

    if bid_pull_detected:
        events.append(
            {
                "event_name": "bid_liquidity_pulled",
                "side": "bid",
                "removed_ratio": _safe_get(curr_signal, "bid_pull", "removed_ratio"),
                "removed_depth": _safe_get(curr_signal, "bid_pull", "removed_depth"),
            }
        )

    if ask_pull_detected:
        events.append(
            {
                "event_name": "ask_liquidity_pulled",
                "side": "ask",
                "removed_ratio": _safe_get(curr_signal, "ask_pull", "removed_ratio"),
                "removed_depth": _safe_get(curr_signal, "ask_pull", "removed_depth"),
            }
        )

    events.extend(wall_strength_events(prev_signal, curr_signal))
    events.extend(liquidity_depth_change_events(prev_signal, curr_signal))
    events.extend(spread_change_events(prev_signal, curr_signal))
    events.extend(candidate_events(curr_signal))

    return enrich_event_contracts(events)