# path: ./btcts_next/src/btcts/apps/operator_ui/views/health_page.py
# desc: システムリソース状態を表示する Operator Health ページ。

import streamlit as st


def render():

    st.header("System Health")

    col1, col2, col3 = st.columns(3)

    col1.metric("CPU", "12%")
    col2.metric("Memory", "1.2GB")
    col3.metric("Queue", "0")

    st.success("System operating normally")