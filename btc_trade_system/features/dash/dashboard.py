# path: ./btc_trade_system/features/dash/dashboard.py
# desc: StreamlitメインUI（Health/Audit）。features配下の新タブにも対応

from __future__ import annotations
import sys, pathlib
import streamlit as st

# V1ルートを sys.path に（保険）
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from btc_trade_system.features.dash.ui_health import render as health_render
from btc_trade_system.features.dash.ui_audit import render as audit_render


# 歯車コンポーネント（単一の正規位置に統一）
from btc_trade_system.apps.components.settings_modal import settings_gear

st.set_page_config(page_title="BtcTS V1", layout="wide")
st.title("BtcTradeSystem V1 ダッシュボード")

# 右上に歯車（クリックでモーダル表示）
settings_gear()

# 設定はモーダルに集約したのでタブは2つ（健康・監査）のみ
tab1, tab2 = st.tabs(["コレクターの健全性", "監査ログ"])
with tab1:
    health_render()
with tab2:
    audit_render()
