# path: ./btc_trade_system/features/dash/ui_main.py
# desc: メインタブの箱（後続で取引サポート・値動き・予測などを実装）

import streamlit as st

def render():
    # メインタブの外側ラッパ（クラス名だけ付与）
    st.markdown("<div class='main-tab'>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
