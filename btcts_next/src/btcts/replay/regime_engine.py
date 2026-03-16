# path: ./btcts_next/src/btcts/replay/regime_engine.py
# desc: Detect replay market regime from replay result rows.

from __future__ import annotations

from typing import Dict, List, Optional


def _safe_get(payload: Optional[Dict], *path, default=None):
    cur = payload
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return cur if cur is not None else default


def _mid_from_row(row: Dict) -> Optional[float]:
    result = row.get("result")
    if not isinstance(result, dict):
        return None

    signal = result.get("signal")
    if isinstance(signal, dict):
        mid = signal.get("mid")
        if mid is not None:
            return float(mid)

    best_bid = result.get("best_bid")
    best_ask = result.get("best_ask")
    if best_bid is not None and best_ask is not None:
        return (float(best_bid) + float(best_ask)) / 2.0

    return None


def _spread_from_row(row: Dict) -> Optional[float]:
    result = row.get("result")
    if not isinstance(result, dict):
        return None

    signal = result.get("signal")
    if isinstance(signal, dict):
        spread = signal.get("spread")
        if spread is not None:
            try:
                return abs(float(spread))
            except Exception:
                return None

        summary = signal.get("summary", {})
        if isinstance(summary, dict):
            spread = summary.get("spread")
            if spread is not None:
                try:
                    return abs(float(spread))
                except Exception:
                    return None

    best_bid = result.get("best_bid")
    best_ask = result.get("best_ask")
    if best_bid is not None and best_ask is not None:
        try:
            bid = float(best_bid)
            ask = float(best_ask)
            return abs(ask - bid)
        except Exception:
            return None

    return None


def _pressure_bias(row: Dict) -> str:
    result = row.get("result")
    if not isinstance(result, dict):
        return "unknown"

    signal = result.get("signal")
    if not isinstance(signal, dict):
        return "unknown"

    pressure = signal.get("pressure", {})
    if not isinstance(pressure, dict):
        return "unknown"

    return str(pressure.get("bias") or "unknown")


def _event_names(row: Dict) -> List[str]:
    names: List[str] = []

    result = row.get("result")
    if isinstance(result, dict):
        for event in result.get("events", []):
            if isinstance(event, dict):
                name = event.get("event_name")
                if name:
                    names.append(str(name))

    for event in row.get("microstructure", []):
        if isinstance(event, dict):
            name = event.get("event_name")
            if name:
                names.append(str(name))

    return names


def detect_market_regime(rows: List[Dict]) -> Dict:
    board_rows = [row for row in rows if row.get("kind") == "board" and isinstance(row.get("result"), dict)]

    if not board_rows:
        return {
            "regime": "unknown",
            "spread_state": "unknown",
            "pressure_state": "unknown",
            "board_count": 0,
            "reason": "no_board_rows",
            "event_name_counts": {},
        }

    mids = [mid for mid in (_mid_from_row(row) for row in board_rows) if mid is not None]
    spreads = [spread for spread in (_spread_from_row(row) for row in board_rows) if spread is not None]

    bias_counts = {
        "buy_pressure": 0,
        "sell_pressure": 0,
        "neutral": 0,
        "unknown": 0,
    }

    event_name_counts: Dict[str, int] = {}

    absorption_count = 0
    sweep_count = 0

    for row in rows:
        for name in _event_names(row):
            event_name_counts[name] = event_name_counts.get(name, 0) + 1
            if name in {"absorption_candidate", "absorption_detected"}:
                absorption_count += 1
            if name in {"sweep_candidate", "liquidity_sweep"}:
                sweep_count += 1

    for row in board_rows:
        bias = _pressure_bias(row)
        if bias not in bias_counts:
            bias = "unknown"
        bias_counts[bias] += 1

    board_count = len(board_rows)

    first_mid = mids[0] if mids else None
    last_mid = mids[-1] if mids else None
    price_change = None
    price_change_pct = None

    if first_mid is not None and last_mid is not None and first_mid != 0:
        price_change = last_mid - first_mid
        price_change_pct = price_change / first_mid

    avg_spread = None
    if spreads:
        avg_spread = sum(spreads) / len(spreads)

    spread_state = "normal"
    if avg_spread is not None:
        if avg_spread >= 6000:
            spread_state = "wide"
        elif avg_spread <= 2500:
            spread_state = "tight"

    dominant_pressure = "neutral"
    if bias_counts["buy_pressure"] > max(bias_counts["sell_pressure"], bias_counts["neutral"]):
        dominant_pressure = "buy_pressure"
    elif bias_counts["sell_pressure"] > max(bias_counts["buy_pressure"], bias_counts["neutral"]):
        dominant_pressure = "sell_pressure"

    regime = "range"
    reason = "balanced"

    if absorption_count >= 2:
        regime = "absorption_zone"
        reason = "absorption_events_detected"
    elif sweep_count >= 2:
        regime = "sweep_risk"
        reason = "sweep_events_detected"
    elif spread_state == "wide":
        regime = "liquidity_vacuum"
        reason = "wide_spread"
    elif price_change_pct is not None and price_change_pct >= 0.001 and dominant_pressure == "buy_pressure":
        regime = "trend_up"
        reason = "price_up_with_buy_pressure"
    elif price_change_pct is not None and price_change_pct <= -0.001 and dominant_pressure == "sell_pressure":
        regime = "trend_down"
        reason = "price_down_with_sell_pressure"

    return {
        "regime": regime,
        "reason": reason,
        "spread_state": spread_state,
        "pressure_state": dominant_pressure,
        "board_count": board_count,
        "avg_spread": avg_spread,
        "first_mid": first_mid,
        "last_mid": last_mid,
        "price_change": price_change,
        "price_change_pct": price_change_pct,
        "absorption_count": absorption_count,
        "sweep_count": sweep_count,
        "bias_counts": bias_counts,
        "event_name_counts": dict(sorted(event_name_counts.items())),
    }