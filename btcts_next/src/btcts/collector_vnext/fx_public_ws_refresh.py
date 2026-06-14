# path: ./btcts_next/src/btcts/collector_vnext/fx_public_ws_refresh.py
# desc: SR-FX public WS canonical refresh helpers that read until fresh board snapshot/trade are observed. No broker calls.

from __future__ import annotations

from typing import Any, Callable, Iterable

from .config import load_config
from .events import EnvelopeContext, EventType, make_record
from .fx_public_rest import execution_market_config, market_identity_payload
from .ids import SequenceManager, make_stream_session_id
from .providers.bitflyer_ws import WSMessage, connect_and_stream_executions
from .providers.bitflyer_ws_board import BoardMessage, connect_and_stream_board
from .transforms.facade import (
    apply_board_structural_hints,
    apply_trade_structural_hints,
    canonical_board_event,
    canonical_ws_trade,
)
from .venue_adapters.bitflyer_board import BitflyerBoardVenueAdapter
from .writer import write_canonical, write_raw


def _exception_blockers(*, prefix: str, exc: Exception) -> list[str]:
    cls = exc.__class__.__name__
    text = str(exc)
    blockers = [f"{prefix}_failed"]
    if "SSL" in cls or "CERT" in cls.upper() or "certificate" in text.lower():
        blockers.append("fx_ws_tls_certificate_verification_failed")
    return list(dict.fromkeys(blockers))


def _exception_result(
    *,
    prefix: str,
    exchange: str,
    product_code: str,
    market_uid: str,
    market_role: str,
    request_class: str,
    stream_session_id: str,
    exc: Exception,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "ok": False,
        "exchange": exchange,
        "product_code": product_code,
        "market_uid": market_uid,
        "market_role": market_role,
        "request_class": request_class,
        "stream_session_id": stream_session_id,
        "blocked_by": _exception_blockers(prefix=prefix, exc=exc),
        "error_class": exc.__class__.__name__,
        "error_message": str(exc),
        "read_only": True,
        "would_send_to_broker": False,
        **dict(extra or {}),
    }


def refresh_fx_ws_board_snapshot_until_seen(
    seq: SequenceManager,
    session_id: str,
    *,
    max_messages: int = 20,
    stream_factory: Callable[..., Iterable[BoardMessage]] = connect_and_stream_board,
) -> dict[str, Any]:
    """Write FX board WS canonical events until at least one snapshot is seen."""

    cfg = execution_market_config(load_config())
    exe = cfg.execution_market.normalized()
    exchange = exe.exchange
    request_class = "public_ws_connect_subscribe"
    stream_session_id = make_stream_session_id(cfg.collector_id, exchange, "fx_board_ws_refresh")
    market_meta = market_identity_payload(exe, source="public_ws", request_class=request_class)
    adapter = BitflyerBoardVenueAdapter()

    raw_path: str | None = None
    canonical_path: str | None = None
    snapshot_canonical_path: str | None = None
    message_count = 0
    snapshot_count = 0
    delta_count = 0
    last_event_type: str | None = None

    try:
        stream = stream_factory(
            exe.product_code,
            ssl_verify=cfg.ws_ssl_verify,
            ca_file=str(cfg.ws_ca_file) if cfg.ws_ca_file else None,
        )
        for msg in stream:
            message_count += 1
            is_snapshot = "snapshot" in str(msg.channel)
            record_type = EventType.MARKET_ORDERBOOK_SNAPSHOT if is_snapshot else EventType.MARKET_ORDERBOOK_DIFF
            event_type = "snapshot" if is_snapshot else "delta"
            last_event_type = event_type
            if is_snapshot:
                snapshot_count += 1
            else:
                delta_count += 1

            raw_payload = {
                "provider": msg.provider,
                "exchange": msg.exchange,
                "transport": msg.transport,
                "channel": msg.channel,
                "received_ts": msg.received_ts,
                "subscription_id": msg.subscription_id,
                "message_id": msg.message_id,
                "source_sequence": msg.source_sequence,
                "raw_message_meta": msg.raw_message_meta,
                "market_identity": market_meta,
                "source_payload": msg.payload,
            }
            raw_ctx = EnvelopeContext(
                config=cfg,
                schema_version="collector.vnext.raw",
                record_type=record_type,
                channel="board_ws",
                transport="websocket",
                sequence_id=seq.next(),
                session_id=session_id,
                stream_session_id=stream_session_id,
                exchange=exchange,
            )
            raw_record = make_record(raw_ctx, raw_payload)
            raw_path = str(write_raw(cfg, exchange=exchange, symbol=exe.product_code, channel="board_ws", record_type=record_type, record=raw_record))

            canonical_payload = canonical_board_event(msg.payload, snapshot=is_snapshot, adapter=adapter)
            canonical_payload["market_identity"] = market_meta
            canonical_payload["product_code"] = exe.product_code
            canonical_payload["market_type"] = exe.market_type
            canonical_payload["market_role"] = exe.role
            canonical_payload["market_uid"] = exe.market_uid
            current_event_id = f"bitflyer:fx_board_ws_refresh:{stream_session_id}:{event_type}:{message_count}"
            canonical_payload["snapshot_id"] = current_event_id if is_snapshot else None
            canonical_payload["base_snapshot_id"] = current_event_id if is_snapshot else canonical_payload.get("base_snapshot_id")
            canonical_payload["continuity_state"] = "continuous" if is_snapshot else str(canonical_payload.get("continuity_state") or "unknown")
            canonical_payload["is_resync"] = False
            apply_board_structural_hints(
                canonical_payload,
                exchange=exchange,
                symbol=exe.product_code,
                channel="board_ws",
                provider="bitflyer_ws_board",
                transport="websocket",
                transport_role="stream_snapshot" if is_snapshot else "stream_delta",
                origin_role="execution_market_realtime_orderbook_stream",
                collector_id=cfg.collector_id,
                stream_session_id=stream_session_id,
                current_event_id=current_event_id,
                base_snapshot_id=canonical_payload.get("base_snapshot_id"),
                continuity_state=str(canonical_payload.get("continuity_state") or "unknown"),
                is_resync=False,
                description="FX execution-market bounded WS board refresh",
            )
            canonical_ctx = EnvelopeContext(
                config=cfg,
                schema_version="collector.vnext.canonical",
                record_type=record_type,
                channel="board_ws",
                transport="websocket",
                sequence_id=seq.next(),
                session_id=session_id,
                stream_session_id=stream_session_id,
                exchange=exchange,
                source_event_id=current_event_id,
                source_sequence=msg.source_sequence,
            )
            canonical_record = make_record(canonical_ctx, canonical_payload)
            canonical_path = str(write_canonical(cfg, exchange=exchange, symbol=exe.product_code, channel="board_ws", record_type=record_type, record=canonical_record))
            if is_snapshot:
                snapshot_canonical_path = canonical_path
                break
            if message_count >= max_messages:
                break
    except Exception as exc:
        return _exception_result(
            prefix="fx_ws_board_refresh",
            exchange=exchange,
            product_code=exe.product_code,
            market_uid=exe.market_uid,
            market_role=exe.role,
            request_class=request_class,
            stream_session_id=stream_session_id,
            exc=exc,
            extra={
                "raw_path": raw_path,
                "canonical_path": canonical_path,
                "snapshot_canonical_path": snapshot_canonical_path,
                "message_count": message_count,
                "snapshot_count": snapshot_count,
                "delta_count": delta_count,
                "last_event_type": last_event_type,
            },
        )

    blocked_by: list[str] = []
    if snapshot_count <= 0:
        blocked_by.append("fx_ws_board_snapshot_not_seen")
    if message_count <= 0:
        blocked_by.append("fx_ws_board_message_not_seen")

    return {
        "ok": not blocked_by,
        "exchange": exchange,
        "product_code": exe.product_code,
        "market_uid": exe.market_uid,
        "market_role": exe.role,
        "request_class": request_class,
        "raw_path": raw_path,
        "canonical_path": canonical_path,
        "snapshot_canonical_path": snapshot_canonical_path,
        "message_count": message_count,
        "snapshot_count": snapshot_count,
        "delta_count": delta_count,
        "last_event_type": last_event_type,
        "stream_session_id": stream_session_id,
        "blocked_by": blocked_by,
        "read_only": True,
        "would_send_to_broker": False,
    }


def refresh_fx_ws_executions_until_seen(
    seq: SequenceManager,
    session_id: str,
    *,
    max_messages: int = 20,
    stream_factory: Callable[..., Iterable[WSMessage]] = connect_and_stream_executions,
) -> dict[str, Any]:
    """Write FX executions WS canonical trades until at least one trade is seen."""

    cfg = execution_market_config(load_config())
    exe = cfg.execution_market.normalized()
    exchange = exe.exchange
    request_class = "public_ws_connect_subscribe"
    stream_session_id = make_stream_session_id(cfg.collector_id, exchange, "fx_executions_ws_refresh")
    market_meta = market_identity_payload(exe, source="public_ws", request_class=request_class)

    raw_path: str | None = None
    canonical_path: str | None = None
    message_count = 0
    trade_count = 0

    try:
        stream = stream_factory(
            exe.product_code,
            ssl_verify=cfg.ws_ssl_verify,
            recv_timeout_sec=60.0,
            ca_file=str(cfg.ws_ca_file) if cfg.ws_ca_file else None,
        )
        for msg in stream:
            message_count += 1
            raw_payload = {
                "provider": msg.provider,
                "exchange": msg.exchange,
                "transport": msg.transport,
                "channel": msg.channel,
                "received_ts": msg.received_ts,
                "subscription_id": msg.subscription_id,
                "message_id": msg.message_id,
                "source_sequence": msg.source_sequence,
                "raw_message_meta": msg.raw_message_meta,
                "market_identity": market_meta,
                "source_payload": msg.payload,
            }
            raw_ctx = EnvelopeContext(
                config=cfg,
                schema_version="collector.vnext.raw",
                record_type=EventType.MARKET_TRADE,
                channel="executions_ws",
                transport="websocket",
                sequence_id=seq.next(),
                session_id=session_id,
                stream_session_id=stream_session_id,
                exchange=exchange,
            )
            raw_record = make_record(raw_ctx, raw_payload)
            raw_path = str(write_raw(cfg, exchange=exchange, symbol=exe.product_code, channel="executions_ws", record_type=EventType.MARKET_TRADE, record=raw_record))

            trade = canonical_ws_trade(msg.payload)
            if trade:
                trade["market_identity"] = market_meta
                trade["product_code"] = exe.product_code
                trade["market_type"] = exe.market_type
                trade["market_role"] = exe.role
                trade["market_uid"] = exe.market_uid
                apply_trade_structural_hints(
                    trade,
                    exchange=exchange,
                    symbol=exe.product_code,
                    channel="executions_ws",
                    provider="bitflyer_ws",
                    transport="websocket",
                    transport_role="realtime_primary",
                    origin_role="execution_market_realtime_trade_stream",
                    collector_id=cfg.collector_id,
                    stream_session_id=stream_session_id,
                    seen_in_rest=False,
                    seen_in_ws=True,
                    description="FX execution-market bounded WS executions refresh",
                )
                canonical_ctx = EnvelopeContext(
                    config=cfg,
                    schema_version="collector.vnext.canonical",
                    record_type=EventType.MARKET_TRADE,
                    channel="executions_ws",
                    transport="websocket",
                    sequence_id=seq.next(),
                    session_id=session_id,
                    stream_session_id=stream_session_id,
                    exchange=exchange,
                    exchange_ts=trade.get("trade_ts"),
                    source_event_id=str(trade["trade_id"]) if trade.get("trade_id") is not None else None,
                    source_sequence=msg.source_sequence,
                )
                record = make_record(canonical_ctx, trade)
                canonical_path = str(write_canonical(cfg, exchange=exchange, symbol=exe.product_code, channel="executions_ws", record_type=EventType.MARKET_TRADE, record=record))
                trade_count += 1
                break
            if message_count >= max_messages:
                break
    except Exception as exc:
        return _exception_result(
            prefix="fx_ws_executions_refresh",
            exchange=exchange,
            product_code=exe.product_code,
            market_uid=exe.market_uid,
            market_role=exe.role,
            request_class=request_class,
            stream_session_id=stream_session_id,
            exc=exc,
            extra={
                "raw_path": raw_path,
                "canonical_path": canonical_path,
                "message_count": message_count,
                "trade_count": trade_count,
            },
        )

    blocked_by: list[str] = []
    if trade_count <= 0:
        blocked_by.append("fx_ws_execution_trade_not_seen")
    if message_count <= 0:
        blocked_by.append("fx_ws_execution_message_not_seen")

    return {
        "ok": not blocked_by,
        "exchange": exchange,
        "product_code": exe.product_code,
        "market_uid": exe.market_uid,
        "market_role": exe.role,
        "request_class": request_class,
        "raw_path": raw_path,
        "canonical_path": canonical_path,
        "message_count": message_count,
        "trade_count": trade_count,
        "stream_session_id": stream_session_id,
        "blocked_by": blocked_by,
        "read_only": True,
        "would_send_to_broker": False,
    }

