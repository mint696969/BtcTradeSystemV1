# path: ./btcts_next/src/btcts/prediction/market_regime/sources/__init__.py
# desc: Read-only source adapters for market-regime engine snapshots. No UI binding or runtime writes.

from __future__ import annotations

from .collector_state_reader import COLLECTOR_STATE_RELATIVE_PATHS, read_collector_state_sources
from .d_hot_latest_manifest import LATEST_MANIFEST_RELATIVE_PATH, load_latest_manifest, resolve_forecast_records_relative_path, resolve_latest_prediction_relative_path
from .d_hot_nowcast import load_nowcast_source_snapshot
from .forecast_records_reader import load_forecast_records_snapshot
from .json_io import read_json_artifact, resolve_under_root
from .snapshot_builder import build_market_regime_source_snapshot
from .warroom_candle_source_reader import load_warroom_candle_source_snapshot, warroom_candle_timeframe_relpath

__all__ = [
    "COLLECTOR_STATE_RELATIVE_PATHS",
    "LATEST_MANIFEST_RELATIVE_PATH",
    "build_market_regime_source_snapshot",
    "load_forecast_records_snapshot",
    "load_latest_manifest",
    "load_nowcast_source_snapshot",
    "load_warroom_candle_source_snapshot",
    "read_collector_state_sources",
    "read_json_artifact",
    "resolve_forecast_records_relative_path",
    "resolve_latest_prediction_relative_path",
    "resolve_under_root",
    "warroom_candle_timeframe_relpath",
]
