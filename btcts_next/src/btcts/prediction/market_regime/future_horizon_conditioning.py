# path: ./btcts_next/src/btcts/prediction/market_regime/future_horizon_conditioning.py
# desc: MR-F9.18A12 pure shadow-only sequential horizon conditioning. Uses predecessor distribution and uncertainty; never copies predecessor labels.

from __future__ import annotations

from math import isfinite
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .contracts import MarketRegimeCode
from .future_forecast_contract import FutureForecastStatus, MarketRegimeFutureForecast

MARKET_REGIME_FUTURE_HORIZON_CONDITIONING_VERSION = (
    "prediction.market_regime.future_horizon_conditioning.mr_f9_18a12.v1"
)


def _normalized_distribution(
    scores: Mapping[MarketRegimeCode, float],
) -> Mapping[MarketRegimeCode, float]:
    cleaned = {
        regime: float(value)
        for regime, value in scores.items()
        if regime is not MarketRegimeCode.UNKNOWN
        and isfinite(float(value))
        and float(value) > 0.0
    }
    total = sum(cleaned.values())
    if total <= 0.0:
        return MappingProxyType({})
    return MappingProxyType({regime: value / total for regime, value in cleaned.items()})


def condition_horizon_regime_scores(
    *,
    local_scores: Mapping[MarketRegimeCode, float],
    predecessor_scores: Mapping[MarketRegimeCode, float],
    predecessor_forecast: MarketRegimeFutureForecast,
    transition_prior_fraction_of_top: float,
) -> Tuple[Mapping[MarketRegimeCode, float], Mapping[str, Any]]:
    local = {regime: float(value) for regime, value in local_scores.items()}
    if any(not isfinite(value) or value < 0.0 for value in local.values()):
        raise ValueError("future_horizon_conditioning_local_score_invalid")
    fraction = float(transition_prior_fraction_of_top)
    if not 0.0 <= fraction < 1.0:
        raise ValueError("future_horizon_conditioning_fraction_invalid")

    base_diagnostics = {
        "schema_version": MARKET_REGIME_FUTURE_HORIZON_CONDITIONING_VERSION,
        "predecessor_horizon_sec": int(predecessor_forecast.target_horizon_sec),
        "predecessor_status": predecessor_forecast.status.value,
        "predecessor_label_copied": False,
        "distribution_context_only": True,
        "transition_prior_fraction_of_top": fraction,
        "conditioning_applied": False,
        "conditioning_weight": 0.0,
        "reason": "",
    }
    if predecessor_forecast.status is FutureForecastStatus.ABSTAIN:
        return MappingProxyType(local), MappingProxyType({
            **base_diagnostics,
            "reason": "predecessor_abstained",
        })

    margin = float(predecessor_forecast.metadata.get("normalized_score_margin") or 0.0)
    margin = max(0.0, min(margin, 1.0))
    predecessor_distribution = _normalized_distribution(predecessor_scores)
    local_total = sum(value for regime, value in local.items() if regime is not MarketRegimeCode.UNKNOWN)
    weight = fraction * margin
    if not predecessor_distribution or local_total <= 0.0 or weight <= 0.0:
        return MappingProxyType(local), MappingProxyType({
            **base_diagnostics,
            "reason": "predecessor_distribution_or_margin_unavailable",
        })

    conditioned = dict(local)
    for regime, probability in predecessor_distribution.items():
        conditioned[regime] = conditioned.get(regime, 0.0) + local_total * weight * probability
    return MappingProxyType(conditioned), MappingProxyType({
        **base_diagnostics,
        "conditioning_applied": True,
        "conditioning_weight": round(weight, 8),
        "predecessor_margin": round(margin, 8),
        "predecessor_distribution": {
            regime.value: round(probability, 8)
            for regime, probability in predecessor_distribution.items()
        },
        "reason": "predecessor_distribution_weighted_by_margin",
    })
