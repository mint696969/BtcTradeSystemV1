# path: ./btcts_next/src/btcts/apps/operator_ui/views/config_page.py
# desc: 取引所設定や接続設定を操作する Operator Config ページ。

import streamlit as st


def render():

    st.header("Exchange Configuration")

    exchange = st.selectbox(
        "Exchange",
        ["binance", "bybit"]
    )

    st.write("Selected:", exchange)

    if st.button("Save"):
        st.success("Configuration saved")