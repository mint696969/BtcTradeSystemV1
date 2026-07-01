# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/market_regime/__init__.py
# desc: WarRoom market-regime adapters. Pure display mapping only; no page mount, Streamlit render, data-root read, or runtime writes.

from __future__ import annotations

from .card_adapter import (
    WARROOM_MARKET_REGIME_CARD_ADAPTER_VERSION,
    adapt_market_regime_prediction_packet_to_cards,
    build_warroom_market_regime_card_adapter_packet,
)
from .live_preview_dry_run import (
    WARROOM_MARKET_REGIME_LIVE_PREVIEW_DRY_RUN_VERSION,
    build_market_regime_live_preview_dry_run_packet,
)
from .preview_binding import (
    WARROOM_MARKET_REGIME_PREVIEW_BINDING_VERSION,
    build_market_regime_warroom_preview_binding_packet,
)

__all__ = [
    "WARROOM_MARKET_REGIME_CARD_ADAPTER_VERSION",
    "WARROOM_MARKET_REGIME_LIVE_PREVIEW_DRY_RUN_VERSION",
    "WARROOM_MARKET_REGIME_PREVIEW_BINDING_VERSION",
    "adapt_market_regime_prediction_packet_to_cards",
    "build_market_regime_live_preview_dry_run_packet",
    "build_market_regime_warroom_preview_binding_packet",
    "build_warroom_market_regime_card_adapter_packet",
]
