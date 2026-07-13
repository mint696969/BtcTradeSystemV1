# path: ./btcts_next/src/btcts/prediction/market_regime/features/current_l4_origin_features.py
# desc: Pure MR-F6.9 calculation contract for canonical current-L4 MA levels and volatility thresholds.

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from types import MappingProxyType
from typing import Any, Mapping, Sequence

CURRENT_L4_ORIGIN_FEATURE_PARAMETER_VERSION = (
    "prediction.market_regime.current_l4_origin_feature_parameters.mr_f6_9.v1"
)
CURRENT_L4_ORIGIN_FEATURE_MAX_ROWS = 60


@dataclass(frozen=True)
class CurrentL4OriginFeatureParameters:
    parameter_set_id: str
    fast_ma_window_rows: int
    slow_ma_window_rows: int
    low_volatility_threshold_bps: float
    high_volatility_threshold_bps: float

    def __post_init__(self) -> None:
        if not str(self.parameter_set_id).strip():
            raise ValueError("current_l4_origin_feature_parameter_set_id_missing")
        if isinstance(self.fast_ma_window_rows, bool) or isinstance(self.slow_ma_window_rows, bool):
            raise ValueError("current_l4_origin_feature_ma_window_invalid")
        fast = int(self.fast_ma_window_rows)
        slow = int(self.slow_ma_window_rows)
        if fast < 2 or slow < 2 or fast >= slow or slow > CURRENT_L4_ORIGIN_FEATURE_MAX_ROWS:
            raise ValueError("current_l4_origin_feature_ma_window_invalid")
        low = float(self.low_volatility_threshold_bps)
        high = float(self.high_volatility_threshold_bps)
        if not isfinite(low) or not isfinite(high) or low < 0.0 or high < 0.0 or low > high:
            raise ValueError("current_l4_origin_feature_volatility_threshold_invalid")


def _finite_close(row: Mapping[str, Any]) -> float | None:
    try:
        value = float(row.get("close"))
    except (TypeError, ValueError):
        return None
    if not isfinite(value) or value <= 0.0:
        return None
    return value


def calculate_current_l4_origin_features(
    rows: Sequence[Mapping[str, Any]],
    *,
    parameters: CurrentL4OriginFeatureParameters,
    realized_volatility_bps: float,
) -> Mapping[str, Any]:
    if isinstance(rows, (str, bytes)) or not isinstance(rows, Sequence):
        raise ValueError("current_l4_origin_feature_rows_invalid")
    if not isinstance(parameters, CurrentL4OriginFeatureParameters):
        raise ValueError("current_l4_origin_feature_parameters_invalid")
    closes = tuple(_finite_close(row) for row in rows)
    if any(value is None for value in closes):
        raise ValueError("current_l4_origin_feature_close_invalid")
    slow = int(parameters.slow_ma_window_rows)
    fast = int(parameters.fast_ma_window_rows)
    if len(closes) < slow:
        raise ValueError("current_l4_origin_feature_insufficient_rows")
    rv = float(realized_volatility_bps)
    if not isfinite(rv) or rv < 0.0:
        raise ValueError("current_l4_origin_feature_realized_volatility_invalid")
    close_values = tuple(float(value) for value in closes)
    fast_ma = sum(close_values[-fast:]) / fast
    slow_ma = sum(close_values[-slow:]) / slow
    return MappingProxyType({
        "schema_version": CURRENT_L4_ORIGIN_FEATURE_PARAMETER_VERSION,
        "parameter_set_id": parameters.parameter_set_id,
        "row_count": len(close_values),
        "fast_ma_window_rows": fast,
        "slow_ma_window_rows": slow,
        "fast_ma": round(fast_ma, 8),
        "slow_ma": round(slow_ma, 8),
        "realized_volatility_bps": round(rv, 8),
        "low_volatility_threshold_bps": float(parameters.low_volatility_threshold_bps),
        "high_volatility_threshold_bps": float(parameters.high_volatility_threshold_bps),
        "semantic_substitution_used": False,
        "source_role": "current_l4_closed_candle_close_series",
        "read_only": True,
        "write_performed": False,
    })
