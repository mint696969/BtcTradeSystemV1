# path: ./btcts_next/src/btcts/apps/operator_ui/app.py
# desc: BTC-TS Operator UI のエントリ。Streamlit サイドバーで各 Operator ページを切り替える。

import streamlit as st

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.views import (
    collector_page,
    health_page,
    logs_page,
    config_page,
    research_page,
    replay_page,
    warroom_page,
)
from btcts.apps.operator_ui.ui_state_store import load_ui_state, save_ui_state

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
    layout="wide",
)

persisted_ui_state = load_ui_state()

if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = persisted_ui_state.get("ui_lang", "en")

if "ui_scale" not in st.session_state:
    st.session_state.ui_scale = persisted_ui_state.get("ui_scale", "100%")

if "ui_auto_refresh" not in st.session_state:
    st.session_state.ui_auto_refresh = persisted_ui_state.get("ui_auto_refresh", True)

if "ui_refresh_interval" not in st.session_state:
    st.session_state.ui_refresh_interval = persisted_ui_state.get("ui_refresh_interval", 5)

if "ui_selected_page_key" not in st.session_state:
    st.session_state.ui_selected_page_key = persisted_ui_state.get("ui_selected_page_key", "collector")

st.session_state.ui_lang = st.sidebar.selectbox(
    get_text(st.session_state.ui_lang, "lang_label"),
    ["ja", "en"],
    index=["ja", "en"].index(st.session_state.ui_lang),
    key="ui_lang_selector",
)

lang = st.session_state.ui_lang

st.session_state.ui_scale = st.sidebar.selectbox(
    get_text(lang, "scale_label"),
    ["50%", "75%", "100%"],
    index=["50%", "75%", "100%"].index(st.session_state.ui_scale),
    key="ui_scale_selector",
)

st.session_state.ui_auto_refresh = st.sidebar.checkbox(
    get_text(lang, "refresh_label"),
    value=st.session_state.ui_auto_refresh,
    key="ui_auto_refresh_checkbox",
)

st.session_state.ui_refresh_interval = st.sidebar.selectbox(
    get_text(lang, "refresh_interval_label"),
    [3, 5, 10, 15, 30],
    index=[3, 5, 10, 15, 30].index(st.session_state.ui_refresh_interval),
    key="ui_refresh_interval_selector",
)

apply_ui_scale(st.session_state.ui_scale)

st.title(get_text(lang, "app_title"))
st.subheader(get_text(lang, "app_subtitle"))

page_defs = [
    ("collector", get_text(lang, "page_collector"), collector_page),
    ("warroom", get_text(lang, "page_warroom"), warroom_page),
    ("health", get_text(lang, "page_health"), health_page),
    ("logs", get_text(lang, "page_logs"), logs_page),
    ("config", get_text(lang, "page_config"), config_page),
    ("research", get_text(lang, "page_research"), research_page),
    ("replay", get_text(lang, "page_replay"), replay_page),
]

page_keys = [page_key for page_key, _, _ in page_defs]
page_labels = [page_label for _, page_label, _ in page_defs]
page_label_to_key = {page_label: page_key for page_key, page_label, _ in page_defs}
pages = {page_key: page_module for page_key, _, page_module in page_defs}

if st.session_state.ui_selected_page_key not in page_keys:
    st.session_state.ui_selected_page_key = page_keys[0]

selected_page_label = next(
    page_label
    for page_key, page_label, _ in page_defs
    if page_key == st.session_state.ui_selected_page_key
)

st.sidebar.title(get_text(lang, "sidebar_title"))

selection = st.sidebar.radio(
    get_text(lang, "sidebar_nav"),
    page_labels,
    index=page_labels.index(selected_page_label),
    key="ui_sidebar_page_radio",
)

st.session_state.ui_selected_page_key = page_label_to_key[selection]

save_ui_state(
    {
        "ui_lang": st.session_state.ui_lang,
        "ui_selected_page_key": st.session_state.ui_selected_page_key,
        "ui_scale": st.session_state.ui_scale,
        "ui_auto_refresh": st.session_state.ui_auto_refresh,
        "ui_refresh_interval": st.session_state.ui_refresh_interval,
    }
)

selected_page_key = str(st.session_state.ui_selected_page_key)
page_module = pages[selected_page_key]

live_shell.reset_registered_slots(selected_page_key)
page_module.render()

is_slot_refresh_target = live_shell.page_supports_auto_refresh(selected_page_key)
is_auto_refresh_target = selected_page_key == "logs" or is_slot_refresh_target

effective_refresh_interval_sec = int(st.session_state.ui_refresh_interval)
if is_slot_refresh_target:
    slot_recommended_interval_sec = live_shell.page_auto_refresh_interval_sec(
        selected_page_key,
        default_sec=effective_refresh_interval_sec,
    )
    effective_refresh_interval_sec = min(
        effective_refresh_interval_sec,
        int(slot_recommended_interval_sec),
    )

if st.session_state.ui_auto_refresh and is_auto_refresh_target:
    st.sidebar.caption(
        f"{get_text(lang, 'refresh_status_on')} / {effective_refresh_interval_sec}s"
    )
else:
    st.sidebar.caption(get_text(lang, "refresh_status_off"))

# Auto refresh は live / monitor 系ページに限定する
live_shell.render_page_auto_refresh(
    enabled=bool(st.session_state.ui_auto_refresh and is_auto_refresh_target),
    interval_sec=effective_refresh_interval_sec,
    page_key=selected_page_key,
)