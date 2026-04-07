# path: ./btcts_next/src/btcts/apps/operator_ui/components/watch_list_panel.py
# desc: War Room 向けの Watch List パネル。AI Operator や手動監視で保存した注目局面を一覧表示し、Replay / Research へ飛べる。

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.ui_time import format_ui_ts
from btcts.apps.operator_ui.watch_store import (
    append_watch,
    load_recent_watch_list,
    overwrite_watch_list,
    watch_jsonl_path,
)


def _ensure_watch_list():
    if "ai_operator_watch_list" not in st.session_state:
        st.session_state.ai_operator_watch_list = load_recent_watch_list(max_items=12)


def _normalize_watch_item(item: dict) -> dict:
    return {
        "ts": item.get("ts"),
        "regime": item.get("regime"),
        "action": item.get("action"),
        "risk": item.get("risk"),
    }


def _sync_latest_watch_note():
    latest = st.session_state.get("ai_operator_watch_note")
    if not latest:
        return

    normalized = _normalize_watch_item(latest)
    watch_list = st.session_state.ai_operator_watch_list

    if not watch_list or watch_list[0] != normalized:
        merged, persisted = append_watch(
            normalized,
            max_items_hint=12,
        )
        st.session_state.ai_operator_watch_list = merged
        st.session_state.ai_operator_watch_persisted = persisted


def render():
    lang = st.session_state.get("ui_lang", "en")

    _ensure_watch_list()
    _sync_latest_watch_note()

    st.markdown(f"### {get_text(lang, 'watch_list_title')}")

    watch_list = st.session_state.ai_operator_watch_list
    persisted_flag = st.session_state.get("ai_operator_watch_persisted")
    summary_widget = load_market_summary_widget_model()

    if persisted_flag is False:
        st.warning(get_text(lang, "watch_list_persist_failed"))
        st.caption(
            f"{get_text(lang, 'watch_list_storage_path')}: {watch_jsonl_path()} / "
            f"{get_text(lang, 'watch_list_storage_state')}: session-only"
        )
    elif persisted_flag is True:
        st.caption(
            f"{get_text(lang, 'watch_list_storage_path')}: {watch_jsonl_path()} / "
            f"{get_text(lang, 'watch_list_storage_state')}: persisted"
        )

    if not watch_list:
        st.info(get_text(lang, "watch_list_empty"))
        st.divider()
        return

    for idx, item in enumerate(watch_list):
        c1, c2, c3, c4 = st.columns([4, 1, 1, 1])

        with c1:
            st.markdown(
                f"**ts**={format_ui_ts(item.get('ts'), lang)} / "
                f"regime={item.get('regime') or '-'} / "
                f"action={item.get('action') or '-'} / "
                f"risk={item.get('risk') or '-'}"
            )

        with c2:
            if st.button(
                get_text(lang, "watch_list_replay"),
                key=f"watch_replay_{idx}",
            ):
                if item.get("ts"):
                    st.session_state.replay_jump_ts = str(item["ts"])
                st.session_state.ui_selected_page_key = "replay"
                st.rerun()

        with c3:
            if st.button(
                get_text(lang, "watch_list_research"),
                key=f"watch_research_{idx}",
            ):
                st.session_state.research_replay_context = {
                    "session_name": "watch_list",
                    "start_ts": "",
                    "end_ts": "",
                    "jump_ts": item.get("ts") or "",
                    "kind_filter": "all",
                    "event_filter": item.get("action") or "",
                    "filtered_rows": 1,
                }
                st.session_state.ui_selected_page_key = "research"
                st.rerun()

        with c4:
            if st.button(
                get_text(lang, "watch_list_remove"),
                key=f"watch_remove_{idx}",
            ):
                new_list = watch_list[:idx] + watch_list[idx + 1 :]
                st.session_state.ai_operator_watch_list = new_list
                ok = overwrite_watch_list(new_list)
                st.session_state.ai_operator_watch_persisted = ok
                st.rerun()

    if st.button(
        get_text(lang, "watch_list_clear_all"),
        key="watch_list_clear_all_button",
    ):
        st.session_state.ai_operator_watch_list = []
        st.session_state.ai_operator_watch_note = None
        ok = overwrite_watch_list([])
        st.session_state.ai_operator_watch_persisted = ok
        st.rerun()

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))

    st.divider()