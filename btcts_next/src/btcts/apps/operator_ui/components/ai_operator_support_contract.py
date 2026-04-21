# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_support_contract.py
# desc: AI Operator の deterministic support contract を組み立てる境界。

from __future__ import annotations

from btcts.apps.operator_ui.components.ai_operator_logic import (
    operator_action,
    operator_risk,
)
from btcts.apps.operator_ui.components.ai_operator_tactic_context import (
    build_operator_tactic_context,
)
from btcts.apps.operator_ui.components.ai_operator_tactic_presenter import (
    build_primary_tactic_interpretation_line,
    build_tactic_interpretation_lines,
    build_tactic_primary_summary_line,
    build_tactic_stance_lines,
)


def build_operator_support_contract(
    *,
    state: dict,
    runtime_source: str,
    tactic_context: dict | None = None,
) -> dict:
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

    normalized_tactic_context = build_operator_tactic_context(tactic_context)
    tactic_summary_lines = build_tactic_stance_lines(normalized_tactic_context)
    tactic_interpretation_lines = build_tactic_interpretation_lines(
        normalized_tactic_context
    )
    primary_tactic_interpretation_line = (
        build_primary_tactic_interpretation_line(
            normalized_tactic_context
        )
    )
    tactic_primary_summary_line = build_tactic_primary_summary_line(
        normalized_tactic_context
    )

    support_context = {
        "event_ts": state.get("event_ts"),
        "regime": state.get("regime"),
        "best_strategy": state.get("best_strategy"),
        "pressure_bias": state.get("pressure_bias"),
        "advisory_action": action,
        "advisory_risk": risk,
        "runtime_source": runtime_source,
    }
    if normalized_tactic_context:
        support_context["tactic_context"] = normalized_tactic_context
    if tactic_summary_lines:
        support_context["tactic_summary_lines"] = tactic_summary_lines
    if tactic_interpretation_lines:
        support_context["tactic_interpretation_lines"] = tactic_interpretation_lines
    if primary_tactic_interpretation_line:
        support_context["primary_tactic_interpretation_line"] = (
            primary_tactic_interpretation_line
        )
    if tactic_primary_summary_line:
        support_context["tactic_primary_summary_line"] = (
            tactic_primary_summary_line
        )

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
        "support_context": support_context,
    }