# path: ./btcts_next/src/btcts/apps/operator_ui/components/trade_flow_monitor.py
# desc: Replay tradeflow から BUY/SELL volume と delta を表示する WarRoom パネル

from __future__ import annotations

import streamlit as st

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
from btcts.apps.operator_ui.components.trade_flow_state import (
    build_trade_flow_state,
)
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.ui_time import format_ui_ts


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

    st.markdown(f"### {get_text(lang, 'trade_flow_title')}")

    flow = build_trade_flow_state()
    if not flow:
        st.warning(get_text(lang, "trade_flow_not_found"))
        return

    source_label = str(flow.get("source_label") or "unknown")

    buy_vol = flow.get("buy_volume")
    sell_vol = flow.get("sell_volume")
    delta = flow.get("trade_delta")
    trade_count = flow.get("trade_count")
    summary_widget = load_market_summary_widget_model()

    c1, c2, c3 = st.columns(3)

    c1.metric(get_text(lang, "trade_flow_buy_volume"), "-" if buy_vol is None else round(float(buy_vol), 4))
    c2.metric(get_text(lang, "trade_flow_sell_volume"), "-" if sell_vol is None else round(float(sell_vol), 4))
    c3.metric(get_text(lang, "trade_flow_delta"), "-" if delta is None else round(float(delta), 4))

    st.caption(
        get_text(lang, "trade_flow_recent_count_caption").format(
            label=get_text(lang, "trade_flow_recent_count"),
            count=trade_count,
        )
    )

    st.caption(
        get_text(lang, "trade_flow_source_ts_caption").format(
            source=source_label,
            ts=format_ui_ts(flow.get("event_ts"), lang),
        )
    )

    micro_names = flow.get("micro_event_names") or []
    if micro_names:
        st.caption(
            get_text(lang, "trade_flow_microstructure_caption").format(
                names=", ".join(micro_names[:5]),
            )
        )

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))

    st.divider()