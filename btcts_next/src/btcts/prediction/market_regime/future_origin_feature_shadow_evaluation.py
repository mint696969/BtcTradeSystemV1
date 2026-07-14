# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_feature_shadow_evaluation.py
# desc: MR-F6.11 pure same-slot evaluation projection for all origin-feature shadow parameter candidates.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from types import MappingProxyType
from typing import Any, Mapping, Sequence, Tuple

from .contracts import MarketRegimeCode
from .features.current_l4_origin_feature_shadow_registry import (
    CurrentL4OriginFeatureShadowCandidate,
    build_default_current_l4_origin_feature_shadow_registry,
    validate_current_l4_origin_feature_shadow_registry,
)
from .features.current_l4_origin_features import calculate_current_l4_origin_features
from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from .future_mandatory_baseline_generators import (
    MandatoryBaselineEvidence,
    generate_mandatory_baselines,
)

MARKET_REGIME_ORIGIN_FEATURE_SHADOW_EVALUATION_VERSION = (
    "prediction.market_regime.origin_feature_shadow_evaluation.mr_f6_11.v1"
)


@dataclass(frozen=True)
class OriginFeatureShadowEvaluationSlot:
    slot_id: str
    prediction_origin: str
    source_snapshot_ref: str
    source_timestamp: str
    target_horizon_sec: int
    current_state: MarketRegimeCode
    previous_state: MarketRegimeCode
    recent_return: float | None
    realized_volatility_bps: float
    current_forecast_label_selection: MarketRegimeCode
    candle_rows: Sequence[Mapping[str, Any]]
    observed_state: MarketRegimeCode
    observation_available: bool
    evaluation_window_ref: str
    target_definition_version: str
    outcome_resolver_version: str

    def __post_init__(self) -> None:
        for name, value in (
            ("slot_id", self.slot_id),
            ("prediction_origin", self.prediction_origin),
            ("source_snapshot_ref", self.source_snapshot_ref),
            ("source_timestamp", self.source_timestamp),
            ("evaluation_window_ref", self.evaluation_window_ref),
            ("target_definition_version", self.target_definition_version),
            ("outcome_resolver_version", self.outcome_resolver_version),
        ):
            if not str(value).strip():
                raise ValueError(f"origin_feature_shadow_evaluation_identity_missing:{name}")
        origin_epoch = _epoch(self.prediction_origin, "prediction_origin")
        source_epoch = _epoch(self.source_timestamp, "source_timestamp")
        if source_epoch > origin_epoch:
            raise ValueError("origin_feature_shadow_evaluation_lookahead_detected")
        horizon = int(self.target_horizon_sec)
        if horizon not in FUTURE_MARKET_REGIME_HORIZONS_SEC:
            raise ValueError("origin_feature_shadow_evaluation_horizon_invalid")
        if self.target_definition_version != f"market_regime_target.{horizon}s.v1":
            raise ValueError("origin_feature_shadow_evaluation_target_definition_mismatch")
        for name, value in (
            ("current_state", self.current_state),
            ("previous_state", self.previous_state),
            ("current_forecast_label_selection", self.current_forecast_label_selection),
            ("observed_state", self.observed_state),
        ):
            if not isinstance(value, MarketRegimeCode):
                raise ValueError(f"origin_feature_shadow_evaluation_regime_invalid:{name}")
        if self.observation_available and self.observed_state is MarketRegimeCode.UNKNOWN:
            raise ValueError("origin_feature_shadow_evaluation_available_observation_unknown")
        if not self.observation_available and self.observed_state is not MarketRegimeCode.UNKNOWN:
            raise ValueError("origin_feature_shadow_evaluation_unavailable_observation_not_unknown")
        if self.recent_return is not None and not isfinite(float(self.recent_return)):
            raise ValueError("origin_feature_shadow_evaluation_recent_return_invalid")
        volatility = float(self.realized_volatility_bps)
        if not isfinite(volatility) or volatility < 0.0:
            raise ValueError("origin_feature_shadow_evaluation_realized_volatility_invalid")
        if isinstance(self.candle_rows, (str, bytes)) or not isinstance(self.candle_rows, Sequence):
            raise ValueError("origin_feature_shadow_evaluation_candle_rows_invalid")
        normalized_rows = tuple(dict(row) for row in self.candle_rows)
        if len(normalized_rows) < 60:
            raise ValueError("origin_feature_shadow_evaluation_candle_rows_insufficient")
        candle_epochs = tuple(
            _epoch(str(row.get("time_utc") or ""), f"candle_rows[{index}].time_utc")
            for index, row in enumerate(normalized_rows)
        )
        for previous, current in zip(candle_epochs, candle_epochs[1:]):
            if current <= previous:
                raise ValueError("origin_feature_shadow_evaluation_candle_time_not_increasing")
            if abs((current - previous) - 60.0) > 1e-6:
                raise ValueError("origin_feature_shadow_evaluation_candle_gap_detected")
        if candle_epochs[-1] > source_epoch:
            raise ValueError("origin_feature_shadow_evaluation_candle_lookahead_detected")
        object.__setattr__(self, "candle_rows", normalized_rows)

    @property
    def prediction_origin_epoch_sec(self) -> float:
        return _epoch(self.prediction_origin, "prediction_origin")

    @property
    def source_timestamp_epoch_sec(self) -> float:
        return _epoch(self.source_timestamp, "source_timestamp")

    @property
    def comparison_key(self) -> tuple[str, str, str, int, str, str]:
        return (
            self.prediction_origin,
            self.evaluation_window_ref,
            self.source_snapshot_ref,
            int(self.target_horizon_sec),
            self.target_definition_version,
            self.outcome_resolver_version,
        )


def _epoch(value: str, field: str) -> float:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"origin_feature_shadow_evaluation_timestamp_invalid:{field}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"origin_feature_shadow_evaluation_timezone_missing:{field}")
    result = parsed.astimezone(timezone.utc).timestamp()
    if result < 0.0:
        raise ValueError(f"origin_feature_shadow_evaluation_epoch_invalid:{field}")
    return result


def _candidate_projection(
    slot: OriginFeatureShadowEvaluationSlot,
    candidate: CurrentL4OriginFeatureShadowCandidate,
) -> Mapping[str, Any]:
    calculated = calculate_current_l4_origin_features(
        slot.candle_rows,
        parameters=candidate.parameters,
        realized_volatility_bps=slot.realized_volatility_bps,
    )
    evidence = MandatoryBaselineEvidence(
        prediction_origin=slot.prediction_origin,
        prediction_origin_epoch_sec=slot.prediction_origin_epoch_sec,
        source_snapshot_ref=slot.source_snapshot_ref,
        source_timestamp_epoch_sec=slot.source_timestamp_epoch_sec,
        target_horizon_sec=slot.target_horizon_sec,
        current_state=slot.current_state,
        previous_state=slot.previous_state,
        recent_return=slot.recent_return,
        fast_ma=float(calculated["fast_ma"]),
        slow_ma=float(calculated["slow_ma"]),
        realized_volatility=float(calculated["realized_volatility_bps"]) / 10000.0,
        low_volatility_threshold=float(calculated["low_volatility_threshold_bps"]) / 10000.0,
        high_volatility_threshold=float(calculated["high_volatility_threshold_bps"]) / 10000.0,
        current_forecast_label_selection=slot.current_forecast_label_selection,
    )
    predictions = generate_mandatory_baselines(evidence)
    prediction_rows = tuple(MappingProxyType({
        "baseline_id": item.baseline_id,
        "predicted_state": item.predicted_state,
        "probability_by_state": item.probability_by_state,
        "prediction_available": item.prediction_available,
        "reason_codes": item.reason_codes,
        "observed_state": slot.observed_state,
        "observation_available": slot.observation_available,
        "hit": (
            item.predicted_state is slot.observed_state
            if item.prediction_available and slot.observation_available
            else None
        ),
    }) for item in predictions)
    return MappingProxyType({
        "candidate_id": candidate.candidate_id,
        "parameter_set_id": candidate.parameters.parameter_set_id,
        "comparison_key": slot.comparison_key,
        "calculated_features": calculated,
        "baseline_predictions": prediction_rows,
        "selected_for_runtime": False,
        "live_parameter_apply_allowed": False,
        "auto_promotion_allowed": False,
        "canonical_replacement_allowed": False,
    })


def build_origin_feature_shadow_evaluation(
    *,
    slot: OriginFeatureShadowEvaluationSlot,
    candidates: Tuple[CurrentL4OriginFeatureShadowCandidate, ...] | None = None,
) -> Mapping[str, Any]:
    if not isinstance(slot, OriginFeatureShadowEvaluationSlot):
        raise ValueError("origin_feature_shadow_evaluation_slot_type_invalid")
    safe_candidates = (
        build_default_current_l4_origin_feature_shadow_registry()
        if candidates is None
        else tuple(candidates)
    )
    validation = validate_current_l4_origin_feature_shadow_registry(safe_candidates)
    if not validation["ok"]:
        raise ValueError(
            "origin_feature_shadow_evaluation_registry_invalid:"
            + ",".join(str(item) for item in validation["failures"])
        )
    projections = tuple(_candidate_projection(slot, candidate) for candidate in safe_candidates)
    comparison_keys = {item["comparison_key"] for item in projections}
    if comparison_keys != {slot.comparison_key}:
        raise RuntimeError("origin_feature_shadow_evaluation_same_window_contract_broken")
    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_FEATURE_SHADOW_EVALUATION_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "origin_feature_shadow_same_slot_evaluation",
        "slot_id": slot.slot_id,
        "comparison_key": slot.comparison_key,
        "candidate_count": len(projections),
        "candidate_projections": projections,
        "observation_available": slot.observation_available,
        "observed_state": slot.observed_state,
        "evaluation_ready": len(projections) == 8,
        "selection_performed": False,
        "selected_candidate_id": None,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "live_parameter_apply_allowed": False,
        "auto_promotion_allowed": False,
        "canonical_replacement_allowed": False,
    })
