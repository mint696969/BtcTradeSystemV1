# path: ./btcts_next/src/btcts/apps/operator_ui/components/liquidity_pressure_panel.py
# desc: Live canonical 優先、replay fallback で壁と流動性圧力を表示する WarRoom パネル

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.liquidity_pressure_state import (
    build_liquidity_pressure_state,
)
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
from btcts.apps.operator_ui.components.slot_definitions import (
    overlay_contract_caption,
    overlay_contract_metric_rows,
)
from btcts.apps.operator_ui.ui_text import get_text

def _badge_class(value: str) -> str:
    if value in ("BUY", "買い"):
        return "badge-buy"

    if value in ("SELL", "売り"):
        return "badge-sell"

    return "badge-neutral"


def render(
    *,
    overlay_contract: dict | None = None,
):
    lang = st.session_state.get("ui_lang", "en")

    if overlay_contract:
        st.caption(overlay_contract_caption(overlay_contract))

        metric_rows = overlay_contract_metric_rows(overlay_contract)
        if metric_rows:
            metric_cols = st.columns(len(metric_rows))
            for col, (label, value) in zip(metric_cols, metric_rows):
                col.metric(label, value)

        with st.expander(get_text(lang, "graph_overlay_contract_title"), expanded=False):
            st.json(overlay_contract)

    st.markdown(f"### {get_text(lang, 'liquidity_pressure_title')}")

    board = build_liquidity_pressure_state()
    if not board:
        st.warning(get_text(lang, "liquidity_pressure_not_found"))
        return

    source_label = str(board.get("source_label") or "unknown")

    top_bid_wall = board.get("bid_wall_size")
    top_ask_wall = board.get("ask_wall_size")
    wall_ratio = board.get("wall_ratio")
    wall_side = board.get("wall_side")
    summary_widget = load_market_summary_widget_model()

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

    st.caption(
        get_text(lang, "warroom_generic_source_caption").format(
            source=source_label,
        )
    )

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))

    st.divider()