# path: ./btcts_next/src/btcts/prediction/market_regime/future_mandatory_baseline_comparison.py
# desc: Pure MR-F6.1 same-window mandatory baseline comparison contract and metrics. No reads, writes, UI, scheduler, broker, promotion, or live apply behavior.

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import isfinite, log
from statistics import mean
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence, Tuple

from .contracts import MarketRegimeCode
from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC

MARKET_REGIME_MANDATORY_BASELINE_COMPARISON_VERSION = (
    "prediction.market_regime.mandatory_baseline_comparison.mr_f6_1.v1"
)

MANDATORY_BASELINE_IDS: Tuple[str, ...] = (
    "always_range",
    "last_state_persists",
    "recent_return_sign",
    "simple_ma_slope",
    "simple_volatility_threshold",
    "current_forecast_label_selection",
)

_EPSILON = 1e-15


@dataclass(frozen=True)
class MandatoryBaselineComparisonRow:
    trace_id: str
    candidate_id: str
    prediction_origin: str
    evaluation_window_ref: str
    source_snapshot_ref: str
    target_horizon_sec: int
    target_definition_version: str
    outcome_resolver_version: str
    predicted_state: MarketRegimeCode
    observed_state: MarketRegimeCode
    probability_by_state: Mapping[MarketRegimeCode, float]
    observation_available: bool
    prediction_available: bool
    avoidable_unknown: bool = False
    observed_transition_at_epoch_sec: float | None = None
    detected_transition_at_epoch_sec: float | None = None
    predicted_state_duration_sec: float | None = None
    observed_state_duration_sec: float | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("trace_id", self.trace_id),
            ("candidate_id", self.candidate_id),
            ("prediction_origin", self.prediction_origin),
            ("evaluation_window_ref", self.evaluation_window_ref),
            ("source_snapshot_ref", self.source_snapshot_ref),
            ("target_definition_version", self.target_definition_version),
            ("outcome_resolver_version", self.outcome_resolver_version),
        ):
            if not str(value).strip():
                raise ValueError(f"mandatory_baseline_comparison_identity_missing:{name}")
        horizon = int(self.target_horizon_sec)
        if horizon not in FUTURE_MARKET_REGIME_HORIZONS_SEC:
            raise ValueError(f"mandatory_baseline_comparison_horizon_invalid:{horizon}")
        if self.target_definition_version != f"market_regime_target.{horizon}s.v1":
            raise ValueError("mandatory_baseline_comparison_target_definition_mismatch")
        if not isinstance(self.predicted_state, MarketRegimeCode):
            raise ValueError("mandatory_baseline_comparison_predicted_state_invalid")
        if not isinstance(self.observed_state, MarketRegimeCode):
            raise ValueError("mandatory_baseline_comparison_observed_state_invalid")
        normalized: dict[MarketRegimeCode, float] = {}
        total = 0.0
        for state, raw_value in self.probability_by_state.items():
            if not isinstance(state, MarketRegimeCode):
                raise ValueError("mandatory_baseline_comparison_probability_key_invalid")
            if state is MarketRegimeCode.UNKNOWN:
                raise ValueError("mandatory_baseline_comparison_unknown_probability_not_allowed")
            value = float(raw_value)
            if not isfinite(value) or value < 0.0 or value > 1.0:
                raise ValueError("mandatory_baseline_comparison_probability_invalid")
            normalized[state] = value
            total += value
        if self.prediction_available:
            if self.predicted_state is MarketRegimeCode.UNKNOWN:
                raise ValueError("mandatory_baseline_comparison_available_prediction_unknown")
            if not normalized:
                raise ValueError("mandatory_baseline_comparison_probability_missing")
            if abs(total - 1.0) > 1e-6:
                raise ValueError("mandatory_baseline_comparison_probability_sum_invalid")
            predicted_probability = normalized.get(self.predicted_state)
            if predicted_probability is None:
                raise ValueError("mandatory_baseline_comparison_predicted_state_probability_missing")
            if predicted_probability + 1e-12 < max(normalized.values()):
                raise ValueError("mandatory_baseline_comparison_predicted_state_not_argmax")
        elif self.predicted_state is not MarketRegimeCode.UNKNOWN:
            raise ValueError("mandatory_baseline_comparison_unavailable_prediction_not_unknown")
        if self.observation_available and self.observed_state is MarketRegimeCode.UNKNOWN:
            raise ValueError("mandatory_baseline_comparison_available_observation_unknown")
        if not self.observation_available and self.observed_state is not MarketRegimeCode.UNKNOWN:
            raise ValueError("mandatory_baseline_comparison_unavailable_observation_not_unknown")
        if self.avoidable_unknown and self.prediction_available:
            raise ValueError("mandatory_baseline_comparison_avoidable_unknown_with_prediction")
        for name, value in (
            ("observed_transition_at_epoch_sec", self.observed_transition_at_epoch_sec),
            ("detected_transition_at_epoch_sec", self.detected_transition_at_epoch_sec),
            ("predicted_state_duration_sec", self.predicted_state_duration_sec),
            ("observed_state_duration_sec", self.observed_state_duration_sec),
        ):
            if value is not None and (not isfinite(float(value)) or float(value) < 0.0):
                raise ValueError(f"mandatory_baseline_comparison_non_finite_or_negative:{name}")
        if (
            self.observed_transition_at_epoch_sec is not None
            and self.detected_transition_at_epoch_sec is not None
            and float(self.detected_transition_at_epoch_sec) < float(self.observed_transition_at_epoch_sec)
        ):
            raise ValueError("mandatory_baseline_comparison_transition_detection_precedes_observation")
        object.__setattr__(self, "probability_by_state", MappingProxyType(normalized))

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


def _safe_div(numerator: float, denominator: float) -> float | None:
    return None if denominator <= 0.0 else numerator / denominator


def _round(value: float | None) -> float | None:
    return None if value is None else round(float(value), 6)


def _confusion_metrics(rows: Sequence[MandatoryBaselineComparisonRow]) -> Mapping[str, float | None]:
    labels = tuple(code for code in MarketRegimeCode if code is not MarketRegimeCode.UNKNOWN)
    correct = sum(1 for row in rows if row.predicted_state is row.observed_state)
    recalls: list[float] = []
    f1_values: list[float] = []
    for label in labels:
        tp = sum(1 for row in rows if row.predicted_state is label and row.observed_state is label)
        fp = sum(1 for row in rows if row.predicted_state is label and row.observed_state is not label)
        fn = sum(1 for row in rows if row.predicted_state is not label and row.observed_state is label)
        observed_count = tp + fn
        predicted_count = tp + fp
        if observed_count:
            recalls.append(tp / observed_count)
        precision = _safe_div(tp, predicted_count)
        recall = _safe_div(tp, observed_count)
        if precision is not None and recall is not None:
            f1_values.append(0.0 if precision + recall == 0.0 else 2.0 * precision * recall / (precision + recall))
    return MappingProxyType({
        "accuracy": _round(_safe_div(correct, len(rows))),
        "balanced_accuracy": _round(mean(recalls) if recalls else None),
        "macro_f1": _round(mean(f1_values) if f1_values else None),
    })


def _probability_metrics(rows: Sequence[MandatoryBaselineComparisonRow]) -> Mapping[str, float | None]:
    labels = tuple(code for code in MarketRegimeCode if code is not MarketRegimeCode.UNKNOWN)
    brier_values: list[float] = []
    log_losses: list[float] = []
    confidence_pairs: list[tuple[float, float]] = []
    for row in rows:
        probabilities = row.probability_by_state
        brier_values.append(sum((probabilities.get(label, 0.0) - (1.0 if row.observed_state is label else 0.0)) ** 2 for label in labels))
        observed_probability = max(_EPSILON, min(1.0, probabilities.get(row.observed_state, 0.0)))
        log_losses.append(-log(observed_probability))
        confidence = max(probabilities.values())
        confidence_pairs.append((confidence, 1.0 if row.predicted_state is row.observed_state else 0.0))
    bins: dict[int, list[tuple[float, float]]] = defaultdict(list)
    for confidence, hit in confidence_pairs:
        bins[min(9, int(confidence * 10.0))].append((confidence, hit))
    ece = 0.0
    for values in bins.values():
        bin_confidence = mean(item[0] for item in values)
        bin_accuracy = mean(item[1] for item in values)
        ece += len(values) / len(confidence_pairs) * abs(bin_accuracy - bin_confidence)
    return MappingProxyType({
        "brier_score": _round(mean(brier_values) if brier_values else None),
        "log_loss": _round(mean(log_losses) if log_losses else None),
        "expected_calibration_error": _round(ece if confidence_pairs else None),
    })


def _sequence_metrics(rows: Sequence[MandatoryBaselineComparisonRow]) -> Mapping[str, float | None]:
    ordered = sorted(rows, key=lambda item: (item.target_horizon_sec, item.prediction_origin, item.trace_id))
    transitions = 0
    previous_by_horizon: dict[int, MarketRegimeCode] = {}
    for row in ordered:
        previous = previous_by_horizon.get(row.target_horizon_sec)
        if previous is not None and previous is not row.predicted_state:
            transitions += 1
        previous_by_horizon[row.target_horizon_sec] = row.predicted_state
    possible = max(0, len(ordered) - len(previous_by_horizon))
    delays = [
        float(row.detected_transition_at_epoch_sec) - float(row.observed_transition_at_epoch_sec)
        for row in rows
        if row.detected_transition_at_epoch_sec is not None and row.observed_transition_at_epoch_sec is not None
    ]
    duration_errors = [
        abs(float(row.predicted_state_duration_sec) - float(row.observed_state_duration_sec))
        / max(float(row.observed_state_duration_sec), 1.0)
        for row in rows
        if row.predicted_state_duration_sec is not None and row.observed_state_duration_sec is not None
    ]
    return MappingProxyType({
        "transition_detection_delay_sec": _round(mean(delays) if delays else None),
        "state_churn_rate": _round(_safe_div(transitions, possible)),
        "regime_duration_consistency": _round(1.0 - min(1.0, mean(duration_errors)) if duration_errors else None),
    })


def _candidate_summary(candidate_id: str, rows: Sequence[MandatoryBaselineComparisonRow], total_slots: int) -> Mapping[str, Any]:
    observed_rows = [row for row in rows if row.observation_available]
    scored_rows = [row for row in observed_rows if row.prediction_available]
    unknown_rows = [row for row in observed_rows if not row.prediction_available]
    payload: dict[str, Any] = {
        "candidate_id": candidate_id,
        "row_count": len(rows),
        "observed_rows": len(observed_rows),
        "scored_rows": len(scored_rows),
        "coverage_rate": _round(_safe_div(len(scored_rows), len(observed_rows))),
        "unknown_rate": _round(_safe_div(len(unknown_rows), len(observed_rows))),
        "avoidable_unknown_rate": _round(_safe_div(sum(1 for row in unknown_rows if row.avoidable_unknown), len(observed_rows))),
        "same_window_slot_coverage_rate": _round(_safe_div(len(rows), total_slots)),
    }
    payload.update(_confusion_metrics(scored_rows))
    payload.update(_probability_metrics(scored_rows))
    payload.update(_sequence_metrics(scored_rows))
    return MappingProxyType(payload)


def summarize_mandatory_baseline_candidate(
    *,
    candidate_id: str,
    rows: Iterable[MandatoryBaselineComparisonRow],
    total_slots: int,
) -> Mapping[str, Any]:
    """Public pure summary surface reused by MR-F8 candidate comparisons."""
    safe_id = str(candidate_id).strip()
    if not safe_id:
        raise ValueError("mandatory_baseline_summary_candidate_id_missing")
    safe_rows = tuple(rows)
    if any(not isinstance(row, MandatoryBaselineComparisonRow) for row in safe_rows):
        raise ValueError("mandatory_baseline_summary_row_type_invalid")
    if any(row.candidate_id != safe_id for row in safe_rows):
        raise ValueError("mandatory_baseline_summary_candidate_id_mismatch")
    if int(total_slots) <= 0:
        raise ValueError("mandatory_baseline_summary_total_slots_invalid")
    return _candidate_summary(safe_id, safe_rows, int(total_slots))


def build_mandatory_baseline_comparison(
    *,
    rows: Iterable[MandatoryBaselineComparisonRow],
    candidate_model_id: str,
    required_baseline_ids: Sequence[str] = MANDATORY_BASELINE_IDS,
) -> Mapping[str, Any]:
    candidate_model_id = str(candidate_model_id).strip()
    if not candidate_model_id:
        raise ValueError("mandatory_baseline_comparison_candidate_model_id_missing")
    required = tuple(dict.fromkeys(str(item).strip() for item in required_baseline_ids))
    if not required or any(not item for item in required):
        raise ValueError("mandatory_baseline_comparison_required_baseline_invalid")
    safe_rows = tuple(rows)
    if not safe_rows:
        raise ValueError("mandatory_baseline_comparison_rows_empty")
    seen_trace_ids: set[str] = set()
    by_candidate: dict[str, list[MandatoryBaselineComparisonRow]] = defaultdict(list)
    slot_sets: dict[str, set[tuple[str, str, str, int, str, str]]] = defaultdict(set)
    for row in safe_rows:
        if not isinstance(row, MandatoryBaselineComparisonRow):
            raise ValueError("mandatory_baseline_comparison_row_type_invalid")
        if row.trace_id in seen_trace_ids:
            raise ValueError(f"mandatory_baseline_comparison_duplicate_trace_id:{row.trace_id}")
        seen_trace_ids.add(row.trace_id)
        if row.comparison_key in slot_sets[row.candidate_id]:
            raise ValueError(f"mandatory_baseline_comparison_duplicate_slot:{row.candidate_id}")
        by_candidate[row.candidate_id].append(row)
        slot_sets[row.candidate_id].add(row.comparison_key)

    expected_ids = (candidate_model_id,) + required
    missing_candidates = tuple(item for item in expected_ids if item not in by_candidate)
    extra_candidates = tuple(sorted(set(by_candidate) - set(expected_ids)))
    reference_slots = slot_sets.get(candidate_model_id, set())
    window_mismatches = tuple(
        candidate_id for candidate_id in expected_ids
        if candidate_id in slot_sets and slot_sets[candidate_id] != reference_slots
    )
    comparison_ready = not missing_candidates and not extra_candidates and bool(reference_slots) and not window_mismatches
    blockers: list[str] = []
    if missing_candidates:
        blockers.append("mandatory_baseline_missing")
    if extra_candidates:
        blockers.append("unexpected_candidate_present")
    if not reference_slots:
        blockers.append("candidate_window_empty")
    if window_mismatches:
        blockers.append("same_window_contract_mismatch")

    summaries = tuple(
        _candidate_summary(candidate_id, tuple(by_candidate[candidate_id]), len(reference_slots))
        for candidate_id in expected_ids
        if candidate_id in by_candidate
    )
    return MappingProxyType({
        "schema_version": MARKET_REGIME_MANDATORY_BASELINE_COMPARISON_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "mandatory_simple_baseline_comparison",
        "candidate_model_id": candidate_model_id,
        "required_baseline_ids": required,
        "present_candidate_ids": tuple(sorted(by_candidate)),
        "comparison_slot_count": len(reference_slots),
        "comparison_ready": comparison_ready,
        "comparison_blockers": tuple(blockers),
        "missing_candidate_ids": missing_candidates,
        "extra_candidate_ids": extra_candidates,
        "window_mismatch_candidate_ids": window_mismatches,
        "candidate_summaries": summaries,
        "safety": MappingProxyType({
            "read_only_inputs": True,
            "writes_dhot": False,
            "shadow_only": True,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "human_gate_required": True,
        }),
    })
