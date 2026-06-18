# path: ./btcts_next/src/btcts/prediction/contracts.py
# desc: Common prediction output and inference bundle contracts. Non-executing; no collection, broker, or AutoTrade side effects.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Tuple

from .horizons import PredictionHorizon


class PredictionFamily(str, Enum):
    MARKET_REGIME = "market_regime"
    TREND_BIAS = "trend_bias"
    REVERSAL_ZONE = "reversal_zone"
    VOLATILITY_RISK = "volatility_risk"
    LIQUIDITY_EXECUTION_QUALITY = "liquidity_execution_quality"
    BREAKOUT_FALSE_BREAK = "breakout_false_break"
    OPPORTUNITY_PARTICIPATION = "opportunity_participation"
    CROSS_VENUE_CONFIRMATION = "cross_venue_confirmation"
    MACRO_RISK_CONTEXT = "macro_risk_context"
    HUMAN_TECHNICAL_STRUCTURE = "human_technical_structure"
    ALGORITHMIC_PARTICIPANT_FOOTPRINT = "algorithmic_participant_footprint"


class PredictionConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SourceIdentity:
    source_id: str
    source_family: str
    venue: str | None = None
    symbol: str | None = None
    market_role: str = "reference"
    public_data_only: bool = True
    execution_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ParameterSetIdentity:
    parameter_set_id: str
    parameter_family: str
    version: str
    status: str = "draft"
    created_by: str = "system"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PredictionOutput:
    prediction_id: str
    generated_at: str
    family: PredictionFamily
    horizon: PredictionHorizon
    parameter_set: ParameterSetIdentity
    sources: Tuple[SourceIdentity, ...] = ()
    confidence: PredictionConfidence = PredictionConfidence.UNKNOWN
    primary_label: str = "unknown"
    score: float | None = None
    drivers: Tuple[str, ...] = ()
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    values: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "generated_at": self.generated_at,
            "family": self.family.value,
            "horizon": self.horizon.to_dict(),
            "parameter_set": self.parameter_set.to_dict(),
            "sources": [source.to_dict() for source in self.sources],
            "confidence": self.confidence.value,
            "primary_label": self.primary_label,
            "score": self.score,
            "drivers": list(self.drivers),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "values": dict(self.values),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
        }


@dataclass(frozen=True)
class InferenceBundle:
    bundle_id: str
    generated_at: str
    logic_version: str
    outputs: Tuple[PredictionOutput, ...]
    source_quality_summary: Mapping[str, Any] = field(default_factory=dict)
    cross_family_agreement: Mapping[str, Any] = field(default_factory=dict)
    risk_context: Mapping[str, Any] = field(default_factory=dict)
    operator_explanation: Tuple[str, ...] = ()
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False

    def families_present(self) -> Tuple[str, ...]:
        return tuple(dict.fromkeys(output.family.value for output in self.outputs))

    def horizons_present_sec(self) -> Tuple[int, ...]:
        return tuple(dict.fromkeys(int(output.horizon.horizon_sec) for output in self.outputs))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "generated_at": self.generated_at,
            "logic_version": self.logic_version,
            "outputs": [output.to_dict() for output in self.outputs],
            "families_present": list(self.families_present()),
            "horizons_present_sec": list(self.horizons_present_sec()),
            "source_quality_summary": dict(self.source_quality_summary),
            "cross_family_agreement": dict(self.cross_family_agreement),
            "risk_context": dict(self.risk_context),
            "operator_explanation": list(self.operator_explanation),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
        }
