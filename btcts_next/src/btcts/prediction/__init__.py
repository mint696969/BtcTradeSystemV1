# path: ./btcts_next/src/btcts/prediction/__init__.py
# desc: Public contract exports for the BTC-TS prediction foundation. Non-executing; no broker or collector side effects.

from __future__ import annotations

from .contracts import InferenceBundle, ParameterSetIdentity, PredictionConfidence, PredictionFamily, PredictionOutput, SourceIdentity
from .feature_registry import FeatureFamily, FeatureRegistryEntry, FeatureSpec, build_default_feature_registry, feature_registry_by_id
from .horizons import CONTEXT_HORIZONS_SEC, EXECUTION_MICRO_HORIZONS_SEC, PRIMARY_TRADE_HORIZONS_SEC, HorizonLayer, PredictionHorizon, build_default_horizons, horizon_by_seconds
from .ohlcv import OHLCVAggregationDiagnostics, OHLCVCandle, Timeframe, aggregate_ohlcv_from_rows, build_default_timeframes, timeframe_by_seconds
from .parameter_sets import (
    AlgorithmicParticipantFootprintParameterSet,
    BreakoutFalseBreakPredictionParameterSet,
    CrossVenueConfirmationParameterSet,
    HumanTechnicalStructureParameterSet,
    LiquidityExecutionQualityParameterSet,
    MacroRiskContextParameterSet,
    MarketRegimePredictionParameterSet,
    OpportunityParticipationParameterSet,
    PredictionParameterSetBase,
    PredictionParameterSetStatus,
    ReversalPredictionParameterSet,
    TrendPredictionParameterSet,
    VolatilityRiskPredictionParameterSet,
    build_default_prediction_parameter_sets,
    default_prediction_parameter_set_for_family,
)
from .source_quality import ContinuityState, SourceQualityStatus, SourceTrustState, assess_source_quality

__all__ = [
    "AlgorithmicParticipantFootprintParameterSet",
    "BreakoutFalseBreakPredictionParameterSet",
    "CONTEXT_HORIZONS_SEC",
    "ContinuityState",
    "CrossVenueConfirmationParameterSet",
    "EXECUTION_MICRO_HORIZONS_SEC",
    "FeatureFamily",
    "FeatureRegistryEntry",
    "FeatureSpec",
    "HorizonLayer",
    "HumanTechnicalStructureParameterSet",
    "InferenceBundle",
    "LiquidityExecutionQualityParameterSet",
    "MacroRiskContextParameterSet",
    "MarketRegimePredictionParameterSet",
    "OHLCVAggregationDiagnostics",
    "OHLCVCandle",
    "OpportunityParticipationParameterSet",
    "PRIMARY_TRADE_HORIZONS_SEC",
    "ParameterSetIdentity",
    "PredictionConfidence",
    "PredictionFamily",
    "PredictionHorizon",
    "PredictionOutput",
    "PredictionParameterSetBase",
    "PredictionParameterSetStatus",
    "ReversalPredictionParameterSet",
    "SourceIdentity",
    "SourceQualityStatus",
    "SourceTrustState",
    "Timeframe",
    "TrendPredictionParameterSet",
    "VolatilityRiskPredictionParameterSet",
    "aggregate_ohlcv_from_rows",
    "assess_source_quality",
    "build_default_feature_registry",
    "build_default_horizons",
    "build_default_prediction_parameter_sets",
    "build_default_timeframes",
    "default_prediction_parameter_set_for_family",
    "feature_registry_by_id",
    "horizon_by_seconds",
    "timeframe_by_seconds",
]
