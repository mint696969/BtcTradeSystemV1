# path: ./btcts_next/src/btcts/prediction/tests/test_warroom_plain_candle_server.py
# desc: Compatibility boundary for legacy prediction chart data server import path.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[2]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.prediction.warroom_plain_candle_server as legacy  # noqa: E402
import btcts.processing.l4_consumer_models.operator_ui.warroom_chart_data_server as canonical  # noqa: E402


def test_prediction_chart_data_server_is_compatibility_shim_only() -> None:
    assert legacy.WARROOM_PLAIN_CANDLE_SERVER_COMPAT_ONLY is True
    assert legacy.WARROOM_PLAIN_CANDLE_SERVER_COMPAT_MODULE == "btcts.prediction.warroom_plain_candle_server"
    assert legacy.WARROOM_CHART_DATA_SERVER_CANONICAL_MODULE == "btcts.processing.l4_consumer_models.operator_ui.warroom_chart_data_server"
    assert legacy.WARROOM_CHART_DATA_SERVER_VERSION == canonical.WARROOM_CHART_DATA_SERVER_VERSION
    assert legacy.run_server is canonical.run_server
    assert legacy.build_plain_candle_server_payload is canonical.build_plain_candle_server_payload
