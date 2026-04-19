# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_display_sources.py
# desc: AI Operator の display source widget 読込を分離した境界。

from __future__ import annotations

from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_summary_widget_model,
    load_prediction_summary_widget_model,
)


def load_operator_display_sources() -> dict:
    return {
        "summary_widget": load_market_summary_widget_model(),
        "prediction_widget": load_prediction_summary_widget_model(),
    }