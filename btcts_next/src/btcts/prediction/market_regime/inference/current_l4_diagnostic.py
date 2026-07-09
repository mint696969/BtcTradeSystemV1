# path: ./btcts_next/src/btcts/prediction/market_regime/inference/current_l4_diagnostic.py
# desc: Compact current-L4 candle evidence diagnostics for MarketRegime inference. Pure projection only; no reads, writes, UI, broker, scheduler, or raw candle payload emission.

from __future__ import annotations

from typing import Any, Mapping

from ..contracts import FeatureGroup
from ..features.feature_bundle import FeatureSignal, MarketRegimeFeatureBundle

# MR_A3_CURRENT_L4_EVIDENCE_DIAGNOSTIC_2026_07_09

_PRICE_KEYS = (
    "current_l4_candle_window_available",
    "current_l4_candle_window_candle_count",
    "current_l4_candle_window_first_ts",
    "current_l4_candle_window_last_ts",
    "current_l4_candle_net_change_bps",
    "current_l4_candle_range_bps",
    "current_l4_candle_close_position",
    "current_l4_candle_regime_hint",
    "current_l4_candle_regime_reason",
    "current_l4_candle_threshold_set_id",
    "current_l4_candle_thresholds",
)
_VOL_KEYS = (
    "current_l4_candle_realized_volatility_bps",
    "current_l4_candle_average_range_bps",
    "current_l4_candle_window_range_bps",
)
_SOURCE_QUALITY_KEYS = (
    "current_l4_candle_window_current_enough",
    "current_l4_candle_window_age_sec",
    "current_l4_candle_window_generated_at",
)


def _signals_by_name(bundle: MarketRegimeFeatureBundle, group: FeatureGroup) -> Mapping[str, FeatureSignal]:
    return {signal.name: signal for signal in bundle.signals_by_group(group)}


def _value(signals: Mapping[str, FeatureSignal], name: str, default: Any = None) -> Any:
    signal = signals.get(name)
    if signal is None or not signal.available:
        return default
    return signal.value


def _refs_and_warnings(*groups: Mapping[str, FeatureSignal]) -> tuple[list[str], list[str]]:
    refs: list[str] = []
    warnings: list[str] = []
    for signals in groups:
        for name, signal in signals.items():
            if not name.startswith("current_l4_candle_"):
                continue
            refs.extend(ref for ref in signal.source_refs if ref)
            warnings.extend(warn for warn in signal.warnings if warn)
    return list(dict.fromkeys(refs)), list(dict.fromkeys(warnings))


def build_current_l4_candle_evidence_digest(bundle: MarketRegimeFeatureBundle) -> dict[str, Any]:
    price = _signals_by_name(bundle, FeatureGroup.PRICE_STRUCTURE)
    volatility = _signals_by_name(bundle, FeatureGroup.VOLATILITY)
    source_quality = _signals_by_name(bundle, FeatureGroup.SOURCE_QUALITY)
    source_refs, warnings = _refs_and_warnings(price, volatility, source_quality)
    return {
        "evidence_kind": "current_l4_candle_window_summary",
        "raw_candle_payload_included": False,
        "window_current_enough": bool(_value(source_quality, "current_l4_candle_window_current_enough", False)),
        "window_age_sec": _value(source_quality, "current_l4_candle_window_age_sec"),
        "window_generated_at": _value(source_quality, "current_l4_candle_window_generated_at", ""),
        "window_available": bool(_value(price, "current_l4_candle_window_available", False)),
        "candle_count": int(_value(price, "current_l4_candle_window_candle_count", 0) or 0),
        "first_ts": _value(price, "current_l4_candle_window_first_ts", ""),
        "last_ts": _value(price, "current_l4_candle_window_last_ts", ""),
        "net_change_bps": _value(price, "current_l4_candle_net_change_bps"),
        "range_bps": _value(price, "current_l4_candle_range_bps"),
        "close_position": _value(price, "current_l4_candle_close_position"),
        "realized_volatility_bps": _value(volatility, "current_l4_candle_realized_volatility_bps"),
        "average_candle_range_bps": _value(volatility, "current_l4_candle_average_range_bps"),
        "window_range_bps": _value(volatility, "current_l4_candle_window_range_bps"),
        "regime_hint": _value(price, "current_l4_candle_regime_hint", ""),
        "regime_reason": _value(price, "current_l4_candle_regime_reason", ""),
        # MR_A4_CURRENT_L4_THRESHOLD_PARAMETER_SET_2026_07_09
        "threshold_set_id": _value(price, "current_l4_candle_threshold_set_id", ""),
        "thresholds": _value(price, "current_l4_candle_thresholds", {}),
        "source_refs": source_refs,
        "warnings": warnings,
    }
