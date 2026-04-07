# path: ./btcts_next/src/btcts/apps/operator_ui/components/decision_log_panel.py
# desc: War Room 向けの AI Operator Decision Log 表示パネル。

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
from btcts.apps.operator_ui.decision_log_store import (
    decision_log_jsonl_path,
    load_recent_decisions,
    overwrite_decisions,
)
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.ui_time import format_ui_ts
from btcts.apps.operator_ui.watch_store import append_watch


def _ensure_decision_log():
    if "ai_operator_decision_log" not in st.session_state:
        st.session_state.ai_operator_decision_log = load_recent_decisions(max_items=5)


def render():
    lang = st.session_state.get("ui_lang", "en")

    _ensure_decision_log()

    st.markdown(f"### {get_text(lang, 'decision_log_title')}")

    rows = st.session_state.ai_operator_decision_log[:5]
    persisted_flag = st.session_state.get("ai_operator_decision_persisted")
    summary_widget = load_market_summary_widget_model()

    if persisted_flag is False:
        st.warning(get_text(lang, "decision_log_persist_failed"))
        st.caption(
            f"{get_text(lang, 'decision_log_storage_path')}: {decision_log_jsonl_path()} / "
            f"{get_text(lang, 'decision_log_storage_state')}: session-only"
        )
    elif persisted_flag is True:
        st.caption(
            f"{get_text(lang, 'decision_log_storage_path')}: {decision_log_jsonl_path()} / "
            f"{get_text(lang, 'decision_log_storage_state')}: persisted"
        )

    if not rows:
        st.info(get_text(lang, "decision_log_empty"))
        st.divider()
        return

    with st.expander(f"{get_text(lang, 'decision_log_title')} (latest 5)", expanded=False):
        for real_idx, item in enumerate(st.session_state.ai_operator_decision_log[:5]):
            c1, c2, c3, c4, c5 = st.columns([4, 1, 1, 1, 1])

            with c1:
                st.markdown(
                    f"**ts**={format_ui_ts(item.get('ts'), lang)} / "
                    f"regime={item.get('regime') or '-'} / "
                    f"spread={item.get('spread_state') or '-'} / "
                    f"imbalance={item.get('imbalance_state') or '-'} / "
                    f"delta={item.get('delta_state') or '-'} / "
                    f"wall={item.get('wall_state') or '-'} / "
                    f"action={item.get('action') or '-'} / "
                    f"risk={item.get('risk') or '-'} / "
                    f"src={item.get('runtime_source') or '-'}"
                )

            with c2:
                if st.button(
                    get_text(lang, "decision_log_replay"),
                    key=f"decision_log_replay_{real_idx}",
                ):
                    if item.get("ts"):
                        st.session_state.replay_jump_ts = str(item["ts"])
                    st.session_state.ui_selected_page_key = "replay"
                    st.rerun()

            with c3:
                if st.button(
                    get_text(lang, "decision_log_research"),
                    key=f"decision_log_research_{real_idx}",
                ):
                    st.session_state.research_replay_context = {
                        "session_name": "ai_operator_decision_log",
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
                    get_text(lang, "decision_log_watch"),
                    key=f"decision_log_watch_{real_idx}",
                ):
                    watch_row = {
                        "ts": item.get("ts"),
                        "regime": item.get("regime"),
                        "action": item.get("action"),
                        "risk": item.get("risk"),
                    }
                    merged_watch, persisted = append_watch(
                        watch_row,
                        max_items_hint=12,
                    )
                    st.session_state.ai_operator_watch_list = merged_watch
                    st.session_state.ai_operator_watch_persisted = persisted
                    st.success(get_text(lang, "decision_log_watch_added"))

            with c5:
                if st.button(
                    get_text(lang, "decision_log_remove"),
                    key=f"decision_log_remove_{real_idx}",
                ):
                    original_rows = st.session_state.ai_operator_decision_log
                    new_rows = original_rows[:real_idx] + original_rows[real_idx + 1 :]
                    st.session_state.ai_operator_decision_log = new_rows
                    ok = overwrite_decisions(new_rows)
                    st.session_state.ai_operator_decision_persisted = ok
                    st.rerun()

        if st.button(
            get_text(lang, "decision_log_clear_all"),
            key="decision_log_clear_all_button",
        ):
            st.session_state.ai_operator_decision_log = []
            ok = overwrite_decisions([])
            st.session_state.ai_operator_decision_persisted = ok
            st.rerun()

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))

    st.divider()