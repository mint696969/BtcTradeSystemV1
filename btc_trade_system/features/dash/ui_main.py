# path: ./btc_trade_system/features/dash/ui_main.py
# desc: メインタブのUIレンダラ（当面はダミー表示）。将来ここに複合カード群を実装。

from __future__ import annotations
import streamlit as st
from btc_trade_system.features.settings import settings_svc as S

def render() -> None:
    cfg = S.load_yaml("main")  # def ⊕ current
    title = (cfg.get("title") or "メイン").strip()
    st.subheader(title)

    st.info("メインタブは将来の複合ダッシュボードです。現在は器のみ先行作成しています。")
    st.caption("※ tabs.yaml で dashboard, settings, 並び順が制御されます。")
