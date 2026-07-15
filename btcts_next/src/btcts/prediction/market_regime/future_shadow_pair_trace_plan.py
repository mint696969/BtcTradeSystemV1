# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_pair_trace_plan.py
# desc: MR-F8.6 pure bridge from paired forecast artifacts to disabled-by-default append-only trace persistence plans.

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping, Sequence, Tuple

from .contracts import MarketRegimeCode
from .future_forecast_contract import FutureForecastStatus
from .future_shadow_runtime_persistence import build_future_shadow_trace_persistence_plan
from .future_trace_identity import MarketRegimeFutureTraceIdentity

MARKET_REGIME_FUTURE_SHADOW_PAIR_TRACE_PLAN_VERSION = (
    "prediction.market_regime.future_shadow_pair_trace_plan.mr_f8_6.v1"
)


def _trace_from_forecast(row: Mapping[str, Any]) -> MarketRegimeFutureTraceIdentity:
    try:
        return MarketRegimeFutureTraceIdentity(
            trace_id=str(row.get("trace_id") or ""),
            origin_timestamp=str(row.get("origin_timestamp") or ""),
            expiry_at=str(row.get("expiry_at") or ""),
            target_horizon_sec=int(row.get("target_horizon_sec") or 0),
            target_horizon_key=f"{int(row.get('target_horizon_sec') or 0)}s",
            target_definition_version=str(row.get("target_definition_version") or ""),
            model_id=str(row.get("model_id") or ""),
            logic_version=str(row.get("logic_version") or ""),
            parameter_set_id=str(row.get("parameter_set_id") or ""),
            feature_snapshot_ref=str(row.get("feature_snapshot_ref") or ""),
            predicted_future_state=MarketRegimeCode(str(row.get("predicted_future_state") or "UNKNOWN")),
            forecast_status=FutureForecastStatus(str(row.get("forecast_status") or "")),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("shadow_pair_trace_plan_forecast_contract_invalid") from exc


def build_future_shadow_pair_trace_plan(*, pair: Mapping[str, Any]) -> Mapping[str, Any]:
    if pair.get("artifact_kind") != "future_shadow_candidate_pair":
        raise ValueError("shadow_pair_trace_plan_pair_kind_invalid")
    forecasts = pair.get("forecasts")
    if not isinstance(forecasts, Sequence) or isinstance(forecasts, (str, bytes)):
        raise ValueError("shadow_pair_trace_plan_forecasts_invalid")
    if len(forecasts) < 2:
        raise ValueError("shadow_pair_trace_plan_fewer_than_two_forecasts")
    if any(not isinstance(row, Mapping) for row in forecasts):
        raise ValueError("shadow_pair_trace_plan_forecast_row_invalid")

    traces: Tuple[MarketRegimeFutureTraceIdentity, ...] = tuple(
        sorted((_trace_from_forecast(row) for row in forecasts), key=lambda item: item.trace_id)
    )
    if len({trace.parameter_set_id for trace in traces}) != len(traces):
        raise ValueError("shadow_pair_trace_plan_duplicate_parameter_set")
    if len({(trace.origin_timestamp, trace.feature_snapshot_ref, trace.target_horizon_sec) for trace in traces}) != 1:
        raise ValueError("shadow_pair_trace_plan_slot_identity_mismatch")

    generated_at = traces[0].origin_timestamp
    plan = build_future_shadow_trace_persistence_plan(traces=traces, generated_at=generated_at)
    if plan.get("would_write") is not False:
        raise ValueError("shadow_pair_trace_plan_write_surface_enabled")

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_PAIR_TRACE_PLAN_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_pair_trace_plan",
        "pair_id": str(pair.get("pair_id") or ""),
        "generated_at": generated_at,
        "trace_count": len(traces),
        "trace_ids": tuple(trace.trace_id for trace in traces),
        "parameter_set_ids": tuple(trace.parameter_set_id for trace in traces),
        "persistence_plan": MappingProxyType(dict(plan)),
        "safety": MappingProxyType({
            "read_only_input": True,
            "writes_dhot": False,
            "writer_invoked": False,
            "would_write": False,
            "scheduler_enabled": False,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
        }),
    })
