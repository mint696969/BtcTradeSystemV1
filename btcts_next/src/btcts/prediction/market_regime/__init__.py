# path: ./btcts_next/src/btcts/prediction/market_regime/__init__.py
# desc: Pure market-regime engine contracts and policies. No UI, runtime artifact, broker, or collector side effects.

from __future__ import annotations

from .contracts import (
    EvidenceQuality,
    FeatureGroup,
    FreshnessState,
    MarketRegimeCode,
    MarketRegimePrediction,
    MarketRegimePredictionPacket,
    MarketRegimeSafetyFlags,
    SourceCoverage,
    TacticalHint,
    build_empty_market_regime_packet,
)
from .freshness_policy import FreshnessThreshold, MarketRegimeFreshnessPolicy, build_default_freshness_policy
from .features import FeatureBundleSafetyFlags, FeatureSignal, MarketRegimeFeatureBundle, build_market_regime_feature_bundle
from .horizon_policy import MarketRegimeHorizon, MarketRegimeHorizonGroup, MarketRegimeHorizonPolicy, build_default_horizon_policy
from .parameter_set import MarketRegimeParameterSet, build_default_market_regime_parameter_set
from .source_priority_policy import HorizonSourcePriority, SourcePriorityPolicy, build_default_source_priority_policy
from .source_snapshot import (
    ForecastRecordsSnapshot,
    JsonSourceArtifact,
    MarketRegimeSourceSnapshot,
    NowcastSourceSnapshot,
    SourceAdapterSafetyFlags,
)
from .sources import build_market_regime_source_snapshot

__all__ = [
    "EvidenceQuality",
    "FeatureBundleSafetyFlags",
    "FeatureGroup",
    "FeatureSignal",
    "FreshnessState",
    "FreshnessThreshold",
    "ForecastRecordsSnapshot",
    "HorizonSourcePriority",
    "JsonSourceArtifact",
    "MarketRegimeCode",
    "MarketRegimeFeatureBundle",
    "MarketRegimeFreshnessPolicy",
    "MarketRegimeHorizon",
    "MarketRegimeHorizonGroup",
    "MarketRegimeHorizonPolicy",
    "MarketRegimeParameterSet",
    "MarketRegimePrediction",
    "MarketRegimePredictionPacket",
    "MarketRegimeSourceSnapshot",
    "MarketRegimeSafetyFlags",
    "NowcastSourceSnapshot",
    "SourceAdapterSafetyFlags",
    "SourceCoverage",
    "SourcePriorityPolicy",
    "TacticalHint",
    "build_default_freshness_policy",
    "build_default_horizon_policy",
    "build_default_market_regime_parameter_set",
    "build_default_source_priority_policy",
    "build_empty_market_regime_packet",
    "build_market_regime_feature_bundle",
    "build_market_regime_source_snapshot",
]
