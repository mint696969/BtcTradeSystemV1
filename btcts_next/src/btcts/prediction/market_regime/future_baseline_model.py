# path: ./btcts_next/src/btcts/prediction/market_regime/future_baseline_model.py
# desc: Pure MR-F5.3 family-owned transparent shadow baseline for horizon-specific future MarketRegime forecasts. No reads, writes, UI, scheduler, broker, or AutoTrade behavior.

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import isfinite
from types import MappingProxyType
from typing import Mapping, Tuple

from .contracts import MarketRegimeCode
from .future_forecast_contract import (
    FutureForecastStatus,
    FutureTransitionStep,
    MarketRegimeFutureForecast,
)
from .future_target_definition import future_target_definitions_by_horizon
from .future_shadow_candidate_registry import BASELINE_CANDIDATE, FutureShadowCandidateParameters

MARKET_REGIME_FUTURE_BASELINE_MODEL_ID = "market_regime.future.transparent_baseline.shadow.v1"
MARKET_REGIME_FUTURE_BASELINE_LOGIC_VERSION = "prediction.market_regime.future_baseline_model.mr_f5_3.v1"
MARKET_REGIME_FUTURE_BASELINE_PARAMETER_SET_ID = "market_regime.future.transparent_baseline.params.v1"

_FUTURE_ALLOWED_TRANSITIONS: Mapping[MarketRegimeCode, Tuple[MarketRegimeCode, ...]] = MappingProxyType({
    MarketRegimeCode.UNKNOWN: tuple(code for code in MarketRegimeCode if code is not MarketRegimeCode.UNKNOWN),
    MarketRegimeCode.RANGE: (MarketRegimeCode.LOW_VOL_COMPRESSION, MarketRegimeCode.BREAKOUT, MarketRegimeCode.HIGH_VOL_CHOP),
    MarketRegimeCode.LOW_VOL_COMPRESSION: (MarketRegimeCode.RANGE, MarketRegimeCode.BREAKOUT),
    MarketRegimeCode.BREAKOUT: (MarketRegimeCode.UP_TREND, MarketRegimeCode.DOWN_TREND, MarketRegimeCode.HIGH_VOL_CHOP, MarketRegimeCode.RANGE),
    MarketRegimeCode.UP_TREND: (MarketRegimeCode.REVERSAL_WATCH, MarketRegimeCode.HIGH_VOL_CHOP, MarketRegimeCode.RANGE),
    MarketRegimeCode.DOWN_TREND: (MarketRegimeCode.REVERSAL_WATCH, MarketRegimeCode.HIGH_VOL_CHOP, MarketRegimeCode.RANGE),
    MarketRegimeCode.REVERSAL_WATCH: (MarketRegimeCode.RANGE, MarketRegimeCode.UP_TREND, MarketRegimeCode.DOWN_TREND, MarketRegimeCode.HIGH_VOL_CHOP),
    MarketRegimeCode.HIGH_VOL_CHOP: (MarketRegimeCode.RANGE, MarketRegimeCode.UP_TREND, MarketRegimeCode.DOWN_TREND, MarketRegimeCode.PANIC_SPIKE),
    MarketRegimeCode.PANIC_SPIKE: (MarketRegimeCode.HIGH_VOL_CHOP, MarketRegimeCode.RANGE),
})


@dataclass(frozen=True)
class FutureBaselineEvidence:
    origin_timestamp: str
    origin_current_state: MarketRegimeCode
    target_horizon_sec: int
    feature_snapshot_ref: str
    regime_scores: Mapping[MarketRegimeCode, float]
    available_feature_families: Tuple[str, ...]
    source_timestamp_epoch_sec: float
    origin_timestamp_epoch_sec: float
    invalidation_conditions: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.origin_current_state, MarketRegimeCode):
            raise ValueError("future_baseline_origin_current_state_invalid")
        definitions = future_target_definitions_by_horizon()
        if int(self.target_horizon_sec) not in definitions:
            raise ValueError(f"unsupported_future_horizon_sec:{self.target_horizon_sec}")
        if not self.origin_timestamp.strip() or not self.feature_snapshot_ref.strip():
            raise ValueError("future_baseline_identity_missing")
        if not isfinite(float(self.source_timestamp_epoch_sec)) or not isfinite(float(self.origin_timestamp_epoch_sec)):
            raise ValueError("future_baseline_timestamp_non_finite")
        if float(self.source_timestamp_epoch_sec) > float(self.origin_timestamp_epoch_sec):
            raise ValueError("lookahead_source_timestamp_after_origin")
        normalized = {}
        for regime, score in self.regime_scores.items():
            if not isinstance(regime, MarketRegimeCode):
                raise ValueError("future_baseline_regime_score_key_invalid")
            value = float(score)
            if not isfinite(value) or value < 0.0:
                raise ValueError("future_baseline_regime_score_invalid")
            normalized[regime] = value
        object.__setattr__(self, "regime_scores", MappingProxyType(normalized))
        raw_families = tuple(str(item).strip() for item in self.available_feature_families)
        if any(not item for item in raw_families):
            raise ValueError("future_baseline_feature_family_invalid")
        families = tuple(dict.fromkeys(raw_families))
        object.__setattr__(self, "available_feature_families", families)


def _transition_prior_runner_up(
    *,
    origin: MarketRegimeCode,
    observed_top: MarketRegimeCode,
) -> MarketRegimeCode | None:
    for candidate in _FUTURE_ALLOWED_TRANSITIONS.get(origin, ()):
        if candidate is not observed_top:
            return candidate
    return None


def _shortest_transition_path(origin: MarketRegimeCode, target: MarketRegimeCode) -> Tuple[MarketRegimeCode, ...]:
    if origin is target:
        return (target,)
    queue = deque([(origin, ())])
    visited = {origin}
    while queue:
        node, path = queue.popleft()
        for nxt in _FUTURE_ALLOWED_TRANSITIONS.get(node, ()):
            if nxt in visited:
                continue
            next_path = path + (nxt,)
            if nxt is target:
                return next_path
            visited.add(nxt)
            queue.append((nxt, next_path))
    return ()


def _abstain(
    evidence: FutureBaselineEvidence,
    reason: str,
    blockers: Tuple[str, ...],
    *,
    candidate: FutureShadowCandidateParameters,
) -> MarketRegimeFutureForecast:
    definition = future_target_definitions_by_horizon()[int(evidence.target_horizon_sec)]
    return MarketRegimeFutureForecast(
        origin_timestamp=evidence.origin_timestamp,
        origin_current_state=evidence.origin_current_state,
        target_horizon_sec=evidence.target_horizon_sec,
        predicted_future_state=MarketRegimeCode.UNKNOWN,
        status=FutureForecastStatus.ABSTAIN,
        transition_path_candidate=(),
        raw_model_score_or_probability=None,
        feature_snapshot_ref=evidence.feature_snapshot_ref,
        model_id=MARKET_REGIME_FUTURE_BASELINE_MODEL_ID,
        logic_version=MARKET_REGIME_FUTURE_BASELINE_LOGIC_VERSION,
        parameter_set_id=candidate.parameter_set_id,
        target_definition_version=definition.target_definition_version,
        invalidation_conditions=tuple(dict.fromkeys(evidence.invalidation_conditions + blockers)),
        abstain_reason=reason,
        metadata={"shadow_only": True, "canonical_replacement": False, "blockers": list(blockers)},
    )


def forecast_future_market_regime_baseline(
    evidence: FutureBaselineEvidence,
    *,
    candidate: FutureShadowCandidateParameters = BASELINE_CANDIDATE,
) -> MarketRegimeFutureForecast:
    definition = future_target_definitions_by_horizon()[int(evidence.target_horizon_sec)]
    available = set(evidence.available_feature_families)
    missing_required = tuple(sorted(set(definition.required_feature_families) - available))
    if missing_required:
        return _abstain(evidence, "required_feature_family_missing", tuple(f"missing_required_feature:{item}" for item in missing_required), candidate=candidate)

    ranked = sorted(
        (
            (regime, score)
            for regime, score in evidence.regime_scores.items()
            if regime is not MarketRegimeCode.UNKNOWN and score > 0.0
        ),
        key=lambda item: (-item[1], item[0].value),
    )
    transition_prior_applied = False
    transition_prior_regime = None
    transition_prior_score = 0.0
    if len(ranked) == 1:
        observed_top_regime, observed_top_score = ranked[0]
        prior_regime = _transition_prior_runner_up(
            origin=evidence.origin_current_state,
            observed_top=observed_top_regime,
        )
        if prior_regime is not None and observed_top_score > 0.0:
            transition_prior_score = observed_top_score * float(candidate.transition_prior_fraction_of_top)
            ranked.append((prior_regime, transition_prior_score))
            ranked.sort(key=lambda item: (-item[1], item[0].value))
            transition_prior_applied = True
            transition_prior_regime = prior_regime
    if len(ranked) < 2:
        return _abstain(evidence, "insufficient_ranked_regime_candidates", ("ranked_candidate_count_below_2",), candidate=candidate)

    (top_regime, top_score), (_, runner_score) = ranked[:2]
    total_positive = sum(score for _, score in ranked if score > 0.0)
    normalized_top = 0.0 if total_positive <= 0.0 else top_score / total_positive
    normalized_runner = 0.0 if total_positive <= 0.0 else runner_score / total_positive
    margin = normalized_top - normalized_runner

    minimum_top, minimum_margin = candidate.thresholds_for_horizon(evidence.target_horizon_sec)
    if normalized_top < minimum_top:
        return _abstain(evidence, "top_score_below_minimum", (f"normalized_top_score:{normalized_top:.4f}",), candidate=candidate)
    if margin < minimum_margin:
        return _abstain(evidence, "score_margin_below_minimum", (f"normalized_score_margin:{margin:.4f}",), candidate=candidate)

    path = _shortest_transition_path(evidence.origin_current_state, top_regime)
    if not path:
        return _abstain(evidence, "future_transition_path_unavailable", ("transition_graph_disconnected",), candidate=candidate)

    step_count = len(path)
    steps = tuple(
        FutureTransitionStep(
            regime=regime,
            earliest_offset_sec=max(1, int(evidence.target_horizon_sec * index / step_count)),
            reason_codes=("transparent_score_rank", "allowed_transition_path"),
        )
        for index, regime in enumerate(path, start=1)
    )
    return MarketRegimeFutureForecast(
        origin_timestamp=evidence.origin_timestamp,
        origin_current_state=evidence.origin_current_state,
        target_horizon_sec=evidence.target_horizon_sec,
        predicted_future_state=top_regime,
        status=FutureForecastStatus.FORECAST,
        transition_path_candidate=steps,
        raw_model_score_or_probability=round(normalized_top, 6),
        feature_snapshot_ref=evidence.feature_snapshot_ref,
        model_id=MARKET_REGIME_FUTURE_BASELINE_MODEL_ID,
        logic_version=MARKET_REGIME_FUTURE_BASELINE_LOGIC_VERSION,
        parameter_set_id=candidate.parameter_set_id,
        target_definition_version=definition.target_definition_version,
        invalidation_conditions=tuple(dict.fromkeys(evidence.invalidation_conditions + ("required_feature_becomes_unavailable", "source_timestamp_after_origin"))),
        metadata={
            "shadow_only": True,
            "canonical_replacement": False,
            "normalized_top_score": round(normalized_top, 6),
            "normalized_runner_score": round(normalized_runner, 6),
            "normalized_score_margin": round(margin, 6),
            "available_feature_families": list(evidence.available_feature_families),
            "candidate_registry_state": candidate.registry_state,
            "transition_prior_applied": transition_prior_applied,
            "transition_prior_regime": transition_prior_regime.value if transition_prior_regime is not None else None,
            "transition_prior_score": round(transition_prior_score, 6) if transition_prior_applied else 0.0,
            "transition_prior_fraction_of_top": candidate.transition_prior_fraction_of_top,
        },
    )
