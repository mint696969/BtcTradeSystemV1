# path: ./btcts_next/src/btcts/collector_vnext/unified_ws_board_lane.py
# desc: Unified Collector 用の最小 WS board lane。長寿命 loop で board snapshot/diff を記録し、unified state を更新する。

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
from .providers.bitflyer_ws_board import connect_and_stream_board
from .transforms.facade import (
    apply_board_structural_hints,
    canonical_board_event,
)
from .unified_state import write_unified_origin_status
from .unified_market_state_lane import UnifiedMarketStateLane
from .venue_adapters.bitflyer_board import BitflyerBoardVenueAdapter
from .writer import write_canonical, write_raw


@dataclass
class UnifiedWsBoardLaneState:
    lane_state: str = "not_started"
    ws_state: str = "NOT_STARTED"
    last_event_ts: Optional[str] = None
    last_error: Optional[str] = None
    restart_count: int = 0
    saw_snapshot: bool = False
    saw_delta: bool = False


class UnifiedWsBoardLane:
    def __init__(self) -> None:
        self.cfg = load_config()
        self.seq = SequenceManager.start()
        self.adapter = BitflyerBoardVenueAdapter()
        self.market_state_lane = UnifiedMarketStateLane()
        self.state = UnifiedWsBoardLaneState()
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
                "last_event_ts": self.state.last_event_ts,
                "last_error": self.state.last_error,
                "restart_count": self.state.restart_count,
                "saw_snapshot": self.state.saw_snapshot,
                "saw_delta": self.state.saw_delta,
            }

    def _set_state(self, **kwargs) -> None:
        with self._lock:
            for key, value in kwargs.items():
                setattr(self.state, key, value)

    def _write_origin_status(self) -> None:
        snap = self.snapshot()
        write_unified_origin_status(
            self.cfg,
            {
                "ts": snap["last_event_ts"] or now_iso_utc(),
                "runtime_kind": "unified",
                "exchange": "bitflyer",
                "channel": "board_ws",
                "ws_state": snap["ws_state"],
                "lane_state": snap["lane_state"],
                "last_error": snap["last_error"],
                "saw_snapshot": snap["saw_snapshot"],
                "saw_delta": snap["saw_delta"],
                "gap_detected": False,
                "resync_active": False,
                "restart_count": snap["restart_count"],
            },
        )

    def run_forever(self, stop_event: threading.Event) -> None:
        provider_name = "bitflyer_ws_board"
        stream_session_id = make_stream_session_id(
            self.cfg.collector_id,
            "bitflyer",
            "unified_board_ws",
        )
        board_event_no = 0
        last_board_event_id: Optional[str] = None
        current_base_snapshot_id: Optional[str] = None
        reconnect_backoff_sec = max(
            0.5,
            self._env_float("BTCTS_UNIFIED_WS_BOARD_RECONNECT_BACKOFF_SEC", 2.0),
        )

        audit.emit(
            "collector_vnext.unified.ws_board.started",
            level="INFO",
            feature="collector_vnext",
            actor="collector_vnext.unified_ws_board_lane",
            site="collector_vnext.unified_ws_board_lane.run_forever",
            payload={
                "collector_id": self.cfg.collector_id,
                "collector_role": self.cfg.collector_role,
                "exchange": "bitflyer",
                "topic": "ws_board",
                "stream_session_id": stream_session_id,
            },
        )

        while not stop_event.is_set():
            try:
                self._set_state(
                    lane_state="connecting",
                    ws_state="CONNECTING",
                    last_error=None,
                )
                self._write_origin_status()

                stream = connect_and_stream_board(
                    self.cfg.symbol,
                    ssl_verify=self.cfg.ws_ssl_verify,
                    ca_file=str(self.cfg.ws_ca_file) if self.cfg.ws_ca_file else None,
                )

                self._set_state(
                    lane_state="connected",
                    ws_state="CONNECTING",
                )
                self._write_origin_status()

                for msg in stream:
                    if stop_event.is_set():
                        break

                    message_kind = self.adapter.classify_board_message_kind(
                        channel=msg.channel,
                        payload=msg.payload,
                    )
                    if message_kind == "unknown":
                        continue

                    board_event_no += 1

                    lane_snapshot = self.snapshot()
                    is_snapshot = message_kind == "snapshot"
                    record_type = (
                        EventType.MARKET_ORDERBOOK_SNAPSHOT
                        if is_snapshot
                        else EventType.MARKET_ORDERBOOK_DIFF
                    )

                    raw_ctx = EnvelopeContext(
                        config=self.cfg,
                        schema_version="collector.vnext.raw",
                        record_type=record_type,
                        channel="board_ws",
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
                        channel="board_ws",
                        record_type=record_type,
                        record=raw_record,
                    )

                    canonical_payload = canonical_board_event(
                        msg.payload,
                        snapshot=is_snapshot,
                        adapter=self.adapter,
                    )
                    event_id_kind = "snapshot" if is_snapshot else "delta"
                    current_event_id = (
                        f"bitflyer:unified:board_ws:{stream_session_id}:{event_id_kind}:{board_event_no}"
                    )

                    if is_snapshot:
                        current_base_snapshot_id = current_event_id

                    continuity_state = (
                        "continuous" if current_base_snapshot_id is not None else "unknown"
                    )

                    canonical_payload["stream_event_no"] = board_event_no
                    canonical_payload["snapshot_id"] = current_event_id if is_snapshot else None
                    canonical_payload["continuity_state"] = continuity_state
                    canonical_payload["base_snapshot_id"] = current_base_snapshot_id
                    canonical_payload["prev_event_id"] = last_board_event_id
                    canonical_payload["rebuild_required"] = current_base_snapshot_id is None and not is_snapshot
                    canonical_payload["is_gap_fill"] = False
                    canonical_payload["is_resync"] = False
                    apply_board_structural_hints(
                        canonical_payload,
                        exchange="bitflyer",
                        symbol=self.cfg.symbol,
                        channel="board_ws",
                        provider=provider_name,
                        transport="websocket",
                        transport_role="stream_snapshot" if is_snapshot else "stream_delta",
                        origin_role="realtime_orderbook_stream",
                        collector_id=self.cfg.collector_id,
                        stream_session_id=stream_session_id,
                        current_event_id=current_event_id,
                        base_snapshot_id=current_base_snapshot_id,
                        continuity_state=continuity_state,
                        is_resync=False,
                        description="unified realtime board snapshot/diff stream",
                    )

                    canonical_ctx = EnvelopeContext(
                        config=self.cfg,
                        schema_version="collector.vnext.canonical",
                        record_type=record_type,
                        channel="board_ws",
                        transport="websocket",
                        sequence_id=self.seq.next(),
                        session_id=f"{self.cfg.collector_id}-unified",
                        stream_session_id=stream_session_id,
                        exchange="bitflyer",
                        source_event_id=current_event_id,
                        source_sequence=msg.source_sequence,
                        continuity_sequence=board_event_no,
                    )

                    canonical_record = make_record(
                        canonical_ctx,
                        canonical_payload,
                    )

                    write_canonical(
                        self.cfg,
                        exchange="bitflyer",
                        symbol=self.cfg.symbol,
                        channel="board_ws",
                        record_type=record_type,
                        record=canonical_record,
                    )
                    self.market_state_lane.step(canonical_record)

                    last_board_event_id = current_event_id

                    self._set_state(
                        lane_state="live",
                        ws_state="LIVE",
                        last_event_ts=msg.received_ts or now_iso_utc(),
                        last_error=None,
                        saw_snapshot=bool(lane_snapshot.get("saw_snapshot")) or is_snapshot,
                        saw_delta=bool(lane_snapshot.get("saw_delta")) or (not is_snapshot),
                    )
                    self._write_origin_status()

            except Exception as exc:
                # Break board continuity chain across provider reconnects.
                last_board_event_id = None
                current_base_snapshot_id = None

                lane_snapshot = self.snapshot()
                next_restart_count = int(lane_snapshot.get("restart_count") or 0) + 1

                self._set_state(
                    lane_state="degraded",
                    ws_state="BROKEN",
                    last_error=str(exc),
                    restart_count=next_restart_count,
                )
                self._write_origin_status()

                audit.emit(
                    "collector_vnext.unified.ws_board.reconnected",
                    level="WARN",
                    feature="collector_vnext",
                    actor="collector_vnext.unified_ws_board_lane",
                    site="collector_vnext.unified_ws_board_lane.run_forever",
                    payload={
                        "collector_id": self.cfg.collector_id,
                        "collector_role": self.cfg.collector_role,
                        "exchange": "bitflyer",
                        "topic": "ws_board",
                        "error": str(exc),
                        "restart_count": next_restart_count,
                        "reconnect_backoff_sec": reconnect_backoff_sec,
                    },
                )

                if stop_event.wait(reconnect_backoff_sec):
                    break