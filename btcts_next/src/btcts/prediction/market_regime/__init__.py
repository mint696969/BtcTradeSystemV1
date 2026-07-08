# path: ./btcts_next/src/btcts/prediction/market_regime/__init__.py
# desc: Pure market-regime engine contracts and policies. No UI, runtime artifact, broker, or collector side effects.

from __future__ import annotations

from .artifact_projection import (
    MARKET_REGIME_ARTIFACT_PROJECTION_VERSION,
    build_market_regime_cards_from_packet,
    build_market_regime_read_model_horizons,
    build_market_regime_read_model_summaries,
)
from .artifact_contracts import (
    LATEST_CARDS_JSON_RELPATH,
    LATEST_JSON_RELPATH,
    LATEST_READ_MODEL_JSON_RELPATH,
    MARKET_REGIME_ARTIFACT_CONTRACT_VERSION,
    MARKET_REGIME_LATEST_CARDS_SCHEMA_VERSION,
    STATUS_JSON_RELPATH,
    artifact_relative_paths,
    build_market_regime_latest_artifact,
    build_market_regime_latest_cards_artifact,
    build_market_regime_latest_read_model_artifact,
    build_market_regime_run_manifest_artifact,
    build_market_regime_status_artifact,
    validate_market_regime_latest_cards_artifact,
)
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
from .inference import MARKET_REGIME_CLASSIFIER_VERSION, classify_market_regime_feature_bundle
from .outcome_resolver import (
    MARKET_REGIME_OUTCOME_RESOLVER_VERSION,
    append_market_regime_outcome_row_once,
    build_market_regime_outcome_row,
    outcome_meta_relpath,
    outcome_part_relpath,
    resolve_market_regime_outcome_label,
    validate_market_regime_outcome_row,
)
from .parameter_set import MarketRegimeParameterSet, build_default_market_regime_parameter_set
from .parameter_set_registry import (
    MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID,
    MARKET_REGIME_PARAMETER_SET_REGISTRY_VERSION,
    MarketRegimeParameterSetRegistry,
    MarketRegimeParameterSetRegistryEntry,
    build_default_market_regime_parameter_set_registry,
    validate_market_regime_parameter_set_registry,
)
from .source_priority_policy import HorizonSourcePriority, SourcePriorityPolicy, build_default_source_priority_policy
from .signal_scoring import (
    MARKET_REGIME_SIGNAL_SCORING_VERSION,
    MARKET_REGIME_SIGNAL_REGISTRY_VERSION,
    score_market_regime_signals,
)
from .trace_ledger import (
    MARKET_REGIME_TRACE_LEDGER_VERSION,
    append_market_regime_trace_row_once,
    build_market_regime_trace_row,
    trace_ledger_meta_relpath,
    trace_ledger_part_relpath,
    validate_market_regime_trace_row,
)
from .source_snapshot import (
    ForecastRecordsSnapshot,
    JsonSourceArtifact,
    MarketRegimeSourceSnapshot,
    NowcastSourceSnapshot,
    SourceAdapterSafetyFlags,
)
from .sources import build_market_regime_source_snapshot

__all__ = [
    "validate_market_regime_outcome_row",
    "resolve_market_regime_outcome_label",
    "outcome_part_relpath",
    "outcome_meta_relpath",
    "build_market_regime_outcome_row",
    "append_market_regime_outcome_row_once",
    "MARKET_REGIME_OUTCOME_RESOLVER_VERSION",
    "validate_market_regime_trace_row",
    "trace_ledger_part_relpath",
    "trace_ledger_meta_relpath",
    "build_market_regime_trace_row",
    "append_market_regime_trace_row_once",
    "MARKET_REGIME_TRACE_LEDGER_VERSION",
    "validate_market_regime_parameter_set_registry",
    "build_default_market_regime_parameter_set_registry",
    "MarketRegimeParameterSetRegistryEntry",
    "MarketRegimeParameterSetRegistry",
    "MARKET_REGIME_PARAMETER_SET_REGISTRY_VERSION",
    "MARKET_REGIME_DEFAULT_ACTIVE_PARAMETER_SET_ID",
    "score_market_regime_signals",
    "MARKET_REGIME_SIGNAL_REGISTRY_VERSION",
    "MARKET_REGIME_SIGNAL_SCORING_VERSION",
    "build_market_regime_read_model_summaries",
    "build_market_regime_read_model_horizons",
    "build_market_regime_cards_from_packet",
    "MARKET_REGIME_ARTIFACT_PROJECTION_VERSION",
    "validate_market_regime_latest_cards_artifact",
    "build_market_regime_status_artifact",
    "build_market_regime_run_manifest_artifact",
    "build_market_regime_latest_read_model_artifact",
    "build_market_regime_latest_cards_artifact",
    "build_market_regime_latest_artifact",
    "artifact_relative_paths",
    "STATUS_JSON_RELPATH",
    "MARKET_REGIME_LATEST_CARDS_SCHEMA_VERSION",
    "MARKET_REGIME_ARTIFACT_CONTRACT_VERSION",
    "LATEST_READ_MODEL_JSON_RELPATH",
    "LATEST_JSON_RELPATH",
    "LATEST_CARDS_JSON_RELPATH",
    "EvidenceQuality",
    "FeatureBundleSafetyFlags",
    "FeatureGroup",
    "FeatureSignal",
    "FreshnessState",
    "FreshnessThreshold",
    "ForecastRecordsSnapshot",
    "HorizonSourcePriority",
    "JsonSourceArtifact",
    "MARKET_REGIME_CLASSIFIER_VERSION",
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
    "classify_market_regime_feature_bundle",
    "build_market_regime_source_snapshot",
]
