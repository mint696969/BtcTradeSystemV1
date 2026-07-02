# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/market_chart_read_model.py
# desc: Read-only market chart series adapter for WarRoom v2. No push, transport, or execution behavior.

from __future__ import annotations

from typing import Any

WARROOM_V2_MARKET_CHART_READ_MODEL_VERSION = "prediction_warroom.v2.market_chart_read_model.ps_q29v.v1"
WARROOM_V2_CHART_WINDOW_ROWS = {"1m": 60, "5m": 240, "15m": 720, "1h": 1440, "1d": 2880}


def _f(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def chart_window_rows_for_timeframe(timeframe: str) -> int:
    return int(WARROOM_V2_CHART_WINDOW_ROWS.get(str(timeframe), WARROOM_V2_CHART_WINDOW_ROWS["5m"]))


def _mid(row: dict[str, Any]) -> float | None:
    value = _f(row.get("mid_price") or row.get("price"))
    if value is not None:
        return value
    bid, ask = _f(row.get("best_bid")), _f(row.get("best_ask"))
    return (bid + ask) / 2.0 if bid is not None and ask is not None else None


def _bps(spread: Any, mid: Any) -> float | None:
    s, m = _f(spread), _f(mid)
    return (s / m * 10000.0) if s is not None and m and m > 0 else None


def _chart_row(row: dict[str, Any]) -> dict[str, Any] | None:
    ts = row.get("collector_ts") or row.get("exchange_ts")
    mid = _mid(row)
    if not ts or mid is None:
        return None
    spread = row.get("spread")
    return {"ts": str(ts), "mid_price": mid, "best_bid": _f(row.get("best_bid")), "best_ask": _f(row.get("best_ask")), "spread": _f(spread), "spread_bps": _bps(spread, mid), "trust_state": row.get("trust_state"), "continuity_state": row.get("continuity_state"), "interpretation_bucket": row.get("interpretation_bucket")}


def _load_rows(max_lines: int) -> tuple[list[dict[str, Any]], str | None]:
    try:
        from btcts.apps.operator_ui.components.market_state_bridge import execution_market_context
        from btcts.apps.operator_ui.market_state_service import load_recent_market_states

        ctx = execution_market_context()
        rows = load_recent_market_states(exchange=str(ctx["exchange"]), symbol_raw=str(ctx["symbol_raw"]), max_lines=max_lines)
        return [dict(row) for row in rows], None
    except Exception as exc:
        return [], str(exc)


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    mids = [float(row["mid_price"]) for row in rows if _f(row.get("mid_price")) is not None]
    if not mids:
        return {"open": None, "high": None, "low": None, "close": None, "change_pct": None, "range_pct": None, "row_count": 0}
    open_, close = mids[0], mids[-1]
    return {"open": open_, "high": max(mids), "low": min(mids), "close": close, "change_pct": ((close - open_) / open_ * 100.0) if open_ else None, "range_pct": ((max(mids) - min(mids)) / close * 100.0) if close else None, "row_count": len(mids)}


def build_warroom_v2_market_chart_read_model(*, rows: list[dict[str, Any]] | None = None, timeframe: str = "5m", max_lines: int | None = None) -> dict[str, Any]:
    window_rows = int(max_lines or chart_window_rows_for_timeframe(timeframe))
    source_error = None
    source_rows = [dict(row) for row in rows] if rows is not None else []
    if rows is None:
        source_rows, source_error = _load_rows(window_rows)
    chart_rows = [item for item in (_chart_row(row) for row in source_rows[-window_rows:]) if item is not None]
    summary = _summary(chart_rows)
    connected = bool(chart_rows)
    return {"ok": connected, "read_model_version": WARROOM_V2_MARKET_CHART_READ_MODEL_VERSION, "source_kind": "dhot_market_state_chart_series_read_only", "timeframe": timeframe, "max_lines": window_rows, "chart_window": {"timeframe": timeframe, "row_limit": window_rows, "window_policy": "bounded_recent_rows"}, "chart_rows": chart_rows, "chart_row_count": len(chart_rows), "range_summary": summary, "source_error": source_error, "actual_chart_series_bound": connected, "chart_series_connected": connected, "read_only": True, "display_only": True, "runtime_connected": False, "push_connected": False, "websocket_enabled": False, "sse_enabled": False, "would_send_to_broker": False}
