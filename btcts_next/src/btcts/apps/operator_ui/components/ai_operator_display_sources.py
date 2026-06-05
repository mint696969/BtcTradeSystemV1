# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_display_sources.py
# desc: AI Operator の display source widget 読込を分離した境界。

from __future__ import annotations

from btcts.apps.operator_ui.components.market_state_bridge import (
    load_market_summary_widget_model,
    load_prediction_summary_widget_model,
    load_prediction_review_hint_summary_payload,
    load_prediction_tactic_proposal_payload,
)
from btcts.apps.operator_ui.components.review_hint_presenter import (
    review_hint_display_sections,
)


def load_operator_display_sources() -> dict:
    review_hint_context = load_prediction_review_hint_summary_payload()
    return {
        "summary_widget": load_market_summary_widget_model(),
        "prediction_widget": load_prediction_summary_widget_model(),
        "tactic_context": load_prediction_tactic_proposal_payload(),
        "review_hint_context": review_hint_context,
        "review_hint_display": review_hint_display_sections(review_hint_context),
    }
