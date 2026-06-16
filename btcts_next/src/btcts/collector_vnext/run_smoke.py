# path: ./btcts_next/src/btcts/collector_vnext/run_smoke.py
# desc: Smoke orchestration for Collector vNext bootstrap, REST, and WS checks.

from __future__ import annotations

from typing import Dict, Optional

from .config import CollectorConfig
from .emit_rest import emit_rest_board_snapshot, emit_rest_trades
from .emit_ws import emit_ws_board_smoke, emit_ws_trade_smoke
from .events import EnvelopeContext, EventType, make_record, make_stream_started_payload, now_iso_utc
from .ids import SequenceManager, make_session_id, make_stream_session_id
from .rate_runtime import VNextRateRuntime
from .writer import write_canonical, write_raw


def build_status(
    mode: str,
    message: str,
    session_id: str,
    stream_session_id: str,
    *,
    consecutive_failures: int = 0,
    last_error: str | None = None,
    last_success_ts: str | None = None,
    ws_trades_warn_streak: int = 0,
    rate_control: Dict[str, object] | None = None,
    origin_continuity: Dict[str, object] | None = None,
) -> Dict[str, object]:
    return {
        "ts": now_iso_utc(),
        "mode": mode,
        "message": message,
        "collector_vnext": True,
        "session_id": session_id,
        "stream_session_id": stream_session_id,
        "consecutive_failures": consecutive_failures,
        "last_error": last_error,
        "last_success_ts": last_success_ts,
        "ws_trades_warn_streak": ws_trades_warn_streak,
        "rate_control": rate_control or {
            "summary_state": "NORMAL",
            "engaged": False,
            "reason": "",
            "wait_ms": 0,
        },
        "origin_continuity": origin_continuity or {},
    }


def emit_stream_started(cfg: CollectorConfig, seq: SequenceManager, session_id: str, stream_session_id: str) -> None:
    raw_ctx = EnvelopeContext(
        config=cfg,
        schema_version="collector.vnext.raw",
        record_type=EventType.STREAM_STARTED,
        channel="bootstrap",
        transport="internal",
        sequence_id=seq.next(),
        session_id=session_id,
        stream_session_id=stream_session_id,
        exchange="system",
    )

    raw_record = make_record(
        raw_ctx,
        make_stream_started_payload(
            reason="collector_bootstrap",
            provider="collector_vnext",
            endpoint_or_channel="bootstrap",
        ),
    )

    write_raw(
        cfg,
        exchange="system",
        symbol=cfg.symbol,
        channel="bootstrap",
        record_type=EventType.STREAM_STARTED,
        record=raw_record,
    )

    canonical_ctx = EnvelopeContext(
        config=cfg,
        schema_version="collector.vnext.canonical",
        record_type=EventType.STREAM_STARTED,
        channel="bootstrap",
        transport="internal",
        sequence_id=seq.next(),
        session_id=session_id,
        stream_session_id=stream_session_id,
        exchange="system",
    )

    canonical_record = make_record(
        canonical_ctx,
        make_stream_started_payload(
            reason="collector_bootstrap",
            provider="collector_vnext",
            endpoint_or_channel="bootstrap",
        ),
    )

    write_canonical(
        cfg,
        exchange="system",
        symbol=cfg.symbol,
        channel="bootstrap",
        record_type=EventType.STREAM_STARTED,
        record=canonical_record,
    )


def run_smoke(
    cfg: CollectorConfig,
    rate_runtime: VNextRateRuntime | None = None,
) -> Dict[str, object]:
    seq = SequenceManager.start(1)
    session_id = make_session_id(cfg.collector_id)
    bootstrap_stream_session_id = make_stream_session_id(cfg.collector_id, "system", "bootstrap")

    emit_stream_started(cfg, seq, session_id, bootstrap_stream_session_id)

    board_info = emit_rest_board_snapshot(seq, session_id, rate_runtime=rate_runtime)
    rest_trades_info = emit_rest_trades(seq, session_id, rate_runtime=rate_runtime)

    ws_trades_ok = False
    ws_trades_error: Optional[str] = None
    ws_trade_info: Dict[str, object]

    try:
        ws_trade_info = emit_ws_trade_smoke(seq, session_id)
        ws_trades_ok = True
    except Exception as exc:
        ws_trade_info = {
            "raw_path": None,
            "canonical_path": None,
            "trade_count": 0,
            "stream_session_id": None,
            "ssl_verify": cfg.ws_ssl_verify,
        }
        ws_trades_error = str(exc)

    ws_board_ok = False
    ws_board_error: Optional[str] = None
    ws_board_info: Dict[str, object]

    try:
        ws_board_info = emit_ws_board_smoke(seq, session_id)
        ws_board_ok = True
    except Exception as exc:
        ws_board_info = {
            "raw_path": None,
            "canonical_path": None,
            "event_type": None,
            "stream_session_id": None,
            "ssl_verify": cfg.ws_ssl_verify,
        }
        ws_board_error = str(exc)

    return {
        "session_id": session_id,
        "bootstrap_stream_session_id": bootstrap_stream_session_id,
        "last_sequence_id": seq.current(),
        "board": board_info,
        "rest_trades": rest_trades_info,
        "ws_trades": {
            "ok": ws_trades_ok,
            "info": ws_trade_info,
            "error": ws_trades_error,
        },
        "ws_board": {
            "ok": ws_board_ok,
            "info": ws_board_info,
            "error": ws_board_error,
        },
    }