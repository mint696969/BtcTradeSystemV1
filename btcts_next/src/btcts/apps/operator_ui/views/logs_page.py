# path: ./btcts_next/src/btcts/apps/operator_ui/views/logs_page.py
# desc: Collector / System のログを表示する Operator Logs ページ。

import streamlit as st


def render():

    st.header("System Logs")

    logs = [
        "collector started",
        "exchange connected",
        "trade event received",
    ]

    for log in logs:
        st.code(log)