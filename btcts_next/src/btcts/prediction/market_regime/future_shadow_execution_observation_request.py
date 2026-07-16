# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_execution_observation_request.py
# desc: MR-F9.15 pure immutable request template for explicit per-trace execution observations from validated runtime preflight.

from __future__ import annotations

from hashlib import sha256
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from .future_shadow_runtime_preflight_bridge import (
    MARKET_REGIME_FUTURE_SHADOW_RUNTIME_PREFLIGHT_BRIDGE_VERSION,
)

MARKET_REGIME_FUTURE_SHADOW_EXECUTION_OBSERVATION_REQUEST_VERSION = (
    "prediction.market_regime.future_shadow_execution_observation_request.mr_f9_15.v1"
)


def _rows(preflight_report: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(preflight_report, Mapping):
        raise ValueError("future_execution_observation_request_preflight_invalid")
    if preflight_report.get("schema_version") != MARKET_REGIME_FUTURE_SHADOW_RUNTIME_PREFLIGHT_BRIDGE_VERSION:
        raise ValueError("future_execution_observation_request_preflight_schema_invalid")
    if preflight_report.get("artifact_kind") != "future_shadow_runtime_preflight_report":
        raise ValueError("future_execution_observation_request_preflight_kind_invalid")
    if preflight_report.get("runtime_source_ready") is not True:
        raise ValueError("future_execution_observation_request_runtime_source_not_ready")
    if preflight_report.get("preflight_only") is not True:
        raise ValueError("future_execution_observation_request_preflight_only_required")
    for field in (
        "writer_invoked",
        "writes_dhot",
        "scheduler_enabled",
        "auto_promotion_allowed",
        "live_parameter_apply_allowed",
        "canonical_replacement_allowed",
    ):
        if preflight_report.get(field) is not False:
            raise ValueError(f"future_execution_observation_request_unsafe_preflight_flag:{field}")
    pairs = preflight_report.get("pairs")
    if not isinstance(pairs, Sequence) or isinstance(pairs, (str, bytes)):
        raise ValueError("future_execution_observation_request_pairs_invalid")
    rows: list[Mapping[str, Any]] = []
    for pair in pairs:
        if not isinstance(pair, Mapping):
            raise ValueError("future_execution_observation_request_pair_invalid")
        forecasts = pair.get("forecasts")
        if not isinstance(forecasts, Sequence) or isinstance(forecasts, (str, bytes)):
            raise ValueError("future_execution_observation_request_forecasts_invalid")
        if len(forecasts) != 2 or any(not isinstance(row, Mapping) for row in forecasts):
            raise ValueError("future_execution_observation_request_candidate_pair_invalid")
        rows.extend(forecasts)
    if len(rows) != 14:
        raise ValueError("future_execution_observation_request_trace_count_invalid")
    return tuple(rows)


def build_future_shadow_execution_observation_request(
    *,
    preflight_report: Mapping[str, Any],
) -> Mapping[str, Any]:
    rows = _rows(preflight_report)
    prediction_origin = str(preflight_report.get("prediction_origin") or "")
    feature_snapshot_ref = str(preflight_report.get("feature_snapshot_ref") or "")
    if not prediction_origin or not feature_snapshot_ref:
        raise ValueError("future_execution_observation_request_identity_missing")

    trace_ids: list[str] = []
    request_rows = []
    for row in rows:
        trace_id = str(row.get("trace_id") or "")
        origin = str(row.get("origin_timestamp") or "")
        snapshot = str(row.get("feature_snapshot_ref") or "")
        horizon = int(row.get("target_horizon_sec") or 0)
        parameter_set_id = str(row.get("parameter_set_id") or "")
        forecast_status = str(row.get("forecast_status") or "")
        if not trace_id or not parameter_set_id or horizon <= 0 or not forecast_status:
            raise ValueError("future_execution_observation_request_forecast_identity_missing")
        if origin != prediction_origin:
            raise ValueError("future_execution_observation_request_origin_mismatch")
        if snapshot != feature_snapshot_ref:
            raise ValueError("future_execution_observation_request_snapshot_mismatch")
        trace_ids.append(trace_id)
        request_rows.append(MappingProxyType({
            "trace_id": trace_id,
            "prediction_origin": origin,
            "feature_snapshot_ref": snapshot,
            "target_horizon_sec": horizon,
            "parameter_set_id": parameter_set_id,
            "forecast_status": forecast_status,
            "inference_mode": None,
            "raw_output_semantics": None,
            "source_freshness_state": None,
            "source_age_sec": None,
            "fallback_reason": "",
            "fallback_source_ref": "",
            "observation_complete": False,
        }))
    if len(set(trace_ids)) != 14:
        raise ValueError("future_execution_observation_request_trace_identity_duplicate")

    request_hash = sha256("|".join(sorted(trace_ids)).encode("utf-8")).hexdigest()
    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_EXECUTION_OBSERVATION_REQUEST_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_execution_observation_request",
        "request_id": "future-shadow-execution-observation-request:" + request_hash,
        "prediction_origin": prediction_origin,
        "feature_snapshot_ref": feature_snapshot_ref,
        "trace_count": 14,
        "rows": tuple(request_rows),
        "request_complete": False,
        "execution_observations_required": True,
        "facts_inferred_from_preflight": False,
        "facts_inferred_from_classifier_diagnostics": False,
        "legacy_confidence_promoted_to_probability": False,
        "would_write": False,
        "safety": MappingProxyType({
            "pure": True,
            "read_only_input": True,
            "writer_invoked": False,
            "writes_dhot": False,
            "writes_repository": False,
            "scheduler_enabled": False,
            "producer_loop_enabled": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_intent_submitted": False,
        }),
    })
