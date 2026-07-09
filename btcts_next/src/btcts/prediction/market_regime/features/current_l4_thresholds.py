# path: ./btcts_next/src/btcts/prediction/market_regime/features/current_l4_thresholds.py
# desc: Current L4 candle regime-hint threshold contract. Pure parameter extraction only; no reads, writes, UI, broker, scheduler, or AutoTrade.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

# MR_A4_CURRENT_L4_THRESHOLD_PARAMETER_SET_2026_07_09
CURRENT_L4_CANDLE_THRESHOLD_SET_ID = "market_regime.current_l4_candle_thresholds.v1"
CURRENT_L4_CANDLE_THRESHOLD_KEY = "current_l4_candle_window"


@dataclass(frozen=True)
class CurrentL4CandleThresholds:
    threshold_set_id: str = CURRENT_L4_CANDLE_THRESHOLD_SET_ID
    high_vol_chop_range_bps_min: float = 180.0
    high_vol_chop_abs_net_range_ratio_max: float = 0.35
    directional_abs_net_bps_min: float = 25.0
    directional_abs_net_range_ratio_min: float = 0.45
    low_vol_range_bps_max: float = 20.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _float_from_mapping(values: Mapping[str, Any], key: str, default: float) -> float:
    try:
        raw = values.get(key, default)
        if raw is None:
            return float(default)
        return float(raw)
    except Exception:
        return float(default)


def current_l4_thresholds_from_mapping(values: Mapping[str, Any] | None) -> CurrentL4CandleThresholds:
    mapping = values if isinstance(values, Mapping) else {}
    default = CurrentL4CandleThresholds()
    return CurrentL4CandleThresholds(
        threshold_set_id=str(mapping.get("threshold_set_id") or default.threshold_set_id),
        high_vol_chop_range_bps_min=_float_from_mapping(mapping, "high_vol_chop_range_bps_min", default.high_vol_chop_range_bps_min),
        high_vol_chop_abs_net_range_ratio_max=_float_from_mapping(mapping, "high_vol_chop_abs_net_range_ratio_max", default.high_vol_chop_abs_net_range_ratio_max),
        directional_abs_net_bps_min=_float_from_mapping(mapping, "directional_abs_net_bps_min", default.directional_abs_net_bps_min),
        directional_abs_net_range_ratio_min=_float_from_mapping(mapping, "directional_abs_net_range_ratio_min", default.directional_abs_net_range_ratio_min),
        low_vol_range_bps_max=_float_from_mapping(mapping, "low_vol_range_bps_max", default.low_vol_range_bps_max),
    )


def current_l4_thresholds_from_parameter_set(parameter_set: object | None) -> CurrentL4CandleThresholds:
    thresholds = getattr(parameter_set, "thresholds", None)
    if not isinstance(thresholds, Mapping):
        return CurrentL4CandleThresholds()
    current_l4_values = thresholds.get(CURRENT_L4_CANDLE_THRESHOLD_KEY)
    if isinstance(current_l4_values, Mapping):
        return current_l4_thresholds_from_mapping(current_l4_values)
    return CurrentL4CandleThresholds()
