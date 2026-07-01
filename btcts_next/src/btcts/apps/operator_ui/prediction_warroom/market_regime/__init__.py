# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/market_regime/__init__.py
# desc: WarRoom market-regime adapters. Pure display mapping only; no page mount, Streamlit render, data-root read, or runtime writes.

from __future__ import annotations

from .card_adapter import (
    WARROOM_MARKET_REGIME_CARD_ADAPTER_VERSION,
    adapt_market_regime_prediction_packet_to_cards,
    build_warroom_market_regime_card_adapter_packet,
)

__all__ = [
    "WARROOM_MARKET_REGIME_CARD_ADAPTER_VERSION",
    "adapt_market_regime_prediction_packet_to_cards",
    "build_warroom_market_regime_card_adapter_packet",
]
