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
from .transforms.raw_to_canonical import canonical_board_snapshot
from .transforms.raw_to_canonical_trades import canonical_trades
from .writer import write_canonical, write_raw


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
        rate_runtime.note_request_sent("bitflyer")

    if not res.ok:
        if rate_runtime is not None and res.status_code == 429:
            rate_runtime.on_429("bitflyer", res.retry_after_sec)
        raise RuntimeError(f"bitflyer fetch_board failed: {res.error}")

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
    board_payload["integration_hint"] = {
        "integration_domain": "board_continuity_series",
        "transport_role": "baseline_snapshot",
        "series_key_hint": f"rest:{stream_session_id}:{snapshot_id}",
        "unified_view_policy": "series_based_not_event_dedupe",
    }
    board_payload["dedupe_hint"] = {
        "entity_kind": "board",
        "event_dedupe_key": {
            "exchange": "bitflyer",
            "instrument_id": f"bitflyer.spot.{cfg.symbol}",
            "channel": "board_snapshot",
            "source_event_id": None,
        },
        "series_key": {
            "exchange": "bitflyer",
            "instrument_id": f"bitflyer.spot.{cfg.symbol}",
            "channel": "board_snapshot",
            "base_snapshot_id": board_payload.get("base_snapshot_id"),
            "stream_session_id": stream_session_id,
        },
        "continuity_policy": {
            "mode": "conservative",
            "mix_unknown": False,
            "split_on_gap": True,
            "split_on_resync": True,
        },
    }

    board_payload["completeness_hint"] = {
        "evaluation_unit": "board_series",
        "completeness": "partial",
        "confidence_hint": "medium_or_low",
        "completeness_basis": {
            "base_snapshot_id_present": bool(board_payload.get("base_snapshot_id")),
            "stream_session_id_present": bool(stream_session_id),
            "continuity_state": str(board_payload.get("continuity_state") or "unknown"),
            "gap_or_resync_observed": False,
            "transport_role": "baseline_snapshot",
        },
        "policy_note": "rest snapshot is useful as baseline but not a continuous board series by itself",
    }

    board_payload["origin_hint"] = {
        "source_layer": "collector",
        "provider": "bitflyer_rest",
        "transport": "rest",
        "endpoint_or_channel": "board_snapshot",
        "origin_role": "baseline_snapshot",
        "collector_id": cfg.collector_id,
        "stream_session_id": stream_session_id,
        "description": "REST snapshot used as baseline reference for board reconstruction",
    }

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
        rate_runtime.note_request_sent("bitflyer")

    if not res.ok:
        if rate_runtime is not None and res.status_code == 429:
            rate_runtime.on_429("bitflyer", res.retry_after_sec)
        raise RuntimeError(f"bitflyer executions failed: {res.error}")

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

        trade["integration_hint"] = {
            "integration_domain": "trade_native_id",
            "transport_role": "backfill_or_reconcile",
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
                "seen_in_rest": True,
                "seen_in_ws": False,
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
                "seen_in_rest": True,
                "seen_in_ws": False,
            },
            "policy_note": "native trade id exists and core fields are present, but provenance is single-sided",
        }

        trade["origin_hint"] = {
            "source_layer": "collector",
            "provider": "bitflyer_rest",
            "transport": "rest",
            "endpoint_or_channel": "executions",
            "origin_role": "historical_or_reconcile",
            "collector_id": cfg.collector_id,
            "stream_session_id": stream_session_id,
            "description": "REST executions used for backfill or reconciliation",
        }

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