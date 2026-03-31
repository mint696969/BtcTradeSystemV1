# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_actions.py
# desc: AI Operator の UI action（research遷移 / AI問い直し / watch登録）を分離した action 層。

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.watch_store import append_watch


def open_research_from_operator_context(operator_context: dict) -> None:
    st.session_state.research_replay_context = {
        "session_name": "warroom_ai_operator",
        "start_ts": "",
        "end_ts": "",
        "jump_ts": operator_context.get("event_ts") or "",
        "kind_filter": "all",
        "event_filter": operator_context.get("pressure_bias") or "",
        "filtered_rows": 1,
    }
    st.session_state.ui_selected_page_key = "research"
    st.rerun()


def ask_ai_why(lang: str) -> None:
    st.session_state.ai_conversation_custom_prompt_input = (
        "Why is this the suggested action right now?"
        if lang == "en"
        else "なぜ今この推奨アクションになるのか説明してください。"
    )
    st.rerun()


def mark_as_watch(operator_context: dict) -> None:
    watch_item = {
        "ts": operator_context.get("event_ts"),
        "regime": operator_context.get("regime"),
        "action": operator_context.get("suggested_action"),
        "risk": operator_context.get("risk"),
    }
    merged, persisted = append_watch(
        watch_item,
        max_items_hint=12,
    )
    st.session_state.ai_operator_watch_list = merged
    st.session_state.ai_operator_watch_persisted = persisted
    st.session_state.ai_operator_watch_note = watch_item
    st.session_state.ui_selected_page_key = "warroom"
    st.rerun()