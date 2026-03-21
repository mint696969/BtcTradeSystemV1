# path: ./btcts_next/src/btcts/apps/operator_ui/components/liquidity_pressure_panel.py
# desc: Live canonical 優先、replay fallback で壁と流動性圧力を表示する WarRoom パネル

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.research_bridge import (
    board_signal_metrics,
    latest_board_row,
    load_latest_replay_payload,
)
from btcts.apps.operator_ui.ui_text import get_text

from btcts.apps.operator_ui.components.live_bridge import latest_live_board_metrics

def _badge_class(value: str) -> str:
    if value in ("BUY", "買い"):
        return "badge-buy"

    if value in ("SELL", "売り"):
        return "badge-sell"

    return "badge-neutral"


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'liquidity_pressure_title')}")

    live_board = latest_live_board_metrics()
    source_label = "replay_board_fallback"

    board = None

    if live_board:
        bid_depth = live_board.get("bid_depth")
        ask_depth = live_board.get("ask_depth")

        wall_ratio = None
        wall_side = None

        if bid_depth is not None and ask_depth is not None:
            try:
                bid_depth_f = float(bid_depth)
                ask_depth_f = float(ask_depth)
                denom = bid_depth_f + ask_depth_f
                if denom > 0:
                    wall_ratio = (bid_depth_f - ask_depth_f) / denom
                    if wall_ratio > 0.05:
                        wall_side = "bid"
                    elif wall_ratio < -0.05:
                        wall_side = "ask"
            except Exception:
                wall_ratio = None
                wall_side = None

        board = {
            "bid_wall_size": bid_depth,
            "ask_wall_size": ask_depth,
            "wall_ratio": wall_ratio,
            "wall_side": wall_side,
            "event_ts": live_board.get("event_ts"),
        }
        source_label = "live_canonical"

    if not board:
        replay_payload = load_latest_replay_payload()
        board = board_signal_metrics(latest_board_row(replay_payload))

    if not board:
        st.warning(get_text(lang, "liquidity_pressure_not_found"))
        return

    top_bid_wall = board.get("bid_wall_size")
    top_ask_wall = board.get("ask_wall_size")
    wall_ratio = board.get("wall_ratio")
    wall_side = board.get("wall_side")

    wall_bias = get_text(lang, "liquidity_pressure_value_neutral")
    if wall_side == "bid":
        wall_bias = get_text(lang, "liquidity_pressure_value_buy")
    elif wall_side == "ask":
        wall_bias = get_text(lang, "liquidity_pressure_value_sell")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        get_text(lang, "liquidity_pressure_top_bid_wall"),
        "-" if top_bid_wall is None else round(float(top_bid_wall), 4),
    )
    c2.metric(
        get_text(lang, "liquidity_pressure_top_ask_wall"),
        "-" if top_ask_wall is None else round(float(top_ask_wall), 4),
    )
    c3.metric(
        get_text(lang, "liquidity_pressure_wall_ratio"),
        "-" if wall_ratio is None else round(float(wall_ratio), 3),
    )
    c4.metric(get_text(lang, "liquidity_pressure_wall_bias"), wall_bias)

    st.markdown(
        f"""
        <div class="warroom-badges">
            <span class="warroom-badge {_badge_class(wall_bias)}">
                {get_text(lang, 'badge_liquidity_bias')}: {wall_bias}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(f"source={source_label}")

    st.divider()