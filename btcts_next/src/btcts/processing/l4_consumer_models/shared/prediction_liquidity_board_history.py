# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_liquidity_board_history.py
# desc: Thin shared builder for liquidity / board-history evidence in Prediction System entry.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l4_consumer_models.shared.health_digest import HealthDigest
from btcts.processing.l4_consumer_models.shared.market_summary import MarketSummary


@dataclass(frozen=True)
class PredictionLiquidityBoardHistoryBuildInput:
    market_summary: MarketSummary | None = None
    health_digest: HealthDigest | None = None
    source_kind: str | None = None
    diagnostics: dict[str, Any] | None = None


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _resolve_source_kind(value: Any) -> str:
    return _safe_str(value) or "market_summary_anchor"


def _resolve_identity(
    market_summary: MarketSummary | None,
    health_digest: HealthDigest | None,
) -> tuple[str | None, str | None, str, bool | None]:
    market_uid = None
    event_ts = None
    freshness = "UNKNOWN"
    is_stale = None

    if market_summary is not None:
        market_uid = market_summary.market_uid
        event_ts = market_summary.event_ts
        freshness = market_summary.freshness
        is_stale = market_summary.is_stale

    if health_digest is not None:
        if market_uid is None:
            market_uid = health_digest.market_uid
        if event_ts is None:
            event_ts = health_digest.event_ts
        if freshness == "UNKNOWN":
            freshness = health_digest.freshness
        if is_stale is None:
            is_stale = health_digest.is_stale

    return market_uid, event_ts, freshness, is_stale


def _resolve_history_window_sec(
    market_summary: MarketSummary | None,
    health_digest: HealthDigest | None,
) -> int:
    if market_summary is None and health_digest is None:
        return 0

    if market_summary is not None:
        if market_summary.freshness == "LIVE":
            return 120
        if market_summary.freshness == "QUIET":
            return 300
        if market_summary.freshness == "STALE":
            return 600

    if health_digest is not None:
        if health_digest.freshness == "LIVE":
            return 120
        if health_digest.freshness == "QUIET":
            return 300
        if health_digest.freshness == "STALE":
            return 600

    return 300


def _resolve_liquidity_pressure_balance(market_summary: MarketSummary | None) -> str:
    if market_summary is None:
        return "unknown"

    if (
        market_summary.orderbook_support_present
        and not market_summary.orderbook_resistance_present
    ):
        return "bid_support"

    if (
        market_summary.orderbook_resistance_present
        and not market_summary.orderbook_support_present
    ):
        return "ask_pressure"

    if (
        market_summary.orderbook_support_present
        and market_summary.orderbook_resistance_present
    ):
        return "balanced"

    return "unknown"


def _resolve_wall_persistence_bias(
    market_summary: MarketSummary | None,
    *,
    liquidity_pressure_balance: str,
) -> str:
    if market_summary is None:
        return "unknown"

    if not market_summary.orderbook_persistence_observable:
        return "unknown"

    if liquidity_pressure_balance == "bid_support":
        return "bid_support"
    if liquidity_pressure_balance == "ask_pressure":
        return "ask_pressure"
    if liquidity_pressure_balance == "balanced":
        return "balanced"

    if market_summary.orderbook_persistence_present:
        return "watch_persistence"

    return "unknown"


def _resolve_persistence_confidence(
    market_summary: MarketSummary | None,
    health_digest: HealthDigest | None,
) -> str:
    if market_summary is None:
        return "unknown"

    if not market_summary.orderbook_persistence_observable:
        return "low"

    if market_summary.is_stale is True:
        return "low"

    if market_summary.orderbook_persistence_present:
        confidence = "high"
    else:
        confidence = "medium"

    if health_digest is not None:
        if health_digest.is_stale is True:
            return "low"

        semantic_usage = dict(health_digest.semantic_usage or {})
        observer_status = _safe_str(semantic_usage.get("observer_status"))
        if observer_status in {"broken", "unknown"}:
            return "low"
        if observer_status == "caution" and confidence == "high":
            return "medium"

    return confidence


def _build_trigger_flags(
    market_summary: MarketSummary | None,
    health_digest: HealthDigest | None,
    *,
    liquidity_pressure_balance: str,
    wall_persistence_bias: str,
) -> tuple[str, ...]:
    out: list[str] = []

    if market_summary is None:
        out.append("market_summary_absent")
        return tuple(out)

    out.append(f"orderbook_active_event_count:{market_summary.orderbook_active_event_count}")
    out.append(f"semantic_active_event_count:{market_summary.semantic_active_event_count}")

    if market_summary.orderbook_support_present:
        out.append("support_present")
    if market_summary.orderbook_resistance_present:
        out.append("resistance_present")
    if market_summary.orderbook_persistence_present:
        out.append("persistence_present")
    if market_summary.orderbook_persistence_observable:
        out.append("persistence_observable")
    else:
        out.append("persistence_not_observable")

    if health_digest is not None:
        if health_digest.is_stale is True:
            out.append("health_digest_stale")

        semantic_usage = dict(health_digest.semantic_usage or {})
        observer_status = _safe_str(semantic_usage.get("observer_status"))
        if observer_status is not None:
            out.append(f"health_observer:{observer_status}")

    out.append(f"liquidity_balance:{liquidity_pressure_balance}")
    out.append(f"wall_persistence_bias:{wall_persistence_bias}")
    return tuple(out)


def build_prediction_liquidity_board_history(
    inp: PredictionLiquidityBoardHistoryBuildInput,
) -> dict[str, Any]:
    market_uid, event_ts, freshness, is_stale = _resolve_identity(
        inp.market_summary,
        inp.health_digest,
    )
    history_window_sec = _resolve_history_window_sec(
        inp.market_summary,
        inp.health_digest,
    )
    liquidity_pressure_balance = _resolve_liquidity_pressure_balance(inp.market_summary)
    wall_persistence_bias = _resolve_wall_persistence_bias(
        inp.market_summary,
        liquidity_pressure_balance=liquidity_pressure_balance,
    )
    persistence_confidence = _resolve_persistence_confidence(
        inp.market_summary,
        inp.health_digest,
    )

    return {
        "evidence_type": "prediction_liquidity_board_history",
        "evidence_version": "phase3.v1alpha1",
        "source_kind": _resolve_source_kind(inp.source_kind),
        "market_uid": market_uid,
        "event_ts": event_ts,
        "freshness": freshness,
        "is_stale": is_stale,
        "history_window_sec": history_window_sec,
        "orderbook_active_event_count": None
        if inp.market_summary is None
        else inp.market_summary.orderbook_active_event_count,
        "semantic_active_event_count": None
        if inp.market_summary is None
        else inp.market_summary.semantic_active_event_count,
        "support_present": False
        if inp.market_summary is None
        else inp.market_summary.orderbook_support_present,
        "resistance_present": False
        if inp.market_summary is None
        else inp.market_summary.orderbook_resistance_present,
        "persistence_present": False
        if inp.market_summary is None
        else inp.market_summary.orderbook_persistence_present,
        "persistence_observable": False
        if inp.market_summary is None
        else inp.market_summary.orderbook_persistence_observable,
        "liquidity_pressure_balance": liquidity_pressure_balance,
        "wall_persistence_bias": wall_persistence_bias,
        "persistence_confidence": persistence_confidence,
        "trigger_flags": _build_trigger_flags(
            inp.market_summary,
            inp.health_digest,
            liquidity_pressure_balance=liquidity_pressure_balance,
            wall_persistence_bias=wall_persistence_bias,
        ),
        "diagnostics": {
            "builder_type": "prediction_liquidity_board_history",
            "market_summary_present": inp.market_summary is not None,
            "health_digest_present": inp.health_digest is not None,
            **dict(inp.diagnostics or {}),
        },
    }