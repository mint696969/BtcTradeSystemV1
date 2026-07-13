# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_evidence_runtime_source.py
# desc: MR-F6.8 pure runtime-source readiness projection for origin-evidence inputs without semantic substitution.

from __future__ import annotations

from math import isfinite
from types import MappingProxyType
from typing import Any, Mapping

from .contracts import FeatureGroup, MarketRegimeCode
from .features import MarketRegimeFeatureBundle
from .future_origin_evidence_adapter import MarketRegimeOriginFeatureInputs

MARKET_REGIME_ORIGIN_EVIDENCE_RUNTIME_SOURCE_VERSION = (
    "prediction.market_regime.origin_evidence_runtime_source.mr_f6_8.v1"
)

_REQUIRED_RUNTIME_FIELDS = (
    "source_timestamp",
    "previous_state",
    "recent_return",
    "fast_ma",
    "slow_ma",
    "realized_volatility",
    "low_volatility_threshold",
    "high_volatility_threshold",
    "current_forecast_label_selection",
)


def _signals(bundle: MarketRegimeFeatureBundle, group: FeatureGroup) -> Mapping[str, Any]:
    return {item.name: item for item in bundle.signals_by_group(group)}


def _available_value(bundle: MarketRegimeFeatureBundle, group: FeatureGroup, name: str) -> Any:
    signal = _signals(bundle, group).get(name)
    if signal is None or not signal.available:
        return None
    return signal.value


def _finite_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if isfinite(result) else None


def _regime(value: Any) -> MarketRegimeCode | None:
    text = str(value or "").strip().upper()
    try:
        regime = MarketRegimeCode(text)
    except ValueError:
        return None
    return None if regime is MarketRegimeCode.UNKNOWN else regime


def build_market_regime_origin_runtime_source(
    *,
    feature_bundle: MarketRegimeFeatureBundle,
    previous_current_state: Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    if not isinstance(feature_bundle, MarketRegimeFeatureBundle):
        raise ValueError("origin_runtime_source_feature_bundle_invalid")
    previous = dict(previous_current_state or {})

    source_timestamp = str(
        _available_value(
            feature_bundle,
            FeatureGroup.SOURCE_QUALITY,
            "current_l4_candle_window_generated_at",
        )
        or ""
    ).strip()
    previous_state = _regime(previous.get("regime_code"))
    net_change_bps = _finite_float(
        _available_value(
            feature_bundle,
            FeatureGroup.PRICE_STRUCTURE,
            "current_l4_candle_net_change_bps",
        )
    )
    realized_volatility_bps = _finite_float(
        _available_value(
            feature_bundle,
            FeatureGroup.VOLATILITY,
            "current_l4_candle_realized_volatility_bps",
        )
    )
    legacy_selection = _regime(
        _available_value(
            feature_bundle,
            FeatureGroup.PRICE_STRUCTURE,
            "current_l4_candle_regime_hint",
        )
    )

    extracted: dict[str, Any] = {
        "source_timestamp": source_timestamp or None,
        "previous_state": previous_state,
        "recent_return": None if net_change_bps is None else net_change_bps / 10000.0,
        "fast_ma": None,
        "slow_ma": None,
        "realized_volatility": (
            None if realized_volatility_bps is None else realized_volatility_bps / 10000.0
        ),
        "low_volatility_threshold": None,
        "high_volatility_threshold": None,
        "current_forecast_label_selection": legacy_selection,
    }
    blockers = tuple(
        f"origin_runtime_source_missing:{field}"
        for field in _REQUIRED_RUNTIME_FIELDS
        if extracted[field] is None
    )
    provenance = MappingProxyType({
        "source_timestamp": "SOURCE_QUALITY.current_l4_candle_window_generated_at",
        "previous_state": "previous_current_state.regime_code",
        "recent_return": "PRICE_STRUCTURE.current_l4_candle_net_change_bps/10000",
        "fast_ma": "unavailable:no_canonical_fast_ma_signal",
        "slow_ma": "unavailable:no_canonical_slow_ma_signal",
        "realized_volatility": "VOLATILITY.current_l4_candle_realized_volatility_bps/10000",
        "low_volatility_threshold": "unavailable:no_canonical_low_volatility_threshold",
        "high_volatility_threshold": "unavailable:no_canonical_high_volatility_threshold",
        "current_forecast_label_selection": "PRICE_STRUCTURE.current_l4_candle_regime_hint",
    })

    inputs = None
    if not blockers:
        inputs = MarketRegimeOriginFeatureInputs(
            source_timestamp=str(extracted["source_timestamp"]),
            previous_state=extracted["previous_state"],
            recent_return=extracted["recent_return"],
            fast_ma=extracted["fast_ma"],
            slow_ma=extracted["slow_ma"],
            realized_volatility=extracted["realized_volatility"],
            low_volatility_threshold=extracted["low_volatility_threshold"],
            high_volatility_threshold=extracted["high_volatility_threshold"],
            current_forecast_label_selection=extracted["current_forecast_label_selection"],
        )

    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_RUNTIME_SOURCE_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_origin_evidence_runtime_source_readiness",
        "runtime_source_ready": not blockers,
        "blockers": blockers,
        "extracted_values": MappingProxyType(extracted),
        "provenance": provenance,
        "feature_inputs": inputs,
        "semantic_substitution_used": False,
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "canonical_replacement": False,
        "live_parameter_apply_allowed": False,
    })
