# path: ./btc_trade_system/features/dash/ui_collector.py
# desc: Collector タブの薄い入口（説明＋設定モーダル誘導）

import streamlit as st
from btc_trade_system.features.audit_dev import writer as W

def render():
    st.subheader("コレクター")
    st.caption("収集状況や閾値の調整は右上の⚙️から。詳細な遅延・異常は Health／監査で確認。")
    if st.button("設定を開く", use_container_width=True):
        st.session_state["__settings_open"] = True
        W.emit("settings.open", level="INFO", feature="settings",
               payload={"source": "tab:collector"})

def get_status() -> str:
    # 将来：監査やメトリクスから warn/crit/urgent へ昇格
    return "normal"

