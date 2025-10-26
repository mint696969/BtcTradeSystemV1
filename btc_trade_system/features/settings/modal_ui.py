# path: ./btc_trade_system/features/settings/modal_ui.py
# desc: 右上の歯車→モーダル（ダイアログ）で設定を開く

from __future__ import annotations
import streamlit as st

# 既存の設定UIを流用（健全性タブで作ったもの）
from btc_trade_system.features.settings import settings_ui as settings_tab
# 今回追加: dash 側の設定UI（監査モード含む）
from btc_trade_system.features.dash.ui_settings import render as render_settings_ui

# Streamlit の dialog API（正式 or experimental）を吸収
_DLG = getattr(st, "dialog", None) or getattr(st, "experimental_dialog", None)

if _DLG is None:
    # 古いStreamlitの場合のフォールバック（サイドバー）
    def settings_gear():
        # 右上寄せの歯車
        c1, c2 = st.columns([9, 1])
        with c2:
            if st.button("⚙️", help="設定", use_container_width=True, key="gear_fallback"):
                st.sidebar.header("設定")
                tabs = st.sidebar.tabs(["基本設定", "健全性", "監査"])
                with tabs[0]:
                    render_settings_ui()  # ← dash 側のUIをここに追加
                with tabs[1]:
                    settings_tab.render()
                with tabs[2]:
                    st.subheader("監査（将来）")
                    st.write("・監査ログの保存期間、サイズ上限、サンプリング等")
else:
    # ダイアログ本体
    @_DLG("設定")
    def _open_settings_dialog():
        tabs = st.tabs(["基本設定", "健全性", "監査"])
        with tabs[0]:
            st.subheader("全体設定")
            st.caption("ダッシュボード全体に関わる基本設定（将来の拡張用）")
            # ↓ここに dash 側の設定UIを統合（運転モード切替など）
            render_settings_ui()
        with tabs[1]:
            settings_tab.render()  # ← 既存の健全性設定UIをそのまま流用
        with tabs[2]:
            st.subheader("監査（将来）")
            st.write("・監査ログの保存期間、サイズ上限、サンプリング等")

    def settings_gear():
        # 右上寄せの歯車（モーダル起動）
        c1, c2 = st.columns([9, 1])
        with c2:
            if st.button("⚙️", help="設定", use_container_width=True, key="gear_dialog"):
                _open_settings_dialog()

