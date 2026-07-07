# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/interactive_chart/selection_packet.py
# desc: Build minimal GPT selection-copy packets. Pure contract; no UI, IO, or execution behavior.

from __future__ import annotations

from typing import Any, Mapping

from .candle_records import iso_utc
from .constants import timeframe_key


def _timeframe_sec(mode: str) -> int:
    return {"Live": 60, "1分足": 60, "5分足": 300, "15分足": 900, "30分足": 1800, "1時間足": 3600, "日足": 86400}.get(str(mode), 60)


def _candle_store_relpath(timeframe_sec: int) -> str:
    return f"data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/timeframe={int(timeframe_sec)}s"


def build_chart_selection_copy_request(
    *,
    mode: str,
    selection_type: str,
    start_candle: Mapping[str, Any],
    end_candle: Mapping[str, Any],
    candle_count: int,
    visible_candle_count: int,
    chart_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    context = dict(chart_context or {})
    timeframe_sec = _timeframe_sec(mode)
    store_relpath = _candle_store_relpath(timeframe_sec)
    start_time = start_candle.get("time_utc") or iso_utc(start_candle.get("time"))
    end_time = end_candle.get("time_utc") or iso_utc(end_candle.get("time"))
    return {
        "schema_version": "warroom_chart_analysis_request.2026_07_06.v2_interactive_selection",
        "selection_origin": "warroom_v2_interactive_candlestick_chart",
        "selection_type": selection_type,
        "purpose": "manual review only; use Actions/data tools for deeper evidence; no order action",
        "timeframe": timeframe_key(mode),
        "timeframe_label": mode,
        "timeframe_sec": timeframe_sec,
        "market": {"exchange": "bitflyer", "symbol": "FX_BTC_JPY"},
        "selected_range": {
            "start_ts_utc": start_time,
            "end_ts_utc": end_time,
            "start_ts_jst": start_candle.get("time_jst"),
            "end_ts_jst": end_candle.get("time_jst"),
            "start_candle_index": start_candle.get("candle_index"),
            "end_candle_index": end_candle.get("candle_index"),
            "candle_count": int(candle_count),
            "inclusive": True,
            "lookup_key": "time_utc",
            "candle_index_role": "frontend_tail_record_index_not_store_index",
            "candle_ts_semantics": "bucket_start_utc",
            "start_candle_status": start_candle.get("candle_status"),
            "end_candle_status": end_candle.get("candle_status"),
            "contains_forming_candle": str(start_candle.get("candle_status") or "").lower() == "forming" or str(end_candle.get("candle_status") or "").lower() == "forming",
        },
        "viewport": {
            "right_edge_is_now_or_latest": True,
            "future_space_is_visual_blank_only": True,
            "visible_candle_count": int(visible_candle_count),
            "viewport_label": context.get("viewport_label"),
            "viewport_minutes": context.get("viewport_minutes"),
            "chart_axis_timezone": "Asia/Tokyo",
        },
        "source": {
            "hot_data_root": "D:/btc_ts_hot",
            "cold_data_root": "E:/btc_ts",
            "cold_root_policy": "Use cold archive only when the operator explicitly asks for archive/replay/historical validation.",
            "primary_market_trade_path": context.get("primary_market_trade_path"),
            "dhot_bootstrap": dict(context.get("dhot_bootstrap") or {}),
            "input_source": context.get("input_source") or "warroom_l4_candle_store_plus_retained_market_state_overlay",
            "candle_store_family": "warroom_l4_candle_store",
            "candle_store_relpath": store_relpath,
            "closed_candles_relpath": f"{store_relpath}/closed.jsonl",
            "forming_candle_relpath": f"{store_relpath}/forming.json",
            "timeframe_meta_relpath": f"{store_relpath}/meta.json",
            "update_state_relpath": "data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/update_state.json",
            "gap_policy": "absent_candles_no_synthetic_null",
            "preferred_analysis_source": "D-hot derived L4 candle store first; use E-cold only when explicitly requested.",
        },
        "display_timezone": "Asia/Tokyo",
        "canonical_timezone": "UTC",
        "safety": {
            "read_only": True,
            "manual_review_only": True,
            "websocket_send_enabled": False,
            "broker_send_enabled": False,
            "order_intent_submitted": False,
            "ledger_append_allowed": False,
            "prediction_invoked": False,
            "classifier_invoked": False,
        },
    }
