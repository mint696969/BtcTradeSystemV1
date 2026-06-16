# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_presenter.py
# desc: AI Operator の表示専用派生 state を組み立てる presenter 層。

from __future__ import annotations

from btcts.apps.operator_ui.components.ai_operator_logic import (
    operator_action_label,
    operator_risk_label,
)
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.ui_time import format_ui_ts


def build_display_state(
    *,
    lang: str,
    state: dict,
    action: str,
    risk: str,
    answer: str,
    runtime_source: str,
    ai_mode: str,
) -> dict:
    is_live_market = state.get("data_source") in {
        "execution_market_live_canonical",
        "live_canonical",
    }

    display_ai_mode = ai_mode
    if is_live_market and runtime_source == "fallback-local":
        display_ai_mode = "live-local"

    display_notice_kind = "info"
    if runtime_source == "fallback-local" and not is_live_market:
        display_notice_kind = "warning"

    display_answer = answer
    if is_live_market and runtime_source == "fallback-local":
        answer_lines = answer.splitlines()
        body_lines = answer_lines[2:] if len(answer_lines) >= 2 else answer_lines
        display_answer = (
            f"{get_text(lang, 'ai_operator_live_local_prefix')}\n\n"
            + "\n".join(body_lines).lstrip()
        )

    status_caption = (
        f"regime={state['regime']} / best_strategy={state['best_strategy']} / "
        f"pressure_bias={state['pressure_bias']} / ts={format_ui_ts(state['event_ts'], lang)}"
    )

    if is_live_market:
        runtime_caption = (
            f"{get_text(lang, 'ai_runtime_source')}=live-local / "
            f"market_source={state.get('data_source', 'unknown')}"
        )
    else:
        runtime_caption = (
            f"{get_text(lang, 'ai_runtime_source')}={runtime_source} / "
            f"market_source={state.get('data_source', 'unknown')}"
        )

    return {
        "is_live_market": is_live_market,
        "display_action_label": operator_action_label(lang, action),
        "display_risk_label": operator_risk_label(lang, risk),
        "display_ai_mode": display_ai_mode,
        "display_notice_kind": display_notice_kind,
        "display_answer": display_answer,
        "status_caption": status_caption,
        "runtime_caption": runtime_caption,
    }