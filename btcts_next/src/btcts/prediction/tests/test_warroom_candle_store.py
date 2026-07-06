# path: ./btcts_next/src/btcts/prediction/tests/test_warroom_candle_store.py
# desc: Compatibility boundary for legacy prediction import path. Candle store implementation is canonical in L4 consumer models.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[2]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.prediction.warroom_candle_store as legacy  # noqa: E402
import btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store as canonical  # noqa: E402


def test_prediction_candle_store_is_compatibility_shim_only() -> None:
    assert legacy.WARROOM_CANDLE_STORE_COMPAT_ONLY is True
    assert legacy.WARROOM_CANDLE_STORE_COMPAT_MODULE == "btcts.prediction.warroom_candle_store"
    assert legacy.WARROOM_CANDLE_STORE_CANONICAL_MODULE == "btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store"
    assert legacy.WARROOM_CANDLE_STORE_VERSION == canonical.WARROOM_CANDLE_STORE_VERSION
    assert legacy.update_candle_store_from_latest_part is canonical.update_candle_store_from_latest_part
