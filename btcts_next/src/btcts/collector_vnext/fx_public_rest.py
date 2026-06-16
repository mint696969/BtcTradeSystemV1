# path: ./btcts_next/src/btcts/collector_vnext/fx_public_rest.py
# desc: SR-FX public REST collection helpers for execution-market bitFlyer FX data.

from __future__ import annotations

import time
from dataclasses import replace
from typing import Any, Dict, Optional

from .config import CollectorConfig, MarketIdentity, load_config, validate_market_identities
from .events import EnvelopeContext, EventType, make_record
from .ids import SequenceManager, make_stream_session_id
from .providers.bitflyer_rest import RestFetchResult, fetch_board, fetch_executions
from .quality import confidence_from_flags, flags_for_missing_exchange_ts, validate_board_payload
from .rate_runtime import VNextRateRuntime
from .transforms.facade import (
    apply_board_structural_hints,
    apply_trade_structural_hints,
    canonical_board_snapshot,
    canonical_trades,
)
from .writer import write_canonical, write_raw


class FxPublicRestError(RuntimeError):
    def __init__(self, message: str, *, status_code: int = 0, retry_after_sec: float = 0.0) -> None:
        super().__init__(message)
        self.status_code = int(status_code or 0)
        self.retry_after_sec = float(retry_after_sec or 0.0)


def execution_market_config(cfg: CollectorConfig) -> CollectorConfig:
    """Return a CollectorConfig view whose legacy envelope fields point at execution_market.

    Existing Collector envelopes/path builders still use cfg.market/cfg.symbol/cfg.instrument_id.
    For SR-FX execution-market collection we intentionally create a narrow config view so raw and
    canonical paths become symbol=FX_BTC_JPY, while reference_market remains available for context.
    """

    validate_market_identities(cfg.reference_market, cfg.execution_market)
    exe = cfg.execution_market.normalized()
    return replace(
        cfg,
        market=exe.market_type,
        symbol=exe.product_code,
        instrument_id=exe.market_uid,
        execution_market=exe,
    )


def market_identity_payload(market: MarketIdentity, *, source: str, request_class: str) -> Dict[str, Any]:
    m = market.normalized()
    return {
        "exchange": m.exchange,
        "product_code": m.product_code,
        "market_type": m.market_type,
        "market_role": m.role,
        "market_uid": m.market_uid,
        "source": source,
        "request_class": request_class,
    }


def _rate_acquire(rate_runtime: VNextRateRuntime | None, exchange: str) -> None:
    if rate_runtime is None:
        return
    ok, wait_ms = rate_runtime.acquire(exchange)
    if not ok and wait_ms > 0:
        time.sleep(wait_ms / 1000.0)


def _note_rate_result(
    rate_runtime: VNextRateRuntime | None,
    *,
    exchange: str,
    request_class: str,
    result: RestFetchResult,
) -> None:
    if rate_runtime is None:
        return
    rate_runtime.note_request_sent(exchange, request_class)
    if result.status_code == 429:
        rate_runtime.on_429(exchange, result.retry_after_sec)
    elif result.ok:
        rate_runtime.on_success(exchange)


def emit_fx_rest_board_snapshot(
    seq: SequenceManager,
    session_id: str,
    *,
    rate_runtime: VNextRateRuntime | None = None,
) -> Dict[str, object]:
    base_cfg = load_config()
    cfg = execution_market_config(base_cfg)
    exe = cfg.execution_market.normalized()
    exchange = exe.exchange
    request_class = "public_rest_market_data"
    stream_session_id = make_stream_session_id(cfg.collector_id, exchange, "fx_board_snapshot")

    _rate_acquire(rate_runtime, exchange)
    res = fetch_board(product_code=exe.product_code, timeout_sec=10.0)
    _note_rate_result(rate_runtime, exchange=exchange, request_class=request_class, result=res)

    if not res.ok:
        raise FxPublicRestError(
            f"bitflyer FX fetch_board failed: {res.error}",
            status_code=res.status_code,
            retry_after_sec=res.retry_after_sec,
        )
    if not isinstance(res.payload, dict):
        raise FxPublicRestError("bitflyer FX fetch_board returned non-dict payload")

    source_payload = res.payload
    quality_flags = []
    quality_flags.extend(validate_board_payload(source_payload))
    quality_flags.extend(flags_for_missing_exchange_ts(None))
    confidence = confidence_from_flags(quality_flags)
    market_meta = market_identity_payload(exe, source="public_rest", request_class=request_class)

    raw_payload = {
        "provider": res.provider,
        "exchange": res.exchange,
        "transport": res.transport,
        "endpoint": res.endpoint,
        "status_code": res.status_code,
        "received_ts": res.received_ts,
        "request": res.request_meta,
        "response": res.response_meta,
        "market_identity": market_meta,
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
        exchange=exchange,
        quality_flags=quality_flags,
        confidence_score=confidence,
    )
    raw_record = make_record(raw_ctx, raw_payload)
    raw_path = write_raw(
        cfg,
        exchange=exchange,
        symbol=exe.product_code,
        channel="board_snapshot",
        record_type=EventType.MARKET_ORDERBOOK_SNAPSHOT,
        record=raw_record,
    )

    snapshot_id = f"snap-fx-rest-{seq.next():012d}"
    board_payload = canonical_board_snapshot(source_payload, depth=50, snapshot_id=snapshot_id)
    board_payload["market_identity"] = market_meta
    board_payload["product_code"] = exe.product_code
    board_payload["market_type"] = exe.market_type
    board_payload["market_role"] = exe.role
    board_payload["market_uid"] = exe.market_uid

    apply_board_structural_hints(
        board_payload,
        exchange=exchange,
        symbol=exe.product_code,
        channel="board_snapshot",
        provider="bitflyer_rest",
        transport="rest",
        transport_role="baseline_snapshot",
        origin_role="execution_market_baseline_snapshot",
        collector_id=cfg.collector_id,
        stream_session_id=stream_session_id,
        current_event_id=None,
        base_snapshot_id=board_payload.get("base_snapshot_id"),
        continuity_state=str(board_payload.get("continuity_state") or "unknown"),
        is_resync=False,
        description="FX execution-market REST snapshot used as trading input baseline",
    )

    canonical_ctx = EnvelopeContext(
        config=cfg,
        schema_version="collector.vnext.canonical",
        record_type=EventType.MARKET_ORDERBOOK_SNAPSHOT,
        channel="board_snapshot",
        transport="rest",
        sequence_id=seq.next(),
        session_id=session_id,
        stream_session_id=stream_session_id,
        exchange=exchange,
        quality_flags=quality_flags,
        confidence_score=confidence,
    )
    canonical_record = make_record(canonical_ctx, board_payload)
    canonical_path = write_canonical(
        cfg,
        exchange=exchange,
        symbol=exe.product_code,
        channel="board_snapshot",
        record_type=EventType.MARKET_ORDERBOOK_SNAPSHOT,
        record=canonical_record,
    )

    return {
        "ok": True,
        "exchange": exchange,
        "product_code": exe.product_code,
        "market_uid": exe.market_uid,
        "market_role": exe.role,
        "request_class": request_class,
        "raw_path": str(raw_path),
        "canonical_path": str(canonical_path),
        "stream_session_id": stream_session_id,
        "status_code": res.status_code,
    }


def emit_fx_rest_trades(
    seq: SequenceManager,
    session_id: str,
    *,
    rate_runtime: VNextRateRuntime | None = None,
) -> Dict[str, object]:
    base_cfg = load_config()
    cfg = execution_market_config(base_cfg)
    exe = cfg.execution_market.normalized()
    exchange = exe.exchange
    request_class = "public_rest_market_data"
    stream_session_id = make_stream_session_id(cfg.collector_id, exchange, "fx_executions")

    _rate_acquire(rate_runtime, exchange)
    res = fetch_executions(product_code=exe.product_code, count=50, timeout_sec=10.0)
    _note_rate_result(rate_runtime, exchange=exchange, request_class=request_class, result=res)

    if not res.ok:
        raise FxPublicRestError(
            f"bitflyer FX executions failed: {res.error}",
            status_code=res.status_code,
            retry_after_sec=res.retry_after_sec,
        )
    if not isinstance(res.payload, dict):
        raise FxPublicRestError("bitflyer FX executions returned non-dict payload")

    source_payload = res.payload
    market_meta = market_identity_payload(exe, source="public_rest", request_class=request_class)

    raw_payload = {
        "provider": res.provider,
        "exchange": res.exchange,
        "transport": res.transport,
        "endpoint": res.endpoint,
        "status_code": res.status_code,
        "received_ts": res.received_ts,
        "request": res.request_meta,
        "response": res.response_meta,
        "market_identity": market_meta,
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
        exchange=exchange,
    )
    raw_record = make_record(raw_ctx, raw_payload)
    raw_path = write_raw(
        cfg,
        exchange=exchange,
        symbol=exe.product_code,
        channel="executions",
        record_type=EventType.MARKET_TRADE,
        record=raw_record,
    )

    canonical_path: Optional[str] = None
    trade_count = 0

    for trade in canonical_trades(source_payload):
        trade["market_identity"] = market_meta
        trade["product_code"] = exe.product_code
        trade["market_type"] = exe.market_type
        trade["market_role"] = exe.role
        trade["market_uid"] = exe.market_uid
        apply_trade_structural_hints(
            trade,
            exchange=exchange,
            symbol=exe.product_code,
            channel="executions",
            provider="bitflyer_rest",
            transport="rest",
            transport_role="backfill_or_reconcile",
            origin_role="execution_market_historical_or_reconcile",
            collector_id=cfg.collector_id,
            stream_session_id=stream_session_id,
            seen_in_rest=True,
            seen_in_ws=False,
            description="FX execution-market REST executions used for trading input backfill/reconciliation",
        )

        canonical_ctx = EnvelopeContext(
            config=cfg,
            schema_version="collector.vnext.canonical",
            record_type=EventType.MARKET_TRADE,
            channel="executions",
            transport="rest",
            sequence_id=seq.next(),
            session_id=session_id,
            stream_session_id=stream_session_id,
            exchange=exchange,
            exchange_ts=trade.get("trade_ts"),
            source_event_id=str(trade["trade_id"]) if trade.get("trade_id") is not None else None,
        )
        record = make_record(canonical_ctx, trade)
        out = write_canonical(
            cfg,
            exchange=exchange,
            symbol=exe.product_code,
            channel="executions",
            record_type=EventType.MARKET_TRADE,
            record=record,
        )
        canonical_path = str(out)
        trade_count += 1

    return {
        "ok": True,
        "exchange": exchange,
        "product_code": exe.product_code,
        "market_uid": exe.market_uid,
        "market_role": exe.role,
        "request_class": request_class,
        "raw_path": str(raw_path),
        "canonical_path": canonical_path,
        "trade_count": trade_count,
        "stream_session_id": stream_session_id,
        "status_code": res.status_code,
    }
