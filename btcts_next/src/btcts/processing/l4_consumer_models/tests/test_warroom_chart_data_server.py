# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_warroom_chart_data_server.py
# desc: Verify WarRoom plain candle read-only chart endpoint payload builder.

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

_SRC_ROOT = Path(__file__).resolve().parents[2]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.operator_ui.warroom_candle_store import WARROOM_CANDLE_STORE_VERSION  # noqa: E402
from btcts.processing.l4_consumer_models.operator_ui.warroom_chart_data_server import (  # noqa: E402
    WARROOM_CHART_DATA_SERVER_CANONICAL_MODULE,
    WARROOM_CHART_DATA_SERVER_LAYER,
    WARROOM_CHART_DATA_SERVER_VERSION,
    WARROOM_PLAIN_CANDLE_SERVER_VERSION,
    cache_frame_to_chart_candles,
)


def test_cache_frame_to_chart_candles_is_frontend_ready_and_read_only_shape() -> None:
    frame = pd.DataFrame(
        [
            {"time_utc": "2026-07-06T17:56:00Z", "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0, "volume": 1.2, "trade_count": 3},
            {"time_utc": "2026-07-06T17:57:00Z", "open": 101.0, "high": 103.0, "low": 100.0, "close": 102.0, "volume": 1.5, "trade_count": 4},
        ]
    )
    candles = cache_frame_to_chart_candles(frame)
    assert len(candles) == 2
    assert candles[0]["time_utc"] == "2026-07-06T17:56:00Z"
    assert candles[0]["time_jst"].startswith("2026-07-07T02:56:00")
    assert candles[0]["open"] == 100.0
    assert candles[0]["volume"] == 1.2
    assert candles[0]["trade_count"] == 3
    assert candles[0]["candle_status"] == "closed"
    assert candles[1]["candle_status"] == "forming"


def test_server_module_declares_read_only_endpoint_version() -> None:
    assert WARROOM_CHART_DATA_SERVER_VERSION.startswith("warroom_chart_data_server.")
    assert WARROOM_PLAIN_CANDLE_SERVER_VERSION == WARROOM_CHART_DATA_SERVER_VERSION
    assert WARROOM_CHART_DATA_SERVER_LAYER == "L4_CONSUMER_MODEL_OPERATOR_UI_RUNTIME"
    assert WARROOM_CHART_DATA_SERVER_CANONICAL_MODULE == "btcts.processing.l4_consumer_models.operator_ui.warroom_chart_data_server"


def test_server_source_allows_private_network_fetch_from_chart_iframe() -> None:
    source = Path(__file__).resolve().parents[1] / "operator_ui" / "warroom_chart_data_server.py"
    text = source.read_text(encoding="utf-8-sig")
    assert "Access-Control-Allow-Origin" in text
    assert "Access-Control-Allow-Private-Network" in text
    assert "read_only_chart_engine_data_endpoint" in text


def test_server_prefers_candle_store_contract() -> None:
    source = Path(__file__).resolve().parents[1] / "operator_ui" / "warroom_chart_data_server.py"
    text = source.read_text(encoding="utf-8-sig")
    assert "read_candle_store_chart_payload" in text
    assert "warroom_candle_store" in text
    assert WARROOM_CANDLE_STORE_VERSION.startswith("warroom_candle_store.")
