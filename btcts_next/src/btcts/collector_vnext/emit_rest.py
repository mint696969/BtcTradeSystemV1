# path: ./btcts_next/src/btcts/collector_vnext/emit_rest.py
# desc: REST smoke emitters for board snapshot and executions in Collector vNext.

from __future__ import annotations

import time
from typing import Dict, Optional

from .config import load_config
from .events import EnvelopeContext, EventType, make_record
from .ids import SequenceManager, make_stream_session_id
from .providers.bitflyer_rest import fetch_board, fetch_executions
from .quality import confidence_from_flags, flags_for_missing_exchange_ts, validate_board_payload
from .rate_runtime import VNextRateRuntime
from .transforms.board_structural_hints import apply_board_structural_hints
from .transforms.raw_to_canonical import canonical_board_snapshot
from .transforms.raw_to_canonical_trades import canonical_trades
from .transforms.trade_structural_hints import apply_trade_structural_hints
from .writer import write_canonical, write_raw


class RestRequestFailedError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = 0,
        retry_after_sec: float = 0.0,
    ) -> None:
        super().__init__(message)
        self.status_code = int(status_code or 0)
        self.retry_after_sec = float(retry_after_sec or 0.0)


def _rate_acquire(rate_runtime: VNextRateRuntime | None, exchange: str) -> None:
    if rate_runtime is None:
        return

    ok, wait_ms = rate_runtime.acquire(exchange)
    if not ok and wait_ms > 0:
        time.sleep(wait_ms / 1000.0)


def emit_rest_board_snapshot(
    seq: SequenceManager,
    session_id: str,
    rate_runtime: VNextRateRuntime | None = None,
) -> Dict[str, object]:
    cfg = load_config()
    stream_session_id = make_stream_session_id(cfg.collector_id, "bitflyer", "board_snapshot")

    _rate_acquire(rate_runtime, "bitflyer")
    res = fetch_board(product_code=cfg.symbol, timeout_sec=10.0)

    if rate_runtime is not None:
        rate_runtime.note_request_sent("bitflyer", "board_snapshot")

    if not res.ok:
        if rate_runtime is not None and res.status_code == 429:
            rate_runtime.on_429("bitflyer", res.retry_after_sec)
        raise RestRequestFailedError(
            f"bitflyer fetch_board failed: {res.error}",
            status_code=res.status_code,
            retry_after_sec=res.retry_after_sec,
        )

    if rate_runtime is not None:
        rate_runtime.on_success("bitflyer")

    if not isinstance(res.payload, dict):
        raise RuntimeError("bitflyer fetch_board returned non-dict payload")

    source_payload = res.payload
    quality_flags = []
    quality_flags.extend(validate_board_payload(source_payload))
    quality_flags.extend(flags_for_missing_exchange_ts(None))
    confidence = confidence_from_flags(quality_flags)

    raw_payload = {
        "provider": res.provider,
        "exchange": res.exchange,
        "transport": res.transport,
        "endpoint": res.endpoint,
        "status_code": res.status_code,
        "received_ts": res.received_ts,
        "request": res.request_meta,
        "response": res.response_meta,
        "source_payload": source_payload,
    }

    raw_ctx = EnvelopeContext(
        config=cfg,
        schema_version="collector.vnext.raw",
        record_type=EventType.MARKET_ORDERBOOK_SNAPSHOT,
        channel="board_snapshot",
        transport="rest",
        sequence_id=seq.next(),
        session_id=session_id,
        stream_session_id=stream_session_id,
        exchange="bitflyer",
        exchange_ts=None,
        source_event_id=None,
        source_sequence=None,
        quality_flags=quality_flags,
        is_partial=False,
        is_reconstructed=False,
        confidence_score=confidence,
    )
    raw_record = make_record(raw_ctx, raw_payload)
    raw_path = write_raw(
        cfg,
        exchange="bitflyer",
        symbol=cfg.symbol,
        channel="board_snapshot",
        record_type=EventType.MARKET_ORDERBOOK_SNAPSHOT,
        record=raw_record,
    )

    snapshot_id = f"snap-rest-{seq.next():012d}"
    canonical_ctx = EnvelopeContext(
        config=cfg,
        schema_version="collector.vnext.canonical",
        record_type=EventType.MARKET_ORDERBOOK_SNAPSHOT,
        channel="board_snapshot",
        transport="rest",
        sequence_id=seq.next(),
        session_id=session_id,
        stream_session_id=stream_session_id,
        exchange="bitflyer",
        exchange_ts=None,
        source_event_id=None,
        source_sequence=None,
        quality_flags=quality_flags,
        is_partial=False,
        is_reconstructed=False,
        confidence_score=confidence,
    )
    board_payload = canonical_board_snapshot(
        source_payload,
        depth=50,
        snapshot_id=snapshot_id,
    )
    apply_board_structural_hints(
        board_payload,
        exchange="bitflyer",
        symbol=cfg.symbol,
        channel="board_snapshot",
        provider="bitflyer_rest",
        transport="rest",
        transport_role="baseline_snapshot",
        origin_role="baseline_snapshot",
        collector_id=cfg.collector_id,
        stream_session_id=stream_session_id,
        current_event_id=None,
        base_snapshot_id=board_payload.get("base_snapshot_id"),
        continuity_state=str(board_payload.get("continuity_state") or "unknown"),
        is_resync=False,
        description="REST snapshot used as baseline reference for board reconstruction",
    )

    canonical_record = make_record(
        canonical_ctx,
        board_payload,
    )
    canonical_path = write_canonical(
        cfg,
        exchange="bitflyer",
        symbol=cfg.symbol,
        channel="board_snapshot",
        record_type=EventType.MARKET_ORDERBOOK_SNAPSHOT,
        record=canonical_record,
    )

    return {
        "raw_path": str(raw_path),
        "canonical_path": str(canonical_path),
        "stream_session_id": stream_session_id,
    }


def emit_rest_trades(
    seq: SequenceManager,
    session_id: str,
    rate_runtime: VNextRateRuntime | None = None,
) -> Dict[str, object]:
    cfg = load_config()

    stream_session_id = make_stream_session_id(
        cfg.collector_id,
        "bitflyer",
        "executions",
    )

    _rate_acquire(rate_runtime, "bitflyer")
    res = fetch_executions(
        product_code=cfg.symbol,
        count=50,
    )

    if rate_runtime is not None:
        rate_runtime.note_request_sent("bitflyer", "rest_trades")

    if not res.ok:
        if rate_runtime is not None and res.status_code == 429:
            rate_runtime.on_429("bitflyer", res.retry_after_sec)
        raise RestRequestFailedError(
            f"bitflyer executions failed: {res.error}",
            status_code=res.status_code,
            retry_after_sec=res.retry_after_sec,
        )

    if rate_runtime is not None:
        rate_runtime.on_success("bitflyer")

    if not isinstance(res.payload, dict):
        raise RuntimeError("bitflyer executions returned non-dict payload")

    source_payload = res.payload

    raw_payload = {
        "provider": res.provider,
        "exchange": res.exchange,
        "transport": res.transport,
        "endpoint": res.endpoint,
        "status_code": res.status_code,
        "received_ts": res.received_ts,
        "request": res.request_meta,
        "response": res.response_meta,
        "source_payload": source_payload,
    }

    raw_ctx = EnvelopeContext(
        config=cfg,
        schema_version="collector.vnext.raw",
        record_type=EventType.MARKET_TRADE,
        channel="executions",
        transport="rest",
        sequence_id=seq.next(),
        session_id=session_id,
        stream_session_id=stream_session_id,
        exchange="bitflyer",
    )

    raw_record = make_record(raw_ctx, raw_payload)

    raw_path = write_raw(
        cfg,
        exchange="bitflyer",
        symbol=cfg.symbol,
        channel="executions",
        record_type=EventType.MARKET_TRADE,
        record=raw_record,
    )

    trade_count = 0
    canonical_path: Optional[str] = None

    trades = canonical_trades(source_payload)

    for trade in trades:
        canonical_ctx = EnvelopeContext(
            config=cfg,
            schema_version="collector.vnext.canonical",
            record_type=EventType.MARKET_TRADE,
            channel="executions",
            transport="rest",
            sequence_id=seq.next(),
            session_id=session_id,
            stream_session_id=stream_session_id,
            exchange="bitflyer",
            exchange_ts=trade.get("trade_ts"),
            source_event_id=str(trade["trade_id"]) if trade.get("trade_id") is not None else None,
            source_sequence=None,
        )

        apply_trade_structural_hints(
            trade,
            exchange="bitflyer",
            symbol=cfg.symbol,
            channel="executions",
            provider="bitflyer_rest",
            transport="rest",
            transport_role="backfill_or_reconcile",
            origin_role="historical_or_reconcile",
            collector_id=cfg.collector_id,
            stream_session_id=stream_session_id,
            seen_in_rest=True,
            seen_in_ws=False,
            description="REST executions used for backfill or reconciliation",
        )

        record = make_record(canonical_ctx, trade)

        out = write_canonical(
            cfg,
            exchange="bitflyer",
            symbol=cfg.symbol,
            channel="executions",
            record_type=EventType.MARKET_TRADE,
            record=record,
        )
        canonical_path = str(out)
        trade_count += 1

    return {
        "raw_path": str(raw_path),
        "canonical_path": canonical_path,
        "trade_count": trade_count,
        "stream_session_id": stream_session_id,
    }