# path: ./btcts_next/src/btcts/autotrade/read_model/__init__.py
# desc: AutoTrade read model package.

from __future__ import annotations

from .forecast import build_rule_based_forecast_5m, score_forecast_outcome, target_ts_for
from .ids import build_forecast_id, build_snapshot_id
from .live_input_adapter import (
    LiveInputAdapterDiagnostics,
    live_input_adapter_diagnostics,
    load_latest_snapshot_from_market_state,
    snapshot_from_market_state_row,
)
from .temporal_flow_adapter import (
    TemporalFlowAdapterDiagnostics,
    build_temporal_flow_features_from_rows,
)
from .models import (
    ActualFiveMinuteChange,
    AutoTradeSnapshot,
    Confidence,
    CurrentMarketInputs,
    Forecast5m,
    ForecastDirection,
    ForecastExpectedChange,
    ForecastOutcome,
    ForecastOutcomeResult,
    ForecastScore,
    GroundDirection,
    GroundState,
    SnapshotUsability,
    TemporalFlowFeatures,
)

__all__ = [
    "ActualFiveMinuteChange",
    "AutoTradeSnapshot",
    "Confidence",
    "CurrentMarketInputs",
    "Forecast5m",
    "ForecastDirection",
    "ForecastExpectedChange",
    "ForecastOutcome",
    "ForecastOutcomeResult",
    "ForecastScore",
    "GroundDirection",
    "GroundState",
    "LiveInputAdapterDiagnostics",
    "SnapshotUsability",
    "TemporalFlowAdapterDiagnostics",
    "TemporalFlowFeatures",
    "build_forecast_id",
    "build_temporal_flow_features_from_rows",
    "build_rule_based_forecast_5m",
    "build_snapshot_id",
    "live_input_adapter_diagnostics",
    "load_latest_snapshot_from_market_state",
    "score_forecast_outcome",
    "snapshot_from_market_state_row",
    "target_ts_for",
]
