# path: ./btcts_next/src/btcts/collector_vnext/emit_ws.py
# desc: WebSocket smoke emitters for executions and board streams in Collector vNext.

from __future__ import annotations

import time

from typing import Dict, List, Optional

from .config import load_config

from .events import (
    EnvelopeContext,
    EventType,
    make_origin_audit_event_name,
    make_origin_audit_payload,
    make_provider_error_payload,
    make_record,
    make_stream_gap_detected_payload,
    make_stream_resync_completed_payload,
    make_stream_resync_started_payload,
    make_stream_started_payload,
)

from .ids import SequenceManager, make_stream_session_id
from .providers.bitflyer_ws import connect_and_stream_executions
from .providers.bitflyer_ws_board import connect_and_stream_board
from .transforms.ws_board_to_canonical import canonical_board_event
from .transforms.ws_trade_to_canonical import canonical_ws_trade
from .venue_adapters.bitflyer_board import BitflyerBoardVenueAdapter
from .state import write_origin_status
from .writer import write_canonical, write_raw
from btcts.core import audit


def emit_ws_trade_smoke(seq: SequenceManager, session_id: str) -> Dict[str, object]:
    cfg = load_config()

    stream_session_id = make_stream_session_id(
        cfg.collector_id,
        "bitflyer",
        "executions_ws",
    )

    stream = connect_and_stream_executions(
        cfg.symbol,
        ssl_verify=cfg.ws_ssl_verify,
        recv_timeout_sec=60.0,
    )

    raw_path: Optional[str] = None
    canonical_path: Optional[str] = None
    trade_count = 0

    for msg in stream:
        raw_ctx = EnvelopeContext(
            config=cfg,
            schema_version="collector.vnext.raw",
            record_type=EventType.MARKET_TRADE,
            channel="executions_ws",
            transport="websocket",
            sequence_id=seq.next(),
            session_id=session_id,
            stream_session_id=stream_session_id,
            exchange="bitflyer",
        )

        raw_record = make_record(
            raw_ctx,
            {
                "provider": msg.provider,
                "exchange": msg.exchange,
                "transport": msg.transport,
                "channel": msg.channel,
                "received_ts": msg.received_ts,
                "subscription_id": msg.subscription_id,
                "message_id": msg.message_id,
                "source_sequence": msg.source_sequence,
                "raw_message_meta": msg.raw_message_meta,
                "source_payload": msg.payload,
            },
        )

        raw_out = write_raw(
            cfg,
            exchange="bitflyer",
            symbol=cfg.symbol,
            channel="executions_ws",
            record_type=EventType.MARKET_TRADE,
            record=raw_record,
        )
        raw_path = str(raw_out)

        trade = canonical_ws_trade(msg.payload)

        if trade:
            trade["integration_hint"] = {
                "integration_domain": "trade_native_id",
                "transport_role": "realtime_primary",
                "unified_key_hint": str(trade["trade_id"]) if trade.get("trade_id") is not None else None,
                "dedupe_domain": "trade_native_id",
                "unified_view_policy": "event_dedupe_by_native_id",
            }
            trade["dedupe_hint"] = {
                "entity_kind": "trade",
                "unified_key": {
                    "exchange": "bitflyer",
                    "instrument_id": f"bitflyer.spot.{cfg.symbol}",
                    "source_event_id": str(trade["trade_id"]) if trade.get("trade_id") is not None else None,
                },
                "native_id_required": True,
                "fallback_key_enabled": False,
                "provenance_policy": {
                    "seen_in_rest": False,
                    "seen_in_ws": True,
                },
            }

            trade["completeness_hint"] = {
                "evaluation_unit": "trade_event",
                "completeness": "mostly_complete",
                "confidence_hint": "medium_high",
                "completeness_basis": {
                    "exchange_present": True,
                    "instrument_id_present": True,
                    "source_event_id_present": trade.get("trade_id") is not None,
                    "price_present": trade.get("price") is not None,
                    "size_present": trade.get("size") is not None,
                    "side_present": trade.get("side") is not None,
                    "event_ts_present": trade.get("trade_ts") is not None,
                    "seen_in_rest": False,
                    "seen_in_ws": True,
                },
                "policy_note": "native trade id exists and core fields are present, but provenance is single-sided",
            }

            trade["origin_hint"] = {
                "source_layer": "collector",
                "provider": "bitflyer_ws",
                "transport": "websocket",
                "endpoint_or_channel": "executions_ws",
                "origin_role": "realtime_primary",
                "collector_id": cfg.collector_id,
                "stream_session_id": stream_session_id,
                "description": "primary realtime trade stream",
            }

            canonical_ctx = EnvelopeContext(
                config=cfg,
                schema_version="collector.vnext.canonical",
                record_type=EventType.MARKET_TRADE,
                channel="executions_ws",
                transport="websocket",
                sequence_id=seq.next(),
                session_id=session_id,
                stream_session_id=stream_session_id,
                exchange="bitflyer",
                exchange_ts=trade.get("trade_ts"),
                source_event_id=str(trade["trade_id"]) if trade.get("trade_id") is not None else None,
                source_sequence=msg.source_sequence,
            )

            record = make_record(canonical_ctx, trade)

            out = write_canonical(
                cfg,
                exchange="bitflyer",
                symbol=cfg.symbol,
                channel="executions_ws",
                record_type=EventType.MARKET_TRADE,
                record=record,
            )
            canonical_path = str(out)
            trade_count += 1

        break

    return {
        "raw_path": raw_path,
        "canonical_path": canonical_path,
        "trade_count": trade_count,
        "stream_session_id": stream_session_id,
        "ssl_verify": cfg.ws_ssl_verify,
    }


def emit_ws_board_smoke(seq: SequenceManager, session_id: str) -> Dict[str, object]:
    cfg = load_config()

    stream_session_id = make_stream_session_id(
        cfg.collector_id,
        "bitflyer",
        "board_ws",
    )

    provider_name = "bitflyer_ws_board"
    endpoint_or_channel = "board_ws"
    board_adapter = BitflyerBoardVenueAdapter()

    raw_path: Optional[str] = None
    canonical_path: Optional[str] = None
    snapshot_canonical_path: Optional[str] = None
    delta_canonical_path: Optional[str] = None
    event_type: Optional[str] = None
    saw_snapshot = False
    saw_delta = False
    board_event_no = 0
    last_board_event_id: Optional[str] = None
    current_base_snapshot_id: Optional[str] = None
    resync_pending = False
    gap_open = False
    resync_started_emitted = False
    skip_canonical = False
    ws_state = "SYNCING"
    sync_started_monotonic = time.monotonic()
    snapshot_to_live_ms: Optional[float] = None
    resync_occurred = False
    pre_snapshot_delta_drop_count = 0

    def _write_control_event(
        *,
        record_type: str,
        payload: Dict[str, object],
        source_event_id: Optional[str] = None,
        last_good_event_id: Optional[str] = None,
        first_uncertain_event_id: Optional[str] = None,
        error_class: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> str:
        control_ctx = EnvelopeContext(
            config=cfg,
            schema_version="collector.vnext.canonical",
            record_type=record_type,
            channel="board_ws_control",
            transport="websocket",
            sequence_id=seq.next(),
            session_id=session_id,
            stream_session_id=stream_session_id,
            exchange="bitflyer",
            source_event_id=source_event_id,
            source_sequence=None,
        )
        control_record = make_record(control_ctx, payload)
        out = write_canonical(
            cfg,
            exchange="bitflyer",
            symbol=cfg.symbol,
            channel="board_ws_control",
            record_type=record_type,
            record=control_record,
        )

        audit.emit(
            make_origin_audit_event_name(record_type),
            level="INFO" if record_type == EventType.STREAM_STARTED else "WARN",
            feature="collector_vnext.origin_audit",
            actor="collector_vnext.emit_ws_board_smoke",
            site="collector_vnext.emit_ws",
            payload=make_origin_audit_payload(
                event_name=str(payload.get("event_name", "")),
                reason=str(payload.get("reason", "")),
                provider=provider_name,
                transport="websocket",
                channel="board_ws",
                endpoint_or_channel=endpoint_or_channel,
                expected_continuity=payload.get("expected_continuity"),
                last_good_event_id=last_good_event_id,
                first_uncertain_event_id=first_uncertain_event_id,
                error_class=error_class,
                error_message=error_message,
                gap_kind=payload.get("gap_kind"),
                resync_required=(
                    True if record_type in (EventType.STREAM_GAP_DETECTED, EventType.STREAM_RESYNC_STARTED) else False
                ),
            ),
        )

        write_origin_status(
            cfg,
            exchange="bitflyer",
            channel="board_ws",
            last_event_name=str(payload.get("event_name", "")),
            reason=str(payload.get("reason", "")),
            stream_session_id=stream_session_id,
            last_good_event_id=last_good_event_id,
            first_uncertain_event_id=first_uncertain_event_id,
            provider=provider_name,
            transport="websocket",
            ws_state=ws_state,
            snapshot_to_live_ms=snapshot_to_live_ms,
            resync_occurred=resync_occurred,
            pre_snapshot_delta_drop_count=pre_snapshot_delta_drop_count,
            error_class=error_class,
            error_message=error_message,
        )

        return str(out)
    
    _write_control_event(
        record_type=EventType.STREAM_STARTED,
        payload=make_stream_started_payload(
            reason="board_ws_smoke_start",
            provider=provider_name,
            endpoint_or_channel=endpoint_or_channel,
        ),
        source_event_id=f"bitflyer:board_ws:{stream_session_id}:control:started",
    )

    try:
        stream = connect_and_stream_board(
            cfg.symbol,
            ssl_verify=cfg.ws_ssl_verify,
        )

        for msg in stream:
            skip_canonical = False

            message_kind = board_adapter.classify_board_message_kind(
                channel=msg.channel,
                payload=msg.payload,
            )

            if message_kind == "unknown":
                continue

            is_snapshot = message_kind == "snapshot"
            record_type = (
                EventType.MARKET_ORDERBOOK_SNAPSHOT
                if is_snapshot
                else EventType.MARKET_ORDERBOOK_DIFF
            )

            raw_ctx = EnvelopeContext(
                config=cfg,
                schema_version="collector.vnext.raw",
                record_type=record_type,
                channel="board_ws",
                transport="websocket",
                sequence_id=seq.next(),
                session_id=session_id,
                stream_session_id=stream_session_id,
                exchange="bitflyer",
            )

            raw_record = make_record(
                raw_ctx,
                {
                    "provider": msg.provider,
                    "exchange": msg.exchange,
                    "transport": msg.transport,
                    "channel": msg.channel,
                    "received_ts": msg.received_ts,
                    "subscription_id": msg.subscription_id,
                    "message_id": msg.message_id,
                    "source_sequence": msg.source_sequence,
                    "raw_message_meta": msg.raw_message_meta,
                    "source_payload": msg.payload,
                },
            )

            raw_out = write_raw(
                cfg,
                exchange="bitflyer",
                symbol=cfg.symbol,
                channel="board_ws",
                record_type=record_type,
                record=raw_record,
            )
            raw_path = str(raw_out)

            canonical_payload = canonical_board_event(
                msg.payload,
                snapshot=is_snapshot,
                adapter=board_adapter,
            )

            board_event_no += 1
            canonical_payload["stream_event_no"] = board_event_no

            if is_snapshot:
                current_event_id = (
                    f"bitflyer:board_ws:{stream_session_id}:snapshot:{board_event_no}"
                )
                snapshot_id = current_event_id
                current_base_snapshot_id = snapshot_id

                if resync_pending or gap_open:
                    continuity_state = "resynced"
                    canonical_payload["is_resync"] = True
                    ws_state = "LIVE"
                    snapshot_to_live_ms = round((time.monotonic() - sync_started_monotonic) * 1000.0, 1)

                    _write_control_event(
                        record_type=EventType.STREAM_RESYNC_COMPLETED,
                        payload=make_stream_resync_completed_payload(
                            reason="snapshot_received_after_gap",
                            provider=provider_name,
                            endpoint_or_channel=endpoint_or_channel,
                            stream_session_id=stream_session_id,
                            resync_target="board_snapshot",
                            new_base_snapshot_id=current_base_snapshot_id,
                        ),
                        source_event_id=f"bitflyer:board_ws:{stream_session_id}:control:resync_completed",
                    )

                    resync_pending = False
                    gap_open = False
                    resync_started_emitted = False
                else:
                    continuity_state = "continuous"
                    ws_state = "LIVE"
                    snapshot_to_live_ms = round((time.monotonic() - sync_started_monotonic) * 1000.0, 1) if saw_snapshot else "unknown"

            else:
                current_event_id = (
                    f"bitflyer:board_ws:{stream_session_id}:delta:{board_event_no}"
                )
                snapshot_id = None
                continuity_state = "continuous" if current_base_snapshot_id is not None else "unknown"

                if current_base_snapshot_id is None:
                    resync_pending = True
                    continuity_state = "gap_detected"
                    ws_state = "STALE"
                    resync_occurred = True
                    pre_snapshot_delta_drop_count += 1

                    if not gap_open:
                        _write_control_event(
                            record_type=EventType.STREAM_GAP_DETECTED,
                            payload=make_stream_gap_detected_payload(
                                reason="delta_arrived_before_snapshot",
                                gap_kind="unknown_continuity",
                                provider=provider_name,
                                endpoint_or_channel=endpoint_or_channel,
                                stream_session_id=stream_session_id,
                                last_good_event_id=last_board_event_id,
                                first_uncertain_event_id=current_event_id,
                            ),
                            source_event_id=f"bitflyer:board_ws:{stream_session_id}:control:gap_detected:{board_event_no}",
                            last_good_event_id=last_board_event_id,
                            first_uncertain_event_id=current_event_id,
                        )
                        gap_open = True

                    if not resync_started_emitted:
                        _write_control_event(
                            record_type=EventType.STREAM_RESYNC_STARTED,
                            payload=make_stream_resync_started_payload(
                                reason="delta_arrived_before_snapshot",
                                provider=provider_name,
                                endpoint_or_channel=endpoint_or_channel,
                                stream_session_id=stream_session_id,
                                resync_target="board_snapshot",
                            ),
                            source_event_id=f"bitflyer:board_ws:{stream_session_id}:control:resync_started:{board_event_no}",
                        )
                        resync_started_emitted = True

                    skip_canonical = True

            if not skip_canonical:
                canonical_payload["snapshot_id"] = snapshot_id
                canonical_payload["base_snapshot_id"] = current_base_snapshot_id
                canonical_payload["prev_event_id"] = last_board_event_id
                canonical_payload["continuity_state"] = continuity_state
                canonical_payload["rebuild_required"] = current_base_snapshot_id is None and not is_snapshot
                canonical_payload["is_gap_fill"] = False
                canonical_payload["is_resync"] = bool(canonical_payload.get("is_resync", False))

                canonical_payload["integration_hint"] = {
                    "integration_domain": "board_continuity_series",
                    "transport_role": "stream_snapshot" if is_snapshot else "stream_delta",
                    "series_key_hint": (
                        f"ws:{stream_session_id}:{current_base_snapshot_id}"
                        if current_base_snapshot_id is not None
                        else f"ws:{stream_session_id}:unknown_base"
                    ),
                    "unified_view_policy": "series_based_not_event_dedupe",
                }
                canonical_payload["dedupe_hint"] = {
                    "entity_kind": "board",
                    "event_dedupe_key": {
                        "exchange": "bitflyer",
                        "instrument_id": f"bitflyer.spot.{cfg.symbol}",
                        "channel": "board_ws",
                        "source_event_id": current_event_id,
                    },
                    "series_key": {
                        "exchange": "bitflyer",
                        "instrument_id": f"bitflyer.spot.{cfg.symbol}",
                        "channel": "board_ws",
                        "base_snapshot_id": current_base_snapshot_id,
                        "stream_session_id": stream_session_id,
                    },
                    "continuity_policy": {
                        "mode": "conservative",
                        "mix_unknown": False,
                        "split_on_gap": True,
                        "split_on_resync": True,
                        "continuous_only_when": continuity_state == "continuous",
                    },
                }

                canonical_payload["completeness_hint"] = {
                    "evaluation_unit": "board_series",
                    "completeness": (
                        "complete"
                        if continuity_state == "continuous" and current_base_snapshot_id is not None and not canonical_payload.get("is_resync", False)
                        else "mostly_complete"
                        if continuity_state == "resynced" and current_base_snapshot_id is not None
                        else "gap_detected"
                        if continuity_state == "gap_detected"
                        else "unknown"
                    ),
                    "confidence_hint": (
                        "high"
                        if continuity_state == "continuous" and current_base_snapshot_id is not None and not canonical_payload.get("is_resync", False)
                        else "medium_high"
                        if continuity_state == "resynced" and current_base_snapshot_id is not None
                        else "low"
                    ),
                    "completeness_basis": {
                        "base_snapshot_id_present": current_base_snapshot_id is not None,
                        "stream_session_id_present": bool(stream_session_id),
                        "source_event_id_present": current_event_id is not None,
                        "continuity_state": continuity_state,
                        "is_resync": bool(canonical_payload.get("is_resync", False)),
                        "transport_role": "stream_snapshot" if is_snapshot else "stream_delta",
                    },
                    "policy_note": "board completeness is evaluated conservatively by continuity series, not by single event",
                }

                canonical_payload["origin_hint"] = {
                    "source_layer": "collector",
                    "provider": "bitflyer_ws_board",
                    "transport": "websocket",
                    "endpoint_or_channel": "board_ws",
                    "origin_role": "realtime_orderbook_stream",
                    "collector_id": cfg.collector_id,
                    "stream_session_id": stream_session_id,
                    "description": "realtime board snapshot/diff stream",
                }

                canonical_ctx = EnvelopeContext(
                    config=cfg,
                    schema_version="collector.vnext.canonical",
                    record_type=record_type,
                    channel="board_ws",
                    transport="websocket",
                    sequence_id=seq.next(),
                    session_id=session_id,
                    stream_session_id=stream_session_id,
                    exchange="bitflyer",
                    exchange_ts=None,  # WSは取引所時刻不明のためNone
                    source_event_id=current_event_id,
                    source_sequence=msg.source_sequence,
                    continuity_sequence=board_event_no,
                )

                canonical_record = make_record(
                    canonical_ctx,
                    canonical_payload,
                )

                out = write_canonical(
                    cfg,
                    exchange="bitflyer",
                    symbol=cfg.symbol,
                    channel="board_ws",
                    record_type=record_type,
                    record=canonical_record,
                )
                canonical_path = str(out)

                if is_snapshot:
                    snapshot_canonical_path = canonical_path
                else:
                    delta_canonical_path = canonical_path

                last_board_event_id = current_event_id

                event_type = canonical_payload["event_type"]

                if is_snapshot:
                    saw_snapshot = True
                else:
                    saw_delta = True

                if saw_snapshot and saw_delta:
                    break

    except Exception as exc:
        _write_control_event(
            record_type=EventType.SYSTEM_PROVIDER_ERROR,
            payload=make_provider_error_payload(
                reason="board_ws_exception",
                provider=provider_name,
                endpoint_or_channel=endpoint_or_channel,
                error_class=exc.__class__.__name__,
                error_message=str(exc),
                retry_after_sec=None,
            ),
            source_event_id=f"bitflyer:board_ws:{stream_session_id}:control:provider_error",
            last_good_event_id=last_board_event_id,
            first_uncertain_event_id=None,
            error_class=exc.__class__.__name__,
            error_message=str(exc),
        )

        _write_control_event(
            record_type=EventType.STREAM_GAP_DETECTED,
            payload=make_stream_gap_detected_payload(
                reason="board_ws_exception",
                gap_kind="provider_error",
                provider=provider_name,
                endpoint_or_channel=endpoint_or_channel,
                stream_session_id=stream_session_id,
                last_good_event_id=last_board_event_id,
                first_uncertain_event_id=None,
            ),
            source_event_id=f"bitflyer:board_ws:{stream_session_id}:control:gap_detected:error",
        )

        _write_control_event(
            record_type=EventType.STREAM_RESYNC_STARTED,
            payload=make_stream_resync_started_payload(
                reason="board_ws_exception",
                provider=provider_name,
                endpoint_or_channel=endpoint_or_channel,
                stream_session_id=stream_session_id,
                resync_target="board_snapshot",
            ),
            source_event_id=f"bitflyer:board_ws:{stream_session_id}:control:resync_started:error",
        )
        raise

    preferred_canonical_path = snapshot_canonical_path or canonical_path
    preferred_event_type = "snapshot" if snapshot_canonical_path else event_type

    return {
        "raw_path": raw_path,
        "canonical_path": preferred_canonical_path,
        "event_type": preferred_event_type,
        "snapshot_canonical_path": snapshot_canonical_path,
        "delta_canonical_path": delta_canonical_path,
        "saw_snapshot": saw_snapshot,
        "saw_delta": saw_delta,
        "ws_state": ws_state,
        "snapshot_to_live_ms": snapshot_to_live_ms,
        "resync_occurred": resync_occurred,
        "pre_snapshot_delta_drop_count": pre_snapshot_delta_drop_count,
        "stream_session_id": stream_session_id,
        "ssl_verify": cfg.ws_ssl_verify,
    }