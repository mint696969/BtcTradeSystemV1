# path: ./btcts_next/src/btcts/autotrade/read_model/fx_market_state_ws_live.py
# desc: Build/persist SR-FX L3 market_state rows from existing FX live canonical WS board/tradeflow. No broker calls.

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from btcts.collector_vnext.config import load_config
from btcts.collector_vnext.fx_public_rest import execution_market_config
from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.market_state.schema import MarketStateRecord
from btcts.market_engine.market_state.writer import MarketStateWriter
from btcts.market_engine.types import BoundaryReason, TrustState

STATE_TYPE = "market.overview"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _date_str_from_ts(ts: str | None) -> str:
    return str(ts or _utc_now())[:10]


def _parse_iso_utc(value: Any) -> datetime | None:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _age_sec(value: Any, *, now: datetime | None = None) -> float | None:
    dt = _parse_iso_utc(value)
    if dt is None:
        return None
    now_dt = now or datetime.now(timezone.utc)
    if now_dt.tzinfo is None:
        now_dt = now_dt.replace(tzinfo=timezone.utc)
    return max((now_dt.astimezone(timezone.utc) - dt).total_seconds(), 0.0)


def _freshness_blockers(
    *,
    board: dict[str, Any],
    flow: dict[str, Any],
    max_age_sec: float,
    now: datetime | None = None,
) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []
    board_age = _age_sec(board.get("event_ts"), now=now)
    flow_age = _age_sec(flow.get("event_ts"), now=now)
    if board_age is None:
        blockers.append("fx_ws_live_board_event_ts_missing_or_invalid")
    elif board_age > max_age_sec:
        blockers.append("fx_ws_live_board_stale")
        warnings.append(f"fx_ws_live_board_age_sec={board_age:.1f}")
    if flow_age is None:
        blockers.append("fx_ws_live_tradeflow_event_ts_missing_or_invalid")
    elif flow_age > max_age_sec:
        blockers.append("fx_ws_live_tradeflow_stale")
        warnings.append(f"fx_ws_live_tradeflow_age_sec={flow_age:.1f}")
    return blockers, warnings


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _imbalance(bid_depth: float | None, ask_depth: float | None) -> float | None:
    if bid_depth is None or ask_depth is None:
        return None
    denom = bid_depth + ask_depth
    if denom <= 0:
        return 0.0
    return (bid_depth - ask_depth) / denom


def _wall_side(ratio: float | None) -> str | None:
    if ratio is None:
        return None
    if ratio > 0.05:
        return "bid"
    if ratio < -0.05:
        return "ask"
    return "balanced"


def _levels_from_best(*, price: float | None, size: float | None) -> list[dict[str, float]]:
    if price is None or size is None:
        return []
    return [{"price": float(price), "size": float(size)}]


def _event_ts(board: dict[str, Any], flow: dict[str, Any]) -> str:
    return str(flow.get("event_ts") or board.get("event_ts") or _utc_now())


def _orderbook_semantics_summary(*, wall_ratio: float | None, wall_side: str | None) -> dict[str, Any]:
    near_wall = None
    active_event_names: list[str] = []
    active_event_contracts: list[dict[str, Any]] = []

    if wall_ratio is not None and wall_side in {"bid", "ask"}:
        event_name = f"near_wall_{wall_side}"
        near_wall = {
            "side": wall_side,
            "wall_ratio": wall_ratio,
            "source": "sr_fx_ws_live_canonical_bridge",
        }
        active_event_names.append(event_name)
        active_event_contracts.append(
            {
                "contract_source": "sr_fx_ws_live_market_state_bridge",
                "event_name": event_name,
                "event_family": "orderbook_near_wall",
                "usage_grade": "structural_context",
                "interpretation_bucket": "allow_structural_use",
                "meaning_version": "sr_fx_ws_live_market_state_bridge.v1",
                "confidence": "medium",
                "trust_bucket": "trusted_live_canonical",
                "consumer_allowed": ["workroom", "operator_ui", "autotrade", "l4_consumer"],
                "actionability": "context_only_not_order_signal",
                "forecast_horizon_hint": "short",
                "half_life_sec": 30,
                "invalidates_on": ["stale_market_state", "ws_gap_or_resync"],
                "evidence_refs": ["latest_fx_ws_canonical_board"],
                "side": wall_side,
            }
        )

    slots = ["near_wall"] if near_wall is not None else []
    return {
        "near_wall": near_wall,
        "support": None,
        "resistance": None,
        "persistence": None,
        "summary_slots_present": slots,
        "summary_slots_count": len(slots),
        "active_event_count": len(active_event_names),
        "active_event_names": active_event_names,
        "active_event_contracts": active_event_contracts,
    }


@dataclass(frozen=True)
class FxWsLiveMarketStateResult:
    ok: bool
    exchange: str
    product_code: str
    market_uid: str
    state_type: str
    market_state_path: Path | None
    blocked_by: tuple[str, ...]
    warnings: tuple[str, ...]
    row: dict[str, Any] | None
    read_only: bool = True
    would_send_to_broker: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["market_state_path"] = str(self.market_state_path) if self.market_state_path is not None else None
        data["blocked_by"] = list(self.blocked_by)
        data["warnings"] = list(self.warnings)
        return data


def build_fx_market_state_record_from_ws_live(
    *,
    board: dict[str, Any],
    flow: dict[str, Any],
    exchange: str,
    product_code: str,
    market_uid: str,
    stream_session_id: str | None,
) -> MarketStateRecord:
    best_bid = _safe_float(board.get("best_bid"))
    best_ask = _safe_float(board.get("best_ask"))
    spread = _safe_float(board.get("spread"))
    bid_depth = _safe_float(board.get("bid_depth"))
    ask_depth = _safe_float(board.get("ask_depth"))
    wall_ratio = _imbalance(bid_depth, ask_depth)
    wall_side = _wall_side(wall_ratio)
    imbalance = wall_ratio
    trade_delta = _safe_float(flow.get("delta"))
    event_ts = _event_ts(board, flow)
    mid_price = None
    if best_bid is not None and best_ask is not None:
        mid_price = (best_bid + best_ask) / 2.0

    valid = best_bid is not None and best_ask is not None and spread is not None and spread >= 0 and trade_delta is not None
    orderbook_summary = _orderbook_semantics_summary(wall_ratio=wall_ratio, wall_side=wall_side)
    orderbook_status = "partial" if orderbook_summary["summary_slots_count"] > 0 else "missing"

    return MarketStateRecord(
        market_uid=market_uid,
        exchange=exchange,
        symbol_raw=product_code,
        collector_ts=event_ts,
        exchange_ts=event_ts,
        trust_state=TrustState.TRUSTED if valid else TrustState.PROVISIONAL,
        boundary_reason=BoundaryReason.NONE,
        continuity_state="continuous" if valid else "unknown",
        interpretation_bucket="allow_structural_use" if valid else "observe_only",
        interpretation_reason="fx_ws_live_canonical_board_and_tradeflow" if valid else "fx_ws_live_canonical_incomplete",
        interpretation_policy={
            "mode": "ws_live_canonical_bridge",
            "review_required": not valid,
            "not_continuous_ws_series": False if valid else True,
            "execution_market_input": True,
            "delta_orderbook_application_complete": False,
            "context_only_not_order_signal": True,
        },
        semantic_observer_status="caution",
        semantic_usage_summary={
            "source_kind": "fx_ws_live_canonical_bridge",
            "contract_source": "sr_fx_ws_live_market_state_bridge",
            "meaning_version": "sr_fx_ws_live_market_state_bridge.v1",
            "observer_status": "caution",
            "total_rows": 1,
            "active_event_count": orderbook_summary["active_event_count"],
            "mapped_event_count": orderbook_summary["active_event_count"],
            "unknown_event_count": 0,
            "event_family_distribution": {"orderbook_near_wall": orderbook_summary["active_event_count"]} if orderbook_summary["active_event_count"] else {},
            "trust_bucket_distribution": {"trusted": 1} if valid else {"provisional": 1},
            "interpretation_bucket_distribution": {"allow_structural_use": 1} if valid else {"observe_only": 1},
            "consumer_distribution": {"workroom": 1, "operator_ui": 1, "autotrade": 1, "l4_consumer": 1},
        },
        semantic_usage_contract_rows=[],
        orderbook_semantics_contract_status=orderbook_status,
        orderbook_semantics_summary=orderbook_summary,
        orderbook_persistence_observable=False,
        best_bid=best_bid,
        best_ask=best_ask,
        spread=spread,
        mid_price=mid_price,
        price=_safe_float(flow.get("last_price")) or mid_price,
        imbalance=imbalance,
        wall_ratio=wall_ratio,
        wall_side=wall_side,
        trade_delta=trade_delta,
        near_zone_bids=_levels_from_best(price=best_bid, size=bid_depth),
        near_zone_asks=_levels_from_best(price=best_ask, size=ask_depth),
        top_book_summary={
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "mid_price": mid_price,
            "bid_levels_visible": board.get("bid_levels"),
            "ask_levels_visible": board.get("ask_levels"),
            "source": "latest_fx_ws_canonical_board",
        },
        near_zone_liquidity_summary={
            "bid_size_total": bid_depth,
            "ask_size_total": ask_depth,
            "bid_notional_total": None if best_bid is None or bid_depth is None else best_bid * bid_depth,
            "ask_notional_total": None if best_ask is None or ask_depth is None else best_ask * ask_depth,
        },
        imbalance_summary={
            "near_size_imbalance": imbalance,
            "wall_ratio": wall_ratio,
            "wall_side": wall_side,
            "bid_size_total": bid_depth,
            "ask_size_total": ask_depth,
        },
        zone_density_metadata={
            "mode": "ws_live_canonical_bridge",
            "source": "latest_live_board_metrics+recent_live_tradeflow_metrics",
            "delta_orderbook_application_complete": False,
            "board_record_type": board.get("record_type"),
            "board_stream_session_id": board.get("stream_session_id"),
        },
        source_series_id=f"{stream_session_id or 'unknown'}:ws_live_canonical_bridge",
        source_stream_session_id=stream_session_id,
    )


def write_fx_market_state_from_ws_live_canonical(
    *,
    latest_board_func: Callable[..., dict[str, Any]],
    recent_tradeflow_func: Callable[..., dict[str, Any]],
    max_age_sec: float = 120.0,
    now: datetime | None = None,
) -> FxWsLiveMarketStateResult:
    base_cfg = load_config()
    cfg = execution_market_config(base_cfg)
    exe = cfg.execution_market.normalized()
    exchange = exe.exchange

    board = latest_board_func(exchange=exchange, symbol=exe.product_code)
    flow = recent_tradeflow_func(exchange=exchange, symbol=exe.product_code, lines=80)
    blocked: list[str] = []
    warnings: list[str] = []

    if not board:
        blocked.append("fx_ws_live_board_missing")
    if not flow:
        blocked.append("fx_ws_live_tradeflow_missing")
    if board and str(board.get("source") or "") != "live_canonical":
        warnings.append("fx_ws_live_board_source_not_live_canonical")
    if flow and str(flow.get("source") or "") != "live_canonical":
        warnings.append("fx_ws_live_tradeflow_source_not_live_canonical")
    if board and flow:
        freshness_blockers, freshness_warnings = _freshness_blockers(
            board=board,
            flow=flow,
            max_age_sec=max_age_sec,
            now=now,
        )
        blocked.extend(freshness_blockers)
        warnings.extend(freshness_warnings)

    if blocked:
        return FxWsLiveMarketStateResult(
            ok=False,
            exchange=exchange,
            product_code=exe.product_code,
            market_uid=exe.market_uid,
            state_type=STATE_TYPE,
            market_state_path=None,
            blocked_by=tuple(dict.fromkeys(blocked)),
            warnings=tuple(dict.fromkeys(warnings)),
            row=None,
        )

    record = build_fx_market_state_record_from_ws_live(
        board=board,
        flow=flow,
        exchange=exchange,
        product_code=exe.product_code,
        market_uid=exe.market_uid,
        stream_session_id=str(board.get("stream_session_id") or flow.get("stream_session_id") or "fx_ws_live_canonical"),
    )
    if record.trust_state != TrustState.TRUSTED:
        blocked.append("fx_ws_live_market_state_incomplete")

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
        date_str=_date_str_from_ts(record.collector_ts),
        part_no=1,
    )
    return FxWsLiveMarketStateResult(
        ok=not blocked,
        exchange=exchange,
        product_code=exe.product_code,
        market_uid=exe.market_uid,
        state_type=STATE_TYPE,
        market_state_path=out,
        blocked_by=tuple(dict.fromkeys(blocked)),
        warnings=tuple(
            dict.fromkeys(
                [
                    *warnings,
                    "ws_live_canonical_bridge_not_full_delta_orderbook_engine",
                ]
            )
        ),
        row=record.to_dict(),
    )
