# path: ./btcts_next/src/btcts/apps/operator_ui/components/system_stats.py
# desc: Derived summary (latest_hourly.json) を読み、Collector の統計情報を表示する WarRoom パネル

import streamlit as st
import json
from pathlib import Path
from btcts.apps.operator_ui.ui_text import get_text

DERIVED_PATH = Path(r"E:\btc_ts\logs\derived\latest_hourly.json")


def render():

    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'system_stats_title')}")

    if not DERIVED_PATH.exists():
        st.warning(get_text(lang, "system_stats_not_found"))
        return

    try:
        data = json.loads(DERIVED_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        st.error(f"{get_text(lang, 'system_stats_load_error')}: {e}")
        return

    collector = data.get("collector", {})
    http = collector.get("http", {})

    c1, c2, c3 = st.columns(3)

    c1.metric(get_text(lang, "system_stats_http_total"), http.get("total", 0))
    c2.metric(get_text(lang, "system_stats_http_429"), http.get("status_429", 0))
    c3.metric(get_text(lang, "system_stats_restarts"), collector.get("proc_restart_count", 0))

    st.divider()