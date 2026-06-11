# path: ./btcts_next/src/btcts/apps/operator_ui/views/config_page.py
# desc: 取引所設定や接続設定を操作する Operator Config ページ。

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)


def render():

    st.header("Exchange Configuration")
    summary_widget = load_market_summary_widget_model()

    exchange = st.selectbox(
        "Exchange",
        ["binance", "bybit"]
    )

    with live_shell.panel_container(label="Configuration selection", tone="neutral"):
        st.write("Selected:", exchange)

        if st.button("Save"):
            st.success("Configuration saved")

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))