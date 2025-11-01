# path: btc_trade_system/features/dash/ui_settings.py
# desc: ダッシュボード側の薄い入り口（健全性タブの説明UIへ導線／詳細は右上ギアの設定モーダル）

from __future__ import annotations
import streamlit as st

# dev_audit
from btc_trade_system.features.audit_dev import writer as W

def render():
    st.subheader("設定（ダッシュボード）")
    st.info("詳細な設定は、右上の ⚙️ から開く『設定』モーダルで行います。", icon="ℹ️")

    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("設定を開く（モーダル）", use_container_width=True):
            # ダイアログの開閉は settings.settings_gear() 側で管理
            st.session_state["__settings_open"] = True
            W.emit("settings.open", level="INFO", feature="settings", payload={"source": "tab_entry"})
            st.toast("右上の⚙️→設定が開きます。", icon="✅")
    with c2:
        st.caption("配色・デモアラート・健全性の閾値などはモーダルの各タブで編集できます。")
