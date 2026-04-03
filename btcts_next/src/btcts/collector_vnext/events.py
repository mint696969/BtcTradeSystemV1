# path: ./btcts_next/src/btcts/collector_vnext/events.py
# desc: Market event taxonomy, timestamp helpers, and common record envelope builders.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from btcts.ingestion.event_types import EventType

from .config import CollectorConfig
from .ids import make_record_id


def now_iso_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_event_ts(exchange_ts: Optional[str], collector_ts: str) -> str:
    return exchange_ts or collector_ts


@dataclass(frozen=True)
class EnvelopeContext:
    config: CollectorConfig
    schema_version: str
    record_type: str
    channel: str
    transport: str
    sequence_id: int
    session_id: str
    stream_session_id: str
    exchange: str
    exchange_ts: Optional[str] = None
    source_event_id: Optional[str] = None
    source_sequence: Optional[int] = None
    continuity_sequence: Optional[int] = None
    quality_flags: Optional[List[str]] = None
    is_partial: bool = False
    is_reconstructed: bool = False
    confidence_score: float = 1.0


def make_record(ctx: EnvelopeContext, payload: Dict[str, Any]) -> Dict[str, Any]:
    collector_ts = now_iso_utc()
    ingest_ts = now_iso_utc()
    event_ts = normalize_event_ts(ctx.exchange_ts, collector_ts)
    quality_flags = list(ctx.quality_flags or [])

    is_canonical = ctx.schema_version == "collector.vnext.canonical"

    record = {
        "schema_version": ctx.schema_version,
        "schema_contract": "collector.vnext.canonical.required.v1" if is_canonical else None,
        "schema_contract_version": 1 if is_canonical else None,
        "payload_contract_version": 1 if is_canonical else None,
        "record_type": ctx.record_type,
        "record_id": make_record_id(
    exchange=ctx.exchange,
    stream=ctx.channel,
    stream_session_id=ctx.stream_session_id,
    event_type=ctx.record_type,
    sequence_id=ctx.sequence_id,
),
        "collector_id": ctx.config.collector_id,
        "collector_role": ctx.config.collector_role,
        "host_name": ctx.config.host_name,
        "session_id": ctx.session_id,
        "stream_session_id": ctx.stream_session_id,
        "exchange": ctx.exchange,
        "market": ctx.config.market,
        "symbol": ctx.config.symbol,
        "instrument_id": ctx.config.instrument_id,
        "channel": ctx.channel,
        "transport": ctx.transport,
        "source_event_id": ctx.source_event_id,
        "source_sequence": ctx.source_sequence,
        "continuity_sequence": ctx.continuity_sequence,
        "sequence_id": ctx.sequence_id,
        "exchange_ts": ctx.exchange_ts,
        "collector_ts": collector_ts,
        "ingest_ts": ingest_ts,
        "event_ts": event_ts,
        "quality_flags": quality_flags,
        "is_partial": ctx.is_partial,
        "is_reconstructed": ctx.is_reconstructed,
        "confidence_score": ctx.confidence_score,
        "payload": payload,
    }
    return record


def make_stream_started_payload(
    *,
    reason: str = "collector_bootstrap",
    provider: str,
    endpoint_or_channel: str,
) -> Dict[str, Any]:
    return {
        "event_name": "stream_started",
        "reason": reason,
        "expected_continuity": False,
        "provider": provider,
        "endpoint_or_channel": endpoint_or_channel,
    }


def make_stream_reconnected_payload(
    *,
    reason: str,
    expected_continuity: bool,
    provider: str,
    endpoint_or_channel: str,
    previous_stream_session_id: str,
    new_stream_session_id: str,
) -> Dict[str, Any]:
    return {
        "event_name": "stream_reconnected",
        "reason": reason,
        "expected_continuity": expected_continuity,
        "provider": provider,
        "endpoint_or_channel": endpoint_or_channel,
        "previous_stream_session_id": previous_stream_session_id,
        "new_stream_session_id": new_stream_session_id,
    }


def make_stream_gap_detected_payload(
    *,
    reason: str,
    gap_kind: str,
    provider: str,
    endpoint_or_channel: str,
    stream_session_id: str,
    last_good_event_id: Optional[str],
    first_uncertain_event_id: Optional[str],
) -> Dict[str, Any]:
    return {
        "event_name": "stream_gap_detected",
        "reason": reason,
        "gap_kind": gap_kind,
        "provider": provider,
        "endpoint_or_channel": endpoint_or_channel,
        "stream_session_id": stream_session_id,
        "last_good_event_id": last_good_event_id,
        "first_uncertain_event_id": first_uncertain_event_id,
    }


def make_stream_resync_started_payload(
    *,
    reason: str,
    provider: str,
    endpoint_or_channel: str,
    stream_session_id: str,
    resync_target: str,
) -> Dict[str, Any]:
    return {
        "event_name": "stream_resync_started",
        "reason": reason,
        "provider": provider,
        "endpoint_or_channel": endpoint_or_channel,
        "stream_session_id": stream_session_id,
        "resync_target": resync_target,
    }


def make_stream_resync_completed_payload(
    *,
    reason: str,
    provider: str,
    endpoint_or_channel: str,
    stream_session_id: str,
    resync_target: str,
    new_base_snapshot_id: Optional[str],
) -> Dict[str, Any]:
    return {
        "event_name": "stream_resync_completed",
        "reason": reason,
        "provider": provider,
        "endpoint_or_channel": endpoint_or_channel,
        "stream_session_id": stream_session_id,
        "resync_target": resync_target,
        "new_base_snapshot_id": new_base_snapshot_id,
    }


def make_provider_error_payload(
    *,
    reason: str,
    provider: str,
    endpoint_or_channel: str,
    error_class: str,
    error_message: str,
    retry_after_sec: Optional[float] = None,
) -> Dict[str, Any]:
    return {
        "event_name": "provider_error",
        "reason": reason,
        "provider": provider,
        "endpoint_or_channel": endpoint_or_channel,
        "error_class": error_class,
        "error_message": error_message,
        "retry_after_sec": retry_after_sec,
    }


def make_origin_audit_payload(
    *,
    event_name: str,
    reason: str,
    provider: str,
    transport: str,
    channel: str,
    endpoint_or_channel: str,
    expected_continuity: bool | None = None,
    last_good_event_id: Optional[str] = None,
    first_uncertain_event_id: Optional[str] = None,
    previous_stream_session_id: Optional[str] = None,
    new_stream_session_id: Optional[str] = None,
    timeout_kind: Optional[str] = None,
    timeout_sec: Optional[float] = None,
    provider_error: Optional[str] = None,
    ssl_verify: Optional[bool] = None,
    error_class: Optional[str] = None,
    error_message: Optional[str] = None,
    retry_after_sec: Optional[float] = None,
    gap_kind: Optional[str] = None,
    resync_required: Optional[bool] = None,
) -> Dict[str, Any]:
    return {
        "event_name": event_name,
        "reason": reason,
        "provider": provider,
        "transport": transport,
        "channel": channel,
        "endpoint_or_channel": endpoint_or_channel,
        "expected_continuity": expected_continuity,
        "last_good_event_id": last_good_event_id,
        "first_uncertain_event_id": first_uncertain_event_id,
        "previous_stream_session_id": previous_stream_session_id,
        "new_stream_session_id": new_stream_session_id,
        "timeout_kind": timeout_kind,
        "timeout_sec": timeout_sec,
        "provider_error": provider_error,
        "ssl_verify": ssl_verify,
        "error_class": error_class,
        "error_message": error_message,
        "retry_after_sec": retry_after_sec,
        "gap_kind": gap_kind,
        "resync_required": resync_required,
    }


def make_origin_audit_event_name(record_type: str) -> str:
    mapping = {
        EventType.STREAM_STARTED: "origin.stream_started",
        EventType.STREAM_RECONNECTED: "origin.stream_reconnected",
        EventType.STREAM_GAP_DETECTED: "origin.stream_gap_detected",
        EventType.STREAM_RESYNC_STARTED: "origin.stream_resync_started",
        EventType.STREAM_RESYNC_COMPLETED: "origin.stream_resync_completed",
        EventType.SYSTEM_PROVIDER_ERROR: "origin.provider_error",
    }
    return mapping.get(record_type, "origin.unknown")