# path: ./btcts_next/src/btcts/autotrade/read_model/fx_market_state_rest_snapshot.py
# desc: Build/persist SR-FX market_state overview rows from public REST board snapshots. No broker calls.

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict

from btcts.collector_vnext.config import load_config
from btcts.collector_vnext.fx_public_rest import _note_rate_result, _rate_acquire, execution_market_config
from btcts.collector_vnext.providers.bitflyer_rest import RestFetchResult, fetch_board, fetch_executions
from btcts.collector_vnext.rate_runtime import VNextRateRuntime
from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.market_state.schema import MarketStateRecord
from btcts.market_engine.market_state.writer import MarketStateWriter
from btcts.market_engine.types import BoundaryReason, TrustState

REQUEST_CLASS = "public_rest_market_data"
STATE_TYPE = "market.overview"


@dataclass(frozen=True)
class FxMarketStateRestSnapshotResult:
    ok: bool
    exchange: str
    product_code: str
    market_uid: str
    request_class: str
    state_type: str
    market_state_path: Path | None
    status_code: int
    blocked_by: tuple[str, ...]
    warnings: tuple[str, ...]
    row: dict[str, Any] | None
    read_only: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["market_state_path"] = str(self.market_state_path) if self.market_state_path is not None else None
        data["blocked_by"] = list(self.blocked_by)
        data["warnings"] = list(self.warnings)
        return data


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _date_str_from_ts(ts: str) -> str:
    return str(ts or _utc_now())[:10]


def _levels(rows: Any) -> list[dict[str, float]]:
    if not isinstance(rows, list):
        return []
    out: list[dict[str, float]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        try:
            price = float(row.get("price"))
            size = float(row.get("size"))
        except Exception:
            continue
        if price <= 0 or size < 0:
            continue
        out.append({"price": price, "size": size})
    return out


def _size_total(levels: list[dict[str, float]]) -> float:
    return sum(float(item.get("size") or 0.0) for item in levels)


def _notional_total(levels: list[dict[str, float]]) -> float:
    return sum(float(item.get("price") or 0.0) * float(item.get("size") or 0.0) for item in levels)


def _trade_delta_from_executions_payload(payload: Dict[str, Any] | None) -> float | None:
    if not isinstance(payload, dict):
        return None
    items = payload.get("items")
    if not isinstance(items, list):
        return None
    total = 0.0
    seen = False
    for item in items:
        if not isinstance(item, dict):
            continue
        side = str(item.get("side") or "").strip().upper()
        try:
            size = float(item.get("size"))
        except Exception:
            continue
        if size < 0:
            continue
        if side == "BUY":
            total += size
            seen = True
        elif side == "SELL":
            total -= size
            seen = True
    return total if seen else None


def build_fx_market_state_record_from_rest_board(
    *,
    payload: Dict[str, Any],
    exchange: str,
    product_code: str,
    market_uid: str,
    received_ts: str | None,
    stream_session_id: str,
    near_zone_levels: int = 50,
    trade_delta: float | None = None,
) -> MarketStateRecord:
    collector_ts = received_ts or _utc_now()
    bids = sorted(_levels(payload.get("bids")), key=lambda item: item["price"], reverse=True)
    asks = sorted(_levels(payload.get("asks")), key=lambda item: item["price"])
    near_bids = bids[:near_zone_levels]
    near_asks = asks[:near_zone_levels]
    best_bid = near_bids[0]["price"] if near_bids else None
    best_ask = near_asks[0]["price"] if near_asks else None
    mid_price = None
    try:
        mid_price = float(payload.get("mid_price")) if payload.get("mid_price") is not None else None
    except Exception:
        mid_price = None
    if mid_price is None and best_bid is not None and best_ask is not None:
        mid_price = (best_bid + best_ask) / 2.0
    spread = (best_ask - best_bid) if best_bid is not None and best_ask is not None else None
    valid_book = best_bid is not None and best_ask is not None and spread is not None and spread >= 0
    bid_size = _size_total(near_bids)
    ask_size = _size_total(near_asks)
    total_size = bid_size + ask_size
    imbalance = 0.0 if total_size == 0 else (bid_size - ask_size) / total_size

    return MarketStateRecord(
        market_uid=market_uid,
        exchange=exchange,
        symbol_raw=product_code,
        collector_ts=collector_ts,
        exchange_ts=collector_ts,
        trust_state=TrustState.TRUSTED if valid_book else TrustState.PROVISIONAL,
        boundary_reason=BoundaryReason.NONE,
        continuity_state="rest_baseline_snapshot",
        interpretation_bucket="allow_structural_use" if valid_book else "observe_only",
        interpretation_reason="fx_public_rest_board_snapshot_baseline" if valid_book else "fx_public_rest_board_snapshot_incomplete",
        interpretation_policy={
            "mode": "public_rest_board_baseline",
            "review_required": not valid_book,
            "not_continuous_ws_series": True,
            "execution_market_input": True,
        },
        semantic_observer_status="caution",
        semantic_usage_summary={
            "source_kind": "fx_public_rest_board_snapshot",
            "contract_source": "sr_fx_market_state_rest_snapshot",
            "meaning_version": "sr_fx_market_state_rest_snapshot.v1",
            "observer_status": "caution",
            "total_rows": 0,
            "active_event_count": 0,
            "mapped_event_count": 0,
            "unknown_event_count": 0,
            "event_family_distribution": {},
            "trust_bucket_distribution": {},
            "interpretation_bucket_distribution": {},
            "consumer_distribution": {},
        },
        semantic_usage_contract_rows=[],
        orderbook_semantics_contract_status="missing",
        orderbook_semantics_summary={
            "near_wall": None,
            "support": None,
            "resistance": None,
            "persistence": None,
            "summary_slots_present": [],
            "summary_slots_count": 0,
            "active_event_count": 0,
            "active_event_names": [],
            "active_event_contracts": [],
        },
        orderbook_persistence_observable=False,
        best_bid=best_bid,
        best_ask=best_ask,
        spread=spread,
        mid_price=mid_price,
        price=mid_price,
        imbalance=imbalance,
        trade_delta=trade_delta,
        near_zone_bids=near_bids,
        near_zone_asks=near_asks,
        top_book_summary={
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "mid_price": mid_price,
            "bid_levels_visible": len(near_bids),
            "ask_levels_visible": len(near_asks),
        },
        near_zone_liquidity_summary={
            "bid_size_total": bid_size,
            "ask_size_total": ask_size,
            "bid_notional_total": _notional_total(near_bids),
            "ask_notional_total": _notional_total(near_asks),
        },
        imbalance_summary={
            "near_size_imbalance": imbalance,
            "bid_size_total": bid_size,
            "ask_size_total": ask_size,
        },
        zone_density_metadata={
            "mode": "rest_board_baseline",
            "near_zone_levels": near_zone_levels,
            "source": "bitflyer_public_rest_board",
        },
        source_series_id=f"{stream_session_id}:rest_board_baseline",
        source_stream_session_id=stream_session_id,
    )


def write_fx_market_state_from_public_rest_board(
    *,
    fetch_board_func: Callable[..., RestFetchResult] = fetch_board,
    fetch_executions_func: Callable[..., RestFetchResult] = fetch_executions,
    rate_runtime: VNextRateRuntime | None = None,
) -> FxMarketStateRestSnapshotResult:
    base_cfg = load_config()
    cfg = execution_market_config(base_cfg)
    exe = cfg.execution_market.normalized()
    exchange = exe.exchange

    _rate_acquire(rate_runtime, exchange)
    res = fetch_board_func(product_code=exe.product_code, timeout_sec=10.0)
    _note_rate_result(rate_runtime, exchange=exchange, request_class=REQUEST_CLASS, result=res)

    _rate_acquire(rate_runtime, exchange)
    executions_res = fetch_executions_func(product_code=exe.product_code, count=50, timeout_sec=10.0)
    _note_rate_result(rate_runtime, exchange=exchange, request_class=REQUEST_CLASS, result=executions_res)
    trade_delta = _trade_delta_from_executions_payload(executions_res.payload) if executions_res.ok else None

    if not res.ok or not isinstance(res.payload, dict):
        return FxMarketStateRestSnapshotResult(
            ok=False,
            exchange=exchange,
            product_code=exe.product_code,
            market_uid=exe.market_uid,
            request_class=REQUEST_CLASS,
            state_type=STATE_TYPE,
            market_state_path=None,
            status_code=res.status_code,
            blocked_by=("fx_public_rest_board_not_ok",),
            warnings=(str(res.error),) if res.error else (),
            row=None,
            read_only=False,
            would_send_to_broker=False,
        )

    stream_session_id = f"{base_cfg.collector_id}:fx_public_rest_board:{_utc_now().replace(':', '').replace('-', '')}"
    record = build_fx_market_state_record_from_rest_board(
        payload=res.payload,
        exchange=exchange,
        product_code=exe.product_code,
        market_uid=exe.market_uid,
        received_ts=res.received_ts,
        stream_session_id=stream_session_id,
        near_zone_levels=50,
        trade_delta=trade_delta,
    )
    market_cfg = MarketEngineConfig(
        exchange=exchange,
        symbol_raw=exe.product_code,
        instrument_id=exe.market_uid,
        market_uid=exe.market_uid,
        profile_name="bitflyer",
        near_zone_levels=50,
        far_zone_levels=200,
        replay_batch_size=1000,
        write_market_state=True,
    )
    out = MarketStateWriter().write(
        cfg=market_cfg,
        state_type=STATE_TYPE,
        record=record,
        date_str=_date_str_from_ts(record.collector_ts or _utc_now()),
        part_no=1,
    )
    return FxMarketStateRestSnapshotResult(
        ok=True,
        exchange=exchange,
        product_code=exe.product_code,
        market_uid=exe.market_uid,
        request_class=REQUEST_CLASS,
        state_type=STATE_TYPE,
        market_state_path=out,
        status_code=res.status_code,
        blocked_by=(),
        warnings=tuple(
            item
            for item in (
                "rest_board_baseline_not_continuous_ws_series",
                None if trade_delta is not None else "fx_public_rest_executions_trade_delta_missing",
            )
            if item is not None
        ),
        row=record.to_dict(),
        read_only=False,
        would_send_to_broker=False,
    )
