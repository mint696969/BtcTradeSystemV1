# path: ./btcts_next/src/btcts/prediction/market_regime/future_mandatory_baseline_origin_evidence.py
# desc: Pure MR-F6.5 prediction-origin evidence bundle for later approved append-only persistence.

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .contracts import MarketRegimeCode
from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC

MARKET_REGIME_ORIGIN_EVIDENCE_VERSION = (
    "prediction.market_regime.mandatory_baseline_origin_evidence.mr_f6_5.v1"
)


@dataclass(frozen=True)
class MarketRegimeOriginEvidence:
    prediction_origin: str
    prediction_origin_epoch_sec: float
    source_timestamp: str
    source_timestamp_epoch_sec: float
    target_horizon_sec: int
    trace_id: str
    model_id: str
    logic_version: str
    parameter_set_id: str
    target_definition_version: str
    feature_snapshot_ref: str
    current_state: MarketRegimeCode
    previous_state: MarketRegimeCode
    regime_scores: Mapping[MarketRegimeCode, float]
    recent_return: float | None
    fast_ma: float | None
    slow_ma: float | None
    realized_volatility: float | None
    low_volatility_threshold: float | None
    high_volatility_threshold: float | None
    current_forecast_label_selection: MarketRegimeCode

    def __post_init__(self) -> None:
        for name, value in (
            ("prediction_origin", self.prediction_origin),
            ("source_timestamp", self.source_timestamp),
            ("trace_id", self.trace_id),
            ("model_id", self.model_id),
            ("logic_version", self.logic_version),
            ("parameter_set_id", self.parameter_set_id),
            ("target_definition_version", self.target_definition_version),
            ("feature_snapshot_ref", self.feature_snapshot_ref),
        ):
            if not str(value).strip():
                raise ValueError(f"origin_evidence_identity_missing:{name}")
        for name, value in (
            ("prediction_origin_epoch_sec", self.prediction_origin_epoch_sec),
            ("source_timestamp_epoch_sec", self.source_timestamp_epoch_sec),
        ):
            if not isfinite(float(value)) or float(value) < 0.0:
                raise ValueError(f"origin_evidence_timestamp_invalid:{name}")
        if float(self.source_timestamp_epoch_sec) > float(self.prediction_origin_epoch_sec):
            raise ValueError("origin_evidence_lookahead_detected")
        horizon = int(self.target_horizon_sec)
        if horizon not in FUTURE_MARKET_REGIME_HORIZONS_SEC:
            raise ValueError("origin_evidence_horizon_invalid")
        if self.target_definition_version != f"market_regime_target.{horizon}s.v1":
            raise ValueError("origin_evidence_target_definition_mismatch")
        for name, value in (
            ("current_state", self.current_state),
            ("previous_state", self.previous_state),
            ("current_forecast_label_selection", self.current_forecast_label_selection),
        ):
            if not isinstance(value, MarketRegimeCode):
                raise ValueError(f"origin_evidence_regime_invalid:{name}")
        normalized_scores: dict[MarketRegimeCode, float] = {}
        for state, raw in self.regime_scores.items():
            if not isinstance(state, MarketRegimeCode):
                raise ValueError("origin_evidence_score_key_invalid")
            if state is MarketRegimeCode.UNKNOWN:
                continue
            value = float(raw)
            if not isfinite(value) or value < 0.0:
                raise ValueError("origin_evidence_score_invalid")
            normalized_scores[state] = value
        if not normalized_scores or sum(normalized_scores.values()) <= 0.0:
            raise ValueError("origin_evidence_positive_score_missing")
        object.__setattr__(self, "regime_scores", MappingProxyType(normalized_scores))
        for name, value in (
            ("recent_return", self.recent_return),
            ("fast_ma", self.fast_ma),
            ("slow_ma", self.slow_ma),
            ("realized_volatility", self.realized_volatility),
            ("low_volatility_threshold", self.low_volatility_threshold),
            ("high_volatility_threshold", self.high_volatility_threshold),
        ):
            if value is not None and not isfinite(float(value)):
                raise ValueError(f"origin_evidence_feature_non_finite:{name}")
        if self.low_volatility_threshold is not None and float(self.low_volatility_threshold) < 0.0:
            raise ValueError("origin_evidence_low_volatility_threshold_negative")
        if self.high_volatility_threshold is not None and float(self.high_volatility_threshold) < 0.0:
            raise ValueError("origin_evidence_high_volatility_threshold_negative")
        if (
            self.low_volatility_threshold is not None
            and self.high_volatility_threshold is not None
            and float(self.low_volatility_threshold) > float(self.high_volatility_threshold)
        ):
            raise ValueError("origin_evidence_volatility_threshold_order_invalid")


def _probability_distribution(scores: Mapping[MarketRegimeCode, float]) -> Mapping[str, float]:
    total = sum(float(value) for value in scores.values())
    if total <= 0.0:
        raise ValueError("origin_evidence_probability_total_invalid")
    values = {state.value: float(score) / total for state, score in scores.items()}
    residual = 1.0 - sum(values.values())
    if values and abs(residual) > 0.0:
        largest = max(values, key=values.get)
        values[largest] += residual
    if any(not isfinite(value) or value < 0.0 or value > 1.0 for value in values.values()):
        raise ValueError("origin_evidence_probability_invalid")
    return MappingProxyType(dict(sorted(values.items())))


def build_market_regime_origin_evidence_bundle(
    evidence: MarketRegimeOriginEvidence,
) -> Mapping[str, Any]:
    if not isinstance(evidence, MarketRegimeOriginEvidence):
        raise ValueError("origin_evidence_type_invalid")
    probabilities = _probability_distribution(evidence.regime_scores)
    feature_payload = {
        "source_timestamp": evidence.source_timestamp,
        "source_timestamp_epoch_sec": float(evidence.source_timestamp_epoch_sec),
        "prediction_origin": evidence.prediction_origin,
        "prediction_origin_epoch_sec": float(evidence.prediction_origin_epoch_sec),
        "current_state": evidence.current_state.value,
        "previous_state": evidence.previous_state.value,
        "recent_return": evidence.recent_return,
        "fast_ma": evidence.fast_ma,
        "slow_ma": evidence.slow_ma,
        "realized_volatility": evidence.realized_volatility,
        "low_volatility_threshold": evidence.low_volatility_threshold,
        "high_volatility_threshold": evidence.high_volatility_threshold,
        "current_forecast_label_selection": evidence.current_forecast_label_selection.value,
    }
    identity_basis = "|".join((
        evidence.trace_id,
        evidence.feature_snapshot_ref,
        evidence.parameter_set_id,
        str(evidence.target_horizon_sec),
        evidence.prediction_origin,
    ))
    bundle_id = "market_regime_origin_evidence:" + sha256(identity_basis.encode("utf-8")).hexdigest()
    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_origin_evidence_bundle",
        "bundle_id": bundle_id,
        "trace_id": evidence.trace_id,
        "model_id": evidence.model_id,
        "logic_version": evidence.logic_version,
        "parameter_set_id": evidence.parameter_set_id,
        "target_horizon_sec": int(evidence.target_horizon_sec),
        "target_definition_version": evidence.target_definition_version,
        "prediction_origin": evidence.prediction_origin,
        "feature_snapshot_ref": evidence.feature_snapshot_ref,
        "feature_snapshot": MappingProxyType(feature_payload),
        "candidate_probability_by_state": probabilities,
        "append_only_required": True,
        "canonical_isolated": True,
        "historical_backfill_allowed": False,
        "scheduler_registration_allowed": False,
        "canonical_replacement": False,
        "parameter_auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "write_performed": False,
    })
