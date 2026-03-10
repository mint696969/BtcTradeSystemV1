# path: ./btcts_next/src/btcts/apps/operator_ui/app.py
# desc: BTC-TS Operator UI のエントリ。Streamlit サイドバーで各 Operator ページを切り替える。

import time
import streamlit as st

from btcts.apps.operator_ui.views import (
    collector_page,
    health_page,
    logs_page,
    config_page,
    research_page,
    replay_page,
)
from btcts.apps.operator_ui.ui_text import get_text


def apply_ui_scale(scale: str):

    scale_map = {
        "50%": 0.50,
        "75%": 0.75,
        "100%": 1.00,
    }

    factor = scale_map.get(scale, 0.75)

    st.markdown(
        f"""
        <style>
        html, body, [class*="css"] {{
            font-size: {factor}em;
        }}

        div[data-testid="stMetric"] label,
        div[data-testid="stMetricValue"],
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] li,
        div[data-testid="stDataFrame"] {{
            font-size: {factor}em !important;
        }}

        h1 {{
            font-size: {2.2 * factor}rem !important;
        }}

        h2 {{
            font-size: {1.8 * factor}rem !important;
        }}

        h3 {{
            font-size: {1.4 * factor}rem !important;
        }}

        .warroom-badges {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 0.4rem;
            margin-bottom: 0.8rem;
        }}

        .warroom-badge {{
            display: inline-block;
            padding: 0.18rem 0.55rem;
            border-radius: 0.5rem;
            font-weight: 700;
            font-size: 0.95em;
            border: 1px solid rgba(255,255,255,0.08);
        }}

        .badge-buy {{
            background: rgba(34, 197, 94, 0.18);
            color: #86efac;
        }}

        .badge-sell {{
            background: rgba(239, 68, 68, 0.18);
            color: #fca5a5;
        }}

        .badge-wait {{
            background: rgba(59, 130, 246, 0.18);
            color: #93c5fd;
        }}

        .badge-neutral {{
            background: rgba(156, 163, 175, 0.18);
            color: #d1d5db;
        }}

        .badge-risk-high {{
            background: rgba(245, 158, 11, 0.18);
            color: #fcd34d;
        }}

        .badge-risk-low {{
            background: rgba(34, 197, 94, 0.18);
            color: #86efac;
        }}
                
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="BTC-TS Operator",
    layout="wide"
)

if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = "ja"

if "ui_scale" not in st.session_state:
    st.session_state.ui_scale = "100%"

if "ui_auto_refresh" not in st.session_state:
    st.session_state.ui_auto_refresh = True

if "ui_refresh_interval" not in st.session_state:
    st.session_state.ui_refresh_interval = 5

st.session_state.ui_lang = st.sidebar.selectbox(
    get_text(st.session_state.ui_lang, "lang_label"),
    ["ja", "en"],
    index=["ja", "en"].index(st.session_state.ui_lang),
)

lang = st.session_state.ui_lang

st.session_state.ui_scale = st.sidebar.selectbox(
    get_text(lang, "scale_label"),
    ["50%", "75%", "100%"],
    index=["50%", "75%", "100%"].index(st.session_state.ui_scale),
)

st.session_state.ui_auto_refresh = st.sidebar.checkbox(
    get_text(lang, "refresh_label"),
    value=st.session_state.ui_auto_refresh,
)

st.session_state.ui_refresh_interval = st.sidebar.selectbox(
    get_text(lang, "refresh_interval_label"),
    [3, 5, 10, 15, 30],
    index=[3, 5, 10, 15, 30].index(st.session_state.ui_refresh_interval),
)

apply_ui_scale(st.session_state.ui_scale)

st.title(get_text(lang, "app_title"))
st.subheader(get_text(lang, "app_subtitle"))

pages = {
    get_text(lang, "page_collector"): collector_page,
    get_text(lang, "page_health"): health_page,
    get_text(lang, "page_logs"): logs_page,
    get_text(lang, "page_config"): config_page,
    get_text(lang, "page_research"): research_page,
    get_text(lang, "page_replay"): replay_page,
}

st.sidebar.title(get_text(lang, "sidebar_title"))

selection = st.sidebar.radio(
    get_text(lang, "sidebar_nav"),
    list(pages.keys())
)

if st.session_state.ui_auto_refresh:
    st.sidebar.caption(
        f"{get_text(lang, 'refresh_status_on')} / {st.session_state.ui_refresh_interval}s"
    )
else:
    st.sidebar.caption(get_text(lang, "refresh_status_off"))

pages[selection].render()

if st.session_state.ui_auto_refresh:
    time.sleep(st.session_state.ui_refresh_interval)
    st.rerun()