# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_summary_state.py
# desc: PredictionSummary first-adopter state owner anchored on market_summary with optional health caution input.

from __future__ import annotations

from typing import TypedDict

from btcts.apps.operator_ui.health_data_service import load_health_current_state_bundle
from btcts.apps.operator_ui.market_state_service import load_latest_market_summary
from btcts.processing.l4_consumer_models.shared import (
    HealthDigest,
    PredictionSummary,
    PredictionSummaryBuildInput,
    build_prediction_summary,
)


class PredictionSummaryState(TypedDict):
    prediction: PredictionSummary
    source_label: str
    summary_source: str
    health_caution_used: bool


def _load_optional_health_digest() -> HealthDigest | None:
    current_bundle = load_health_current_state_bundle()
    if not isinstance(current_bundle, dict):
        return None

    digest = current_bundle.get("health_digest")
    if isinstance(digest, HealthDigest):
        return digest

    return None


def load_prediction_summary_state(
    *,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
    include_health_caution: bool = True,
) -> PredictionSummaryState:
    market_summary = load_latest_market_summary(
        exchange=exchange,
        symbol_raw=symbol_raw,
        state_type="market.overview",
    )
    health_digest = _load_optional_health_digest() if include_health_caution else None

    prediction = build_prediction_summary(
        PredictionSummaryBuildInput(
            market_summary=market_summary,
            health_digest=health_digest,
            horizon="short",
        )
    )

    source_label = "market_summary"
    if health_digest is not None:
        source_label = "market_summary + health_digest_caution"

    return {
        "prediction": prediction,
        "source_label": source_label,
        "summary_source": prediction.source_kind,
        "health_caution_used": health_digest is not None,
    }