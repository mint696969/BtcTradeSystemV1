# path: ./btcts_next/src/btcts/prediction/market_regime/sources/snapshot_builder.py
# desc: Composes read-only market-regime source snapshots from manifest, forecast records, latest prediction, and nowcast artifacts.

from __future__ import annotations

from pathlib import Path

from ..source_snapshot import MarketRegimeSourceSnapshot
from .d_hot_latest_manifest import load_latest_manifest, resolve_forecast_records_relative_path, resolve_latest_prediction_relative_path
from .d_hot_nowcast import load_nowcast_source_snapshot
from .forecast_records_reader import load_forecast_records_snapshot
from .json_io import read_json_artifact
from .warroom_candle_source_reader import load_warroom_candle_source_snapshot


def build_market_regime_source_snapshot(hot_root: str | Path) -> MarketRegimeSourceSnapshot:
    root = Path(hot_root)
    manifest = load_latest_manifest(root)
    manifest_data = manifest.data if manifest.ok else {}
    latest_prediction_relative = resolve_latest_prediction_relative_path(manifest_data)
    latest_prediction = read_json_artifact(root, latest_prediction_relative)
    forecast_records_relative = resolve_forecast_records_relative_path(manifest_data)
    forecast_records = load_forecast_records_snapshot(root, forecast_records_relative)
    nowcast = load_nowcast_source_snapshot(root)
    warroom_candles = load_warroom_candle_source_snapshot(root)

    missing: list[str] = []
    warnings: list[str] = []
    if not manifest.ok:
        missing.append("latest_manifest")
    if not latest_prediction.ok:
        missing.append("latest_prediction")
    if not forecast_records.ok:
        missing.append("forecast_records")
    if forecast_records.ok and forecast_records.market_regime_record_count == 0:
        warnings.append("market_regime_records_missing")
    if not nowcast.market_state.ok:
        missing.append("collector_market_state")
    if not nowcast.health.ok:
        missing.append("collector_health")
    if not nowcast.executions.ok:
        warnings.append("collector_executions_missing")
    if not nowcast.daemon.ok:
        warnings.append("collector_daemon_missing")
    if not warroom_candles.ok:
        warnings.append("warroom_candles_missing_or_unavailable")

    return MarketRegimeSourceSnapshot(
        hot_root=str(root),
        latest_manifest=manifest,
        latest_prediction=latest_prediction,
        forecast_records=forecast_records,
        nowcast=nowcast,
        warroom_candles=warroom_candles,
        missing_sources=tuple(dict.fromkeys(missing)),
        warnings=tuple(dict.fromkeys(warnings + list(forecast_records.warnings) + list(warroom_candles.warnings))),
    )
