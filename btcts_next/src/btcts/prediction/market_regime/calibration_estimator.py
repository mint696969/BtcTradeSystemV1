# path: ./btcts_next/src/btcts/prediction/market_regime/calibration_estimator.py
# desc: Pure MR-F7 hierarchical calibration estimator, caps, and diagnostics. No runtime I/O or live apply.

from __future__ import annotations

from dataclasses import dataclass, field
from math import log
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from .calibration_dataset import (
    CalibrationSampleMaturity,
    CalibrationSplitRole,
    MarketRegimeCalibrationDatasetSplit,
    MarketRegimeCalibrationMaturityPolicy,
    MarketRegimeCalibrationObservation,
)

MARKET_REGIME_CALIBRATION_ESTIMATOR_VERSION = "prediction.market_regime.calibration_estimator.mr_f7.v1"
MARKET_REGIME_CALIBRATION_DIAGNOSTICS_VERSION = "prediction.market_regime.calibration_diagnostics.mr_f7.v1"
MARKET_REGIME_CONFIDENCE_CAP_POLICY_VERSION = "prediction.market_regime.confidence_cap_policy.mr_f7.v1"


@dataclass(frozen=True)
class MarketRegimeConfidenceCapPolicy:
    stale_cap: float = 0.60
    degraded_quality_cap: float = 0.65
    reference_only_cap: float = 0.55
    long_horizon_sec: int = 14_400
    long_horizon_cap: float = 0.70
    sparse_cap: float = 0.55
    provisional_cap: float = 0.75
    policy_version: str = MARKET_REGIME_CONFIDENCE_CAP_POLICY_VERSION

    def __post_init__(self) -> None:
        for name, value in {
            "stale_cap": self.stale_cap,
            "degraded_quality_cap": self.degraded_quality_cap,
            "reference_only_cap": self.reference_only_cap,
            "long_horizon_cap": self.long_horizon_cap,
            "sparse_cap": self.sparse_cap,
            "provisional_cap": self.provisional_cap,
        }.items():
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name}_out_of_range")
        if int(self.long_horizon_sec) <= 0:
            raise ValueError("long_horizon_sec_must_be_positive")


@dataclass(frozen=True)
class MarketRegimeCalibrationEstimate:
    raw_confidence: float
    calibrated_reliability: float | None
    display_confidence: float | None
    sample_count: int
    maturity: CalibrationSampleMaturity
    matched_level: str
    matched_key: str | None
    fallback_chain: tuple[str, ...]
    cap_reasons: tuple[str, ...]
    calibrated_probability_claim: bool
    estimator_version: str = MARKET_REGIME_CALIBRATION_ESTIMATOR_VERSION
    read_only: bool = True


@dataclass(frozen=True)
class MarketRegimeCalibrationDiagnostics:
    sample_count: int
    brier_score: float | None
    log_loss: float | None
    expected_calibration_error: float | None
    high_confidence_miss_count: int
    high_confidence_miss_rate: float | None
    overconfidence_gap: float | None
    underconfidence_gap: float | None
    abstention_count: int
    abstention_rate: float | None
    unscored_count: int
    selective_accuracy: float | None
    coverage: float | None
    evaluation_role: str
    confidence_bucket_reliability: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    diagnostic_version: str = MARKET_REGIME_CALIBRATION_DIAGNOSTICS_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "confidence_bucket_reliability",
            MappingProxyType({str(k): MappingProxyType(dict(v)) for k, v in self.confidence_bucket_reliability.items()}),
        )


@dataclass(frozen=True)
class _BetaBucket:
    success_sum: float
    sample_count: int


class MarketRegimeHierarchicalCalibrator:
    def __init__(
        self,
        *,
        prior_mean: float = 0.50,
        prior_strength: float = 20.0,
        maturity_policy: MarketRegimeCalibrationMaturityPolicy | None = None,
        cap_policy: MarketRegimeConfidenceCapPolicy | None = None,
    ) -> None:
        if not 0.0 < float(prior_mean) < 1.0:
            raise ValueError("prior_mean_out_of_range")
        if float(prior_strength) <= 0.0:
            raise ValueError("prior_strength_must_be_positive")
        self.prior_mean = float(prior_mean)
        self.prior_strength = float(prior_strength)
        self.maturity_policy = maturity_policy or MarketRegimeCalibrationMaturityPolicy()
        self.cap_policy = cap_policy or MarketRegimeConfidenceCapPolicy()
        self._buckets: dict[tuple[str, str], _BetaBucket] = {}

    @staticmethod
    def _levels(row: MarketRegimeCalibrationObservation) -> tuple[tuple[str, str], ...]:
        c = row.bucket_context
        confidence_bucket = _confidence_bucket(row.raw_confidence)
        return (
            ("full_confidence", "|".join((c.full_key, confidence_bucket))),
            (
                "horizon_regime_model_parameter_confidence",
                "|".join(
                    (
                        c.horizon_key,
                        c.predicted_regime,
                        c.model_id,
                        c.logic_version,
                        c.parameter_set_id,
                        confidence_bucket,
                    )
                ),
            ),
            (
                "horizon_regime_model_confidence",
                "|".join((c.horizon_key, c.predicted_regime, c.model_id, c.logic_version, confidence_bucket)),
            ),
            ("horizon_regime_confidence", "|".join((c.horizon_key, c.predicted_regime, confidence_bucket))),
            ("horizon_confidence", "|".join((c.horizon_key, confidence_bucket))),
            ("confidence", confidence_bucket),
            ("horizon_regime", "|".join((c.horizon_key, c.predicted_regime))),
            ("horizon", c.horizon_key),
            ("global", "market_regime"),
        )

    def fit(self, observations: Iterable[MarketRegimeCalibrationObservation]) -> "MarketRegimeHierarchicalCalibrator":
        sums: dict[tuple[str, str], float] = {}
        counts: dict[tuple[str, str], int] = {}
        for row in observations:
            if not row.evaluable or row.strict_target is None:
                continue
            for level in self._levels(row):
                sums[level] = sums.get(level, 0.0) + float(row.strict_target)
                counts[level] = counts.get(level, 0) + 1
        self._buckets = {key: _BetaBucket(success_sum=sums[key], sample_count=counts[key]) for key in counts}
        return self

    def estimate(self, row: MarketRegimeCalibrationObservation) -> MarketRegimeCalibrationEstimate:
        fallback_chain: list[str] = []
        selected: tuple[str, str, _BetaBucket] | None = None
        for level, key in self._levels(row):
            fallback_chain.append(level)
            bucket = self._buckets.get((level, key))
            if bucket is None:
                continue
            maturity = self.maturity_policy.classify(bucket.sample_count)
            if maturity in {CalibrationSampleMaturity.PROVISIONAL, CalibrationSampleMaturity.MATURE}:
                selected = (level, key, bucket)
                break
            if selected is None:
                selected = (level, key, bucket)
        if selected is None:
            return MarketRegimeCalibrationEstimate(
                raw_confidence=row.raw_confidence,
                calibrated_reliability=None,
                display_confidence=None,
                sample_count=0,
                maturity=CalibrationSampleMaturity.EMPTY,
                matched_level="none",
                matched_key=None,
                fallback_chain=tuple(fallback_chain),
                cap_reasons=("insufficient_sample",),
                calibrated_probability_claim=False,
            )
        level, key, bucket = selected
        maturity = self.maturity_policy.classify(bucket.sample_count)
        alpha = self.prior_mean * self.prior_strength
        beta = (1.0 - self.prior_mean) * self.prior_strength
        reliability = (bucket.success_sum + alpha) / (bucket.sample_count + alpha + beta)
        display, reasons = self._apply_caps(row, reliability, maturity)
        claim = maturity is CalibrationSampleMaturity.MATURE and not reasons
        return MarketRegimeCalibrationEstimate(
            raw_confidence=row.raw_confidence,
            calibrated_reliability=round(reliability, 6),
            display_confidence=round(display, 6),
            sample_count=bucket.sample_count,
            maturity=maturity,
            matched_level=level,
            matched_key=key,
            fallback_chain=tuple(fallback_chain),
            cap_reasons=tuple(reasons),
            calibrated_probability_claim=claim,
        )

    def _apply_caps(
        self,
        row: MarketRegimeCalibrationObservation,
        reliability: float,
        maturity: CalibrationSampleMaturity,
    ) -> tuple[float, list[str]]:
        cap = 1.0
        reasons: list[str] = []
        c = row.bucket_context
        if c.freshness_bucket.lower() in {"stale", "expired", "degraded"}:
            cap = min(cap, self.cap_policy.stale_cap)
            reasons.append("freshness_cap")
        if c.source_quality_bucket.lower() in {"degraded", "low", "unknown"}:
            cap = min(cap, self.cap_policy.degraded_quality_cap)
            reasons.append("source_quality_cap")
        if c.source_quality_bucket.lower() in {"reference", "reference_only"}:
            cap = min(cap, self.cap_policy.reference_only_cap)
            reasons.append("reference_only_cap")
        if row.horizon_sec >= self.cap_policy.long_horizon_sec:
            cap = min(cap, self.cap_policy.long_horizon_cap)
            reasons.append("long_horizon_cap")
        if maturity is CalibrationSampleMaturity.SPARSE:
            cap = min(cap, self.cap_policy.sparse_cap)
            reasons.append("sparse_sample_cap")
        elif maturity is CalibrationSampleMaturity.PROVISIONAL:
            cap = min(cap, self.cap_policy.provisional_cap)
            reasons.append("provisional_sample_cap")
        return min(float(reliability), cap), list(dict.fromkeys(reasons))


def _confidence_bucket(value: float) -> str:
    if value < 0.50:
        return "lt_50"
    if value < 0.60:
        return "50_59"
    if value < 0.70:
        return "60_69"
    if value < 0.80:
        return "70_79"
    if value < 0.90:
        return "80_89"
    return "90_100"


def build_market_regime_calibration_diagnostics(
    observations: Sequence[MarketRegimeCalibrationObservation],
    estimates: Sequence[MarketRegimeCalibrationEstimate],
    *,
    high_confidence_threshold: float = 0.80,
    abstention_flags: Sequence[bool] | None = None,
    evaluation_role: CalibrationSplitRole = CalibrationSplitRole.TEST,
) -> MarketRegimeCalibrationDiagnostics:
    if evaluation_role is CalibrationSplitRole.TRAIN:
        raise ValueError("in_sample_diagnostics_not_allowed")
    if not 0.0 <= float(high_confidence_threshold) <= 1.0:
        raise ValueError("high_confidence_threshold_out_of_range")
    if len(observations) != len(estimates):
        raise ValueError("observation_estimate_length_mismatch")
    if abstention_flags is None:
        abstention_flags = (False,) * len(observations)
    if len(abstention_flags) != len(observations):
        raise ValueError("abstention_flag_length_mismatch")
    rows: list[tuple[float, float]] = []
    bucket_rows: dict[str, list[tuple[float, float]]] = {}
    abstention_count = 0
    unscored_count = 0
    covered_hits = 0
    covered_count = 0
    high_miss = 0
    high_total = 0
    for row, estimate, abstained in zip(observations, estimates, abstention_flags):
        if bool(abstained):
            abstention_count += 1
            continue
        if not row.evaluable or row.strict_target is None or estimate.display_confidence is None:
            unscored_count += 1
            continue
        p = min(max(float(estimate.display_confidence), 1e-9), 1.0 - 1e-9)
        y = float(row.strict_target)
        rows.append((p, y))
        bucket_rows.setdefault(_confidence_bucket(p), []).append((p, y))
        covered_count += 1
        covered_hits += int(y == 1.0)
        if p >= high_confidence_threshold:
            high_total += 1
            high_miss += int(y == 0.0)
    total = len(observations)
    if not rows:
        return MarketRegimeCalibrationDiagnostics(
            sample_count=0,
            brier_score=None,
            log_loss=None,
            expected_calibration_error=None,
            high_confidence_miss_count=0,
            high_confidence_miss_rate=None,
            overconfidence_gap=None,
            underconfidence_gap=None,
            abstention_count=abstention_count,
            abstention_rate=(abstention_count / total) if total else None,
            unscored_count=unscored_count,
            selective_accuracy=None,
            coverage=0.0 if total else None,
            evaluation_role=evaluation_role.value,
            confidence_bucket_reliability={},
        )
    brier = sum((p - y) ** 2 for p, y in rows) / len(rows)
    ll = -sum(y * log(p) + (1.0 - y) * log(1.0 - p) for p, y in rows) / len(rows)
    ece = 0.0
    bucket_payload: dict[str, Mapping[str, Any]] = {}
    over = 0.0
    under = 0.0
    for name, values in bucket_rows.items():
        avg_p = sum(p for p, _ in values) / len(values)
        hit_rate = sum(y for _, y in values) / len(values)
        gap = avg_p - hit_rate
        ece += (len(values) / len(rows)) * abs(gap)
        over = max(over, gap)
        under = max(under, -gap)
        bucket_payload[name] = {
            "sample_count": len(values),
            "average_confidence": round(avg_p, 6),
            "strict_hit_rate": round(hit_rate, 6),
            "calibration_gap": round(gap, 6),
        }
    return MarketRegimeCalibrationDiagnostics(
        sample_count=len(rows),
        brier_score=round(brier, 6),
        log_loss=round(ll, 6),
        expected_calibration_error=round(ece, 6),
        high_confidence_miss_count=high_miss,
        high_confidence_miss_rate=round(high_miss / high_total, 6) if high_total else None,
        overconfidence_gap=round(over, 6),
        underconfidence_gap=round(under, 6),
        abstention_count=abstention_count,
        abstention_rate=round(abstention_count / total, 6) if total else None,
        unscored_count=unscored_count,
        selective_accuracy=round(covered_hits / covered_count, 6) if covered_count else None,
        coverage=round(covered_count / total, 6) if total else None,
        evaluation_role=evaluation_role.value,
        confidence_bucket_reliability=bucket_payload,
    )


def evaluate_market_regime_calibrator_oos(
    split: MarketRegimeCalibrationDatasetSplit,
    *,
    role: CalibrationSplitRole,
    calibrator: MarketRegimeHierarchicalCalibrator | None = None,
    abstention_flags: Sequence[bool] | None = None,
    high_confidence_threshold: float = 0.80,
) -> tuple[tuple[MarketRegimeCalibrationEstimate, ...], MarketRegimeCalibrationDiagnostics]:
    if role is CalibrationSplitRole.TRAIN:
        raise ValueError("oos_role_must_be_validation_or_test")
    fitted = calibrator or MarketRegimeHierarchicalCalibrator(
        maturity_policy=split.maturity_policy,
    )
    fitted.fit(split.train)
    evaluation_rows = split.validation if role is CalibrationSplitRole.VALIDATION else split.test
    estimates = tuple(fitted.estimate(row) for row in evaluation_rows)
    diagnostics = build_market_regime_calibration_diagnostics(
        evaluation_rows,
        estimates,
        high_confidence_threshold=high_confidence_threshold,
        abstention_flags=abstention_flags,
        evaluation_role=role,
    )
    return estimates, diagnostics
