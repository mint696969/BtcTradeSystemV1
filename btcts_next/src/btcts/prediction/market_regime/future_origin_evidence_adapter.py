# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_evidence_adapter.py
# desc: Pure MR-F6.7 adapter from generated future forecasts and explicit origin features to immutable evidence bundles.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .contracts import MarketRegimeCode
from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from .future_mandatory_baseline_origin_evidence import (
    MarketRegimeOriginEvidence,
    build_market_regime_origin_evidence_bundle,
)
from .future_shadow_adapter import MarketRegimeFutureShadowPacket
from .future_trace_identity import build_market_regime_future_trace_set

MARKET_REGIME_ORIGIN_EVIDENCE_ADAPTER_VERSION = (
    "prediction.market_regime.origin_evidence_adapter.mr_f6_7.v1"
)


@dataclass(frozen=True)
class MarketRegimeOriginFeatureInputs:
    source_timestamp: str
    previous_state: MarketRegimeCode
    recent_return: float | None
    fast_ma: float | None
    slow_ma: float | None
    realized_volatility: float | None
    low_volatility_threshold: float | None
    high_volatility_threshold: float | None
    current_forecast_label_selection: MarketRegimeCode

    def __post_init__(self) -> None:
        text = str(self.source_timestamp or "").strip()
        if not text:
            raise ValueError("origin_feature_inputs_source_timestamp_missing")
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("origin_feature_inputs_source_timestamp_invalid") from exc
        if parsed.tzinfo is None:
            raise ValueError("origin_feature_inputs_source_timestamp_timezone_missing")
        if parsed.astimezone(timezone.utc).timestamp() < 0.0:
            raise ValueError("origin_feature_inputs_source_epoch_invalid")
        if not isinstance(self.previous_state, MarketRegimeCode):
            raise ValueError("origin_feature_inputs_previous_state_invalid")
        if not isinstance(self.current_forecast_label_selection, MarketRegimeCode):
            raise ValueError("origin_feature_inputs_legacy_selection_invalid")
        for name, value in (
            ("recent_return", self.recent_return),
            ("fast_ma", self.fast_ma),
            ("slow_ma", self.slow_ma),
            ("realized_volatility", self.realized_volatility),
            ("low_volatility_threshold", self.low_volatility_threshold),
            ("high_volatility_threshold", self.high_volatility_threshold),
        ):
            if value is not None and not isfinite(float(value)):
                raise ValueError(f"origin_feature_inputs_non_finite:{name}")
        if (
            self.low_volatility_threshold is not None
            and self.high_volatility_threshold is not None
            and float(self.low_volatility_threshold) > float(self.high_volatility_threshold)
        ):
            raise ValueError("origin_feature_inputs_threshold_order_invalid")

    @property
    def source_timestamp_epoch_sec(self) -> float:
        parsed = datetime.fromisoformat(self.source_timestamp.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc).timestamp()


def _origin_epoch(origin_timestamp: str) -> float:
    try:
        parsed = datetime.fromisoformat(str(origin_timestamp).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("origin_evidence_adapter_origin_timestamp_invalid") from exc
    if parsed.tzinfo is None:
        raise ValueError("origin_evidence_adapter_origin_timezone_missing")
    return parsed.astimezone(timezone.utc).timestamp()


def _score_rows(signal_score_report: Mapping[str, Any]) -> Mapping[int, Mapping[MarketRegimeCode, float]]:
    rows = signal_score_report.get("horizons")
    if not isinstance(rows, (tuple, list)):
        raise ValueError("origin_evidence_adapter_score_rows_missing")
    result: dict[int, Mapping[MarketRegimeCode, float]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("origin_evidence_adapter_score_row_invalid")
        horizon = int(raw.get("horizon_sec") or 0)
        if horizon not in FUTURE_MARKET_REGIME_HORIZONS_SEC:
            raise ValueError(f"origin_evidence_adapter_horizon_invalid:{horizon}")
        scores = raw.get("regime_scores")
        if not isinstance(scores, Mapping):
            raise ValueError(f"origin_evidence_adapter_scores_missing:{horizon}")
        normalized: dict[MarketRegimeCode, float] = {}
        for raw_state, raw_value in scores.items():
            state = raw_state if isinstance(raw_state, MarketRegimeCode) else MarketRegimeCode(str(raw_state))
            value = float(raw_value)
            if not isfinite(value) or value < 0.0:
                raise ValueError(f"origin_evidence_adapter_score_invalid:{horizon}:{state.value}")
            normalized[state] = value
        if horizon in result:
            raise ValueError(f"origin_evidence_adapter_duplicate_horizon:{horizon}")
        result[horizon] = MappingProxyType(normalized)
    missing = tuple(item for item in FUTURE_MARKET_REGIME_HORIZONS_SEC if item not in result)
    if missing:
        raise ValueError("origin_evidence_adapter_missing_horizons:" + ",".join(str(item) for item in missing))
    return MappingProxyType(result)


def build_market_regime_origin_evidence_bundles(
    *,
    packet: MarketRegimeFutureShadowPacket,
    signal_score_report: Mapping[str, Any],
    feature_inputs: MarketRegimeOriginFeatureInputs,
) -> Tuple[Mapping[str, Any], ...]:
    if not isinstance(packet, MarketRegimeFutureShadowPacket):
        raise ValueError("origin_evidence_adapter_packet_invalid")
    if not isinstance(feature_inputs, MarketRegimeOriginFeatureInputs):
        raise ValueError("origin_evidence_adapter_feature_inputs_invalid")
    origin_epoch = _origin_epoch(packet.generated_at)
    if float(feature_inputs.source_timestamp_epoch_sec) > origin_epoch:
        raise ValueError("origin_evidence_adapter_lookahead_detected")
    score_rows = _score_rows(signal_score_report)
    traces = build_market_regime_future_trace_set(packet)
    forecasts_by_horizon = {item.target_horizon_sec: item for item in packet.forecasts}
    traces_by_horizon = {item.target_horizon_sec: item for item in traces}
    bundles = []
    for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC:
        forecast = forecasts_by_horizon[horizon]
        trace = traces_by_horizon[horizon]
        bundles.append(build_market_regime_origin_evidence_bundle(MarketRegimeOriginEvidence(
            prediction_origin=packet.generated_at,
            prediction_origin_epoch_sec=origin_epoch,
            source_timestamp=feature_inputs.source_timestamp,
            source_timestamp_epoch_sec=feature_inputs.source_timestamp_epoch_sec,
            target_horizon_sec=horizon,
            trace_id=trace.trace_id,
            model_id=forecast.model_id,
            logic_version=forecast.logic_version,
            parameter_set_id=forecast.parameter_set_id,
            target_definition_version=forecast.target_definition_version,
            feature_snapshot_ref=packet.feature_snapshot_ref,
            current_state=packet.origin_current_state,
            previous_state=feature_inputs.previous_state,
            regime_scores=score_rows[horizon],
            recent_return=feature_inputs.recent_return,
            fast_ma=feature_inputs.fast_ma,
            slow_ma=feature_inputs.slow_ma,
            realized_volatility=feature_inputs.realized_volatility,
            low_volatility_threshold=feature_inputs.low_volatility_threshold,
            high_volatility_threshold=feature_inputs.high_volatility_threshold,
            current_forecast_label_selection=feature_inputs.current_forecast_label_selection,
        )))
    return tuple(bundles)
