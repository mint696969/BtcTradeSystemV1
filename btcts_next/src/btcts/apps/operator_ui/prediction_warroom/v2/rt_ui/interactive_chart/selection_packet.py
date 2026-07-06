# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/interactive_chart/selection_packet.py
# desc: Build minimal GPT selection-copy packets. Pure contract; no UI, IO, or execution behavior.

from __future__ import annotations

from typing import Any, Mapping

from .candle_records import iso_utc
from .constants import timeframe_key


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
    start_time = start_candle.get("time_utc") or iso_utc(start_candle.get("time"))
    end_time = end_candle.get("time_utc") or iso_utc(end_candle.get("time"))
    return {
        "schema_version": "warroom_chart_analysis_request.2026_07_06.v2_interactive_selection",
        "selection_origin": "warroom_v2_interactive_candlestick_chart",
        "selection_type": selection_type,
        "purpose": "manual review only; use Actions/data tools for deeper evidence; no order action",
        "timeframe": timeframe_key(mode),
        "timeframe_label": mode,
        "selected_range": {
            "start_ts_utc": start_time,
            "end_ts_utc": end_time,
            "start_ts_jst": start_candle.get("time_jst"),
            "end_ts_jst": end_candle.get("time_jst"),
            "start_candle_index": start_candle.get("candle_index"),
            "end_candle_index": end_candle.get("candle_index"),
            "candle_count": int(candle_count),
            "inclusive": True,
        },
        "viewport": {
            "right_edge_is_now_or_latest": True,
            "future_space_is_visual_blank_only": True,
            "visible_candle_count": int(visible_candle_count),
        },
        "source": {
            "hot_data_root": "D:/btc_ts_hot",
            "cold_data_root": "E:/btc_ts",
            "cold_root_policy": "Use cold archive only when the operator explicitly asks for archive/replay/historical validation.",
            "primary_market_trade_path": context.get("primary_market_trade_path"),
            "dhot_bootstrap": dict(context.get("dhot_bootstrap") or {}),
            "input_source": context.get("input_source") or "retained_market_state_rows_plus_dhot_market_trade_bootstrap",
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
