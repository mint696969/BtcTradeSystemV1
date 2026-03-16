# path: ./btcts_next/src/btcts/collector_vnext/orderbook/event_enrichment.py
# desc: Enrich liquidity signal comparisons into higher-level market microstructure events.

from __future__ import annotations

from typing import Dict, List, Optional


def _safe_get(payload: Optional[Dict], *path, default=None):
    cur = payload
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def wall_strength_events(prev_signal: Optional[Dict], curr_signal: Dict, *, ratio_threshold: float = 0.05) -> List[Dict]:
    events: List[Dict] = []

    prev_ratio = _safe_get(prev_signal, "wall", "strongest_ratio")
    curr_ratio = _safe_get(curr_signal, "wall", "strongest_ratio")
    prev_side = _safe_get(prev_signal, "wall", "strongest_side")
    curr_side = _safe_get(curr_signal, "wall", "strongest_side")

    if prev_ratio is None or curr_ratio is None:
        return events

    if prev_side != curr_side:
        return events

    diff = float(curr_ratio) - float(prev_ratio)

    if diff >= ratio_threshold:
        events.append(
            {
                "event_name": "wall_strengthened",
                "side": curr_side,
                "prev_ratio": prev_ratio,
                "curr_ratio": curr_ratio,
                "ratio_delta": diff,
            }
        )
    elif diff <= -ratio_threshold:
        events.append(
            {
                "event_name": "wall_weakened",
                "side": curr_side,
                "prev_ratio": prev_ratio,
                "curr_ratio": curr_ratio,
                "ratio_delta": diff,
            }
        )

    return events


def liquidity_depth_change_events(
    prev_signal: Optional[Dict],
    curr_signal: Dict,
    *,
    added_threshold: float = 0.15,
    removed_threshold: float = 0.15,
) -> List[Dict]:
    events: List[Dict] = []

    for side_key, label in (("bid", "bid"), ("ask", "ask")):
        prev_depth = _safe_get(prev_signal, "summary", f"{side_key}_depth")
        curr_depth = _safe_get(curr_signal, "summary", f"{side_key}_depth")

        if prev_depth is None or curr_depth is None:
            continue

        prev_depth = float(prev_depth)
        curr_depth = float(curr_depth)

        if prev_depth <= 0:
            continue

        delta = curr_depth - prev_depth
        ratio = delta / prev_depth

        if ratio >= added_threshold:
            events.append(
                {
                    "event_name": f"{label}_liquidity_added",
                    "side": label,
                    "prev_depth": prev_depth,
                    "curr_depth": curr_depth,
                    "depth_delta": delta,
                    "depth_ratio": ratio,
                }
            )
        elif ratio <= -removed_threshold:
            events.append(
                {
                    "event_name": f"{label}_liquidity_removed",
                    "side": label,
                    "prev_depth": prev_depth,
                    "curr_depth": curr_depth,
                    "depth_delta": delta,
                    "depth_ratio": ratio,
                }
            )

    return events


def spread_change_events(
    prev_signal: Optional[Dict],
    curr_signal: Dict,
    *,
    expansion_threshold: float = 1.0,
    compression_threshold: float = 1.0,
) -> List[Dict]:
    events: List[Dict] = []

    prev_spread = _safe_get(prev_signal, "summary", "spread")
    curr_spread = _safe_get(curr_signal, "summary", "spread")

    if prev_spread is None or curr_spread is None:
        return events

    prev_spread = float(prev_spread)
    curr_spread = float(curr_spread)
    delta = curr_spread - prev_spread

    if delta >= expansion_threshold:
        events.append(
            {
                "event_name": "spread_expansion",
                "prev_spread": prev_spread,
                "curr_spread": curr_spread,
                "spread_delta": delta,
            }
        )
    elif delta <= -compression_threshold:
        events.append(
            {
                "event_name": "spread_compression",
                "prev_spread": prev_spread,
                "curr_spread": curr_spread,
                "spread_delta": delta,
            }
        )

    return events


def candidate_events(curr_signal: Dict) -> List[Dict]:
    events: List[Dict] = []

    pressure_bias = _safe_get(curr_signal, "pressure", "bias")
    wall_detected = bool(_safe_get(curr_signal, "wall", "wall_detected", default=False))
    wall_side = _safe_get(curr_signal, "wall", "strongest_side")
    bid_pull = bool(_safe_get(curr_signal, "bid_pull", "detected", default=False))
    ask_pull = bool(_safe_get(curr_signal, "ask_pull", "detected", default=False))
    spread = _safe_get(curr_signal, "summary", "spread")
    imbalance = _safe_get(curr_signal, "summary", "imbalance")

    if wall_detected:
        if wall_side == "ask" and pressure_bias == "buy_pressure":
            events.append(
                {
                    "event_name": "absorption_candidate",
                    "side": "ask",
                    "reason": "buy_pressure_against_ask_wall",
                    "imbalance": imbalance,
                    "spread": spread,
                }
            )
        elif wall_side == "bid" and pressure_bias == "sell_pressure":
            events.append(
                {
                    "event_name": "absorption_candidate",
                    "side": "bid",
                    "reason": "sell_pressure_against_bid_wall",
                    "imbalance": imbalance,
                    "spread": spread,
                }
            )

    if ask_pull and pressure_bias == "buy_pressure":
        events.append(
            {
                "event_name": "sweep_candidate",
                "side": "ask",
                "reason": "ask_liquidity_pulled_under_buy_pressure",
                "imbalance": imbalance,
                "spread": spread,
            }
        )

    if bid_pull and pressure_bias == "sell_pressure":
        events.append(
            {
                "event_name": "sweep_candidate",
                "side": "bid",
                "reason": "bid_liquidity_pulled_under_sell_pressure",
                "imbalance": imbalance,
                "spread": spread,
            }
        )

    return events