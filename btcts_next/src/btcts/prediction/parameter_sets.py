# path: ./btcts_next/src/btcts/prediction/parameter_sets.py
# desc: Immutable parameter-set skeletons for all prediction families. Contract-only; no live mutation or execution behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from typing import Any, Dict, Mapping, Tuple, Type

from .contracts import ParameterSetIdentity, PredictionFamily
from .horizons import CONTEXT_HORIZONS_SEC, EXECUTION_MICRO_HORIZONS_SEC, PRIMARY_TRADE_HORIZONS_SEC

LOGIC_VERSION = "prediction_parameter_sets.s123.v1"
ALL_DEFAULT_HORIZONS_SEC: Tuple[int, ...] = EXECUTION_MICRO_HORIZONS_SEC + PRIMARY_TRADE_HORIZONS_SEC + CONTEXT_HORIZONS_SEC


class PredictionParameterSetStatus(str, Enum):
    DRAFT = "draft"
    SHADOW = "shadow"
    PAPER = "paper"
    LIVE_ACTIVE = "live_active"
    RETIRED = "retired"
    ROLLBACK_CANDIDATE = "rollback_candidate"


@dataclass(frozen=True)
class PredictionParameterSetBase:
    parameter_set_id: str
    family: PredictionFamily
    parameter_family: str
    version: str = "0.1.0"
    status: PredictionParameterSetStatus = PredictionParameterSetStatus.DRAFT
    created_at: str = "2026-06-18T00:00:00Z"
    created_by: str = "system"
    change_reason: str = "initial_prediction_parameter_set_skeleton"
    logic_version: str = LOGIC_VERSION
    supported_horizons_sec: Tuple[int, ...] = ALL_DEFAULT_HORIZONS_SEC
    required_feature_families: Tuple[str, ...] = ()
    thresholds: Mapping[str, Any] = field(default_factory=dict)
    weights: Mapping[str, float] = field(default_factory=dict)
    notes: str = "contract-only; no collection, execution, or live mutation"
    read_only: bool = True
    non_executing: bool = True
    live_mutation_allowed: bool = False

    def identity(self) -> ParameterSetIdentity:
        return ParameterSetIdentity(
            parameter_set_id=self.parameter_set_id,
            parameter_family=self.parameter_family,
            version=self.version,
            status=self.status.value,
            created_by=self.created_by,
        )

    def activate_shadow(self) -> "PredictionParameterSetBase":
        return replace(self, status=PredictionParameterSetStatus.SHADOW, change_reason="activate_shadow_copy")

    def retire(self) -> "PredictionParameterSetBase":
        return replace(self, status=PredictionParameterSetStatus.RETIRED, change_reason="retire_copy")

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["family"] = self.family.value
        data["status"] = self.status.value
        data["supported_horizons_sec"] = list(self.supported_horizons_sec)
        data["required_feature_families"] = list(self.required_feature_families)
        data["thresholds"] = dict(self.thresholds)
        data["weights"] = dict(self.weights)
        data["identity"] = self.identity().to_dict()
        return data


@dataclass(frozen=True)
class MarketRegimePredictionParameterSet(PredictionParameterSetBase):
    parameter_set_id: str = "market_regime_prediction_v0_1_0"
    family: PredictionFamily = PredictionFamily.MARKET_REGIME
    parameter_family: str = "MarketRegimePredictionParameterSet"
    required_feature_families: Tuple[str, ...] = ("ohlcv", "volatility", "liquidity", "orderbook_pressure", "spot_fx_basis")
    thresholds: Mapping[str, Any] = field(default_factory=lambda: {
        "trend_strength_min": 0.65,
        "range_score_min": 0.60,
        "volatile_score_min": 0.75,
        "thin_liquidity_score_min": 0.70,
    })


@dataclass(frozen=True)
class TrendPredictionParameterSet(PredictionParameterSetBase):
    parameter_set_id: str = "trend_bias_prediction_v0_1_0"
    family: PredictionFamily = PredictionFamily.TREND_BIAS
    parameter_family: str = "TrendPredictionParameterSet"
    required_feature_families: Tuple[str, ...] = ("returns", "moving_average_slope", "tradeflow", "orderbook_pressure", "cross_venue_lead_lag")
    thresholds: Mapping[str, Any] = field(default_factory=lambda: {
        "long_bias_score_min": 0.60,
        "short_bias_score_min": 0.60,
        "no_edge_band": 0.10,
    })


@dataclass(frozen=True)
class ReversalPredictionParameterSet(PredictionParameterSetBase):
    parameter_set_id: str = "reversal_zone_prediction_v0_1_0"
    family: PredictionFamily = PredictionFamily.REVERSAL_ZONE
    parameter_family: str = "ReversalPredictionParameterSet"
    required_feature_families: Tuple[str, ...] = ("recent_high_low", "range_boundary", "vwap", "wall_persistence", "absorption", "volatility_exhaustion")
    thresholds: Mapping[str, Any] = field(default_factory=lambda: {
        "zone_confidence_min": 0.55,
        "invalidation_distance_atr_mult": 0.75,
        "reaction_score_min": 0.58,
    })


@dataclass(frozen=True)
class VolatilityRiskPredictionParameterSet(PredictionParameterSetBase):
    parameter_set_id: str = "volatility_risk_prediction_v0_1_0"
    family: PredictionFamily = PredictionFamily.VOLATILITY_RISK
    parameter_family: str = "VolatilityRiskPredictionParameterSet"
    required_feature_families: Tuple[str, ...] = ("realized_volatility", "atr", "range_width", "shock_detection")
    thresholds: Mapping[str, Any] = field(default_factory=lambda: {
        "compressed_volatility_max": 0.25,
        "expanding_volatility_min": 0.70,
        "shock_score_min": 0.85,
    })


@dataclass(frozen=True)
class LiquidityExecutionQualityParameterSet(PredictionParameterSetBase):
    parameter_set_id: str = "liquidity_execution_quality_prediction_v0_1_0"
    family: PredictionFamily = PredictionFamily.LIQUIDITY_EXECUTION_QUALITY
    parameter_family: str = "LiquidityExecutionQualityParameterSet"
    required_feature_families: Tuple[str, ...] = ("spread", "depth", "wall_persistence", "micro_flow", "fx_book_stability")
    thresholds: Mapping[str, Any] = field(default_factory=lambda: {
        "max_spread_score": 0.65,
        "min_depth_score": 0.50,
        "slippage_risk_block_min": 0.80,
    })


@dataclass(frozen=True)
class BreakoutFalseBreakPredictionParameterSet(PredictionParameterSetBase):
    parameter_set_id: str = "breakout_false_break_prediction_v0_1_0"
    family: PredictionFamily = PredictionFamily.BREAKOUT_FALSE_BREAK
    parameter_family: str = "BreakoutFalseBreakPredictionParameterSet"
    required_feature_families: Tuple[str, ...] = ("range_boundary", "volume_confirmation", "retest_state", "wick_structure", "cross_venue_confirmation")
    thresholds: Mapping[str, Any] = field(default_factory=lambda: {
        "breakout_probability_min": 0.62,
        "false_break_risk_block_min": 0.70,
        "retest_confirmation_min": 0.55,
    })


@dataclass(frozen=True)
class OpportunityParticipationParameterSet(PredictionParameterSetBase):
    parameter_set_id: str = "opportunity_participation_prediction_v0_1_0"
    family: PredictionFamily = PredictionFamily.OPPORTUNITY_PARTICIPATION
    parameter_family: str = "OpportunityParticipationParameterSet"
    required_feature_families: Tuple[str, ...] = ("blocked_reason_history", "near_miss", "entry_quality_gap", "outcome_ledger")
    thresholds: Mapping[str, Any] = field(default_factory=lambda: {
        "opportunity_score_watch_min": 0.55,
        "opportunity_score_review_min": 0.70,
        "max_entry_quality_gap_for_near_miss": 8,
    })


@dataclass(frozen=True)
class CrossVenueConfirmationParameterSet(PredictionParameterSetBase):
    parameter_set_id: str = "cross_venue_confirmation_prediction_v0_1_0"
    family: PredictionFamily = PredictionFamily.CROSS_VENUE_CONFIRMATION
    parameter_family: str = "CrossVenueConfirmationParameterSet"
    required_feature_families: Tuple[str, ...] = ("global_reference_price", "basis", "lead_lag", "external_volume", "venue_agreement")
    thresholds: Mapping[str, Any] = field(default_factory=lambda: {
        "global_agreement_min": 0.60,
        "basis_dislocation_warn_min": 0.50,
        "bitflyer_lag_candidate_min": 0.55,
    })


@dataclass(frozen=True)
class MacroRiskContextParameterSet(PredictionParameterSetBase):
    parameter_set_id: str = "macro_risk_context_prediction_v0_1_0"
    family: PredictionFamily = PredictionFamily.MACRO_RISK_CONTEXT
    parameter_family: str = "MacroRiskContextParameterSet"
    required_feature_families: Tuple[str, ...] = ("usd_jpy", "usd_proxy", "rates_proxy", "equity_risk_proxy", "economic_calendar")
    thresholds: Mapping[str, Any] = field(default_factory=lambda: {
        "macro_event_window_warn_min": 0.60,
        "risk_off_score_warn_min": 0.65,
        "risk_context_confidence_min": 0.40,
    })


@dataclass(frozen=True)
class HumanTechnicalStructureParameterSet(PredictionParameterSetBase):
    parameter_set_id: str = "human_technical_structure_prediction_v0_1_0"
    family: PredictionFamily = PredictionFamily.HUMAN_TECHNICAL_STRUCTURE
    parameter_family: str = "HumanTechnicalStructureParameterSet"
    required_feature_families: Tuple[str, ...] = ("support_resistance", "range_boundary", "retest", "higher_high_lower_low", "wick_rejection", "moving_average", "vwap")
    thresholds: Mapping[str, Any] = field(default_factory=lambda: {
        "structure_confidence_min": 0.55,
        "support_resistance_reaction_min": 0.50,
        "wick_rejection_score_min": 0.58,
    })


@dataclass(frozen=True)
class AlgorithmicParticipantFootprintParameterSet(PredictionParameterSetBase):
    parameter_set_id: str = "algorithmic_participant_footprint_prediction_v0_1_0"
    family: PredictionFamily = PredictionFamily.ALGORITHMIC_PARTICIPANT_FOOTPRINT
    parameter_family: str = "AlgorithmicParticipantFootprintParameterSet"
    required_feature_families: Tuple[str, ...] = ("orderbook_update_burst", "wall_vanish", "stop_run", "cross_venue_synchronization", "reaction_speed", "crowding_proxy")
    thresholds: Mapping[str, Any] = field(default_factory=lambda: {
        "liquidity_mirage_risk_warn_min": 0.65,
        "stop_run_risk_warn_min": 0.65,
        "crowding_risk_warn_min": 0.70,
        "avoid_chase_score_min": 0.75,
    })


_PARAMETER_SET_BY_FAMILY: Dict[PredictionFamily, Type[PredictionParameterSetBase]] = {
    PredictionFamily.MARKET_REGIME: MarketRegimePredictionParameterSet,
    PredictionFamily.TREND_BIAS: TrendPredictionParameterSet,
    PredictionFamily.REVERSAL_ZONE: ReversalPredictionParameterSet,
    PredictionFamily.VOLATILITY_RISK: VolatilityRiskPredictionParameterSet,
    PredictionFamily.LIQUIDITY_EXECUTION_QUALITY: LiquidityExecutionQualityParameterSet,
    PredictionFamily.BREAKOUT_FALSE_BREAK: BreakoutFalseBreakPredictionParameterSet,
    PredictionFamily.OPPORTUNITY_PARTICIPATION: OpportunityParticipationParameterSet,
    PredictionFamily.CROSS_VENUE_CONFIRMATION: CrossVenueConfirmationParameterSet,
    PredictionFamily.MACRO_RISK_CONTEXT: MacroRiskContextParameterSet,
    PredictionFamily.HUMAN_TECHNICAL_STRUCTURE: HumanTechnicalStructureParameterSet,
    PredictionFamily.ALGORITHMIC_PARTICIPANT_FOOTPRINT: AlgorithmicParticipantFootprintParameterSet,
}


def default_prediction_parameter_set_for_family(family: PredictionFamily | str) -> PredictionParameterSetBase:
    normalized = family if isinstance(family, PredictionFamily) else PredictionFamily(str(family))
    cls = _PARAMETER_SET_BY_FAMILY[normalized]
    return cls()


def build_default_prediction_parameter_sets() -> Tuple[PredictionParameterSetBase, ...]:
    return tuple(default_prediction_parameter_set_for_family(family) for family in PredictionFamily)
