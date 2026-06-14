# path: ./btcts_next/src/btcts/collector_vnext/fx_public_ws.py
# desc: SR-FX public WebSocket helpers for execution-market bitFlyer FX data.

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Optional

from .events import EnvelopeContext, EventType, make_record
from .fx_public_rest import execution_market_config, market_identity_payload
from .ids import SequenceManager, make_stream_session_id
from .config import load_config
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


def fx_ws_channel_plan() -> Dict[str, object]:
    cfg = execution_market_config(load_config())
    exe = cfg.execution_market.normalized()
    channels = {
        "board_snapshot": f"lightning_board_snapshot_{exe.product_code}",
        "board_delta": f"lightning_board_{exe.product_code}",
        "executions": f"lightning_executions_{exe.product_code}",
    }
    return {
        "ok": True,
        "exchange": exe.exchange,
        "product_code": exe.product_code,
        "market_type": exe.market_type,
        "market_role": exe.role,
        "market_uid": exe.market_uid,
        "channels": channels,
        "path_guard": {
            "all_channels_are_fx_symbol": all("FX_BTC_JPY" in v for v in channels.values()),
            "no_channel_is_spot_symbol": not any(v.endswith("BTC_JPY") and "FX_BTC_JPY" not in v for v in channels.values()),
        },
    }


def emit_fx_ws_trade_smoke(
    seq: SequenceManager,
    session_id: str,
    *,
    stream_factory: Callable[..., Iterable[WSMessage]] = connect_and_stream_executions,
) -> Dict[str, object]:
    cfg = execution_market_config(load_config())
    exe = cfg.execution_market.normalized()
    exchange = exe.exchange
    request_class = "public_ws_connect_subscribe"
    stream_session_id = make_stream_session_id(cfg.collector_id, exchange, "fx_executions_ws")
    market_meta = market_identity_payload(exe, source="public_ws", request_class=request_class)

    raw_path: Optional[str] = None
    canonical_path: Optional[str] = None
    trade_count = 0

    for msg in stream_factory(exe.product_code, ssl_verify=cfg.ws_ssl_verify, recv_timeout_sec=60.0):
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
        raw_path = str(write_raw(
            cfg,
            exchange=exchange,
            symbol=exe.product_code,
            channel="executions_ws",
            record_type=EventType.MARKET_TRADE,
            record=raw_record,
        ))

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
                description="FX execution-market realtime trade stream",
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
            canonical_path = str(write_canonical(
                cfg,
                exchange=exchange,
                symbol=exe.product_code,
                channel="executions_ws",
                record_type=EventType.MARKET_TRADE,
                record=record,
            ))
            trade_count += 1
        break

    return {
        "ok": True,
        "exchange": exchange,
        "product_code": exe.product_code,
        "market_uid": exe.market_uid,
        "market_role": exe.role,
        "request_class": request_class,
        "raw_path": raw_path,
        "canonical_path": canonical_path,
        "trade_count": trade_count,
        "stream_session_id": stream_session_id,
        "ssl_verify": cfg.ws_ssl_verify,
    }


def emit_fx_ws_board_smoke(
    seq: SequenceManager,
    session_id: str,
    *,
    stream_factory: Callable[..., Iterable[BoardMessage]] = connect_and_stream_board,
) -> Dict[str, object]:
    cfg = execution_market_config(load_config())
    exe = cfg.execution_market.normalized()
    exchange = exe.exchange
    request_class = "public_ws_connect_subscribe"
    stream_session_id = make_stream_session_id(cfg.collector_id, exchange, "fx_board_ws")
    market_meta = market_identity_payload(exe, source="public_ws", request_class=request_class)
    adapter = BitflyerBoardVenueAdapter()

    raw_path: Optional[str] = None
    canonical_path: Optional[str] = None
    event_type: Optional[str] = None

    for msg in stream_factory(exe.product_code, ssl_verify=cfg.ws_ssl_verify):
        is_snapshot = "snapshot" in str(msg.channel)
        record_type = EventType.MARKET_ORDERBOOK_SNAPSHOT if is_snapshot else EventType.MARKET_ORDERBOOK_DIFF
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
        raw_path = str(write_raw(
            cfg,
            exchange=exchange,
            symbol=exe.product_code,
            channel="board_ws",
            record_type=record_type,
            record=raw_record,
        ))

        canonical_payload = canonical_board_event(msg.payload, snapshot=is_snapshot, adapter=adapter)
        canonical_payload["market_identity"] = market_meta
        canonical_payload["product_code"] = exe.product_code
        canonical_payload["market_type"] = exe.market_type
        canonical_payload["market_role"] = exe.role
        canonical_payload["market_uid"] = exe.market_uid
        current_event_id = f"bitflyer:fx_board_ws:{stream_session_id}:{'snapshot' if is_snapshot else 'delta'}:1"
        canonical_payload["snapshot_id"] = current_event_id if is_snapshot else None
        canonical_payload["base_snapshot_id"] = current_event_id if is_snapshot else None
        canonical_payload["continuity_state"] = "continuous" if is_snapshot else "unknown"
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
            description="FX execution-market realtime board stream",
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
        canonical_path = str(write_canonical(
            cfg,
            exchange=exchange,
            symbol=exe.product_code,
            channel="board_ws",
            record_type=record_type,
            record=canonical_record,
        ))
        event_type = "snapshot" if is_snapshot else "delta"
        break

    return {
        "ok": True,
        "exchange": exchange,
        "product_code": exe.product_code,
        "market_uid": exe.market_uid,
        "market_role": exe.role,
        "request_class": request_class,
        "raw_path": raw_path,
        "canonical_path": canonical_path,
        "event_type": event_type,
        "stream_session_id": stream_session_id,
        "ssl_verify": cfg.ws_ssl_verify,
    }



def _payload_shape(payload: Any) -> Dict[str, object]:
    if isinstance(payload, dict):
        return {"payload_type": "dict", "payload_keys": sorted(str(k) for k in payload.keys())}
    if isinstance(payload, list):
        return {"payload_type": "list", "payload_len": len(payload)}
    return {"payload_type": type(payload).__name__}


def _safe_next_message(stream: Iterable[Any]) -> Any:
    iterator = iter(stream)
    return next(iterator)


def preflight_fx_public_ws(
    *,
    check_executions: bool = True,
    check_board: bool = True,
    executions_stream_factory: Callable[..., Iterable[WSMessage]] = connect_and_stream_executions,
    board_stream_factory: Callable[..., Iterable[BoardMessage]] = connect_and_stream_board,
) -> Dict[str, object]:
    """Safely check SR-FX public WS connectivity/channel identity.

    This function is diagnostic only. It does not write market data and never sends broker orders.
    Connection/SSL failures are returned as structured attempt records instead of bubbling up.
    """

    cfg = execution_market_config(load_config())
    exe = cfg.execution_market.normalized()
    plan = fx_ws_channel_plan()
    attempts: Dict[str, object] = {}

    if check_executions:
        expected_channel = str(plan["channels"]["executions"])
        try:
            msg = _safe_next_message(executions_stream_factory(exe.product_code, ssl_verify=cfg.ws_ssl_verify, recv_timeout_sec=10.0))
            actual_channel = str(getattr(msg, "channel", ""))
            attempts["executions"] = {
                "ok": actual_channel == expected_channel,
                "expected_channel": expected_channel,
                "actual_channel": actual_channel,
                "provider": getattr(msg, "provider", None),
                "received_ts": getattr(msg, "received_ts", None),
                "message_shape": _payload_shape(getattr(msg, "payload", None)),
            }
        except Exception as exc:
            attempts["executions"] = {
                "ok": False,
                "expected_channel": expected_channel,
                "actual_channel": None,
                "error_class": exc.__class__.__name__,
                "error_message": str(exc),
            }

    if check_board:
        expected_channels = {
            str(plan["channels"]["board_snapshot"]),
            str(plan["channels"]["board_delta"]),
        }
        try:
            msg = _safe_next_message(board_stream_factory(exe.product_code, ssl_verify=cfg.ws_ssl_verify))
            actual_channel = str(getattr(msg, "channel", ""))
            attempts["board"] = {
                "ok": actual_channel in expected_channels,
                "expected_channels": sorted(expected_channels),
                "actual_channel": actual_channel,
                "provider": getattr(msg, "provider", None),
                "received_ts": getattr(msg, "received_ts", None),
                "message_shape": _payload_shape(getattr(msg, "payload", None)),
            }
        except Exception as exc:
            attempts["board"] = {
                "ok": False,
                "expected_channels": sorted(expected_channels),
                "actual_channel": None,
                "error_class": exc.__class__.__name__,
                "error_message": str(exc),
            }

    attempted = [v for v in attempts.values() if isinstance(v, dict)]
    return {
        "ok": bool(attempted) and all(bool(v.get("ok")) for v in attempted),
        "exchange": exe.exchange,
        "product_code": exe.product_code,
        "market_type": exe.market_type,
        "market_role": exe.role,
        "market_uid": exe.market_uid,
        "ssl_verify": cfg.ws_ssl_verify,
        "channel_plan": plan,
        "attempts": attempts,
        "read_only": True,
        "would_send_to_broker": False,
    }
