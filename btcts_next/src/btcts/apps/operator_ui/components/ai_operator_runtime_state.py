# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_runtime_state.py
# desc: AI Operator の session 初期化 / state 読込 / memory 同期を分離した runtime state boundary。

from __future__ import annotations

from btcts.apps.operator_ui.ai_memory_store import (
    append_memory,
    load_recent_memory,
)
from btcts.apps.operator_ui.ai_runtime import (
    default_mode,
)
from btcts.apps.operator_ui.components.ai_operator_state import (
    analyze_operator_state,
)


def ensure_operator_session_state(session_state) -> None:
    if "ai_operator_mode" not in session_state:
        session_state.ai_operator_mode = default_mode()

    if "ai_operator_memory" not in session_state:
        session_state.ai_operator_memory = load_recent_memory(max_items=8)


def load_operator_runtime_state(session_state) -> dict | None:
    state = analyze_operator_state()
    if not state:
        return None

    latest_memory_entry = {
        "spread": state["spread"],
        "imbalance": state["imbalance"],
        "delta": state["delta"],
        "wall_ratio": state["wall_ratio"],
    }

    memory = session_state.ai_operator_memory
    if not memory or any(
        abs(latest_memory_entry[k] - memory[0][k]) > 1e-9
        for k in latest_memory_entry
    ):
        session_state.ai_operator_memory = append_memory(
            latest_memory_entry,
            max_items_hint=8,
        )

    return {
        "state": state,
        "memory": session_state.ai_operator_memory,
    }