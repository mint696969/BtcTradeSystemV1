# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_panel.py
# desc: War Room 向けの AI Operator パネル。live canonical 優先で現在の市場状態を要約し、research 補助付きで推奨アクションを提示する。

from __future__ import annotations

import streamlit as st

from btcts.apps.operator_ui.components.ai_operator_actions import (
    ask_ai_why,
    mark_watch_item,
    open_research_from_replay_context,
)
from btcts.apps.operator_ui.components.ai_operator_action_payloads import (
    build_research_replay_context,
    build_watch_item,
)
from btcts.apps.operator_ui.components.ai_operator_advisory import (
    read_operator_advisory_answer,
)
from btcts.apps.operator_ui.components.ai_operator_persistence import (
    persist_operator_decision,
)
from btcts.apps.operator_ui.components.ai_operator_presenter import (
    build_display_state,
)
from btcts.apps.operator_ui.components.ai_operator_tactic_presenter import (
    advisory_support_caption,
    build_tactic_interpretation_display_lines,
    build_tactic_stance_display_lines,
    prediction_snapshot_section_title,
    tactic_interpretation_support_caption,
    tactic_stance_section_title,
    tactic_stance_support_caption,
)
from btcts.apps.operator_ui.components.ai_operator_display_payloads import (
    build_operator_display_payloads,
)
from btcts.apps.operator_ui.components.ai_operator_display_sources import (
    load_operator_display_sources,
)
from btcts.apps.operator_ui.components.ai_operator_runtime_state import (
    ensure_operator_session_state,
    load_operator_runtime_state,
)
from btcts.apps.operator_ui.components.ai_operator_support_contract import (
    build_operator_support_contract,
)

from btcts.apps.operator_ui.ui_text import get_text


def render():
    lang = st.session_state.get("ui_lang", "en")

    ensure_operator_session_state(st.session_state)

    st.markdown(f"### {get_text(lang, 'ai_operator_title')}")

    runtime_state = load_operator_runtime_state(st.session_state)
    if not runtime_state:
        st.warning(get_text(lang, "ai_operator_missing_data"))
        st.divider()
        return

    state = runtime_state["state"]
    operator_memory = runtime_state["memory"]

    display_sources = load_operator_display_sources()
    summary_widget = display_sources["summary_widget"]
    prediction_widget = display_sources["prediction_widget"]
    tactic_context = display_sources.get("tactic_context")

    display_payloads = build_operator_display_payloads(
        summary_widget=summary_widget,
        prediction_widget=prediction_widget,
        watch_note=st.session_state.get("ai_operator_watch_note"),
        is_live_market=False,
        tactic_context=tactic_context,
    )
    operator_explanation_note = display_payloads["operator_explanation_note"]
    advisory_tactic_summary_lines = display_payloads["tactic_summary_lines"]
    advisory_tactic_interpretation_lines = display_payloads[
        "tactic_interpretation_lines"
    ]
    advisory_primary_tactic_interpretation_line = display_payloads[
        "primary_tactic_interpretation_line"
    ]
    advisory_tactic_primary_summary_line = display_payloads[
        "tactic_primary_summary_line"
    ]

    advisory_answer = read_operator_advisory_answer(
        lang=lang,
        ai_mode=st.session_state.ai_operator_mode,
        operator_prompt=get_text(lang, "ai_operator_prompt"),
        intent=get_text(lang, "ai_conversation_intent_decide"),
        style=get_text(lang, "ai_conversation_style_normal"),
        state=state,
        memory=operator_memory,
        note=operator_explanation_note,
        tactic_summary_lines=advisory_tactic_summary_lines,
        tactic_interpretation_lines=advisory_tactic_interpretation_lines,
        primary_tactic_interpretation_line=(
            advisory_primary_tactic_interpretation_line
        ),
        tactic_primary_summary_line=advisory_tactic_primary_summary_line,
    )
    answer = advisory_answer["answer"]
    runtime_source = advisory_answer["runtime_source"]
    advisory_note_used = advisory_answer["advisory_note_used"]

    support_contract = build_operator_support_contract(
        state=state,
        runtime_source=runtime_source,
        tactic_context=tactic_context,
    )
    action = support_contract["action"]
    risk = support_contract["risk"]
    decision_row = support_contract["decision_row"]
    support_context = support_contract["support_context"]
    research_replay_context = build_research_replay_context(support_context)
    watch_item = build_watch_item(support_context)

    persist_operator_decision(
        decision_row,
        st.session_state,
        max_items_hint=20,
    )

    display_state = build_display_state(
        lang=lang,
        state=state,
        action=action,
        risk=risk,
        answer=answer,
        runtime_source=runtime_source,
        ai_mode=st.session_state.ai_operator_mode,
    )
    display_ai_mode = display_state["display_ai_mode"]
    is_live_market = display_state["is_live_market"]
    display_action_label = display_state["display_action_label"]
    display_risk_label = display_state["display_risk_label"]
    display_notice_kind = display_state["display_notice_kind"]
    display_answer = display_state["display_answer"]
    status_caption = display_state["status_caption"]
    runtime_caption = display_state["runtime_caption"]

    display_payloads = build_operator_display_payloads(
        summary_widget=summary_widget,
        prediction_widget=prediction_widget,
        watch_note=st.session_state.get("ai_operator_watch_note"),
        is_live_market=is_live_market,
        tactic_context=tactic_context,
    )
    watch_note_caption = display_payloads["watch_note_caption"]
    summary_caption = display_payloads["summary_caption"]
    prediction_lines = display_payloads["prediction_lines"]
    tactic_summary_lines = display_payloads["tactic_summary_lines"]
    tactic_interpretation_lines = display_payloads["tactic_interpretation_lines"]
    primary_tactic_interpretation_line = display_payloads[
        "primary_tactic_interpretation_line"
    ]
    tactic_primary_summary_line = display_payloads["tactic_primary_summary_line"]

    c1, c2, c3 = st.columns(3)
    c1.metric(get_text(lang, "ai_operator_action"), display_action_label)
    c2.metric(get_text(lang, "ai_operator_risk"), display_risk_label)
    c3.metric(get_text(lang, "ai_operator_mode"), display_ai_mode)

    if display_notice_kind == "warning":
        st.warning(display_answer)
    else:
        st.info(display_answer)

    st.caption(status_caption)
    st.caption(runtime_caption)

    b1, b2, b3, b4 = st.columns(4)

    with b2:
        if st.button(
            get_text(lang, "ai_operator_open_research"),
            key="ai_operator_open_research",
        ):
            open_research_from_replay_context(research_replay_context)

    with b3:
        if st.button(
            get_text(lang, "ai_operator_ask_ai_why"),
            key="ai_operator_ask_why",
        ):
            ask_ai_why(lang)

    with b4:
        if st.button(
            get_text(lang, "ai_operator_mark_as_watch"),
            key="ai_operator_mark_watch",
        ):
            mark_watch_item(watch_item)

    if watch_note_caption:
        st.caption(watch_note_caption)

    if summary_caption:
        st.caption(summary_caption)

    if tactic_summary_lines:
        st.markdown(f"**{tactic_stance_section_title(lang)}**")
        st.caption(tactic_stance_support_caption(lang))
        for line in build_tactic_stance_display_lines(tactic_summary_lines, lang):
            st.markdown(f"- {line}")

        if (
            tactic_primary_summary_line
            or tactic_interpretation_lines
            or primary_tactic_interpretation_line
        ):
            st.caption(tactic_interpretation_support_caption(lang))

            if tactic_primary_summary_line:
                st.caption(f"★ {tactic_primary_summary_line}")

            if primary_tactic_interpretation_line:
                for line in build_tactic_interpretation_display_lines(
                    (primary_tactic_interpretation_line,),
                    lang,
                ):
                    st.caption(f"★ {line}")

            if tactic_interpretation_lines:
                for line in build_tactic_interpretation_display_lines(
                    tactic_interpretation_lines,
                    lang,
                ):
                    st.caption(line)

    if advisory_note_used:
        st.caption(advisory_support_caption(lang))

    if prediction_lines:
        st.markdown(f"**{prediction_snapshot_section_title(lang)}**")
        for line in prediction_lines:
            st.markdown(f"- {line}")

    st.divider()