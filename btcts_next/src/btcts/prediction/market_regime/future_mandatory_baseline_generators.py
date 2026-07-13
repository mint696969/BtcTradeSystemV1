# path: ./btcts_next/src/btcts/prediction/market_regime/future_mandatory_baseline_generators.py
# desc: Pure deterministic MR-F6.2 mandatory baseline generators from one no-lookahead evidence contract.

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from types import MappingProxyType
from typing import Mapping, Tuple

from .contracts import MarketRegimeCode
from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC
from .future_mandatory_baseline_comparison import MANDATORY_BASELINE_IDS

MARKET_REGIME_MANDATORY_BASELINE_GENERATORS_VERSION = (
    "prediction.market_regime.mandatory_baseline_generators.mr_f6_2.v1"
)


@dataclass(frozen=True)
class MandatoryBaselineEvidence:
    prediction_origin: str
    prediction_origin_epoch_sec: float
    source_snapshot_ref: str
    source_timestamp_epoch_sec: float
    target_horizon_sec: int
    current_state: MarketRegimeCode
    previous_state: MarketRegimeCode
    recent_return: float | None
    fast_ma: float | None
    slow_ma: float | None
    realized_volatility: float | None
    low_volatility_threshold: float | None
    high_volatility_threshold: float | None
    current_forecast_label_selection: MarketRegimeCode

    def __post_init__(self) -> None:
        if not self.prediction_origin.strip() or not self.source_snapshot_ref.strip():
            raise ValueError("mandatory_baseline_evidence_identity_missing")
        for name, value in (
            ("prediction_origin_epoch_sec", self.prediction_origin_epoch_sec),
            ("source_timestamp_epoch_sec", self.source_timestamp_epoch_sec),
        ):
            if not isfinite(float(value)) or float(value) < 0.0:
                raise ValueError(f"mandatory_baseline_evidence_timestamp_invalid:{name}")
        if float(self.source_timestamp_epoch_sec) > float(self.prediction_origin_epoch_sec):
            raise ValueError("mandatory_baseline_evidence_lookahead_detected")
        if int(self.target_horizon_sec) not in FUTURE_MARKET_REGIME_HORIZONS_SEC:
            raise ValueError("mandatory_baseline_evidence_horizon_invalid")
        for name, value in (
            ("current_state", self.current_state),
            ("previous_state", self.previous_state),
            ("current_forecast_label_selection", self.current_forecast_label_selection),
        ):
            if not isinstance(value, MarketRegimeCode):
                raise ValueError(f"mandatory_baseline_evidence_regime_invalid:{name}")
        for name, value in (
            ("recent_return", self.recent_return),
            ("fast_ma", self.fast_ma),
            ("slow_ma", self.slow_ma),
            ("realized_volatility", self.realized_volatility),
            ("low_volatility_threshold", self.low_volatility_threshold),
            ("high_volatility_threshold", self.high_volatility_threshold),
        ):
            if value is not None and not isfinite(float(value)):
                raise ValueError(f"mandatory_baseline_evidence_non_finite:{name}")
        if self.low_volatility_threshold is not None and float(self.low_volatility_threshold) < 0.0:
            raise ValueError("mandatory_baseline_evidence_low_volatility_threshold_negative")
        if self.high_volatility_threshold is not None and float(self.high_volatility_threshold) < 0.0:
            raise ValueError("mandatory_baseline_evidence_high_volatility_threshold_negative")
        if (
            self.low_volatility_threshold is not None
            and self.high_volatility_threshold is not None
            and float(self.low_volatility_threshold) > float(self.high_volatility_threshold)
        ):
            raise ValueError("mandatory_baseline_evidence_volatility_threshold_order_invalid")


@dataclass(frozen=True)
class MandatoryBaselinePrediction:
    baseline_id: str
    predicted_state: MarketRegimeCode
    probability_by_state: Mapping[MarketRegimeCode, float]
    prediction_available: bool
    reason_codes: Tuple[str, ...]

    def __post_init__(self) -> None:
        if self.baseline_id not in MANDATORY_BASELINE_IDS:
            raise ValueError("mandatory_baseline_prediction_id_invalid")
        if not isinstance(self.predicted_state, MarketRegimeCode):
            raise ValueError("mandatory_baseline_prediction_state_invalid")
        normalized: dict[MarketRegimeCode, float] = {}
        total = 0.0
        for state, raw in self.probability_by_state.items():
            if not isinstance(state, MarketRegimeCode) or state is MarketRegimeCode.UNKNOWN:
                raise ValueError("mandatory_baseline_prediction_probability_state_invalid")
            value = float(raw)
            if not isfinite(value) or value < 0.0 or value > 1.0:
                raise ValueError("mandatory_baseline_prediction_probability_invalid")
            normalized[state] = value
            total += value
        if self.prediction_available:
            if self.predicted_state is MarketRegimeCode.UNKNOWN:
                raise ValueError("mandatory_baseline_prediction_available_unknown")
            if abs(total - 1.0) > 1e-6:
                raise ValueError("mandatory_baseline_prediction_probability_sum_invalid")
            if self.predicted_state not in normalized:
                raise ValueError("mandatory_baseline_prediction_selected_probability_missing")
            if normalized[self.predicted_state] + 1e-12 < max(normalized.values()):
                raise ValueError("mandatory_baseline_prediction_selected_not_argmax")
        else:
            if self.predicted_state is not MarketRegimeCode.UNKNOWN or normalized:
                raise ValueError("mandatory_baseline_prediction_unavailable_contract_invalid")
        if not self.reason_codes or any(not str(item).strip() for item in self.reason_codes):
            raise ValueError("mandatory_baseline_prediction_reason_missing")
        object.__setattr__(self, "probability_by_state", MappingProxyType(normalized))
        object.__setattr__(self, "reason_codes", tuple(dict.fromkeys(self.reason_codes)))


def _available(baseline_id: str, state: MarketRegimeCode, confidence: float, reason: str) -> MandatoryBaselinePrediction:
    confidence = max(0.5, min(float(confidence), 1.0))
    alternatives = tuple(code for code in MarketRegimeCode if code not in {MarketRegimeCode.UNKNOWN, state})
    remainder = 1.0 - confidence
    probabilities = {state: confidence}
    if alternatives and remainder > 0.0:
        share = remainder / len(alternatives)
        probabilities.update({item: share for item in alternatives})
    return MandatoryBaselinePrediction(
        baseline_id=baseline_id,
        predicted_state=state,
        probability_by_state=probabilities,
        prediction_available=True,
        reason_codes=(reason,),
    )


def _unavailable(baseline_id: str, reason: str) -> MandatoryBaselinePrediction:
    return MandatoryBaselinePrediction(
        baseline_id=baseline_id,
        predicted_state=MarketRegimeCode.UNKNOWN,
        probability_by_state={},
        prediction_available=False,
        reason_codes=(reason,),
    )


def _always_range(_: MandatoryBaselineEvidence) -> MandatoryBaselinePrediction:
    return _available("always_range", MarketRegimeCode.RANGE, 1.0, "constant_range")


def _last_state_persists(evidence: MandatoryBaselineEvidence) -> MandatoryBaselinePrediction:
    state = evidence.current_state
    if state is MarketRegimeCode.UNKNOWN:
        state = evidence.previous_state
    if state is MarketRegimeCode.UNKNOWN:
        return _unavailable("last_state_persists", "current_and_previous_state_unknown")
    return _available("last_state_persists", state, 1.0, "last_known_state_persists")


def _recent_return_sign(evidence: MandatoryBaselineEvidence) -> MandatoryBaselinePrediction:
    if evidence.recent_return is None:
        return _unavailable("recent_return_sign", "recent_return_missing")
    value = float(evidence.recent_return)
    if value > 0.0:
        return _available("recent_return_sign", MarketRegimeCode.UP_TREND, 0.6, "recent_return_positive")
    if value < 0.0:
        return _available("recent_return_sign", MarketRegimeCode.DOWN_TREND, 0.6, "recent_return_negative")
    return _available("recent_return_sign", MarketRegimeCode.RANGE, 0.6, "recent_return_flat")


def _simple_ma_slope(evidence: MandatoryBaselineEvidence) -> MandatoryBaselinePrediction:
    if evidence.fast_ma is None or evidence.slow_ma is None:
        return _unavailable("simple_ma_slope", "moving_average_missing")
    fast = float(evidence.fast_ma)
    slow = float(evidence.slow_ma)
    if fast > slow:
        return _available("simple_ma_slope", MarketRegimeCode.UP_TREND, 0.6, "fast_ma_above_slow_ma")
    if fast < slow:
        return _available("simple_ma_slope", MarketRegimeCode.DOWN_TREND, 0.6, "fast_ma_below_slow_ma")
    return _available("simple_ma_slope", MarketRegimeCode.RANGE, 0.6, "moving_averages_equal")


def _simple_volatility_threshold(evidence: MandatoryBaselineEvidence) -> MandatoryBaselinePrediction:
    if (
        evidence.realized_volatility is None
        or evidence.low_volatility_threshold is None
        or evidence.high_volatility_threshold is None
    ):
        return _unavailable("simple_volatility_threshold", "volatility_input_missing")
    volatility = float(evidence.realized_volatility)
    low = float(evidence.low_volatility_threshold)
    high = float(evidence.high_volatility_threshold)
    if volatility <= low:
        return _available("simple_volatility_threshold", MarketRegimeCode.LOW_VOL_COMPRESSION, 0.6, "volatility_at_or_below_low_threshold")
    if volatility >= high:
        return _available("simple_volatility_threshold", MarketRegimeCode.HIGH_VOL_CHOP, 0.6, "volatility_at_or_above_high_threshold")
    return _available("simple_volatility_threshold", MarketRegimeCode.RANGE, 0.6, "volatility_between_thresholds")


def _current_forecast_label_selection(evidence: MandatoryBaselineEvidence) -> MandatoryBaselinePrediction:
    state = evidence.current_forecast_label_selection
    if state is MarketRegimeCode.UNKNOWN:
        return _unavailable("current_forecast_label_selection", "legacy_forecast_label_selection_unknown")
    return _available("current_forecast_label_selection", state, 1.0, "legacy_forecast_label_selection")


def generate_mandatory_baselines(evidence: MandatoryBaselineEvidence) -> Tuple[MandatoryBaselinePrediction, ...]:
    if not isinstance(evidence, MandatoryBaselineEvidence):
        raise ValueError("mandatory_baseline_evidence_type_invalid")
    predictions = (
        _always_range(evidence),
        _last_state_persists(evidence),
        _recent_return_sign(evidence),
        _simple_ma_slope(evidence),
        _simple_volatility_threshold(evidence),
        _current_forecast_label_selection(evidence),
    )
    ids = tuple(item.baseline_id for item in predictions)
    if ids != MANDATORY_BASELINE_IDS:
        raise RuntimeError("mandatory_baseline_generator_coverage_mismatch")
    return predictions
