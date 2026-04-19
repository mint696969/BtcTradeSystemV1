# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_support_contract.py
# desc: AI Operator の deterministic support contract を組み立てる境界。

from __future__ import annotations

from btcts.apps.operator_ui.components.ai_operator_logic import (
    operator_action,
    operator_risk,
)


def build_operator_support_contract(*, state: dict, runtime_source: str) -> dict:
    action = operator_action(state)
    risk = operator_risk(state)

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
        "action": action,
        "risk": risk,
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
        "support_context": {
            "event_ts": state.get("event_ts"),
            "regime": state.get("regime"),
            "best_strategy": state.get("best_strategy"),
            "pressure_bias": state.get("pressure_bias"),
            "advisory_action": action,
            "advisory_risk": risk,
            "runtime_source": runtime_source,
        },
    }