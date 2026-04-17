# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_regime_turning_point.py
# desc: Thin shared builder for regime / turning-point evidence in Prediction System entry.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from btcts.processing.l4_consumer_models.shared.health_digest import HealthDigest
from btcts.processing.l4_consumer_models.shared.market_summary import MarketSummary


@dataclass(frozen=True)
class PredictionRegimeTurningPointBuildInput:
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


def _resolve_transition_sign(
    market_summary: MarketSummary | None,
    health_digest: HealthDigest | None,
) -> str:
    if market_summary is None:
        return "unknown"

    if market_summary.interpretation_bucket == "reanchor_required":
        return "transition_underway"
    if market_summary.continuity_state == "resynced":
        return "transition_underway"

    if market_summary.is_stale is True:
        return "weakening_continuation"
    if market_summary.trust_state not in {None, "trusted"}:
        return "weakening_continuation"
    if market_summary.interpretation_bucket == "observe_only":
        return "weakening_continuation"

    if (
        market_summary.orderbook_support_present
        and market_summary.orderbook_resistance_present
    ):
        return "balanced_pressure"

    if health_digest is not None:
        if health_digest.is_stale is True:
            return "weakening_continuation"

        market_runtime = dict(health_digest.market_runtime or {})
        digest_bucket = _safe_str(market_runtime.get("interpretation_bucket"))
        if digest_bucket == "reanchor_required":
            return "transition_underway"
        if digest_bucket == "observe_only":
            return "weakening_continuation"

        semantic_usage = dict(health_digest.semantic_usage or {})
        observer_status = _safe_str(semantic_usage.get("observer_status"))
        if observer_status == "caution":
            return "weakening_continuation"
        if observer_status in {"broken", "unknown"}:
            return "transition_underway"

    return "stable_continuation"


def _resolve_turning_point_risk(
    market_summary: MarketSummary | None,
    health_digest: HealthDigest | None,
) -> str:
    if market_summary is None:
        return "unknown"

    if market_summary.interpretation_bucket == "reanchor_required":
        return "high"
    if market_summary.continuity_state == "resynced":
        return "high"
    if market_summary.is_stale is True:
        return "high"
    if market_summary.trust_state not in {None, "trusted"}:
        return "high"

    if market_summary.interpretation_bucket == "observe_only":
        return "medium"
    if (
        market_summary.orderbook_support_present
        and market_summary.orderbook_resistance_present
    ):
        return "medium"
    if not market_summary.orderbook_persistence_observable:
        return "medium"

    if health_digest is not None:
        if health_digest.is_stale is True:
            return "high"

        market_runtime = dict(health_digest.market_runtime or {})
        digest_bucket = _safe_str(market_runtime.get("interpretation_bucket"))
        if digest_bucket == "reanchor_required":
            return "high"
        if digest_bucket == "observe_only":
            return "medium"

        semantic_usage = dict(health_digest.semantic_usage or {})
        observer_status = _safe_str(semantic_usage.get("observer_status"))
        if observer_status in {"broken", "unknown"}:
            return "high"
        if observer_status == "caution":
            return "medium"

    return "low"


def _resolve_continuity_bias(
    market_summary: MarketSummary | None,
    *,
    transition_sign: str,
    turning_point_risk: str,
) -> str:
    if market_summary is None:
        return "unknown"
    if market_summary.continuity_state == "resynced":
        return "resynced"
    if transition_sign == "transition_underway":
        return "broken"
    if turning_point_risk == "high":
        return "fragile"
    if turning_point_risk == "medium":
        return "weakening"
    return "continuous"


def _build_trigger_flags(
    market_summary: MarketSummary | None,
    health_digest: HealthDigest | None,
    *,
    transition_sign: str,
    turning_point_risk: str,
) -> tuple[str, ...]:
    out: list[str] = []

    if market_summary is None:
        out.append("market_summary_absent")
        return tuple(out)

    if market_summary.interpretation_bucket == "reanchor_required":
        out.append("interpretation_reanchor_required")
    elif market_summary.interpretation_bucket == "observe_only":
        out.append("interpretation_observe_only")

    if market_summary.continuity_state == "resynced":
        out.append("continuity_resynced")
    if market_summary.is_stale is True:
        out.append("market_summary_stale")
    if market_summary.trust_state not in {None, "trusted"}:
        out.append("trust_not_trusted")

    if (
        market_summary.orderbook_support_present
        and market_summary.orderbook_resistance_present
    ):
        out.append("support_resistance_balance")
    if not market_summary.orderbook_persistence_observable:
        out.append("persistence_not_observable")

    if health_digest is not None:
        if health_digest.is_stale is True:
            out.append("health_digest_stale")

        semantic_usage = dict(health_digest.semantic_usage or {})
        observer_status = _safe_str(semantic_usage.get("observer_status"))
        if observer_status is not None:
            out.append(f"health_observer:{observer_status}")

    out.append(f"transition_sign:{transition_sign}")
    out.append(f"turning_point_risk:{turning_point_risk}")
    return tuple(out)


def build_prediction_regime_turning_point(
    inp: PredictionRegimeTurningPointBuildInput,
) -> dict[str, Any]:
    market_uid, event_ts, freshness, is_stale = _resolve_identity(
        inp.market_summary,
        inp.health_digest,
    )
    transition_sign = _resolve_transition_sign(
        inp.market_summary,
        inp.health_digest,
    )
    turning_point_risk = _resolve_turning_point_risk(
        inp.market_summary,
        inp.health_digest,
    )
    continuity_bias = _resolve_continuity_bias(
        inp.market_summary,
        transition_sign=transition_sign,
        turning_point_risk=turning_point_risk,
    )

    return {
        "evidence_type": "prediction_regime_turning_point",
        "evidence_version": "phase3.v1alpha1",
        "source_kind": _resolve_source_kind(inp.source_kind),
        "market_uid": market_uid,
        "event_ts": event_ts,
        "freshness": freshness,
        "is_stale": is_stale,
        "continuity_state": None
        if inp.market_summary is None
        else inp.market_summary.continuity_state,
        "interpretation_bucket": None
        if inp.market_summary is None
        else inp.market_summary.interpretation_bucket,
        "trust_state": None
        if inp.market_summary is None
        else inp.market_summary.trust_state,
        "transition_sign": transition_sign,
        "turning_point_risk": turning_point_risk,
        "continuity_bias": continuity_bias,
        "trigger_flags": _build_trigger_flags(
            inp.market_summary,
            inp.health_digest,
            transition_sign=transition_sign,
            turning_point_risk=turning_point_risk,
        ),
        "diagnostics": {
            "builder_type": "prediction_regime_turning_point",
            "market_summary_present": inp.market_summary is not None,
            "health_digest_present": inp.health_digest is not None,
            **dict(inp.diagnostics or {}),
        },
    }