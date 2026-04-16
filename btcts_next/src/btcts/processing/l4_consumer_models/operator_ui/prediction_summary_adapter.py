# path: ./btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/prediction_summary_adapter.py
# desc: Thin operator UI adapter over shared PredictionSummary bundle.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from btcts.processing.l4_consumer_models.shared import PredictionSummary


@dataclass(frozen=True)
class PredictionSummaryWidgetModel:
    widget_kind: str
    freshness_key: str
    horizon_key: str
    caution_level_key: str
    short_horizon_bias_key: str
    continuation_likelihood_key: str
    mean_reversion_likelihood_key: str
    regime_transition_risk_key: str
    liquidity_deterioration_risk_key: str
    execution_feasibility_hint_key: str
    confidence: float
    market_uid: str | None = None
    event_ts: str | None = None
    source_kind: str = "unknown"
    health_caution_used_key: str = "false"
    notable_tags: list[str] = field(default_factory=list)
    alert_tags: list[str] = field(default_factory=list)


def _key(value: Any, *, fallback: str) -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def prediction_summary_widget_model(
    summary: PredictionSummary | None,
) -> PredictionSummaryWidgetModel:
    if summary is None:
        return PredictionSummaryWidgetModel(
            widget_kind="prediction_summary",
            freshness_key="UNKNOWN",
            horizon_key="short",
            caution_level_key="blocked",
            short_horizon_bias_key="unknown",
            continuation_likelihood_key="unknown",
            mean_reversion_likelihood_key="unknown",
            regime_transition_risk_key="unknown",
            liquidity_deterioration_risk_key="unknown",
            execution_feasibility_hint_key="unknown",
            confidence=0.0,
            market_uid=None,
            event_ts=None,
            source_kind="unknown",
            health_caution_used_key="false",
            notable_tags=[],
            alert_tags=[],
        )

    evidence = dict(summary.evidence or {})
    notable_tags = list(evidence.get("notable_events") or [])
    alert_tags = list(evidence.get("alert_candidates") or [])
    health_caution_used = bool(evidence.get("health_digest_present"))

    return PredictionSummaryWidgetModel(
        widget_kind=summary.prediction_type,
        freshness_key=_key(summary.freshness, fallback="UNKNOWN"),
        horizon_key=_key(summary.horizon, fallback="short"),
        caution_level_key=_key(summary.caution_level, fallback="blocked"),
        short_horizon_bias_key=_key(summary.short_horizon_bias, fallback="unknown"),
        continuation_likelihood_key=_key(
            summary.continuation_likelihood,
            fallback="unknown",
        ),
        mean_reversion_likelihood_key=_key(
            summary.mean_reversion_likelihood,
            fallback="unknown",
        ),
        regime_transition_risk_key=_key(
            summary.regime_transition_risk,
            fallback="unknown",
        ),
        liquidity_deterioration_risk_key=_key(
            summary.liquidity_deterioration_risk,
            fallback="unknown",
        ),
        execution_feasibility_hint_key=_key(
            summary.execution_feasibility_hint,
            fallback="unknown",
        ),
        confidence=float(summary.confidence),
        market_uid=summary.market_uid,
        event_ts=summary.event_ts,
        source_kind=_key(summary.source_kind, fallback="unknown"),
        health_caution_used_key="true" if health_caution_used else "false",
        notable_tags=notable_tags,
        alert_tags=alert_tags,
    )


def prediction_summary_status_payload(
    summary: PredictionSummary | None,
) -> dict[str, Any]:
    if summary is None:
        return {}

    return {
        "prediction_type": summary.prediction_type,
        "prediction_version": summary.prediction_version,
        "source_kind": summary.source_kind,
        "market_uid": summary.market_uid,
        "event_ts": summary.event_ts,
        "freshness": summary.freshness,
        "is_stale": summary.is_stale,
        "horizon": summary.horizon,
        "confidence": float(summary.confidence),
        "caution_level": summary.caution_level,
        "short_horizon_bias": summary.short_horizon_bias,
        "continuation_likelihood": summary.continuation_likelihood,
        "mean_reversion_likelihood": summary.mean_reversion_likelihood,
        "regime_transition_risk": summary.regime_transition_risk,
        "liquidity_deterioration_risk": summary.liquidity_deterioration_risk,
        "execution_feasibility_hint": summary.execution_feasibility_hint,
        "evidence": dict(summary.evidence),
        "diagnostics": dict(summary.diagnostics),
    }