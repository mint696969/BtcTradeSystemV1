# path: ./btcts_next/src/btcts/prediction/warroom_candle_store.py
# desc: Compatibility shim. Canonical WarRoom candle store lives in L4 consumer models.

from __future__ import annotations

from btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store import *  # noqa: F401,F403
from btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store import WARROOM_CANDLE_STORE_CANONICAL_MODULE, WARROOM_CANDLE_STORE_LAYER, WARROOM_CANDLE_STORE_VERSION

WARROOM_CANDLE_STORE_COMPAT_MODULE = "btcts.prediction.warroom_candle_store"
WARROOM_CANDLE_STORE_COMPAT_ONLY = True
