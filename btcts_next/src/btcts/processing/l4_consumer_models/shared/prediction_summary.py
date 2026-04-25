# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_summary.py
# desc: Shared prediction summary first-slice bundle anchored on MarketSummary.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from btcts.processing.l4_consumer_models.shared._value_utils import safe_str
from btcts.processing.l4_consumer_models.shared.health_digest import HealthDigest
from btcts.processing.l4_consumer_models.shared.market_summary import MarketSummary


@dataclass(frozen=True)
class PredictionSummary:
    prediction_type: str
    prediction_version: str
    source_kind: str
    market_uid: str | None
    event_ts: str | None
    freshness: str
    is_stale: bool | None
    horizon: str
    confidence: float
    caution_level: str
    short_horizon_bias: str
    continuation_likelihood: str
    mean_reversion_likelihood: str
    regime_transition_risk: str
    liquidity_deterioration_risk: str
    execution_feasibility_hint: str
    evidence: dict[str, Any] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PredictionSummaryBuildInput:
    market_summary: MarketSummary | None = None
    health_digest: HealthDigest | None = None
    source_kind: str | None = None
    horizon: str = "short"


def _normalize_source_kind(value: Any) -> str:
    normalized = safe_str(value)
    return normalized or "market_summary_anchor"


def _normalize_horizon(value: Any) -> str:
    normalized = safe_str(value)
    if normalized in {"micro", "short"}:
        return normalized
    return "short"


def _resolve_caution_level(
    summary: MarketSummary,
    health_digest: HealthDigest | None = None,
) -> str:
    if summary.is_stale is True:
        return "high"
    if summary.interpretation_bucket == "reanchor_required":
        return "blocked"
    if summary.trust_state not in {None, "trusted"}:
        return "high"
    if summary.interpretation_bucket == "observe_only":
        return "medium"

    if health_digest is not None:
        if health_digest.is_stale is True:
            return "high"

        market_runtime = dict(health_digest.market_runtime or {})
        digest_bucket = safe_str(market_runtime.get("interpretation_bucket"))
        if digest_bucket == "reanchor_required":
            return "blocked"
        if digest_bucket == "observe_only":
            return "medium"

        semantic_usage = dict(health_digest.semantic_usage or {})
        observer_status = safe_str(semantic_usage.get("observer_status"))
        if observer_status in {"broken", "unknown"}:
            return "high"
        if observer_status == "caution":
            return "medium"

        orderbook_runtime = dict(health_digest.orderbook_runtime or {})
        digest_wiring_status = safe_str(orderbook_runtime.get("wiring_status"))
        if digest_wiring_status == "missing":
            return "high"

    return "low"


def _resolve_short_horizon_bias(summary: MarketSummary) -> str:
    if summary.interpretation_bucket == "reanchor_required":
        return "unknown"

    if summary.orderbook_support_present and not summary.orderbook_resistance_present:
        return "bullish"
    if summary.orderbook_resistance_present and not summary.orderbook_support_present:
        return "bearish"

    if summary.orderbook_near_wall_present:
        active_names = set(summary.orderbook_active_event_names)
        if "support_candidate" in active_names:
            return "bullish"
        if "resistance_candidate" in active_names:
            return "bearish"

    return "neutral"


def _resolve_continuation_likelihood(summary: MarketSummary) -> str:
    if summary.interpretation_bucket == "reanchor_required":
        return "unknown"
    if (
        summary.orderbook_persistence_present
        and summary.orderbook_persistence_observable
        and summary.trust_state == "trusted"
    ):
        return "high"
    if summary.orderbook_active_event_count > 0:
        return "medium"
    return "low"


def _resolve_mean_reversion_likelihood(summary: MarketSummary) -> str:
    if summary.interpretation_bucket == "reanchor_required":
        return "unknown"
    if summary.orderbook_support_present and summary.orderbook_resistance_present:
        return "high"
    if summary.orderbook_near_wall_present:
        return "medium"
    return "low"


def _resolve_regime_transition_risk(summary: MarketSummary) -> str:
    if summary.interpretation_bucket == "reanchor_required":
        return "high"
    if summary.continuity_state == "resynced":
        return "high"
    if summary.interpretation_bucket == "observe_only":
        return "medium"
    return "low"


def _resolve_liquidity_deterioration_risk(summary: MarketSummary) -> str:
    if summary.orderbook_wiring_status == "missing":
        return "unknown"
    if not summary.orderbook_persistence_observable:
        return "medium"
    if summary.orderbook_summary_slots_count == 0:
        return "high"
    if summary.orderbook_summary_slots_count <= 2:
        return "medium"
    return "low"


def _resolve_execution_feasibility_hint(
    *,
    caution_level: str,
    liquidity_deterioration_risk: str,
) -> str:
    if caution_level == "blocked":
        return "unfavorable"
    if caution_level == "high" or liquidity_deterioration_risk == "high":
        return "unfavorable"
    if caution_level == "medium" or liquidity_deterioration_risk == "medium":
        return "caution"
    if liquidity_deterioration_risk == "low":
        return "favorable"
    return "unknown"


def _resolve_confidence(
    *,
    caution_level: str,
    continuation_likelihood: str,
    regime_transition_risk: str,
) -> float:
    if caution_level == "blocked":
        return 0.0
    if caution_level == "high":
        return 0.25
    if continuation_likelihood == "high" and regime_transition_risk == "low":
        return 0.75
    if continuation_likelihood == "medium":
        return 0.55
    if regime_transition_risk == "high":
        return 0.30
    return 0.45


def _build_evidence(
    summary: MarketSummary,
    health_digest: HealthDigest | None = None,
) -> dict[str, Any]:
    evidence = {
        "summary_source": summary.source_kind,
        "semantic_runtime_wiring_status": summary.semantic_runtime_wiring_status,
        "orderbook_wiring_status": summary.orderbook_wiring_status,
        "interpretation_bucket": summary.interpretation_bucket,
        "trust_state": summary.trust_state,
        "continuity_state": summary.continuity_state,
        "semantic_active_event_count": summary.semantic_active_event_count,
        "orderbook_active_event_count": summary.orderbook_active_event_count,
        "orderbook_summary_slots_present": list(summary.orderbook_summary_slots_present),
        "orderbook_persistence_observable": summary.orderbook_persistence_observable,
        "notable_events": list(summary.notable_events),
        "alert_candidates": list(summary.alert_candidates),
    }

    if health_digest is not None:
        evidence["health_digest_present"] = True
        evidence["health_freshness"] = health_digest.freshness
        evidence["health_is_stale"] = health_digest.is_stale

        semantic_usage = dict(health_digest.semantic_usage or {})
        evidence["health_semantic_observer_status"] = (
            safe_str(semantic_usage.get("observer_status")) or "unknown"
        )

        orderbook_runtime = dict(health_digest.orderbook_runtime or {})
        evidence["health_orderbook_wiring_status"] = (
            safe_str(orderbook_runtime.get("wiring_status")) or "missing"
        )
    else:
        evidence["health_digest_present"] = False

    return evidence


def build_prediction_summary(inp: PredictionSummaryBuildInput) -> PredictionSummary:
    summary = inp.market_summary
    health_digest = inp.health_digest
    if summary is None:
        caution_level = "blocked"
        continuation_likelihood = "unknown"
        mean_reversion_likelihood = "unknown"
        regime_transition_risk = "unknown"
        liquidity_deterioration_risk = "unknown"
        execution_feasibility_hint = "unknown"
        confidence = 0.0
        return PredictionSummary(
            prediction_type="shared_prediction_summary",
            prediction_version="phase3.v1alpha1",
            source_kind=_normalize_source_kind(inp.source_kind),
            market_uid=None,
            event_ts=None,
            freshness="UNKNOWN",
            is_stale=None,
            horizon=_normalize_horizon(inp.horizon),
            confidence=confidence,
            caution_level=caution_level,
            short_horizon_bias="unknown",
            continuation_likelihood=continuation_likelihood,
            mean_reversion_likelihood=mean_reversion_likelihood,
            regime_transition_risk=regime_transition_risk,
            liquidity_deterioration_risk=liquidity_deterioration_risk,
            execution_feasibility_hint=execution_feasibility_hint,
            evidence={},
            diagnostics={},
        )

    caution_level = _resolve_caution_level(
        summary,
        health_digest=health_digest,
    )
    short_horizon_bias = _resolve_short_horizon_bias(summary)
    continuation_likelihood = _resolve_continuation_likelihood(summary)
    mean_reversion_likelihood = _resolve_mean_reversion_likelihood(summary)
    regime_transition_risk = _resolve_regime_transition_risk(summary)
    liquidity_deterioration_risk = _resolve_liquidity_deterioration_risk(summary)
    execution_feasibility_hint = _resolve_execution_feasibility_hint(
        caution_level=caution_level,
        liquidity_deterioration_risk=liquidity_deterioration_risk,
    )
    confidence = _resolve_confidence(
        caution_level=caution_level,
        continuation_likelihood=continuation_likelihood,
        regime_transition_risk=regime_transition_risk,
    )

    return PredictionSummary(
        prediction_type="shared_prediction_summary",
        prediction_version="phase3.v1alpha1",
        source_kind=_normalize_source_kind(inp.source_kind),
        market_uid=summary.market_uid,
        event_ts=summary.event_ts,
        freshness=summary.freshness,
        is_stale=summary.is_stale,
        horizon=_normalize_horizon(inp.horizon),
        confidence=confidence,
        caution_level=caution_level,
        short_horizon_bias=short_horizon_bias,
        continuation_likelihood=continuation_likelihood,
        mean_reversion_likelihood=mean_reversion_likelihood,
        regime_transition_risk=regime_transition_risk,
        liquidity_deterioration_risk=liquidity_deterioration_risk,
        execution_feasibility_hint=execution_feasibility_hint,
        evidence=_build_evidence(
            summary,
            health_digest=health_digest,
        ),
        diagnostics={
            "semantic_contract_rows_count": summary.semantic_contract_rows_count,
            "orderbook_summary_slots_count": summary.orderbook_summary_slots_count,
            "orderbook_contract_status_source": summary.orderbook_contract_status_source,
            "health_digest_present": health_digest is not None,
        },
    )