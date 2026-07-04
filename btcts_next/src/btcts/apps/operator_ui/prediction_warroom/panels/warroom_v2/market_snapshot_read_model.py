# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/market_snapshot_read_model.py
# desc: Read-only D-hot market snapshot adapter for WarRoom v2. No push, transport, or execution behavior.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

WARROOM_V2_MARKET_SNAPSHOT_READ_MODEL_VERSION = "prediction_warroom.v2.market_snapshot_read_model.ps_q34a.v1"


def _float(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def _fmt_price(value: Any) -> str:
    num = _float(value)
    return f"{num:,.0f}" if num is not None else "--"


def _age_from_ts(value: Any) -> float | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return max((datetime.now(timezone.utc) - dt).total_seconds(), 0.0)


def _market_label(symbol: Any) -> str:
    raw = str(symbol or "FX_BTC_JPY")
    return "BTC-FX-JPY" if raw == "FX_BTC_JPY" else raw.replace("_", "-")


def _spread_bps(spread: Any, mid: Any) -> float | None:
    s, m = _float(spread), _float(mid)
    return (s / m * 10000.0) if s is not None and m and m > 0 else None


def _book_quality(row: dict[str, Any]) -> dict[str, Any]:
    bid, ask, spread = _float(row.get("best_bid")), _float(row.get("best_ask")), _float(row.get("spread"))
    computed = ask - bid if bid is not None and ask is not None else None
    crossed = bool(bid is not None and ask is not None and bid > ask)
    sign_valid = bool(spread is None or spread >= 0)
    matches = bool(spread is not None and computed is not None and abs(spread - computed) <= 1e-9)
    state = "NO_DATA" if not row else "CROSSED_BOOK" if crossed else "SPREAD_SIGN_INVALID" if not sign_valid else "SPREAD_MISSING" if spread is None else "SPREAD_MISMATCH" if not matches else "OK"
    return {"best_bid": bid, "best_ask": ask, "reported_spread": spread, "computed_spread": computed, "bid_ask_crossed": crossed, "spread_sign_valid": sign_valid, "spread_matches_best_bid_ask": matches, "market_data_quality_state": state, "display_label": state}


def _freshness(row: dict[str, Any], diag: dict[str, Any], age: float | None) -> str:
    label = str(diag.get("preferred_row_freshness") or "").upper()
    if label:
        return label
    if not row:
        return "NO_DATA"
    if age is None:
        return "UNKNOWN"
    return "LIVE" if age <= 30 else "QUIET" if age <= 120 else "STALE"


def _load_execution_market() -> tuple[dict[str, Any], dict[str, Any], str | None]:
    try:
        from btcts.apps.operator_ui.components.market_state_bridge import execution_market_context, load_execution_market_overview
        from btcts.apps.operator_ui.market_state_service import market_state_diagnostics

        ctx = execution_market_context()
        row = dict(load_execution_market_overview() or {})
        diag = dict(market_state_diagnostics(exchange=str(ctx["exchange"]), symbol_raw=str(ctx["symbol_raw"])))
        return row, diag, None
    except Exception as exc:
        return {}, {}, str(exc)


def _values(row: dict[str, Any], diag: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    mid = row.get("mid_price") or row.get("price")
    ltp = row.get("price") if row.get("price") is not None else mid
    spread = row.get("spread")
    age = diag.get("preferred_row_age_sec") or _age_from_ts(row.get("collector_ts") or row.get("exchange_ts"))
    bps = _spread_bps(spread, mid)
    state = _freshness(row, diag, age)
    quality = _book_quality(row)
    liquidity = row.get("near_zone_liquidity_summary") or {}
    raw = {
        "market": _market_label(row.get("symbol_raw")), "ltp": ltp, "best_bid": row.get("best_bid"), "best_ask": row.get("best_ask"),
        "spread": spread, "spread_bps": bps, "data_age_sec": age, "data_state": state,
        "change_1m_pct": None, "change_5m_pct": None, "change_15m_pct": None, "change_1h_pct": None,
        "invalidation_watch": "PREVIEW_ONLY" if row else "NO_DATA",
        "board_imbalance": (row.get("imbalance_summary") or {}).get("near_size_imbalance"),
        "bid_size_total": liquidity.get("bid_size_total"), "ask_size_total": liquidity.get("ask_size_total"),
        "data_quality": quality, "bid_ask_crossed": quality["bid_ask_crossed"], "spread_sign_valid": quality["spread_sign_valid"],
        "spread_matches_best_bid_ask": quality["spread_matches_best_bid_ask"], "market_data_quality_state": quality["market_data_quality_state"],
    }
    display = {
        "market": raw["market"], "ltp": _fmt_price(ltp), "best_bid": _fmt_price(raw["best_bid"]), "best_ask": _fmt_price(raw["best_ask"]),
        "spread": f"{_fmt_price(spread)} / {bps:.2f} bps" if bps is not None else "-- / -- bps",
        "data_age_sec": f"{float(age):.1f} sec" if _float(age) is not None else "-- sec", "data_state": state,
        "change_1m_pct": "--", "change_5m_pct": "--", "change_15m_pct": "--", "change_1h_pct": "--",
        "invalidation_watch": raw["invalidation_watch"], "data_quality": quality["display_label"], "market_data_quality_state": quality["market_data_quality_state"],
    }
    return raw, display


def build_warroom_v2_market_snapshot_dhot_read_model(*, row: dict[str, Any] | None = None, diagnostics: dict[str, Any] | None = None) -> dict[str, Any]:
    source_error = None
    source_row, source_diag = dict(row or {}), dict(diagnostics or {})
    if row is None:
        source_row, source_diag, source_error = _load_execution_market()
    raw, display = _values(source_row, source_diag)
    connected = bool(source_row)
    return {
        "ok": connected, "read_model_version": WARROOM_V2_MARKET_SNAPSHOT_READ_MODEL_VERSION,
        "source_kind": "dhot_market_state_read_only", "explicit_dhot_read_only_binding": True, "source_error": source_error,
        "raw_values": raw, "display_values": display, "data_quality_diagnostics": raw["data_quality"], "diagnostics": source_diag, "data_connected": connected,
        "runtime_connected": False, "push_connected": False, "websocket_enabled": False, "sse_enabled": False,
        "read_only": True, "display_only": True, "would_send_to_broker": False,
    }
