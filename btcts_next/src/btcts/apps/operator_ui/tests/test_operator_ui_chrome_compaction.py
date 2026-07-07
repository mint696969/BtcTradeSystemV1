# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_operator_ui_chrome_compaction.py
# desc: Structural guard for compact shared Operator UI chrome. Display-only; no runtime/data mutation.

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[6]
APP = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/app.py"


def test_shared_app_brand_is_sidebar_chrome_not_body_header() -> None:
    text = APP.read_text(encoding="utf-8-sig")

    assert "def render_sidebar_brand(lang: str)" in text
    assert "btcts-sidebar-brand" in text
    assert "render_sidebar_brand(st.session_state.ui_lang)" in text
    assert "st.title(get_text(lang, \"app_title\"))" not in text
    assert "st.subheader(get_text(lang, \"app_subtitle\"))" not in text

    brand_pos = text.index("render_sidebar_brand(st.session_state.ui_lang)")
    lang_selector_pos = text.index("st.session_state.ui_lang = st.sidebar.selectbox(")
    assert brand_pos < lang_selector_pos


def test_sidebar_operator_panel_is_compact_label() -> None:
    text = APP.read_text(encoding="utf-8-sig")

    assert "def render_sidebar_section_label(label: str)" in text
    assert "btcts-sidebar-section-label" in text
    assert "render_sidebar_section_label(get_text(lang, \"sidebar_title\"))" in text
    assert "st.sidebar.title(get_text(lang, \"sidebar_title\"))" not in text


def test_viewport_top_padding_is_compacted_without_hiding_streamlit_toolbar() -> None:
    text = APP.read_text(encoding="utf-8-sig")

    assert "[data-testid=\"stMainBlockContainer\"]" in text
    assert "padding-top: 0.35rem !important;" in text
    assert "[data-testid=\"stSidebarContent\"]" in text
    assert "padding-top: 0.05rem !important;" in text
    assert "display: none" not in text
    assert "visibility: hidden" not in text

def test_sidebar_brand_is_readable_and_top_packed() -> None:
    text = APP.read_text(encoding="utf-8-sig")

    assert "font-size: 1.03rem;" in text
    assert "font-weight: 800;" in text
    assert "margin: 0.00rem 0 0.12rem 0;" in text


def test_warroom_navigation_uses_v2_page_under_war_room_label() -> None:
    text = APP.read_text(encoding="utf-8-sig")

    assert "warroom_page," not in text
    assert '("warroom", get_text(lang, "page_warroom"), warroom_page)' not in text
    assert '("warroom_v2", "WarRoom v2", warroom_v2_page)' not in text
    assert '("warroom_v2", get_text(lang, "page_warroom"), warroom_v2_page)' in text
    assert '"warroom": "warroom_v2"' in text
    assert "LEGACY_PAGE_KEY_REDIRECTS" in text

def test_sidebar_brand_has_live_jst_24h_clock() -> None:
    text = APP.read_text(encoding="utf-8-sig")

    assert "import streamlit.components.v1 as components" in text
    assert "def _sidebar_clock_html(lang: str)" in text
    assert "components.html(_sidebar_clock_html(lang), height=44)" in text
    assert "日本時間" not in text
    assert "btcts-clock-label" not in text
    assert "labelEl" not in text
    assert 'timeZone: "Asia/Tokyo"' in text
    assert "hour12: false" in text
    assert "window.setInterval(renderClock, 1000)" in text
    assert "font-size: 1.28rem;" in text
    assert "justify-content: center;" in text
    assert "min-height: 39px;" in text

def test_sidebar_navigation_is_visually_under_clock_before_settings() -> None:
    text = APP.read_text(encoding="utf-8-sig")

    brand_pos = text.index("render_sidebar_brand(st.session_state.ui_lang)")
    nav_slot_pos = text.index("nav_slot = st.sidebar.container()")
    lang_selector_pos = text.index("st.session_state.ui_lang = st.sidebar.selectbox(")
    assert brand_pos < nav_slot_pos < lang_selector_pos

    with_nav_pos = text.index("with nav_slot:")
    save_state_pos = text.index("save_ui_state(")
    assert with_nav_pos < save_state_pos
    assert "selection = st.sidebar.radio(" not in text
    assert "selection = st.radio(" in text


def test_operation_panel_and_uicheck_status_are_after_refresh_resolution() -> None:
    text = APP.read_text(encoding="utf-8-sig")

    refresh_plan_pos = text.index("refresh_plan = live_shell.resolve_page_refresh_plan(")
    operation_pos = text.index('render_sidebar_section_label(get_text(lang, "sidebar_title"))', refresh_plan_pos)
    dashboard_pos = text.index("render_dashboard_hub_status_strip(", operation_pos)
    assert refresh_plan_pos < operation_pos < dashboard_pos
    assert text.index("ui_check_save_status_slot = st.sidebar.empty()", operation_pos) < dashboard_pos
    assert 'st.sidebar.caption(get_text(lang, "refresh_status_off"))' not in text
    assert "st.sidebar.caption(" not in text
    assert "refresh_status_on" not in text

def test_live_shell_page_title_matches_warroom_sized_compact_heading() -> None:
    text = (REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/live_shell.py").read_text(encoding="utf-8-sig")

    assert ".live-shell-page-title" in text
    assert "font-size: 1.40rem;" in text
    assert "font-weight: 800;" in text
    assert "line-height: 1.12;" in text


def test_operator_page_top_headings_use_compact_labels() -> None:
    files = {
        "collector": REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/collector_page.py",
        "health": REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/health_page.py",
        "autotrade": REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/autotrade_page.py",
        "logs": REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/logs_page.py",
        "config": REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/config_page.py",
        "research": REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/research_page.py",
        "replay": REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/replay_page.py",
        "warroom": REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/compact_layout_view.py",
    }

    assert 'render_compact_page_header(get_text(lang, "page_collector"))' in files["collector"].read_text(encoding="utf-8-sig")
    assert 'render_compact_page_header(get_text(lang, "page_health"))' in files["health"].read_text(encoding="utf-8-sig")
    assert 'live_shell.render_compact_page_header("AutoTrade")' in files["autotrade"].read_text(encoding="utf-8-sig")
    assert 'live_shell.render_compact_page_header("Logs")' in files["logs"].read_text(encoding="utf-8-sig")
    assert 'live_shell.render_compact_page_header("Config")' in files["config"].read_text(encoding="utf-8-sig")
    assert 'render_compact_page_header(get_text(lang, "page_research"))' in files["research"].read_text(encoding="utf-8-sig")
    assert 'render_compact_page_header(get_text(lang, "page_replay"))' in files["replay"].read_text(encoding="utf-8-sig")
    assert 'st_api.subheader("War Room")' in files["warroom"].read_text(encoding="utf-8-sig")

    combined = "\n".join(p.read_text(encoding="utf-8-sig") for p in files.values())
    assert 'st.title("AutoTrade")' not in combined
    assert 'st.header("System Logs")' not in combined
    assert 'st.header("Exchange Configuration")' not in combined
    assert 'st.title(get_text(lang, "research_title"))' not in combined
    assert 'st.title(get_text(lang, "replay_title"))' not in combined
