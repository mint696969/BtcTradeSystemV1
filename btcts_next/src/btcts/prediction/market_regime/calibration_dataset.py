# path: ./btcts_next/src/btcts/prediction/market_regime/calibration_dataset.py
# desc: Pure MR-F7 calibration dataset/source-flag contribution contracts and time-ordered OOS split. No runtime I/O, UI, broker, AutoTrade, or live parameter apply.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

MARKET_REGIME_CALIBRATION_DATASET_VERSION = "prediction.market_regime.calibration_dataset.mr_f7_1.v1"
MARKET_REGIME_CONTRIBUTION_LEDGER_VERSION = "prediction.market_regime.contribution_ledger.mr_f7_1.v1"
MARKET_REGIME_CALIBRATION_SPLIT_VERSION = "prediction.market_regime.calibration_split.mr_f7_1.v1"
MARKET_REGIME_CALIBRATION_TARGET_VERSION = "market_regime.strict_hit_target.mr_f7.v1"
MARKET_REGIME_GRADED_TARGET_VERSION = "market_regime.graded_hit_partial_target.mr_f7.v1"

_EVALUABLE_LABELS = {"hit", "partial", "miss"}
_ALLOWED_LABELS = _EVALUABLE_LABELS | {"invalidated", "unknown"}


class CalibrationSplitRole(str, Enum):
    TRAIN = "TRAIN"
    VALIDATION = "VALIDATION"
    TEST = "TEST"


class CalibrationSampleMaturity(str, Enum):
    EMPTY = "EMPTY"
    SPARSE = "SPARSE"
    PROVISIONAL = "PROVISIONAL"
    MATURE = "MATURE"


@dataclass(frozen=True)
class MarketRegimeCalibrationMaturityPolicy:
    provisional_min_samples: int = 20
    mature_min_samples: int = 100
    policy_version: str = "market_regime.calibration_maturity.mr_f7.v1"

    def __post_init__(self) -> None:
        if self.provisional_min_samples < 1:
            raise ValueError("provisional_min_samples_must_be_positive")
        if self.mature_min_samples <= self.provisional_min_samples:
            raise ValueError("mature_min_samples_must_exceed_provisional_min_samples")

    def classify(self, sample_count: int) -> CalibrationSampleMaturity:
        count = int(sample_count)
        if count < 0:
            raise ValueError("sample_count_must_be_non_negative")
        if count == 0:
            return CalibrationSampleMaturity.EMPTY
        if count < self.provisional_min_samples:
            return CalibrationSampleMaturity.SPARSE
        if count < self.mature_min_samples:
            return CalibrationSampleMaturity.PROVISIONAL
        return CalibrationSampleMaturity.MATURE


@dataclass(frozen=True)
class MarketRegimeEvidenceContribution:
    source_id: str
    flag_id: str
    observed_state: str
    supports_regime: str
    parameter_id: str
    parameter_version: str
    base_reliability: float
    signed_contribution: float
    source_refs: tuple[str, ...] = ()
    interaction_adjustment: float = 0.0
    quality_adjustment: float = 0.0
    freshness_adjustment: float = 0.0
    final_contribution: float = 0.0
    cap_reasons: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = {
            "source_id": self.source_id,
            "flag_id": self.flag_id,
            "supports_regime": self.supports_regime,
            "parameter_id": self.parameter_id,
            "parameter_version": self.parameter_version,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise ValueError("contribution_identity_missing:" + ",".join(missing))
        if not 0.0 <= float(self.base_reliability) <= 1.0:
            raise ValueError("base_reliability_out_of_range")
        for name, value in {
            "signed_contribution": self.signed_contribution,
            "interaction_adjustment": self.interaction_adjustment,
            "quality_adjustment": self.quality_adjustment,
            "freshness_adjustment": self.freshness_adjustment,
            "final_contribution": self.final_contribution,
        }.items():
            numeric = float(value)
            if not -1.0 <= numeric <= 1.0:
                raise ValueError(f"{name}_out_of_range")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def contribution_key(self) -> str:
        return f"{self.source_id}|{self.flag_id}|{self.supports_regime}|{self.parameter_id}|{self.parameter_version}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "flag_id": self.flag_id,
            "observed_state": self.observed_state,
            "supports_regime": self.supports_regime,
            "parameter_id": self.parameter_id,
            "parameter_version": self.parameter_version,
            "base_reliability": float(self.base_reliability),
            "signed_contribution": float(self.signed_contribution),
            "source_refs": list(self.source_refs),
            "interaction_adjustment": float(self.interaction_adjustment),
            "quality_adjustment": float(self.quality_adjustment),
            "freshness_adjustment": float(self.freshness_adjustment),
            "final_contribution": float(self.final_contribution),
            "cap_reasons": list(self.cap_reasons),
            "metadata": dict(self.metadata),
            "contribution_key": self.contribution_key,
        }


@dataclass(frozen=True)
class MarketRegimeCalibrationBucketContext:
    horizon_key: str
    predicted_regime: str
    model_id: str
    logic_version: str
    parameter_set_id: str
    session_bucket: str
    volatility_bucket: str
    liquidity_bucket: str
    freshness_bucket: str
    source_quality_bucket: str
    bucket_policy_version: str

    def __post_init__(self) -> None:
        missing = [name for name, value in asdict(self).items() if not str(value).strip()]
        if missing:
            raise ValueError("bucket_context_missing:" + ",".join(missing))

    @property
    def full_key(self) -> str:
        return "|".join(str(value) for value in asdict(self).values())


@dataclass(frozen=True)
class MarketRegimeCalibrationObservation:
    outcome_id: str
    prediction_id: str
    run_id: str
    origin_timestamp: str
    resolved_at: str
    horizon_sec: int
    predicted_regime: str
    observed_regime: str
    raw_confidence: float
    strict_target: float | None
    graded_target: float | None
    outcome_label: str
    evaluable: bool
    observation_source: str
    observation_evaluator_version: str
    target_definition_version: str
    strict_target_version: str
    graded_target_version: str
    trace_ref: str
    bucket_context: MarketRegimeCalibrationBucketContext
    contributions: tuple[MarketRegimeEvidenceContribution, ...]
    safety_read_only: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = {
            "outcome_id": self.outcome_id,
            "prediction_id": self.prediction_id,
            "origin_timestamp": self.origin_timestamp,
            "resolved_at": self.resolved_at,
            "predicted_regime": self.predicted_regime,
            "observed_regime": self.observed_regime,
            "observation_source": self.observation_source,
            "target_definition_version": self.target_definition_version,
            "strict_target_version": self.strict_target_version,
            "graded_target_version": self.graded_target_version,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise ValueError("calibration_observation_identity_missing:" + ",".join(missing))
        if int(self.horizon_sec) < 0:
            raise ValueError("horizon_sec_must_be_non_negative")
        if not 0.0 <= float(self.raw_confidence) <= 1.0:
            raise ValueError("raw_confidence_out_of_range")
        if self.outcome_label not in _ALLOWED_LABELS:
            raise ValueError("outcome_label_invalid")
        expected_evaluable = self.outcome_label in _EVALUABLE_LABELS
        if self.evaluable is not expected_evaluable:
            raise ValueError("evaluable_state_mismatch")
        if expected_evaluable:
            if self.strict_target not in {0.0, 1.0}:
                raise ValueError("strict_target_invalid")
            if self.graded_target not in {0.0, 0.5, 1.0}:
                raise ValueError("graded_target_invalid")
        elif self.strict_target is not None or self.graded_target is not None:
            raise ValueError("non_evaluable_target_must_be_none")
        if self.safety_read_only is not True:
            raise ValueError("calibration_observation_must_be_read_only")
        keys = [item.contribution_key for item in self.contributions]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate_contribution_key")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def observation_key(self) -> str:
        return f"{self.outcome_id}|{self.bucket_context.full_key}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_version": MARKET_REGIME_CALIBRATION_DATASET_VERSION,
            "contribution_ledger_version": MARKET_REGIME_CONTRIBUTION_LEDGER_VERSION,
            "outcome_id": self.outcome_id,
            "prediction_id": self.prediction_id,
            "run_id": self.run_id,
            "origin_timestamp": self.origin_timestamp,
            "resolved_at": self.resolved_at,
            "horizon_sec": int(self.horizon_sec),
            "predicted_regime": self.predicted_regime,
            "observed_regime": self.observed_regime,
            "raw_confidence": float(self.raw_confidence),
            "strict_target": self.strict_target,
            "graded_target": self.graded_target,
            "outcome_label": self.outcome_label,
            "evaluable": self.evaluable,
            "observation_source": self.observation_source,
            "observation_evaluator_version": self.observation_evaluator_version,
            "target_definition_version": self.target_definition_version,
            "strict_target_version": self.strict_target_version,
            "graded_target_version": self.graded_target_version,
            "trace_ref": self.trace_ref,
            "bucket_context": asdict(self.bucket_context),
            "bucket_key": self.bucket_context.full_key,
            "contributions": [item.to_dict() for item in self.contributions],
            "safety_read_only": self.safety_read_only,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class MarketRegimeCalibrationDatasetSplit:
    train: tuple[MarketRegimeCalibrationObservation, ...]
    validation: tuple[MarketRegimeCalibrationObservation, ...]
    test: tuple[MarketRegimeCalibrationObservation, ...]
    train_end_exclusive: str
    validation_end_exclusive: str
    maturity_policy: MarketRegimeCalibrationMaturityPolicy = field(default_factory=MarketRegimeCalibrationMaturityPolicy)

    def __post_init__(self) -> None:
        train_end = _parse_utc(self.train_end_exclusive)
        validation_end = _parse_utc(self.validation_end_exclusive)
        if train_end >= validation_end:
            raise ValueError("split_boundaries_not_monotonic")
        all_rows = self.train + self.validation + self.test
        keys = [item.observation_key for item in all_rows]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate_observation_across_splits")
        for row in self.train:
            if _parse_utc(row.origin_timestamp) >= train_end:
                raise ValueError("train_row_after_boundary")
            if _parse_utc(row.resolved_at) >= train_end:
                raise ValueError("train_outcome_not_available_at_boundary")
        for row in self.validation:
            origin = _parse_utc(row.origin_timestamp)
            if origin < train_end or origin >= validation_end:
                raise ValueError("validation_row_outside_boundary")
            if _parse_utc(row.resolved_at) >= validation_end:
                raise ValueError("validation_outcome_not_available_at_boundary")
        for row in self.test:
            if _parse_utc(row.origin_timestamp) < validation_end:
                raise ValueError("test_row_before_boundary")

    def maturity(self, role: CalibrationSplitRole) -> CalibrationSampleMaturity:
        rows = {
            CalibrationSplitRole.TRAIN: self.train,
            CalibrationSplitRole.VALIDATION: self.validation,
            CalibrationSplitRole.TEST: self.test,
        }[role]
        evaluable_count = sum(1 for row in rows if row.evaluable)
        return self.maturity_policy.classify(evaluable_count)

    def to_dict(self) -> dict[str, Any]:
        return {
            "split_version": MARKET_REGIME_CALIBRATION_SPLIT_VERSION,
            "train_end_exclusive": self.train_end_exclusive,
            "validation_end_exclusive": self.validation_end_exclusive,
            "train_count": len(self.train),
            "validation_count": len(self.validation),
            "test_count": len(self.test),
            "train_maturity": self.maturity(CalibrationSplitRole.TRAIN).value,
            "validation_maturity": self.maturity(CalibrationSplitRole.VALIDATION).value,
            "test_maturity": self.maturity(CalibrationSplitRole.TEST).value,
            "random_split_allowed": False,
            "future_leakage_allowed": False,
            "read_only": True,
        }


def _parse_utc(value: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError("timestamp_missing")
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _as_probability(value: object) -> float:
    numeric = float(value)
    if numeric > 1.0:
        numeric /= 100.0
    if not 0.0 <= numeric <= 1.0:
        raise ValueError("confidence_out_of_range")
    return numeric


def _target_values(label: str) -> tuple[bool, float | None, float | None]:
    if label == "hit":
        return True, 1.0, 1.0
    if label == "partial":
        return True, 0.0, 0.5
    if label == "miss":
        return True, 0.0, 0.0
    if label in {"invalidated", "unknown"}:
        return False, None, None
    raise ValueError("outcome_label_invalid")


def build_market_regime_calibration_observation(
    *,
    outcome_row: Mapping[str, Any],
    bucket_context: MarketRegimeCalibrationBucketContext,
    contributions: Sequence[MarketRegimeEvidenceContribution],
    model_id: str,
    logic_version: str,
    target_definition_version: str,
) -> MarketRegimeCalibrationObservation:
    if bucket_context.model_id != model_id:
        raise ValueError("bucket_model_id_mismatch")
    if bucket_context.logic_version != logic_version:
        raise ValueError("bucket_logic_version_mismatch")
    if bucket_context.parameter_set_id != str(outcome_row.get("parameter_set_id") or ""):
        raise ValueError("bucket_parameter_set_id_mismatch")
    horizon_sec = int(outcome_row.get("horizon_sec") or 0)
    expected_horizon_key = "current" if horizon_sec == 0 else f"{horizon_sec}s"
    if bucket_context.horizon_key != expected_horizon_key:
        raise ValueError("bucket_horizon_key_mismatch")
    predicted_regime = str(outcome_row.get("predicted_regime_code") or "UNKNOWN")
    if bucket_context.predicted_regime != predicted_regime:
        raise ValueError("bucket_predicted_regime_mismatch")
    label = str(outcome_row.get("outcome_label") or "unknown")
    evaluable, strict_target, graded_target = _target_values(label)
    origin_timestamp = str(outcome_row.get("generated_at") or "")
    resolved_at = str(outcome_row.get("resolved_at") or "")
    if _parse_utc(resolved_at) < _parse_utc(origin_timestamp):
        raise ValueError("resolved_at_precedes_origin_timestamp")
    return MarketRegimeCalibrationObservation(
        outcome_id=str(outcome_row.get("outcome_id") or ""),
        prediction_id=str(outcome_row.get("prediction_id") or ""),
        run_id=str(outcome_row.get("run_id") or ""),
        origin_timestamp=origin_timestamp,
        resolved_at=resolved_at,
        horizon_sec=horizon_sec,
        predicted_regime=predicted_regime,
        observed_regime=str(outcome_row.get("observed_regime_code") or "UNKNOWN"),
        raw_confidence=_as_probability(outcome_row.get("confidence_percent") or 0),
        strict_target=strict_target,
        graded_target=graded_target,
        outcome_label=label,
        evaluable=evaluable,
        observation_source=str(outcome_row.get("observation_source") or "unknown"),
        observation_evaluator_version=str(outcome_row.get("observation_evaluator_version") or "unknown"),
        target_definition_version=target_definition_version,
        strict_target_version=MARKET_REGIME_CALIBRATION_TARGET_VERSION,
        graded_target_version=MARKET_REGIME_GRADED_TARGET_VERSION,
        trace_ref=str(outcome_row.get("trace_part_jsonl") or ""),
        bucket_context=bucket_context,
        contributions=tuple(contributions),
        metadata={
            "model_id": model_id,
            "logic_version": logic_version,
            "source_outcome_schema_version": str(outcome_row.get("schema_version") or ""),
        },
    )


def split_market_regime_calibration_observations(
    observations: Iterable[MarketRegimeCalibrationObservation],
    *,
    train_end_exclusive: str,
    validation_end_exclusive: str,
    maturity_policy: MarketRegimeCalibrationMaturityPolicy | None = None,
) -> MarketRegimeCalibrationDatasetSplit:
    train_end = _parse_utc(train_end_exclusive)
    validation_end = _parse_utc(validation_end_exclusive)
    if train_end >= validation_end:
        raise ValueError("split_boundaries_not_monotonic")
    ordered = sorted(tuple(observations), key=lambda item: (_parse_utc(item.origin_timestamp), item.observation_key))
    keys = [item.observation_key for item in ordered]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate_observation_key")
    train: list[MarketRegimeCalibrationObservation] = []
    validation: list[MarketRegimeCalibrationObservation] = []
    test: list[MarketRegimeCalibrationObservation] = []
    for row in ordered:
        origin = _parse_utc(row.origin_timestamp)
        if origin >= _parse_utc(row.resolved_at):
            raise ValueError("outcome_not_resolved_after_prediction")
        resolved = _parse_utc(row.resolved_at)
        if origin < train_end:
            if resolved >= train_end:
                raise ValueError("train_outcome_not_available_at_boundary")
            train.append(row)
        elif origin < validation_end:
            if resolved >= validation_end:
                raise ValueError("validation_outcome_not_available_at_boundary")
            validation.append(row)
        else:
            test.append(row)
    return MarketRegimeCalibrationDatasetSplit(
        train=tuple(train),
        validation=tuple(validation),
        test=tuple(test),
        train_end_exclusive=train_end_exclusive,
        validation_end_exclusive=validation_end_exclusive,
        maturity_policy=maturity_policy or MarketRegimeCalibrationMaturityPolicy(),
    )
