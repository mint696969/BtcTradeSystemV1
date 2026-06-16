# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_display_sources.py
# desc: AI Operator の display source widget 読込を分離した境界。

from __future__ import annotations

from btcts.apps.operator_ui.components.market_state_bridge import (
    load_execution_market_summary_widget_model,
    load_execution_market_prediction_summary_widget_model,
    load_execution_market_prediction_tactic_proposal_payload,
    load_prediction_review_hint_summary_payload,
)
from btcts.apps.operator_ui.components.review_hint_presenter import (
    review_hint_display_sections,
)

AI_OPERATOR_DISPLAY_SOURCE_CATALOG = (
    {
        "source_key": "summary_widget",
        "source_type": "execution_market_summary_widget_model",
        "consumer_scope": ("dashboard", "collector_tab", "warroom_tab", "health_tab", "future_widget"),
        "read_only_contract": True,
        "widget_reusable": True,
        "layout_decision_free": True,
    },
    {
        "source_key": "prediction_widget",
        "source_type": "execution_market_prediction_summary_widget_model",
        "consumer_scope": ("dashboard", "ai_tab", "prediction_tab", "future_widget"),
        "read_only_contract": True,
        "widget_reusable": True,
        "layout_decision_free": True,
    },
    {
        "source_key": "tactic_context",
        "source_type": "execution_market_prediction_tactic_context",
        "consumer_scope": ("ai_tab", "prediction_tab", "future_widget"),
        "read_only_contract": True,
        "widget_reusable": True,
        "layout_decision_free": True,
    },
    {
        "source_key": "review_hint_context",
        "source_type": "prediction_review_hint_summary_context",
        "consumer_scope": ("ai_tab", "prediction_tab", "position_tab", "execution_tab", "future_widget"),
        "read_only_contract": True,
        "widget_reusable": True,
        "layout_decision_free": True,
    },
    {
        "source_key": "review_hint_display",
        "source_type": "prediction_review_hint_display_context",
        "consumer_scope": ("ai_tab", "prediction_tab", "position_tab", "execution_tab", "future_widget"),
        "read_only_contract": True,
        "widget_reusable": True,
        "layout_decision_free": True,
    },
)


def load_operator_display_source_catalog() -> tuple[dict, ...]:
    return tuple(dict(item) for item in AI_OPERATOR_DISPLAY_SOURCE_CATALOG)



def load_operator_display_sources() -> dict:
    review_hint_context = load_prediction_review_hint_summary_payload()
    return {
        "summary_widget": load_execution_market_summary_widget_model(),
        "prediction_widget": load_execution_market_prediction_summary_widget_model(),
        "tactic_context": load_execution_market_prediction_tactic_proposal_payload(),
        "review_hint_context": review_hint_context,
        "review_hint_display": review_hint_display_sections(review_hint_context),
        "source_catalog": load_operator_display_source_catalog(),
    }
