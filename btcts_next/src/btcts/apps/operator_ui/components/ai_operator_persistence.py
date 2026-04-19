# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_persistence.py
# desc: AI Operator の decision persist を panel から分離した persistence boundary。

from __future__ import annotations

from btcts.apps.operator_ui.decision_log_store import append_decision


def persist_operator_decision(
    decision_row: dict,
    session_state,
    *,
    max_items_hint: int = 20,
) -> None:
    merged_decisions, persisted = append_decision(
        decision_row,
        max_items_hint=max_items_hint,
    )
    session_state.ai_operator_decision_log = merged_decisions
    session_state.ai_operator_decision_persisted = persisted