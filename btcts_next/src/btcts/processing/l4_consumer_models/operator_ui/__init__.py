# path: ./btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/__init__.py
# desc: Thin operator UI adapter package over shared L4 bundles.

"""
Operator UI adapters.

Rules:
- thin conversion only
- do not redefine market meaning
- do not own layout or CSS
- do not produce widget-library-final render shapes
"""

from .market_summary_adapter import (
    MarketSummaryWidgetModel,
    market_summary_status_payload,
    market_summary_widget_model,
)

__all__ = [
    "MarketSummaryWidgetModel",
    "market_summary_status_payload",
    "market_summary_widget_model",
]