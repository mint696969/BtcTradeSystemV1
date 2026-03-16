# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_monitor.py
# desc: Replay board signal から market metrics を表示する WarRoom パネル

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.research_bridge import (
    board_signal_metrics,
    latest_board_row,
    load_latest_replay_payload,
)
from btcts.apps.operator_ui.ui_text import get_text


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'market_monitor_title')}")

    replay_payload = load_latest_replay_payload()
    board = board_signal_metrics(latest_board_row(replay_payload))

    if not board:
        st.warning(get_text(lang, "market_monitor_not_found"))
        return

    spread = board.get("spread")
    bid_depth = board.get("bid_depth")
    ask_depth = board.get("ask_depth")
    imbalance = board.get("imbalance")

    c1, c2, c3 = st.columns(3)
    c1.metric(get_text(lang, "market_monitor_spread"), "-" if spread is None else round(float(spread), 2))
    c2.metric(get_text(lang, "market_monitor_bid_volume"), "-" if bid_depth is None else round(float(bid_depth), 4))
    c3.metric(get_text(lang, "market_monitor_ask_volume"), "-" if ask_depth is None else round(float(ask_depth), 4))

    st.metric(
        get_text(lang, "market_monitor_imbalance"),
        "-" if imbalance is None else round(float(imbalance), 3),
    )

    st.caption(
        f"best_bid={board.get('best_bid')} / best_ask={board.get('best_ask')} / ts={board.get('event_ts')}"
    )

    st.divider()