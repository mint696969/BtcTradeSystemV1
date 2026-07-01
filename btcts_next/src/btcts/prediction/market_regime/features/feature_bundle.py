# path: ./btcts_next/src/btcts/prediction/market_regime/features/feature_bundle.py
# desc: Pure feature-bundle contracts for market-regime engine. No data-root reads or runtime writes.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Tuple

from ..contracts import FeatureGroup, SourceCoverage

MARKET_REGIME_FEATURE_BUNDLE_VERSION = "prediction.market_regime.feature_bundle.ps_q27i.v1"


@dataclass(frozen=True)
class FeatureBundleSafetyFlags:
    read_only: bool = True
    non_executing: bool = True
    source_snapshot_input_only: bool = True
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
class FeatureSignal:
    feature_group: FeatureGroup
    name: str
    value: Any
    available: bool
    source_refs: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    weight_hint: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature_group": self.feature_group.value,
            "name": self.name,
            "value": self.value,
            "available": self.available,
            "source_refs": list(self.source_refs),
            "warnings": list(self.warnings),
            "weight_hint": float(self.weight_hint),
        }


@dataclass(frozen=True)
class MarketRegimeFeatureBundle:
    generated_at: str
    signals: Tuple[FeatureSignal, ...]
    coverage: Tuple[SourceCoverage, ...]
    source_snapshot_ok: bool
    missing_sources: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    logic_version: str = MARKET_REGIME_FEATURE_BUNDLE_VERSION
    safety: FeatureBundleSafetyFlags = field(default_factory=FeatureBundleSafetyFlags)

    def signals_by_group(self, feature_group: FeatureGroup | str) -> Tuple[FeatureSignal, ...]:
        normalized = feature_group if isinstance(feature_group, FeatureGroup) else FeatureGroup(str(feature_group))
        return tuple(signal for signal in self.signals if signal.feature_group == normalized)

    def available_signal_count(self) -> int:
        return sum(1 for signal in self.signals if signal.available)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "logic_version": self.logic_version,
            "signals": [signal.to_dict() for signal in self.signals],
            "coverage": [item.to_dict() for item in self.coverage],
            "source_snapshot_ok": self.source_snapshot_ok,
            "available_signal_count": self.available_signal_count(),
            "missing_sources": list(self.missing_sources),
            "warnings": list(self.warnings),
            "safety": self.safety.to_dict(),
        }
