# path: ./btcts_next/src/btcts/apps/operator_ui/app.py
# desc: BTC-TS Operator UI のエントリ。Streamlit サイドバーで各 Operator ページを切り替える。

import html

import streamlit as st
import streamlit.components.v1 as components
import time

from btcts.apps.operator_ui.components import live_shell
from btcts.apps.operator_ui.views import (
    collector_page,
    health_page,
    logs_page,
    config_page,
    research_page,
    replay_page,
    warroom_v2_page,
    autotrade_page,
)
from btcts.apps.operator_ui.ui_state_store import load_ui_state, save_ui_state
from btcts.apps.operator_ui.ui_check_exporter import (
    load_gpt_ui_check_auto_save_enabled,
    save_gpt_ui_check_auto_save_enabled,
    save_gpt_ui_check_snapshot,
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

        [data-testid="stMainBlockContainer"] {{
            padding-top: 0.35rem !important;
        }}

        [data-testid="stSidebarContent"] {{
            padding-top: 0.05rem !important;
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

        .btcts-sidebar-brand {{
            margin: 0.00rem 0 0.12rem 0;
            font-size: 1.03rem;
            font-weight: 800;
            line-height: 1.04;
            letter-spacing: 0.005em;
            color: rgba(49, 51, 63, 0.96);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .btcts-sidebar-section-label {{
            margin: 0.72rem 0 0.20rem 0;
            font-size: 0.78rem;
            font-weight: 700;
            line-height: 1.10;
            letter-spacing: 0.02em;
            color: rgba(49, 51, 63, 0.70);
        }}

        .btcts-page-top-label {{
            margin: 0.00rem 0 0.38rem 0;
            font-size: 1.18rem;
            font-weight: 850;
            line-height: 1.08;
            letter-spacing: 0.01em;
            color: rgba(49, 51, 63, 0.82);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
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



def _sidebar_clock_html(lang: str) -> str:
    """Return a display-only live JST 24-hour clock for the sidebar brand area."""
    return """
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<style>
html, body {
    margin: 0;
    padding: 0;
    background: transparent;
    overflow: hidden;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.btcts-clock {
    box-sizing: border-box;
    width: 100%;
    min-height: 39px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.10rem 0.42rem;
    border-radius: 0.42rem;
    background: rgba(49, 51, 63, 0.055);
    border: 1px solid rgba(49, 51, 63, 0.08);
    color: rgba(49, 51, 63, 0.86);
    white-space: nowrap;
}
.btcts-clock-time {
    font-size: 1.28rem;
    font-weight: 850;
    font-variant-numeric: tabular-nums;
    letter-spacing: 0.035em;
}
</style>
</head>
<body>
<div class="btcts-clock" aria-label="JST 24-hour clock">
  <span id="btcts-clock-time" class="btcts-clock-time">--:--:--</span>
</div>
<script>
const timeEl = document.getElementById("btcts-clock-time");
const formatter = new Intl.DateTimeFormat("ja-JP", {
  timeZone: "Asia/Tokyo",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false
});
function renderClock() {
  timeEl.textContent = formatter.format(new Date());
}
renderClock();
window.setInterval(renderClock, 1000);
</script>
</body>
</html>
"""


def render_sidebar_brand(lang: str) -> None:
    """Render the shared app brand in the sidebar without consuming main viewport height."""
    title = html.escape(get_text(lang, "app_title"))
    st.sidebar.markdown(
        f"<div class='btcts-sidebar-brand'>{title}</div>",
        unsafe_allow_html=True,
    )
    with st.sidebar:
        components.html(_sidebar_clock_html(lang), height=44)


def render_page_top_label(label: str) -> None:
    """Render a compact selected-page label above the page body."""
    safe_label = html.escape(str(label))
    st.markdown(
        f"<div class='btcts-page-top-label'>{safe_label}</div>",
        unsafe_allow_html=True,
    )


def _page_top_scroll_html() -> str:
    """Return a display-only script that scrolls the parent Streamlit view to top."""
    return """
<!doctype html>
<html>
<body style="margin:0;padding:0;overflow:hidden">
<script>
(function scrollOperatorPageToTop() {
  const parentWindow = window.parent;
  const parentDocument = parentWindow.document;
  const candidates = [
    parentDocument.querySelector('[data-testid="stAppViewContainer"]'),
    parentDocument.querySelector('[data-testid="stMain"]'),
    parentDocument.querySelector('section.main'),
    parentDocument.scrollingElement,
  ].filter(Boolean);

  function forceTop() {
    for (const element of candidates) {
      try { element.scrollTo({ top: 0, left: 0, behavior: 'auto' }); } catch (err) { /* ignore unsupported targets */ }
      try { element.scrollTop = 0; } catch (err) { /* ignore read-only targets */ }
    }
    try { parentWindow.scrollTo({ top: 0, left: 0, behavior: 'auto' }); } catch (err) { /* ignore */ }
  }

  parentWindow.requestAnimationFrame(() => {
    parentWindow.requestAnimationFrame(forceTop);
  });
  parentWindow.setTimeout(forceTop, 80);
  parentWindow.setTimeout(forceTop, 240);
})();
</script>
</body>
</html>
"""


def render_page_change_scroll_to_top(*, page_changed: bool) -> None:
    """Scroll only after sidebar navigation, not on refresh or same-page reruns."""
    if not page_changed:
        return
    components.html(_page_top_scroll_html(), height=0)


def render_sidebar_section_label(label: str) -> None:
    safe_label = html.escape(str(label))
    st.sidebar.markdown(
        f"<div class='btcts-sidebar-section-label'>{safe_label}</div>",
        unsafe_allow_html=True,
    )


def render_dashboard_hub_status_strip(
    *,
    lang: str,
    selected_page_label: str,
    selected_page_key: str,
    refresh_plan: dict,
) -> None:
    """Render a display-only dashboard hub status strip after page render.

    This does not decide market meaning, load data, or change routing. It only
    summarizes current UI navigation/refresh state and registered widget count.
    """
    slot_rows = live_shell.get_registered_slots(selected_page_key)
    registered_widget_count = len(slot_rows)
    refresh_visible = bool(refresh_plan.get("refresh_status_visible"))
    refresh_interval = int(refresh_plan.get("effective_refresh_interval_sec") or 0)
    alert_key = (
        "dashboard_hub_alert_normal"
        if registered_widget_count > 0
        else "dashboard_hub_alert_attention"
    )

    with live_shell.panel_container(
        label=get_text(lang, "dashboard_hub_status_title"),
        tone="neutral",
        help_text=get_text(lang, "dashboard_hub_status_caption"),
    ):
        c1, c2, c3 = st.columns(3)
        c1.metric(get_text(lang, "dashboard_hub_selected_page"), selected_page_label)
        c2.metric(
            get_text(lang, "dashboard_hub_refresh"),
            f"{refresh_interval}s" if refresh_visible else get_text(lang, "refresh_status_off"),
        )
        c3.metric(
            get_text(lang, "dashboard_hub_registered_widgets"),
            registered_widget_count,
        )
        st.caption(get_text(lang, alert_key))

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

LEGACY_PAGE_KEY_REDIRECTS = {
    "warroom": "warroom_v2",
}
st.session_state.ui_selected_page_key = LEGACY_PAGE_KEY_REDIRECTS.get(
    str(st.session_state.ui_selected_page_key),
    st.session_state.ui_selected_page_key,
)

render_sidebar_brand(st.session_state.ui_lang)
nav_slot = st.sidebar.container()

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
    help=get_text(lang, "refresh_help"),
)

st.session_state.ui_refresh_interval = st.sidebar.selectbox(
    get_text(lang, "refresh_interval_label"),
    [3, 5, 10, 15, 30],
    index=[3, 5, 10, 15, 30].index(st.session_state.ui_refresh_interval),
    key="ui_refresh_interval_selector",
)

apply_ui_scale(st.session_state.ui_scale)

# Shared app brand is rendered as compact sidebar chrome to preserve vertical viewport.

page_defs = [
    ("collector", get_text(lang, "page_collector"), collector_page),
    ("warroom_v2", get_text(lang, "page_warroom"), warroom_v2_page),
    ("autotrade", get_text(lang, "page_autotrade"), autotrade_page),
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

if "ui_check_auto_save_enabled" not in st.session_state:
    st.session_state.ui_check_auto_save_enabled = load_gpt_ui_check_auto_save_enabled()

with nav_slot:
    selection = st.radio(
        get_text(lang, "sidebar_nav"),
        page_labels,
        index=page_labels.index(selected_page_label),
        key="ui_sidebar_page_radio",
    )

st.session_state.ui_selected_page_key = page_label_to_key[selection]
selected_page_label = selection
selected_page_key = str(st.session_state.ui_selected_page_key)
previous_page_key = str(st.session_state.get("_ui_last_rendered_page_key") or "")
page_changed = bool(previous_page_key and previous_page_key != selected_page_key)

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
render_page_top_label(selected_page_label)
page_render_started_at = time.perf_counter()
page_module.render()
page_render_elapsed_ms = int((time.perf_counter() - page_render_started_at) * 1000)
render_page_change_scroll_to_top(page_changed=page_changed)

refresh_plan = live_shell.resolve_page_refresh_plan(
    page_key=selected_page_key,
    ui_auto_refresh=bool(st.session_state.ui_auto_refresh),
    ui_refresh_interval_sec=int(st.session_state.ui_refresh_interval),
)

effective_refresh_interval_sec = int(
    refresh_plan["effective_refresh_interval_sec"]
)

render_sidebar_section_label(get_text(lang, "sidebar_title"))
previous_auto_save_enabled = bool(st.session_state.ui_check_auto_save_enabled)
st.session_state.ui_check_auto_save_enabled = st.sidebar.checkbox(
    "GPT UI Auto Save",
    value=previous_auto_save_enabled,
    key="ui_check_auto_save_checkbox",
    help="Save one GPT-facing UI Check file after a full page render. Turn this off during normal browsing.",
)
ui_check_auto_save_enabled = bool(st.session_state.ui_check_auto_save_enabled)
if ui_check_auto_save_enabled != previous_auto_save_enabled:
    save_gpt_ui_check_auto_save_enabled(ui_check_auto_save_enabled)

ui_check_save_status_slot = st.sidebar.empty()
if not ui_check_auto_save_enabled:
    ui_check_save_status_slot.caption("GPT UI Check auto-save is OFF")

render_dashboard_hub_status_strip(
    lang=lang,
    selected_page_label=selected_page_label,
    selected_page_key=selected_page_key,
    refresh_plan=refresh_plan,
)

if ui_check_auto_save_enabled:
    try:
        auto_ui_check_path = save_gpt_ui_check_snapshot(
            page_key=selected_page_key,
            page_label=selected_page_label,
            previous_page_key=previous_page_key,
            page_changed=page_changed,
            refresh_plan=refresh_plan,
            session_state=st.session_state,
            slot_registry=live_shell.get_registered_slots(selected_page_key),
            page_render_ms=page_render_elapsed_ms,
            human_note="post-render auto snapshot; auto-save toggle was ON; captured after full page render without a snapshot button rerun",
        )
        st.session_state["_ui_last_post_render_uicheck_path"] = auto_ui_check_path
        ui_check_save_status_slot.success(f"GPT UI Check saved: {auto_ui_check_path}")
    except Exception as exc:
        st.session_state["_ui_last_post_render_uicheck_error"] = repr(exc)
        ui_check_save_status_slot.warning(f"GPT UI Check auto-save failed: {exc}")

# Auto refresh は live / monitor 系ページに限定する
live_shell.render_page_auto_refresh(
    enabled=bool(refresh_plan["page_reload_enabled"]),
    interval_sec=effective_refresh_interval_sec,
    page_key=selected_page_key,
)

st.session_state["_ui_last_rendered_page_key"] = selected_page_key
