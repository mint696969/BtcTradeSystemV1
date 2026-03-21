# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_monitor.py
# desc: Replay board signal から market metrics を表示する WarRoom パネル

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_overview,
    market_monitor_metrics,
    market_state_age_seconds,
    market_state_freshness_label,
    market_state_status_caption,
)
from btcts.apps.operator_ui.components.research_bridge import (
    board_signal_metrics,
    latest_board_row,
    load_latest_replay_payload,
)
from btcts.apps.operator_ui.ui_text import get_text


from btcts.apps.operator_ui.components.live_bridge import (
    latest_live_board_metrics,
)


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'market_monitor_title')}")

    live_board = latest_live_board_metrics()
    state = load_market_overview()
    board = {}
    source_label = "unknown"

    if live_board:
        best_bid = live_board.get("best_bid")
        best_ask = live_board.get("best_ask")
        spread = live_board.get("spread")
        bid_depth = live_board.get("bid_depth")
        ask_depth = live_board.get("ask_depth")

        imbalance = None
        if bid_depth is not None and ask_depth is not None:
            try:
                bid_depth_f = float(bid_depth)
                ask_depth_f = float(ask_depth)
                denom = bid_depth_f + ask_depth_f
                if denom > 0:
                    imbalance = (bid_depth_f - ask_depth_f) / denom
            except Exception:
                imbalance = None

        board = {
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "bid_depth": bid_depth,
            "ask_depth": ask_depth,
            "imbalance": imbalance,
            "event_ts": live_board.get("event_ts"),
            "trust_state": None,
            "boundary_reason": None,
            "continuity_state": None,
            "interpretation_bucket": None,
            "interpretation_reason": None,
        }
        source_label = "live_canonical"

    if not board:
        board = market_monitor_metrics(state)
        source_label = "market_state_live"

    if not board:
        replay_payload = load_latest_replay_payload()
        board = board_signal_metrics(latest_board_row(replay_payload))
        source_label = "replay_board_fallback"

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

    st.caption(f"source={source_label}")

    interpretation_bucket = board.get("interpretation_bucket")
    interpretation_reason = board.get("interpretation_reason")
    if interpretation_bucket or interpretation_reason:
        st.caption(
            f"interpretation_bucket={interpretation_bucket or '-'} / "
            f"interpretation_reason={interpretation_reason or '-'}"
        )

    if state:
        freshness = market_state_freshness_label(state)
        age = market_state_age_seconds(state)
        st.caption(market_state_status_caption(state))
        st.caption(
            f"market_state_freshness={freshness} / "
            f"market_state_age_sec={'-' if age is None else round(float(age), 1)}"
        )

    st.divider()