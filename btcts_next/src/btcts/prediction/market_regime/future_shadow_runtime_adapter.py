# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_runtime_adapter.py
# desc: MR-F5.15 pure runtime bridge from future-shadow packet and target observations to exact trace/evidence identities. No I/O or scheduler registration.

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping, Sequence

from .contracts import MarketRegimeCode
from .future_shadow_adapter import MarketRegimeFutureShadowPacket
from .future_shadow_outcome import FutureShadowOutcomeEvidence
from .future_trace_identity import MarketRegimeFutureTraceIdentity, build_market_regime_future_trace_identity

MARKET_REGIME_FUTURE_SHADOW_RUNTIME_ADAPTER_VERSION = "prediction.market_regime.future_shadow_runtime_adapter.mr_f5_15.v1"


def capture_market_regime_future_shadow_traces(
    packet: MarketRegimeFutureShadowPacket,
) -> tuple[MarketRegimeFutureTraceIdentity, ...]:
    if not isinstance(packet, MarketRegimeFutureShadowPacket):
        raise ValueError("future_shadow_runtime_packet_invalid")
    traces = tuple(
        sorted(
            (build_market_regime_future_trace_identity(forecast) for forecast in packet.forecasts),
            key=lambda item: item.trace_id,
        )
    )
    if len(traces) != len(packet.forecasts):
        raise ValueError("future_shadow_runtime_trace_count_mismatch")
    if len({item.trace_id for item in traces}) != len(traces):
        raise ValueError("future_shadow_runtime_trace_duplicate")
    if any(item.origin_timestamp != packet.generated_at for item in traces):
        raise ValueError("future_shadow_runtime_trace_origin_mismatch")
    if any(item.feature_snapshot_ref != packet.feature_snapshot_ref for item in traces):
        raise ValueError("future_shadow_runtime_trace_snapshot_mismatch")
    return traces


def _as_regime(value: object) -> MarketRegimeCode:
    try:
        return value if isinstance(value, MarketRegimeCode) else MarketRegimeCode(str(value or "UNKNOWN"))
    except ValueError as exc:
        raise ValueError("future_shadow_runtime_observed_regime_invalid") from exc


def build_market_regime_future_shadow_evidence_by_trace(
    *,
    traces: Sequence[MarketRegimeFutureTraceIdentity],
    observations_by_trace_id: Mapping[str, Mapping[str, Any]],
) -> Mapping[str, FutureShadowOutcomeEvidence]:
    trace_rows = tuple(traces)
    if not trace_rows:
        raise ValueError("future_shadow_runtime_traces_missing")
    if any(not isinstance(item, MarketRegimeFutureTraceIdentity) for item in trace_rows):
        raise ValueError("future_shadow_runtime_trace_invalid")
    trace_ids = tuple(item.trace_id for item in trace_rows)
    if len(trace_ids) != len(set(trace_ids)):
        raise ValueError("future_shadow_runtime_trace_duplicate")
    unknown = tuple(sorted(set(observations_by_trace_id) - set(trace_ids)))
    if unknown:
        raise ValueError("future_shadow_runtime_unknown_observation_trace")

    result: dict[str, FutureShadowOutcomeEvidence] = {}
    for trace in sorted(trace_rows, key=lambda item: item.trace_id):
        raw = observations_by_trace_id.get(trace.trace_id)
        if raw is None:
            continue
        if not isinstance(raw, Mapping):
            raise ValueError("future_shadow_runtime_observation_invalid")
        observation_available = raw.get("observation_available")
        if type(observation_available) is not bool:
            raise ValueError("future_shadow_runtime_observation_available_invalid")
        resolved_at = str(raw.get("resolved_at") or raw.get("observation_at") or "")
        observed_at = str(raw.get("observed_at") or raw.get("observation_at") or "") if observation_available else ""
        source_ref = str(raw.get("observation_source_ref") or "")
        if not source_ref:
            refs = raw.get("source_refs")
            if isinstance(refs, Sequence) and not isinstance(refs, (str, bytes)):
                source_ref = next((str(item).strip() for item in refs if str(item).strip()), "")
        invalidated = raw.get("invalidated", False)
        if type(invalidated) is not bool:
            raise ValueError("future_shadow_runtime_invalidated_flag_invalid")
        invalidation_reason = str(raw.get("invalidation_reason") or "").strip()
        if not invalidation_reason:
            reasons = raw.get("invalidation_reasons")
            if isinstance(reasons, Sequence) and not isinstance(reasons, (str, bytes)):
                invalidation_reason = next(
                    (str(item).strip() for item in reasons if str(item).strip()), ""
                )
        if invalidated and not invalidation_reason:
            raise ValueError("future_shadow_runtime_invalidation_reason_missing")
        evidence = FutureShadowOutcomeEvidence(
            resolved_at=resolved_at,
            observation_available=observation_available,
            observed_at=observed_at,
            observed_future_state=_as_regime(raw.get("observed_future_state") or raw.get("observed_regime_code")) if observation_available else MarketRegimeCode.UNKNOWN,
            invalidated=invalidated,
            invalidation_reason=invalidation_reason,
            observation_source_ref=source_ref if observation_available else "",
        )
        result[trace.trace_id] = evidence
    return MappingProxyType(result)


def build_market_regime_future_shadow_runtime_bridge(
    *,
    packet: MarketRegimeFutureShadowPacket,
    observations_by_trace_id: Mapping[str, Mapping[str, Any]],
) -> Mapping[str, Any]:
    traces = capture_market_regime_future_shadow_traces(packet)
    evidence = build_market_regime_future_shadow_evidence_by_trace(
        traces=traces,
        observations_by_trace_id=observations_by_trace_id,
    )
    missing = tuple(item.trace_id for item in traces if item.trace_id not in evidence)
    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_RUNTIME_ADAPTER_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_runtime_bridge",
        "packet_generated_at": packet.generated_at,
        "trace_count": len(traces),
        "evidence_count": len(evidence),
        "missing_evidence_trace_ids": missing,
        "runtime_bridge_ready": not missing,
        "traces": traces,
        "evidence_by_trace_id": evidence,
        "safety": MappingProxyType({
            "pure_adapter": True,
            "reads_dhot": False,
            "writes_dhot": False,
            "writer_invoked": False,
            "scheduler_enabled": False,
            "canonical_replacement": False,
            "legacy_outcome_ledger_used": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "ui_change": False,
        }),
    })
