# path: ./btcts_next/src/btcts/prediction/market_regime/future_mandatory_baseline_runner.py
# desc: Pure MR-F6.3 same-slot adapter joining one accepted candidate with six mandatory baselines.

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Tuple

from .contracts import MarketRegimeCode
from .future_mandatory_baseline_comparison import (
    MandatoryBaselineComparisonRow,
    build_mandatory_baseline_comparison,
)
from .future_mandatory_baseline_generators import (
    MandatoryBaselineEvidence,
    generate_mandatory_baselines,
)

MARKET_REGIME_MANDATORY_BASELINE_RUNNER_VERSION = (
    "prediction.market_regime.mandatory_baseline_runner.mr_f6_3.v1"
)


@dataclass(frozen=True)
class MandatoryBaselineEvaluationSlot:
    slot_id: str
    candidate_trace_id: str
    candidate_model_id: str
    prediction_origin: str
    prediction_origin_epoch_sec: float
    evaluation_window_ref: str
    source_snapshot_ref: str
    source_timestamp_epoch_sec: float
    target_horizon_sec: int
    target_definition_version: str
    outcome_resolver_version: str
    candidate_predicted_state: MarketRegimeCode
    candidate_probability_by_state: Mapping[MarketRegimeCode, float]
    candidate_prediction_available: bool
    observed_state: MarketRegimeCode
    observation_available: bool
    current_state: MarketRegimeCode
    previous_state: MarketRegimeCode
    recent_return: float | None
    fast_ma: float | None
    slow_ma: float | None
    realized_volatility: float | None
    low_volatility_threshold: float | None
    high_volatility_threshold: float | None
    current_forecast_label_selection: MarketRegimeCode
    observed_transition_at_epoch_sec: float | None = None
    candidate_detected_transition_at_epoch_sec: float | None = None
    candidate_predicted_state_duration_sec: float | None = None
    observed_state_duration_sec: float | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("slot_id", self.slot_id),
            ("candidate_trace_id", self.candidate_trace_id),
            ("candidate_model_id", self.candidate_model_id),
            ("prediction_origin", self.prediction_origin),
            ("evaluation_window_ref", self.evaluation_window_ref),
            ("source_snapshot_ref", self.source_snapshot_ref),
            ("target_definition_version", self.target_definition_version),
            ("outcome_resolver_version", self.outcome_resolver_version),
        ):
            if not str(value).strip():
                raise ValueError(f"mandatory_baseline_slot_identity_missing:{name}")
        for name, value in (
            ("prediction_origin_epoch_sec", self.prediction_origin_epoch_sec),
            ("source_timestamp_epoch_sec", self.source_timestamp_epoch_sec),
        ):
            if not isfinite(float(value)) or float(value) < 0.0:
                raise ValueError(f"mandatory_baseline_slot_timestamp_invalid:{name}")
        if float(self.source_timestamp_epoch_sec) > float(self.prediction_origin_epoch_sec):
            raise ValueError("mandatory_baseline_slot_lookahead_detected")
        horizon = int(self.target_horizon_sec)
        if self.target_definition_version != f"market_regime_target.{horizon}s.v1":
            raise ValueError("mandatory_baseline_slot_target_definition_mismatch")
        if self.candidate_prediction_available:
            if self.candidate_predicted_state is MarketRegimeCode.UNKNOWN:
                raise ValueError("mandatory_baseline_slot_available_candidate_unknown")
        elif self.candidate_predicted_state is not MarketRegimeCode.UNKNOWN:
            raise ValueError("mandatory_baseline_slot_unavailable_candidate_not_unknown")
        if self.observation_available:
            if self.observed_state is MarketRegimeCode.UNKNOWN:
                raise ValueError("mandatory_baseline_slot_available_observation_unknown")
        elif self.observed_state is not MarketRegimeCode.UNKNOWN:
            raise ValueError("mandatory_baseline_slot_unavailable_observation_not_unknown")
        object.__setattr__(self, "candidate_probability_by_state", MappingProxyType(dict(self.candidate_probability_by_state)))

    @property
    def evidence(self) -> MandatoryBaselineEvidence:
        return MandatoryBaselineEvidence(
            prediction_origin=self.prediction_origin,
            prediction_origin_epoch_sec=self.prediction_origin_epoch_sec,
            source_snapshot_ref=self.source_snapshot_ref,
            source_timestamp_epoch_sec=self.source_timestamp_epoch_sec,
            target_horizon_sec=self.target_horizon_sec,
            current_state=self.current_state,
            previous_state=self.previous_state,
            recent_return=self.recent_return,
            fast_ma=self.fast_ma,
            slow_ma=self.slow_ma,
            realized_volatility=self.realized_volatility,
            low_volatility_threshold=self.low_volatility_threshold,
            high_volatility_threshold=self.high_volatility_threshold,
            current_forecast_label_selection=self.current_forecast_label_selection,
        )


def _candidate_row(slot: MandatoryBaselineEvaluationSlot) -> MandatoryBaselineComparisonRow:
    return MandatoryBaselineComparisonRow(
        trace_id=slot.candidate_trace_id,
        candidate_id=slot.candidate_model_id,
        prediction_origin=slot.prediction_origin,
        evaluation_window_ref=slot.evaluation_window_ref,
        source_snapshot_ref=slot.source_snapshot_ref,
        target_horizon_sec=slot.target_horizon_sec,
        target_definition_version=slot.target_definition_version,
        outcome_resolver_version=slot.outcome_resolver_version,
        predicted_state=slot.candidate_predicted_state,
        observed_state=slot.observed_state,
        probability_by_state=slot.candidate_probability_by_state,
        observation_available=slot.observation_available,
        prediction_available=slot.candidate_prediction_available,
        avoidable_unknown=False,
        observed_transition_at_epoch_sec=slot.observed_transition_at_epoch_sec,
        detected_transition_at_epoch_sec=slot.candidate_detected_transition_at_epoch_sec,
        predicted_state_duration_sec=slot.candidate_predicted_state_duration_sec,
        observed_state_duration_sec=slot.observed_state_duration_sec,
    )


def _baseline_rows(slot: MandatoryBaselineEvaluationSlot) -> Tuple[MandatoryBaselineComparisonRow, ...]:
    rows = []
    for prediction in generate_mandatory_baselines(slot.evidence):
        rows.append(MandatoryBaselineComparisonRow(
            trace_id=f"{slot.slot_id}:{prediction.baseline_id}",
            candidate_id=prediction.baseline_id,
            prediction_origin=slot.prediction_origin,
            evaluation_window_ref=slot.evaluation_window_ref,
            source_snapshot_ref=slot.source_snapshot_ref,
            target_horizon_sec=slot.target_horizon_sec,
            target_definition_version=slot.target_definition_version,
            outcome_resolver_version=slot.outcome_resolver_version,
            predicted_state=prediction.predicted_state,
            observed_state=slot.observed_state,
            probability_by_state=prediction.probability_by_state,
            observation_available=slot.observation_available,
            prediction_available=prediction.prediction_available,
            avoidable_unknown=False,
            observed_transition_at_epoch_sec=slot.observed_transition_at_epoch_sec,
            detected_transition_at_epoch_sec=None,
            predicted_state_duration_sec=None,
            observed_state_duration_sec=slot.observed_state_duration_sec,
        ))
    return tuple(rows)


def build_rows_for_mandatory_baseline_slot(
    slot: MandatoryBaselineEvaluationSlot,
) -> Tuple[MandatoryBaselineComparisonRow, ...]:
    if not isinstance(slot, MandatoryBaselineEvaluationSlot):
        raise ValueError("mandatory_baseline_slot_type_invalid")
    return (_candidate_row(slot),) + _baseline_rows(slot)


def run_mandatory_baseline_comparison(
    *,
    slots: Iterable[MandatoryBaselineEvaluationSlot],
    candidate_model_id: str,
) -> Mapping[str, Any]:
    safe_slots = tuple(slots)
    if not safe_slots:
        raise ValueError("mandatory_baseline_runner_slots_empty")
    candidate_model_id = str(candidate_model_id).strip()
    if not candidate_model_id:
        raise ValueError("mandatory_baseline_runner_candidate_model_id_missing")
    slot_ids: set[str] = set()
    rows = []
    for slot in safe_slots:
        if not isinstance(slot, MandatoryBaselineEvaluationSlot):
            raise ValueError("mandatory_baseline_runner_slot_type_invalid")
        if slot.slot_id in slot_ids:
            raise ValueError(f"mandatory_baseline_runner_duplicate_slot_id:{slot.slot_id}")
        slot_ids.add(slot.slot_id)
        if slot.candidate_model_id != candidate_model_id:
            raise ValueError("mandatory_baseline_runner_candidate_model_mismatch")
        rows.extend(build_rows_for_mandatory_baseline_slot(slot))
    result = dict(build_mandatory_baseline_comparison(rows=rows, candidate_model_id=candidate_model_id))
    result.update({
        "runner_schema_version": MARKET_REGIME_MANDATORY_BASELINE_RUNNER_VERSION,
        "input_slot_count": len(safe_slots),
        "generated_row_count": len(rows),
        "rows_per_slot": 7,
    })
    return MappingProxyType(result)
