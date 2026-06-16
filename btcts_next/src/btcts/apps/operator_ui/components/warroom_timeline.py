# path: ./btcts_next/src/btcts/apps/operator_ui/components/warroom_timeline.py
# desc: Replay / Research artifact から War Room 用の最新状況変化ログを組み立てて表示するタイムラインパネル。

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.warroom_timeline_state import (
    build_warroom_timeline_state,
)
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.ui_time import format_ui_ts


def render():
    lang = st.session_state.get("ui_lang", "en")

    st.markdown(f"### {get_text(lang, 'warroom_timeline_title')}")

    state = build_warroom_timeline_state(lang=lang)
    timeline = state["timeline"]
    timeline_is_live = bool(state["timeline_is_live"])

    if not timeline:
        st.info(get_text(lang, "warroom_timeline_empty"))
        st.divider()
        return

    for idx, item in enumerate(reversed(timeline)):
        c1, c2 = st.columns([6, 1])

        with c1:
            st.markdown(
                f"**{format_ui_ts(item['ts'], lang)}**  "
                f"{item['label']} → `{item['value']}`"
            )

        with c2:
            if not timeline_is_live:
                if st.button(
                    "Replay",
                    key=f"warroom_timeline_replay_{idx}",
                ):
                    st.session_state.replay_jump_ts = str(item["ts"])
                    st.session_state.ui_selected_page_key = "replay"
                    st.rerun()

    st.caption(get_text(lang, "warroom_timeline_caption"))
    st.divider()