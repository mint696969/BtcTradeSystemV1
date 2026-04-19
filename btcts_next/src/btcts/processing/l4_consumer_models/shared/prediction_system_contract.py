# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_system_contract.py
# desc: Shared Prediction System contract skeleton for Phase 3 Scenario Prediction Core entry.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from btcts.processing.l4_consumer_models.shared.health_digest import HealthDigest
from btcts.processing.l4_consumer_models.shared.market_summary import MarketSummary

DEFAULT_PREDICTION_SYSTEM_VERSION = "phase3.v1alpha1"
DEFAULT_PREDICTION_SYSTEM_SOURCE_KIND = "market_summary_anchor"
DEFAULT_REQUESTED_HORIZONS = ("5m", "10m", "30m")


@dataclass(frozen=True)
class PredictionEvidenceBundle:
    market_summary: MarketSummary | None = None
    health_digest: HealthDigest | None = None
    liquidity_board_history: dict[str, Any] = field(default_factory=dict)
    regime_turning_point: dict[str, Any] = field(default_factory=dict)
    external_context: dict[str, Any] = field(default_factory=dict)
    position_context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PredictionEvidenceTrace:
    trace_type: str = "prediction_evidence_trace"
    trace_version: str = DEFAULT_PREDICTION_SYSTEM_VERSION
    active_families: tuple[str, ...] = field(default_factory=tuple)
    missing_families: tuple[str, ...] = field(default_factory=tuple)
    caution_flags: tuple[str, ...] = field(default_factory=tuple)
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PredictionCalibrationHint:
    hint_type: str = "prediction_calibration_hint"
    hint_version: str = DEFAULT_PREDICTION_SYSTEM_VERSION
    confidence_bias: str = "unknown"
    caution_bias: str = "unknown"
    invalidation_sensitivity: str = "unknown"
    replay_priority: str = "normal"
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PredictionScenarioHorizonOutput:
    horizon: str
    regime_bias: str = "unknown"
    continuation_likelihood: str = "unknown"
    reversal_likelihood: str = "unknown"
    turning_point_risk: str = "unknown"
    confidence: float = 0.0
    caution_level: str = "unknown"


@dataclass(frozen=True)
class PredictionScenarioOutput:
    prediction_type: str = "prediction_scenario_output"
    prediction_version: str = DEFAULT_PREDICTION_SYSTEM_VERSION
    source_kind: str = "prediction_system_input"
    market_uid: str | None = None
    event_ts: str | None = None
    freshness: str = "UNKNOWN"
    is_stale: bool | None = None
    current_regime_state: str = "unknown"
    current_hypothesis_health: str = "unknown"
    current_confidence: float = 0.0
    current_caution_level: str = "unknown"
    outlooks: tuple[PredictionScenarioHorizonOutput, ...] = field(default_factory=tuple)
    invalidation_state: str = "unknown"
    invalidation_signals: tuple[str, ...] = field(default_factory=tuple)
    scenario_switch_hint: str = "unknown"
    scenario_trace: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)
    evidence_trace: PredictionEvidenceTrace = field(default_factory=PredictionEvidenceTrace)
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PredictionSystemInput:
    system_type: str = "prediction_system_input"
    system_version: str = DEFAULT_PREDICTION_SYSTEM_VERSION
    source_kind: str = DEFAULT_PREDICTION_SYSTEM_SOURCE_KIND
    market_uid: str | None = None
    event_ts: str | None = None
    freshness: str = "UNKNOWN"
    is_stale: bool | None = None
    requested_horizons: tuple[str, ...] = field(
        default_factory=lambda: DEFAULT_REQUESTED_HORIZONS
    )
    evidence_bundle: PredictionEvidenceBundle = field(
        default_factory=PredictionEvidenceBundle
    )
    evidence_trace: PredictionEvidenceTrace = field(
        default_factory=PredictionEvidenceTrace
    )
    diagnostics: dict[str, Any] = field(default_factory=dict)