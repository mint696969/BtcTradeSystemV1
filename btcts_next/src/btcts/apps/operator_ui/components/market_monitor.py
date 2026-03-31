# path: ./btcts_next/src/btcts/apps/operator_ui/components/market_monitor.py
# desc: Replay board signal から market metrics を表示する WarRoom パネル

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.market_state_bridge import (
    market_state_age_seconds,
    market_state_freshness_label,
    market_state_status_caption,
)
from btcts.apps.operator_ui.components.market_monitor_logic import (
    monitor_status_values,
)
from btcts.apps.operator_ui.components.market_monitor_presenter import (
    best_bid_ask_ts_caption,
    interpretation_caption,
    source_caption,
)
from btcts.apps.operator_ui.components.market_monitor_state import (
    analyze_market_monitor_state,
)
from btcts.apps.operator_ui.ui_text import get_text


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'market_monitor_title')}")

    state_bundle = analyze_market_monitor_state()
    if not state_bundle:
        st.warning(get_text(lang, "market_monitor_not_found"))
        return

    board = state_bundle["board"]
    state = state_bundle["state"]
    state_diag = state_bundle["state_diag"]
    source_label = state_bundle["source_label"]

    spread = board.get("spread")
    bid_depth = board.get("bid_depth")
    ask_depth = board.get("ask_depth")
    imbalance = board.get("imbalance")
    status_values = monitor_status_values(board, state)
    trust_state = status_values["trust_state"]
    continuity_state = status_values["continuity_state"]
    interpretation_bucket = status_values["interpretation_bucket"]

    c1, c2, c3 = st.columns(3)
    c1.metric(get_text(lang, "market_monitor_spread"), "-" if spread is None else round(float(spread), 2))
    c2.metric(get_text(lang, "market_monitor_bid_volume"), "-" if bid_depth is None else round(float(bid_depth), 4))
    c3.metric(get_text(lang, "market_monitor_ask_volume"), "-" if ask_depth is None else round(float(ask_depth), 4))

    st.metric(
        get_text(lang, "market_monitor_imbalance"),
        "-" if imbalance is None else round(float(imbalance), 3),
    )

    p1, p2, p3 = st.columns(3)
    p1.metric(get_text(lang, "market_monitor_trust"), trust_state or "-")
    p2.metric(get_text(lang, "market_monitor_continuity"), continuity_state or "-")
    p3.metric(get_text(lang, "market_monitor_interpretation"), interpretation_bucket or "-")

    st.caption(best_bid_ask_ts_caption(lang, board))

    preferred_freshness = state_diag.get("preferred_row_freshness") or "-"
    st.caption(
        source_caption(
            lang=lang,
            source_label=source_label,
            has_state=bool(state),
            preferred_freshness=preferred_freshness,
        )
    )

    interpretation_reason = status_values["interpretation_reason"]
    if interpretation_bucket or interpretation_reason or continuity_state:
        st.caption(
            interpretation_caption(
                lang=lang,
                continuity_state=continuity_state,
                interpretation_bucket=interpretation_bucket,
                interpretation_reason=interpretation_reason,
            )
        )

    if state:
        freshness = market_state_freshness_label(state)
        age = market_state_age_seconds(state)
        st.caption(market_state_status_caption(state))
        st.caption(
            get_text(lang, "market_monitor_market_state_line").format(
                market_state_freshness=freshness,
                market_state_age_sec="-" if age is None else round(float(age), 1),
            )
        )

        if state_diag.get("preferred_row_is_stale") and trust_state == "trusted":
            st.caption(get_text(lang, "market_monitor_stale_posture_caption"))

    st.divider()