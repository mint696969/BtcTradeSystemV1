# path: ./btcts_next/src/btcts/prediction/feature_depth.py
# desc: Standalone feature-depth contracts for already-provided orderbook/tradeflow/liquidity snapshots. Non-collecting, non-executing, context-only in PS-E1.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterable, Mapping, Tuple

from .source_quality import ProviderReliabilityRegistry

LOGIC_VERSION = "prediction_feature_depth.ps_e1.v1"


class FeatureDepthInputKind(str, Enum):
    ORDERBOOK = "orderbook"
    TRADEFLOW = "tradeflow"
    LIQUIDITY = "liquidity"
    ALGORITHMIC_FOOTPRINT = "algorithmic_footprint"


class FeatureDepthState(str, Enum):
    UNAVAILABLE = "unavailable"
    CONTEXT_ONLY = "context_only"
    USABLE_CONTEXT = "usable_context"
    WARNING_CONTEXT = "warning_context"


@dataclass(frozen=True)
class FeatureDepthInputRef:
    input_ref_id: str
    input_kind: FeatureDepthInputKind
    source_id: str | None = None
    venue: str | None = None
    symbol: str | None = None
    event_ts: str | None = None
    usable: bool = True
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["input_kind"] = self.input_kind.value
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        data["logic_version"] = LOGIC_VERSION
        return data


@dataclass(frozen=True)
class OrderBookFeatureSummary:
    state: FeatureDepthState = FeatureDepthState.UNAVAILABLE
    snapshot_count: int = 0
    source_ids: Tuple[str, ...] = ()
    min_spread_bps: float | None = None
    max_spread_bps: float | None = None
    average_spread_bps: float | None = None
    max_abs_imbalance_ratio: float | None = None
    thin_book_warning: bool = False
    spread_warning: bool = False
    primary_direction_owner: bool = False
    usable_for_primary_short_horizon: bool = False
    context_only: bool = True
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    @property
    def usable(self) -> bool:
        return not self.blockers and self.state in (FeatureDepthState.USABLE_CONTEXT, FeatureDepthState.WARNING_CONTEXT)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state.value
        data["source_ids"] = list(self.source_ids)
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        data["usable"] = self.usable
        return data


@dataclass(frozen=True)
class TradeFlowFeatureSummary:
    state: FeatureDepthState = FeatureDepthState.UNAVAILABLE
    window_count: int = 0
    source_ids: Tuple[str, ...] = ()
    total_trade_count: int = 0
    buy_sell_imbalance_ratio: float | None = None
    aggressive_flow_ratio: float | None = None
    burst_warning: bool = False
    primary_direction_owner: bool = False
    usable_for_primary_short_horizon: bool = False
    context_only: bool = True
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    @property
    def usable(self) -> bool:
        return not self.blockers and self.state in (FeatureDepthState.USABLE_CONTEXT, FeatureDepthState.WARNING_CONTEXT)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state.value
        data["source_ids"] = list(self.source_ids)
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        data["usable"] = self.usable
        return data


@dataclass(frozen=True)
class FeatureDepthSnapshot:
    generated_at: str
    input_refs: Tuple[FeatureDepthInputRef, ...] = ()
    orderbook: OrderBookFeatureSummary = OrderBookFeatureSummary()
    tradeflow: TradeFlowFeatureSummary = TradeFlowFeatureSummary()
    provider_reliability_summary: Mapping[str, Any] = field(default_factory=dict)
    feature_depth_state: FeatureDepthState = FeatureDepthState.UNAVAILABLE
    primary_direction_owner: bool = False
    usable_for_primary_short_horizon: bool = False
    context_only: bool = True
    read_only: bool = True
    non_executing: bool = True
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    @property
    def usable(self) -> bool:
        return not self.blockers and self.feature_depth_state in (FeatureDepthState.USABLE_CONTEXT, FeatureDepthState.WARNING_CONTEXT)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "input_refs": [item.to_dict() for item in self.input_refs],
            "orderbook": self.orderbook.to_dict(),
            "tradeflow": self.tradeflow.to_dict(),
            "provider_reliability_summary": dict(self.provider_reliability_summary),
            "feature_depth_state": self.feature_depth_state.value,
            "primary_direction_owner": self.primary_direction_owner,
            "usable_for_primary_short_horizon": self.usable_for_primary_short_horizon,
            "context_only": self.context_only,
            "usable": self.usable,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "logic_version": LOGIC_VERSION,
        }


def _now(now: datetime | None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if now.tzinfo is None:
        return now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _int_or_zero(value: Any) -> int:
    try:
        return int(value or 0)
    except Exception:
        return 0


def _input_ref(item: Mapping[str, Any], kind: FeatureDepthInputKind, index: int) -> FeatureDepthInputRef:
    source_id = str(item.get("source_id") or item.get("source") or "").strip() or None
    event_ts = str(item.get("event_ts") or item.get("ts") or "").strip() or None
    blockers: list[str] = []
    if not source_id:
        blockers.append("feature_depth_source_id_missing")
    return FeatureDepthInputRef(
        input_ref_id=f"{LOGIC_VERSION}:{kind.value}:{source_id or 'unknown'}:{index}",
        input_kind=kind,
        source_id=source_id,
        venue=str(item.get("venue") or "").strip() or None,
        symbol=str(item.get("symbol") or "").strip() or None,
        event_ts=event_ts,
        usable=not blockers,
        blockers=tuple(blockers),
    )


def _summarize_orderbook(orderbook_snapshots: Iterable[Mapping[str, Any]] | None) -> tuple[OrderBookFeatureSummary, Tuple[FeatureDepthInputRef, ...]]:
    rows = tuple(orderbook_snapshots or ())
    refs = tuple(_input_ref(row, FeatureDepthInputKind.ORDERBOOK, idx) for idx, row in enumerate(rows))
    if not rows:
        return OrderBookFeatureSummary(blockers=("orderbook_feature_depth_missing",)), refs
    spreads: list[float] = []
    imbalances: list[float] = []
    warnings: list[str] = []
    blockers: list[str] = []
    source_ids: list[str] = []
    for row in rows:
        source_id = str(row.get("source_id") or row.get("source") or "").strip()
        if source_id:
            source_ids.append(source_id)
        spread = _float_or_none(row.get("spread_bps"))
        if spread is None:
            bid = _float_or_none(row.get("bid_price") or row.get("best_bid"))
            ask = _float_or_none(row.get("ask_price") or row.get("best_ask"))
            if bid and ask and bid > 0:
                spread = max(((ask - bid) / bid) * 10_000.0, 0.0)
        if spread is not None:
            spreads.append(spread)
        imbalance = _float_or_none(row.get("imbalance_ratio") or row.get("book_imbalance_ratio"))
        if imbalance is not None:
            imbalances.append(max(min(imbalance, 1.0), -1.0))
        bid_depth = _float_or_none(row.get("bid_depth") or row.get("depth_bid") or row.get("bid_size"))
        ask_depth = _float_or_none(row.get("ask_depth") or row.get("depth_ask") or row.get("ask_size"))
        if bid_depth is not None and ask_depth is not None and min(bid_depth, ask_depth) <= 0:
            warnings.append("thin_book_depth_warning")
    if not spreads:
        warnings.append("orderbook_spread_unavailable")
    spread_warning = bool(spreads and max(spreads) >= 12.0)
    if spread_warning:
        warnings.append("wide_spread_context_warning")
    thin_book_warning = "thin_book_depth_warning" in warnings
    state = FeatureDepthState.WARNING_CONTEXT if warnings else FeatureDepthState.USABLE_CONTEXT
    return OrderBookFeatureSummary(
        state=state,
        snapshot_count=len(rows),
        source_ids=tuple(dict.fromkeys(source_ids)),
        min_spread_bps=round(min(spreads), 6) if spreads else None,
        max_spread_bps=round(max(spreads), 6) if spreads else None,
        average_spread_bps=round(sum(spreads) / len(spreads), 6) if spreads else None,
        max_abs_imbalance_ratio=round(max(abs(item) for item in imbalances), 6) if imbalances else None,
        thin_book_warning=thin_book_warning,
        spread_warning=spread_warning,
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    ), refs


def _summarize_tradeflow(tradeflow_windows: Iterable[Mapping[str, Any]] | None) -> tuple[TradeFlowFeatureSummary, Tuple[FeatureDepthInputRef, ...]]:
    rows = tuple(tradeflow_windows or ())
    refs = tuple(_input_ref(row, FeatureDepthInputKind.TRADEFLOW, idx) for idx, row in enumerate(rows))
    if not rows:
        return TradeFlowFeatureSummary(blockers=("tradeflow_feature_depth_missing",)), refs
    source_ids: list[str] = []
    buy_volume = 0.0
    sell_volume = 0.0
    aggressive_buy = 0.0
    aggressive_sell = 0.0
    trade_count = 0
    warnings: list[str] = []
    for row in rows:
        source_id = str(row.get("source_id") or row.get("source") or "").strip()
        if source_id:
            source_ids.append(source_id)
        buy_volume += _float_or_none(row.get("buy_volume")) or 0.0
        sell_volume += _float_or_none(row.get("sell_volume")) or 0.0
        aggressive_buy += _float_or_none(row.get("aggressive_buy_volume")) or 0.0
        aggressive_sell += _float_or_none(row.get("aggressive_sell_volume")) or 0.0
        trade_count += _int_or_zero(row.get("trade_count"))
    total_volume = buy_volume + sell_volume
    buy_sell_imbalance = ((buy_volume - sell_volume) / total_volume) if total_volume > 0 else None
    aggressive_total = aggressive_buy + aggressive_sell
    aggressive_ratio = ((aggressive_buy - aggressive_sell) / aggressive_total) if aggressive_total > 0 else None
    burst_warning = trade_count >= 1000
    if burst_warning:
        warnings.append("tradeflow_burst_context_warning")
    if total_volume <= 0:
        warnings.append("tradeflow_volume_unavailable")
    state = FeatureDepthState.WARNING_CONTEXT if warnings else FeatureDepthState.USABLE_CONTEXT
    return TradeFlowFeatureSummary(
        state=state,
        window_count=len(rows),
        source_ids=tuple(dict.fromkeys(source_ids)),
        total_trade_count=trade_count,
        buy_sell_imbalance_ratio=round(buy_sell_imbalance, 6) if buy_sell_imbalance is not None else None,
        aggressive_flow_ratio=round(aggressive_ratio, 6) if aggressive_ratio is not None else None,
        burst_warning=burst_warning,
        blockers=tuple(),
        warnings=tuple(dict.fromkeys(warnings)),
    ), refs


def build_feature_depth_snapshot(
    *,
    orderbook_snapshots: Iterable[Mapping[str, Any]] | None = None,
    tradeflow_windows: Iterable[Mapping[str, Any]] | None = None,
    provider_reliability_registry: ProviderReliabilityRegistry | None = None,
    now: datetime | None = None,
) -> FeatureDepthSnapshot:
    """Build a context-only feature-depth snapshot from already-provided inputs.

    PS-E1 intentionally does not collect, import Collector runtime, write artifacts, call external APIs,
    append AutoTrade decisions, request mode changes, or send broker orders.
    """
    now_dt = _now(now)
    orderbook, orderbook_refs = _summarize_orderbook(orderbook_snapshots)
    tradeflow, tradeflow_refs = _summarize_tradeflow(tradeflow_windows)
    blockers = list(orderbook.blockers) + list(tradeflow.blockers)
    warnings = list(orderbook.warnings) + list(tradeflow.warnings)
    provider_summary: Mapping[str, Any] = {}
    if provider_reliability_registry is not None:
        provider_summary = provider_reliability_registry.to_dict()
        if provider_reliability_registry.unknown_source_ids:
            warnings.append("feature_depth_unknown_provider_context_only")
        if not provider_reliability_registry.primary_direction_owner_allowed:
            warnings.append("provider_reliability_primary_direction_disabled")
    if orderbook.usable or tradeflow.usable:
        state = FeatureDepthState.WARNING_CONTEXT if warnings else FeatureDepthState.USABLE_CONTEXT
    else:
        state = FeatureDepthState.UNAVAILABLE
    return FeatureDepthSnapshot(
        generated_at=_iso(now_dt),
        input_refs=tuple(orderbook_refs + tradeflow_refs),
        orderbook=orderbook,
        tradeflow=tradeflow,
        provider_reliability_summary=provider_summary,
        feature_depth_state=state,
        primary_direction_owner=False,
        usable_for_primary_short_horizon=False,
        context_only=True,
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
