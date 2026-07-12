# path: ./btcts_next/src/btcts/prediction/market_regime/future_trace_identity.py
# desc: Pure MR-F5.5 immutable trace identity and resolver-input projection for shadow future MarketRegime forecasts. No reads, writes, UI, scheduler, broker, or AutoTrade behavior.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Dict, Mapping, Tuple

from .contracts import MarketRegimeCode
from .future_forecast_contract import (
    FUTURE_MARKET_REGIME_HORIZONS_SEC,
    FutureForecastStatus,
    MarketRegimeFutureForecast,
)
from .future_shadow_adapter import MarketRegimeFutureShadowPacket

MARKET_REGIME_FUTURE_TRACE_IDENTITY_VERSION = "prediction.market_regime.future_trace_identity.mr_f5_5.v1"


def _parse_utc(value: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError("future_trace_origin_timestamp_missing")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception as exc:
        raise ValueError("future_trace_origin_timestamp_invalid") from exc
    if parsed.tzinfo is None:
        raise ValueError("future_trace_origin_timestamp_timezone_missing")
    return parsed.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _trace_id_from_parts(
    *,
    origin_timestamp: str,
    target_horizon_sec: int,
    target_definition_version: str,
    model_id: str,
    logic_version: str,
    parameter_set_id: str,
    feature_snapshot_ref: str,
    predicted_future_state: MarketRegimeCode,
    forecast_status: FutureForecastStatus,
) -> str:
    identity_parts = (
        origin_timestamp,
        str(int(target_horizon_sec)),
        target_definition_version,
        model_id,
        logic_version,
        parameter_set_id,
        feature_snapshot_ref,
        predicted_future_state.value,
        forecast_status.value,
    )
    digest = sha256("|".join(identity_parts).encode("utf-8")).hexdigest()
    return f"market_regime_future_trace:{digest}"


@dataclass(frozen=True)
class MarketRegimeFutureTraceIdentity:
    trace_id: str
    origin_timestamp: str
    expiry_at: str
    target_horizon_sec: int
    target_horizon_key: str
    target_definition_version: str
    model_id: str
    logic_version: str
    parameter_set_id: str
    feature_snapshot_ref: str
    predicted_future_state: MarketRegimeCode
    forecast_status: FutureForecastStatus
    contract_version: str = MARKET_REGIME_FUTURE_TRACE_IDENTITY_VERSION

    def __post_init__(self) -> None:
        required = {
            "trace_id": self.trace_id,
            "origin_timestamp": self.origin_timestamp,
            "expiry_at": self.expiry_at,
            "target_horizon_key": self.target_horizon_key,
            "target_definition_version": self.target_definition_version,
            "model_id": self.model_id,
            "logic_version": self.logic_version,
            "parameter_set_id": self.parameter_set_id,
            "feature_snapshot_ref": self.feature_snapshot_ref,
        }
        missing = tuple(key for key, value in required.items() if not str(value).strip())
        if missing:
            raise ValueError("future_trace_identity_missing:" + ",".join(missing))
        if not isinstance(self.predicted_future_state, MarketRegimeCode):
            raise ValueError("future_trace_predicted_state_invalid")
        if not isinstance(self.forecast_status, FutureForecastStatus):
            raise ValueError("future_trace_forecast_status_invalid")
        horizon = int(self.target_horizon_sec)
        if horizon not in FUTURE_MARKET_REGIME_HORIZONS_SEC:
            raise ValueError(f"future_trace_horizon_invalid:{horizon}")
        if self.target_horizon_key != f"{horizon}s":
            raise ValueError("future_trace_horizon_key_mismatch")
        if self.target_definition_version != f"market_regime_target.{horizon}s.v1":
            raise ValueError("future_trace_target_definition_mismatch")
        origin = _parse_utc(self.origin_timestamp)
        canonical_origin = _iso(origin)
        if self.origin_timestamp != canonical_origin:
            raise ValueError("future_trace_origin_timestamp_not_canonical_utc")
        expected_expiry = _iso(origin + timedelta(seconds=horizon))
        if self.expiry_at != expected_expiry:
            raise ValueError("future_trace_expiry_mismatch")
        if self.forecast_status is FutureForecastStatus.ABSTAIN and self.predicted_future_state is not MarketRegimeCode.UNKNOWN:
            raise ValueError("future_trace_abstain_state_mismatch")
        if self.forecast_status is FutureForecastStatus.FORECAST and self.predicted_future_state is MarketRegimeCode.UNKNOWN:
            raise ValueError("future_trace_forecast_state_mismatch")
        expected_trace_id = _trace_id_from_parts(
            origin_timestamp=self.origin_timestamp,
            target_horizon_sec=horizon,
            target_definition_version=self.target_definition_version,
            model_id=self.model_id,
            logic_version=self.logic_version,
            parameter_set_id=self.parameter_set_id,
            feature_snapshot_ref=self.feature_snapshot_ref,
            predicted_future_state=self.predicted_future_state,
            forecast_status=self.forecast_status,
        )
        if self.trace_id != expected_trace_id:
            raise ValueError("future_trace_id_mismatch")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "trace_id": self.trace_id,
            "origin_timestamp": self.origin_timestamp,
            "expiry_at": self.expiry_at,
            "target_horizon_sec": int(self.target_horizon_sec),
            "target_horizon_key": self.target_horizon_key,
            "target_definition_version": self.target_definition_version,
            "model_id": self.model_id,
            "logic_version": self.logic_version,
            "parameter_set_id": self.parameter_set_id,
            "feature_snapshot_ref": self.feature_snapshot_ref,
            "predicted_future_state": self.predicted_future_state.value,
            "forecast_status": self.forecast_status.value,
            "shadow_only": True,
            "canonical_replacement": False,
        }

    def to_outcome_resolver_prediction(self) -> Mapping[str, Any]:
        return MappingProxyType({
            "run_id": self.trace_id,
            "prediction_id": self.trace_id,
            "generated_at": self.origin_timestamp,
            "horizon_sec": int(self.target_horizon_sec),
            "horizon_key": self.target_horizon_key,
            "regime_code": self.predicted_future_state.value,
            "parameter_set_id": self.parameter_set_id,
            "trace_part_jsonl": "",
            "target_definition_version": self.target_definition_version,
            "model_id": self.model_id,
            "logic_version": self.logic_version,
            "feature_snapshot_ref": self.feature_snapshot_ref,
            "shadow_only": True,
            "canonical_replacement": False,
        })


def build_market_regime_future_trace_identity(
    forecast: MarketRegimeFutureForecast,
) -> MarketRegimeFutureTraceIdentity:
    origin = _parse_utc(forecast.origin_timestamp)
    expiry_at = _iso(origin + timedelta(seconds=int(forecast.target_horizon_sec)))
    canonical_origin = _iso(origin)
    if forecast.origin_timestamp != canonical_origin:
        raise ValueError("future_trace_origin_timestamp_not_canonical_utc")
    trace_id = _trace_id_from_parts(
        origin_timestamp=forecast.origin_timestamp,
        target_horizon_sec=int(forecast.target_horizon_sec),
        target_definition_version=forecast.target_definition_version,
        model_id=forecast.model_id,
        logic_version=forecast.logic_version,
        parameter_set_id=forecast.parameter_set_id,
        feature_snapshot_ref=forecast.feature_snapshot_ref,
        predicted_future_state=forecast.predicted_future_state,
        forecast_status=forecast.status,
    )
    return MarketRegimeFutureTraceIdentity(
        trace_id=trace_id,
        origin_timestamp=forecast.origin_timestamp,
        expiry_at=expiry_at,
        target_horizon_sec=int(forecast.target_horizon_sec),
        target_horizon_key=forecast.target_horizon_key,
        target_definition_version=forecast.target_definition_version,
        model_id=forecast.model_id,
        logic_version=forecast.logic_version,
        parameter_set_id=forecast.parameter_set_id,
        feature_snapshot_ref=forecast.feature_snapshot_ref,
        predicted_future_state=forecast.predicted_future_state,
        forecast_status=forecast.status,
    )


def build_market_regime_future_trace_set(
    packet: MarketRegimeFutureShadowPacket,
) -> Tuple[MarketRegimeFutureTraceIdentity, ...]:
    traces = tuple(build_market_regime_future_trace_identity(item) for item in packet.forecasts)
    trace_ids = tuple(item.trace_id for item in traces)
    if len(trace_ids) != len(set(trace_ids)):
        raise ValueError("future_trace_id_collision")
    if any(item.origin_timestamp != packet.generated_at for item in traces):
        raise ValueError("future_trace_packet_origin_mismatch")
    if any(item.feature_snapshot_ref != packet.feature_snapshot_ref for item in traces):
        raise ValueError("future_trace_packet_feature_snapshot_mismatch")
    return traces
