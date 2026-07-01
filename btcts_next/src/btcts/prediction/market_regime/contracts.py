# path: ./btcts_next/src/btcts/prediction/market_regime/contracts.py
# desc: Pure contracts for the market-regime engine. No UI import, data-root read, runtime write, broker, or AutoTrade behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Tuple

MARKET_REGIME_CONTRACT_VERSION = "prediction.market_regime.contracts.ps_q27g.v1"


class MarketRegimeCode(str, Enum):
    UP_TREND = "UP_TREND"
    DOWN_TREND = "DOWN_TREND"
    RANGE = "RANGE"
    LOW_VOL_COMPRESSION = "LOW_VOL_COMPRESSION"
    HIGH_VOL_CHOP = "HIGH_VOL_CHOP"
    BREAKOUT = "BREAKOUT"
    PANIC_SPIKE = "PANIC_SPIKE"
    REVERSAL_WATCH = "REVERSAL_WATCH"
    UNKNOWN = "UNKNOWN"


class EvidenceQuality(str, Enum):
    STRONG = "STRONG"
    PARTIAL = "PARTIAL"
    WEAK = "WEAK"
    CONFLICTED = "CONFLICTED"
    MISSING = "MISSING"


class FreshnessState(str, Enum):
    LIVE = "LIVE"
    WARM = "WARM"
    STALE = "STALE"
    MISSING = "MISSING"


class TacticalHint(str, Enum):
    OBSERVE_ONLY = "OBSERVE_ONLY"
    RANGE_TACTIC = "RANGE_TACTIC"
    TREND_FOLLOW_WATCH = "TREND_FOLLOW_WATCH"
    BREAKOUT_WATCH = "BREAKOUT_WATCH"
    REVERSAL_WATCH = "REVERSAL_WATCH"
    RISK_REDUCE = "RISK_REDUCE"
    NO_NEW_ENTRY = "NO_NEW_ENTRY"
    UNKNOWN_HOLD = "UNKNOWN_HOLD"


class FeatureGroup(str, Enum):
    PRICE_STRUCTURE = "price_structure"
    VOLATILITY = "volatility"
    LIQUIDITY = "liquidity"
    ORDERFLOW = "orderflow"
    CROSS_VENUE = "cross_venue"
    SOURCE_QUALITY = "source_quality"


@dataclass(frozen=True)
class MarketRegimeSafetyFlags:
    read_only: bool = True
    non_executing: bool = True
    ui_display_only: bool = True
    runtime_artifact_write_allowed: bool = False
    status_artifact_write_allowed: bool = False
    prediction_artifact_write_allowed: bool = False
    view_artifact_write_allowed: bool = False
    scheduler_enabled: bool = False
    producer_enabled: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    ledger_append_allowed: bool = False
    mode_apply_allowed: bool = False
    parameter_apply_allowed: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourceCoverage:
    feature_group: FeatureGroup
    available: bool
    freshness_state: FreshnessState = FreshnessState.MISSING
    used_sources: Tuple[str, ...] = ()
    missing_sources: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    feature_version: str = MARKET_REGIME_CONTRACT_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature_group": self.feature_group.value,
            "available": self.available,
            "freshness_state": self.freshness_state.value,
            "used_sources": list(self.used_sources),
            "missing_sources": list(self.missing_sources),
            "warnings": list(self.warnings),
            "feature_version": self.feature_version,
        }


@dataclass(frozen=True)
class MarketRegimePrediction:
    horizon_label: str
    horizon_sec: int
    regime_code: MarketRegimeCode = MarketRegimeCode.UNKNOWN
    confidence_percent: int = 0
    evidence_quality: EvidenceQuality = EvidenceQuality.MISSING
    freshness_state: FreshnessState = FreshnessState.MISSING
    tactical_hint: TacticalHint = TacticalHint.UNKNOWN_HOLD
    drivers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    missing_sources: Tuple[str, ...] = ()
    invalidation_hints: Tuple[str, ...] = ()
    parameter_set_id: str = "market_regime_parameter_set.v1"
    source_priority_policy_id: str = "market_regime_source_priority.v1"
    feature_bundle_hash: str | None = None
    diagnostic_record: Mapping[str, Any] = field(default_factory=dict)
    safety: MarketRegimeSafetyFlags = field(default_factory=MarketRegimeSafetyFlags)

    def __post_init__(self) -> None:
        clamped = max(0, min(int(self.confidence_percent), 99))
        object.__setattr__(self, "confidence_percent", clamped)

    @property
    def horizon_key(self) -> str:
        return "current" if int(self.horizon_sec) == 0 else f"{int(self.horizon_sec)}s"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "horizon_label": self.horizon_label,
            "horizon_sec": int(self.horizon_sec),
            "horizon_key": self.horizon_key,
            "regime_code": self.regime_code.value,
            "confidence_percent": self.confidence_percent,
            "evidence_quality": self.evidence_quality.value,
            "freshness_state": self.freshness_state.value,
            "tactical_hint": self.tactical_hint.value,
            "drivers": list(self.drivers),
            "warnings": list(self.warnings),
            "missing_sources": list(self.missing_sources),
            "invalidation_hints": list(self.invalidation_hints),
            "parameter_set_id": self.parameter_set_id,
            "source_priority_policy_id": self.source_priority_policy_id,
            "feature_bundle_hash": self.feature_bundle_hash,
            "diagnostic_record": dict(self.diagnostic_record),
            "safety": self.safety.to_dict(),
        }


@dataclass(frozen=True)
class MarketRegimePredictionPacket:
    generated_at: str
    predictions: Tuple[MarketRegimePrediction, ...]
    source_coverage: Tuple[SourceCoverage, ...] = ()
    missing_sources: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    parameter_set_id: str = "market_regime_parameter_set.v1"
    source_priority_policy_id: str = "market_regime_source_priority.v1"
    logic_version: str = MARKET_REGIME_CONTRACT_VERSION
    safety: MarketRegimeSafetyFlags = field(default_factory=MarketRegimeSafetyFlags)

    def horizons_present_sec(self) -> Tuple[int, ...]:
        return tuple(prediction.horizon_sec for prediction in self.predictions)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "logic_version": self.logic_version,
            "predictions": [prediction.to_dict() for prediction in self.predictions],
            "horizons_present_sec": list(self.horizons_present_sec()),
            "source_coverage": [coverage.to_dict() for coverage in self.source_coverage],
            "missing_sources": list(self.missing_sources),
            "warnings": list(self.warnings),
            "parameter_set_id": self.parameter_set_id,
            "source_priority_policy_id": self.source_priority_policy_id,
            "safety": self.safety.to_dict(),
        }


def build_empty_market_regime_packet(*, generated_at: str) -> MarketRegimePredictionPacket:
    return MarketRegimePredictionPacket(
        generated_at=generated_at,
        predictions=(),
        missing_sources=("market_regime_predictions_not_built_yet",),
        warnings=("pure_contract_packet_only",),
    )
