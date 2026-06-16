# path: ./btcts_next/src/btcts/collector_vnext/unified_ws_executions_lane.py
# desc: Unified Collector 用の最小 WS executions lane。長寿命 loop で executions を記録し、unified executions state を更新する。

from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass
from typing import Optional

from btcts.core import audit

from .config import load_config
from .events import EnvelopeContext, EventType, now_iso_utc, make_record
from .ids import SequenceManager, make_stream_session_id
from .providers.bitflyer_ws import connect_and_stream_executions
from .transforms.facade import (
    apply_trade_structural_hints,
    canonical_ws_trade,
)
from .unified_state import write_unified_executions_status
from .writer import write_canonical, write_raw


@dataclass
class UnifiedWsExecutionsLaneState:
    lane_state: str = "not_started"
    ws_state: str = "NOT_STARTED"
    connected_ts: Optional[str] = None
    last_event_ts: Optional[str] = None
    last_error: Optional[str] = None
    restart_count: int = 0
    trade_count: int = 0


class UnifiedWsExecutionsLane:
    def __init__(self) -> None:
        self.cfg = load_config()
        self.seq = SequenceManager.start()
        self.state = UnifiedWsExecutionsLaneState()
        self._lock = threading.Lock()

    def _env_float(self, name: str, default: float) -> float:
        raw = os.getenv(name, "").strip()
        if not raw:
            return default
        try:
            return float(raw)
        except Exception:
            return default

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "lane_state": self.state.lane_state,
                "ws_state": self.state.ws_state,
                "connected_ts": self.state.connected_ts,
                "last_event_ts": self.state.last_event_ts,
                "last_error": self.state.last_error,
                "restart_count": self.state.restart_count,
                "trade_count": self.state.trade_count,
            }

    def _set_state(self, **kwargs) -> None:
        with self._lock:
            for key, value in kwargs.items():
                setattr(self.state, key, value)

    def _write_status(self) -> None:
        snap = self.snapshot()
        write_unified_executions_status(
            self.cfg,
            {
                "ts": snap["last_event_ts"] or snap["connected_ts"] or now_iso_utc(),
                "runtime_kind": "unified",
                "exchange": "bitflyer",
                "channel": "executions_ws",
                "ws_state": snap["ws_state"],
                "lane_state": snap["lane_state"],
                "connected_ts": snap["connected_ts"],
                "last_error": snap["last_error"],
                "restart_count": snap["restart_count"],
                "trade_count": snap["trade_count"],
            },
        )

    def run_forever(self, stop_event: threading.Event) -> None:
        stream_session_id = make_stream_session_id(
            self.cfg.collector_id,
            "bitflyer",
            "unified_executions_ws",
        )
        reconnect_backoff_sec = max(
            0.5,
            self._env_float("BTCTS_UNIFIED_WS_EXECUTIONS_RECONNECT_BACKOFF_SEC", 2.0),
        )

        audit.emit(
            "collector_vnext.unified.ws_executions.started",
            level="INFO",
            feature="collector_vnext",
            actor="collector_vnext.unified_ws_executions_lane",
            site="collector_vnext.unified_ws_executions_lane.run_forever",
            payload={
                "collector_id": self.cfg.collector_id,
                "collector_role": self.cfg.collector_role,
                "exchange": "bitflyer",
                "topic": "ws_executions",
                "stream_session_id": stream_session_id,
                "symbol": self.cfg.symbol,
                "ssl_verify": self.cfg.ws_ssl_verify,
            },
        )

        while not stop_event.is_set():
            try:
                self._set_state(
                    lane_state="connecting",
                    ws_state="CONNECTING",
                    last_error=None,
                )
                self._write_status()

                stream = connect_and_stream_executions(
                    self.cfg.symbol,
                    ssl_verify=self.cfg.ws_ssl_verify,
                    recv_timeout_sec=60.0,
                    ca_file=str(self.cfg.ws_ca_file) if self.cfg.ws_ca_file else None,
                )

                audit.emit(
                    "collector_vnext.unified.ws_executions.connected",
                    level="INFO",
                    feature="collector_vnext",
                    actor="collector_vnext.unified_ws_executions_lane",
                    site="collector_vnext.unified_ws_executions_lane.run_forever",
                    payload={
                        "collector_id": self.cfg.collector_id,
                        "collector_role": self.cfg.collector_role,
                        "exchange": "bitflyer",
                        "topic": "ws_executions",
                        "stream_session_id": stream_session_id,
                    },
                )

                self._set_state(
                    lane_state="connected",
                    ws_state="CONNECTING",
                    connected_ts=now_iso_utc(),
                    last_error=None,
                )
                self._write_status()

                for msg in stream:
                    if stop_event.is_set():
                        break

                    audit.emit(
                        "collector_vnext.unified.ws_executions.message.received",
                        level="INFO",
                        feature="collector_vnext",
                        actor="collector_vnext.unified_ws_executions_lane",
                        site="collector_vnext.unified_ws_executions_lane.run_forever",
                        payload={
                            "collector_id": self.cfg.collector_id,
                            "collector_role": self.cfg.collector_role,
                            "exchange": "bitflyer",
                            "topic": "ws_executions",
                            "stream_session_id": stream_session_id,
                            "received_ts": msg.received_ts,
                            "provider": msg.provider,
                            "channel": msg.channel,
                        },
                    )

                    record_type = (
                        EventType.MARKET_TRADE
                        if msg.provider == "bitflyer_ws_executions"
                        else EventType.SYSTEM_PROVIDER_ERROR
                    )

                    raw_ctx = EnvelopeContext(
                        config=self.cfg,
                        schema_version="collector.vnext.raw",
                        record_type=record_type,
                        channel="executions_ws",
                        transport="websocket",
                        sequence_id=self.seq.next(),
                        session_id=f"{self.cfg.collector_id}-unified",
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

                    write_raw(
                        self.cfg,
                        exchange="bitflyer",
                        symbol=self.cfg.symbol,
                        channel="executions_ws",
                        record_type=record_type,
                        record=raw_record,
                    )

                    if msg.provider != "bitflyer_ws_executions":
                        audit.emit(
                            "collector_vnext.unified.ws_executions.message.meta",
                            level="WARN",
                            feature="collector_vnext",
                            actor="collector_vnext.unified_ws_executions_lane",
                            site="collector_vnext.unified_ws_executions_lane.run_forever",
                            payload={
                                "collector_id": self.cfg.collector_id,
                                "collector_role": self.cfg.collector_role,
                                "exchange": "bitflyer",
                                "topic": "ws_executions",
                                "stream_session_id": stream_session_id,
                                "provider": msg.provider,
                                "meta_event": msg.payload.get("_meta_event") if isinstance(msg.payload, dict) else None,
                            },
                        )
                        continue

                    trade = canonical_ws_trade(msg.payload)
                    if not trade:
                        audit.emit(
                            "collector_vnext.unified.ws_executions.message.skipped",
                            level="WARN",
                            feature="collector_vnext",
                            actor="collector_vnext.unified_ws_executions_lane",
                            site="collector_vnext.unified_ws_executions_lane.run_forever",
                            payload={
                                "collector_id": self.cfg.collector_id,
                                "collector_role": self.cfg.collector_role,
                                "exchange": "bitflyer",
                                "topic": "ws_executions",
                                "stream_session_id": stream_session_id,
                                "reason": "canonical_ws_trade_returned_none",
                                "payload_keys": sorted(list(msg.payload.keys())) if isinstance(msg.payload, dict) else None,
                            },
                        )
                        continue

                    apply_trade_structural_hints(
                        trade,
                        exchange="bitflyer",
                        symbol=self.cfg.symbol,
                        channel="executions_ws",
                        provider="bitflyer_ws_executions",
                        transport="websocket",
                        transport_role="realtime_primary",
                        origin_role="realtime_trade_stream",
                        collector_id=self.cfg.collector_id,
                        stream_session_id=stream_session_id,
                        seen_in_rest=False,
                        seen_in_ws=True,
                        description="unified realtime executions stream",
                    )

                    canonical_ctx = EnvelopeContext(
                        config=self.cfg,
                        schema_version="collector.vnext.canonical",
                        record_type=EventType.MARKET_TRADE,
                        channel="executions_ws",
                        transport="websocket",
                        sequence_id=self.seq.next(),
                        session_id=f"{self.cfg.collector_id}-unified",
                        stream_session_id=stream_session_id,
                        exchange="bitflyer",
                        exchange_ts=trade.get("trade_ts"),
                        source_event_id=str(trade.get("trade_id")) if trade.get("trade_id") is not None else None,
                        source_sequence=msg.source_sequence,
                    )

                    canonical_record = make_record(
                        canonical_ctx,
                        trade,
                    )

                    write_canonical(
                        self.cfg,
                        exchange="bitflyer",
                        symbol=self.cfg.symbol,
                        channel="executions_ws",
                        record_type=EventType.MARKET_TRADE,
                        record=canonical_record,
                    )

                    lane_snapshot = self.snapshot()
                    self._set_state(
                        lane_state="live",
                        ws_state="LIVE",
                        last_event_ts=msg.received_ts or now_iso_utc(),
                        last_error=None,
                        trade_count=int(lane_snapshot.get("trade_count") or 0) + 1,
                    )
                    self._write_status()

                    audit.emit(
                        "collector_vnext.unified.ws_executions.trade.written",
                        level="INFO",
                        feature="collector_vnext",
                        actor="collector_vnext.unified_ws_executions_lane",
                        site="collector_vnext.unified_ws_executions_lane.run_forever",
                        payload={
                            "collector_id": self.cfg.collector_id,
                            "collector_role": self.cfg.collector_role,
                            "exchange": "bitflyer",
                            "topic": "ws_executions",
                            "stream_session_id": stream_session_id,
                            "trade_id": trade.get("trade_id"),
                            "trade_count": int(self.snapshot().get("trade_count") or 0),
                        },
                    )

            except Exception as exc:
                lane_snapshot = self.snapshot()
                next_restart_count = int(lane_snapshot.get("restart_count") or 0) + 1

                self._set_state(
                    lane_state="degraded",
                    ws_state="BROKEN",
                    last_error=str(exc),
                    restart_count=next_restart_count,
                )
                self._write_status()

                audit.emit(
                    "collector_vnext.unified.ws_executions.reconnected",
                    level="WARN",
                    feature="collector_vnext",
                    actor="collector_vnext.unified_ws_executions_lane",
                    site="collector_vnext.unified_ws_executions_lane.run_forever",
                    payload={
                        "collector_id": self.cfg.collector_id,
                        "collector_role": self.cfg.collector_role,
                        "exchange": "bitflyer",
                        "topic": "ws_executions",
                        "error": str(exc),
                        "restart_count": next_restart_count,
                        "reconnect_backoff_sec": reconnect_backoff_sec,
                    },
                )

                if stop_event.wait(reconnect_backoff_sec):
                    break