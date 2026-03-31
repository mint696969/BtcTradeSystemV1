# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_presenter.py
# desc: AI Operator の表示用派生 state を組み立てる presenter 層。

from __future__ import annotations

from btcts.apps.operator_ui.ui_text import get_text


def build_decision_state(state: dict, action: str, risk: str, runtime_source: str) -> dict:
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

    return {
        "spread_state": spread_state,
        "imbalance_state": imbalance_state,
        "delta_state": delta_state,
        "wall_state": wall_state,
        "decision_row": {
            "ts": state.get("event_ts"),
            "regime": state.get("regime"),
            "spread_state": spread_state,
            "imbalance_state": imbalance_state,
            "delta_state": delta_state,
            "wall_state": wall_state,
            "action": action,
            "risk": risk,
            "runtime_source": runtime_source,
        },
        "operator_context": {
            "event_ts": state.get("event_ts"),
            "regime": state.get("regime"),
            "best_strategy": state.get("best_strategy"),
            "pressure_bias": state.get("pressure_bias"),
            "suggested_action": action,
            "risk": risk,
        },
    }


def build_display_state(
    *,
    lang: str,
    state: dict,
    answer: str,
    runtime_source: str,
    ai_mode: str,
) -> dict:
    is_live_market = state.get("data_source") == "live_canonical"

    display_ai_mode = ai_mode
    if is_live_market and runtime_source == "fallback-local":
        display_ai_mode = "live-local"

    display_answer = answer
    if is_live_market and runtime_source == "fallback-local":
        answer_lines = answer.splitlines()
        body_lines = answer_lines[2:] if len(answer_lines) >= 2 else answer_lines
        display_answer = (
            f"{get_text(lang, 'ai_operator_live_local_prefix')}\n\n"
            + "\n".join(body_lines).lstrip()
        )

    return {
        "is_live_market": is_live_market,
        "display_ai_mode": display_ai_mode,
        "display_answer": display_answer,
    }