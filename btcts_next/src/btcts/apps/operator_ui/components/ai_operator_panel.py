# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_panel.py
# desc: War Room 向けの AI Operator パネル。現在の市場状態を要約し、推奨アクションを提示する。

from __future__ import annotations

import streamlit as st
from btcts.apps.operator_ui.decision_log_store import append_decision
from btcts.apps.operator_ui.ai_memory_store import (
    append_memory,
    load_recent_memory,
)
from btcts.apps.operator_ui.ai_runtime import (
    default_mode,
    generate_answer,
)
from btcts.apps.operator_ui.components.research_bridge import (
    board_signal_metrics,
    latest_best_strategy_name,
    latest_board_row,
    latest_regime_name,
    latest_trade_row,
    load_latest_experiment_payload,
    load_latest_replay_payload,
    tradeflow_metrics,
)
from btcts.apps.operator_ui.ui_text import get_text


def _analyze_state():
    replay_payload = load_latest_replay_payload()
    experiment_payload = load_latest_experiment_payload()

    board = board_signal_metrics(latest_board_row(replay_payload))
    flow = tradeflow_metrics(latest_trade_row(replay_payload))

    if not board or not flow:
        return None

    spread = board.get("spread")
    imbalance = board.get("imbalance")
    delta = flow.get("trade_delta")
    wall_ratio = board.get("wall_ratio")

    if spread is None or imbalance is None or delta is None or wall_ratio is None:
        return None

    return {
        "spread": float(spread),
        "imbalance": float(imbalance),
        "delta": float(delta),
        "wall_ratio": float(wall_ratio),
        "regime": latest_regime_name(experiment_payload),
        "best_strategy": latest_best_strategy_name(experiment_payload),
        "pressure_bias": board.get("pressure_bias"),
        "event_ts": flow.get("event_ts") or board.get("event_ts"),
    }


def _operator_action(state: dict) -> str:
    imbalance = state["imbalance"]
    delta = state["delta"]
    wall_ratio = state["wall_ratio"]
    regime = state["regime"]

    if regime == "trend_up" and imbalance > 0.2 and delta > 0.2:
        return "long_watch"

    if regime == "trend_down" and imbalance < -0.2 and delta < -0.2:
        return "short_watch"

    if abs(wall_ratio) > 0.45:
        return "trap_caution"

    return "wait"


def _operator_risk(state: dict) -> str:
    spread = state["spread"]
    imbalance = state["imbalance"]
    delta = state["delta"]
    wall_ratio = state["wall_ratio"]

    score = 0

    if spread > 7000:
        score += 2
    elif spread > 4500:
        score += 1

    if (imbalance > 0.2 and delta < 0) or (imbalance < -0.2 and delta > 0):
        score += 2

    if abs(wall_ratio) > 0.45:
        score += 2
    elif abs(wall_ratio) > 0.25:
        score += 1

    if score >= 4:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def _operator_action_label(lang: str, value: str) -> str:
    mapping = {
        "long_watch": get_text(lang, "ai_operator_action_long_watch"),
        "short_watch": get_text(lang, "ai_operator_action_short_watch"),
        "trap_caution": get_text(lang, "ai_operator_action_trap_caution"),
        "wait": get_text(lang, "ai_operator_action_wait"),
    }
    return mapping.get(value, value)


def _operator_risk_label(lang: str, value: str) -> str:
    mapping = {
        "low": get_text(lang, "ai_operator_risk_low"),
        "medium": get_text(lang, "ai_operator_risk_medium"),
        "high": get_text(lang, "ai_operator_risk_high"),
    }
    return mapping.get(value, value)


def render():
    lang = st.session_state.get("ui_lang", "en")

    if "ai_operator_mode" not in st.session_state:
        st.session_state.ai_operator_mode = default_mode()

    if "ai_operator_memory" not in st.session_state:
        st.session_state.ai_operator_memory = load_recent_memory(max_items=8)

    st.markdown(f"### {get_text(lang, 'ai_operator_title')}")

    state = _analyze_state()
    if not state:
        st.warning(get_text(lang, "ai_operator_missing_data"))
        st.divider()
        return

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

    action = _operator_action(state)
    risk = _operator_risk(state)

    spread_state = "normal"
    if state["spread"] > 7000:
        spread_state = "wide"
    elif state["spread"] < 3000:
        spread_state = "tight"

    imbalance_state = "mixed"
    if state["imbalance"] > 0.2:
        imbalance_state = "bid_bias"
    elif state["imbalance"] < -0.2:
        imbalance_state = "ask_bias"

    delta_state = "mixed"
    if state["delta"] > 0.2:
        delta_state = "buy_flow"
    elif state["delta"] < -0.2:
        delta_state = "sell_flow"

    wall_state = "neutral"
    if state["wall_ratio"] > 0.25:
        wall_state = "bid_wall"
    elif state["wall_ratio"] < -0.25:
        wall_state = "ask_wall"

    operator_context = {
        "event_ts": state.get("event_ts"),
        "regime": state.get("regime"),
        "best_strategy": state.get("best_strategy"),
        "pressure_bias": state.get("pressure_bias"),
        "suggested_action": action,
        "risk": risk,
    }

    c1, c2, c3 = st.columns(3)
    c1.metric(get_text(lang, "ai_operator_action"), _operator_action_label(lang, action))
    c2.metric(get_text(lang, "ai_operator_risk"), _operator_risk_label(lang, risk))
    c3.metric(get_text(lang, "ai_operator_mode"), st.session_state.ai_operator_mode)

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

    decision_row = {
        "ts": state.get("event_ts"),
        "regime": state.get("regime"),
        "spread_state": spread_state,
        "imbalance_state": imbalance_state,
        "delta_state": delta_state,
        "wall_state": wall_state,
        "action": action,
        "risk": risk,
        "runtime_source": runtime_source,
    }

    merged_decisions, persisted = append_decision(
        decision_row,
        max_items_hint=20,
    )
    st.session_state.ai_operator_decision_log = merged_decisions
    st.session_state.ai_operator_decision_persisted = persisted

    if runtime_source == "fallback-local":
        st.warning(answer)
    else:
        st.info(answer)

    st.caption(
        f"regime={state['regime']} / best_strategy={state['best_strategy']} / "
        f"pressure_bias={state['pressure_bias']} / ts={state['event_ts']} / "
        f"{get_text(lang, 'ai_runtime_source')}={runtime_source}"
    )

    b1, b2, b3, b4 = st.columns(4)

    with b1:
        if st.button(
            get_text(lang, "ai_operator_send_to_replay"),
            key="ai_operator_send_to_replay",
        ):
            if operator_context.get("event_ts"):
                st.session_state.replay_jump_ts = str(operator_context["event_ts"])
            st.session_state.ui_selected_page = get_text(lang, "page_replay")
            st.rerun()

    with b2:
        if st.button(
            get_text(lang, "ai_operator_open_research"),
            key="ai_operator_open_research",
        ):
            st.session_state.research_replay_context = {
                "session_name": "warroom_ai_operator",
                "start_ts": "",
                "end_ts": "",
                "jump_ts": operator_context.get("event_ts") or "",
                "kind_filter": "all",
                "event_filter": operator_context.get("pressure_bias") or "",
                "filtered_rows": 1,
            }
            st.session_state.ui_selected_page = get_text(lang, "page_research")
            st.rerun()

    with b3:
        if st.button(
            get_text(lang, "ai_operator_ask_ai_why"),
            key="ai_operator_ask_why",
        ):
            st.session_state.ai_conversation_custom_prompt_input = (
                "Why is this the suggested action right now?"
                if lang == "en"
                else "なぜ今この推奨アクションになるのか説明してください。"
            )
            st.session_state.ui_selected_page = get_text(lang, "page_warroom")
            st.rerun()

    with b4:
        if st.button(
            get_text(lang, "ai_operator_mark_as_watch"),
            key="ai_operator_mark_watch",
        ):
            st.session_state.ai_operator_watch_note = {
                "ts": operator_context.get("event_ts"),
                "regime": operator_context.get("regime"),
                "action": operator_context.get("suggested_action"),
                "risk": operator_context.get("risk"),
            }
            st.success(get_text(lang, "ai_operator_watch_saved"))

    watch_note = st.session_state.get("ai_operator_watch_note")
    if watch_note:
        st.caption(
            f"watch ts={watch_note.get('ts')} / "
            f"regime={watch_note.get('regime')} / "
            f"action={watch_note.get('action')} / "
            f"risk={watch_note.get('risk')}"
        )

    st.divider()