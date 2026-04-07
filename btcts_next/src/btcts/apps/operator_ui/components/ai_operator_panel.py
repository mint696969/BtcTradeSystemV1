# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_panel.py
# desc: War Room 向けの AI Operator パネル。live canonical 優先で現在の市場状態を要約し、research 補助付きで推奨アクションを提示する。

from __future__ import annotations

import streamlit as st
from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_summary_widget_model,
)
from btcts.apps.operator_ui.components.market_summary_presenter import (
    summary_widget_caption,
)
from btcts.apps.operator_ui.decision_log_store import append_decision
from btcts.apps.operator_ui.ai_memory_store import (
    append_memory,
    load_recent_memory,
)
from btcts.apps.operator_ui.ai_runtime import (
    default_mode,
    generate_answer,
)
from btcts.apps.operator_ui.components.ai_operator_logic import (
    operator_action,
    operator_action_label,
    operator_risk,
    operator_risk_label,
)
from btcts.apps.operator_ui.components.ai_operator_state import (
    analyze_operator_state,
)
from btcts.apps.operator_ui.components.ai_operator_actions import (
    ask_ai_why,
    mark_as_watch,
    open_research_from_operator_context,
)
from btcts.apps.operator_ui.components.ai_operator_presenter import (
    build_decision_state,
    build_display_state,
)

from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.ui_time import format_ui_ts


def render():
    lang = st.session_state.get("ui_lang", "en")

    if "ai_operator_mode" not in st.session_state:
        st.session_state.ai_operator_mode = default_mode()

    if "ai_operator_memory" not in st.session_state:
        st.session_state.ai_operator_memory = load_recent_memory(max_items=8)

    st.markdown(f"### {get_text(lang, 'ai_operator_title')}")

    state = analyze_operator_state()
    if not state:
        st.warning(get_text(lang, "ai_operator_missing_data"))
        st.divider()
        return

    summary_widget = load_market_summary_widget_model()

    latest_memory_entry = {
        "spread": state["spread"],
        "imbalance": state["imbalance"],
        "delta": state["delta"],
        "wall_ratio": state["wall_ratio"],
    }

    memory = st.session_state.ai_operator_memory
    if not memory or any(
        abs(latest_memory_entry[k] - memory[0][k]) > 1e-9
        for k in latest_memory_entry
    ):
        st.session_state.ai_operator_memory = append_memory(
            latest_memory_entry,
            max_items_hint=8,
        )

    action = operator_action(state)
    risk = operator_risk(state)

    operator_prompt = get_text(lang, "ai_operator_prompt")
    answer, runtime_source = generate_answer(
        mode=st.session_state.ai_operator_mode,
        lang=lang,
        prompt=operator_prompt,
        state=state,
        note="",
        memory=st.session_state.ai_operator_memory,
        intent=get_text(lang, "ai_conversation_intent_decide"),
        style=get_text(lang, "ai_conversation_style_normal"),
    )

    decision_state = build_decision_state(
        state=state,
        action=action,
        risk=risk,
        runtime_source=runtime_source,
    )
    decision_row = decision_state["decision_row"]
    operator_context = decision_state["operator_context"]

    merged_decisions, persisted = append_decision(
        decision_row,
        max_items_hint=20,
    )
    st.session_state.ai_operator_decision_log = merged_decisions
    st.session_state.ai_operator_decision_persisted = persisted

    display_state = build_display_state(
        lang=lang,
        state=state,
        answer=answer,
        runtime_source=runtime_source,
        ai_mode=st.session_state.ai_operator_mode,
    )
    display_ai_mode = display_state["display_ai_mode"]
    is_live_market = display_state["is_live_market"]
    display_answer = display_state["display_answer"]

    c1, c2, c3 = st.columns(3)
    c1.metric(get_text(lang, "ai_operator_action"), operator_action_label(lang, action))
    c2.metric(get_text(lang, "ai_operator_risk"), operator_risk_label(lang, risk))
    c3.metric(get_text(lang, "ai_operator_mode"), display_ai_mode)

    if runtime_source == "fallback-local" and not is_live_market:
        st.warning(display_answer)
    else:
        st.info(display_answer)

    st.caption(
        f"regime={state['regime']} / best_strategy={state['best_strategy']} / "
        f"pressure_bias={state['pressure_bias']} / ts={format_ui_ts(state['event_ts'], lang)}"
    )
    if is_live_market:
        st.caption(
            f"{get_text(lang, 'ai_runtime_source')}=live-local / "
            f"market_source={state.get('data_source', 'unknown')}"
        )
    else:
        st.caption(
            f"{get_text(lang, 'ai_runtime_source')}={runtime_source} / "
            f"market_source={state.get('data_source', 'unknown')}"
        )

    b1, b2, b3, b4 = st.columns(4)

    with b2:
        if st.button(
            get_text(lang, "ai_operator_open_research"),
            key="ai_operator_open_research",
        ):
            open_research_from_operator_context(operator_context)

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
            mark_as_watch(operator_context)

    watch_note = st.session_state.get("ai_operator_watch_note")
    if watch_note and not is_live_market:
        st.caption(
            f"watch ts={watch_note.get('ts')} / "
            f"regime={watch_note.get('regime')} / "
            f"action={watch_note.get('action')} / "
            f"risk={watch_note.get('risk')}"
        )

    if summary_widget:
        st.caption(summary_widget_caption(summary_widget))

    st.divider()