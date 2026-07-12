# path: ./btcts_next/src/btcts/prediction/market_regime/parameter_set.py
# desc: Immutable parameter-set contract for market-regime engine. Proposal-ready, but live apply is disabled.

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Dict, Mapping, Tuple

from .contracts import FeatureGroup

MARKET_REGIME_PARAMETER_SET_VERSION = "prediction.market_regime.parameter_set.ps_q27g.v1"


@dataclass(frozen=True)
class MarketRegimeParameterSet:
    parameter_set_id: str = "market_regime_engine_parameter_set.v1"
    version: str = "0.1.0"
    status: str = "draft"
    created_by: str = "system"
    change_reason: str = "pure_contract_policy_initial"
    supported_horizons_sec: Tuple[int, ...] = (0, 300, 900, 1800, 3600, 21600, 43200, 86400)
    required_feature_groups: Tuple[FeatureGroup, ...] = (
        FeatureGroup.PRICE_STRUCTURE,
        FeatureGroup.VOLATILITY,
        FeatureGroup.LIQUIDITY,
        FeatureGroup.ORDERFLOW,
        FeatureGroup.CROSS_VENUE,
        FeatureGroup.SOURCE_QUALITY,
    )
    thresholds: Mapping[str, Any] = field(default_factory=lambda: {
        "confidence_high_min": 70,
        "confidence_medium_min": 45,
        "unknown_confidence_floor": 0,
        "debounce_required_consensus": 2,
        "debounce_window": 3,
        "minimum_tactical_confidence_percent": 65,
        # MR_A4_CURRENT_L4_THRESHOLD_PARAMETER_SET_2026_07_09
        "current_l4_candle_window": {
            "threshold_set_id": "market_regime.current_l4_candle_thresholds.v1",
            "high_vol_chop_range_bps_min": 180.0,
            "high_vol_chop_abs_net_range_ratio_max": 0.35,
            "directional_abs_net_bps_min": 25.0,
            "directional_abs_net_range_ratio_min": 0.45,
            "low_vol_range_bps_max": 20.0,
        },
        # MR-F4_TRANSITION_AND_PERSISTENCE_POLICY_2026_07_12
        "transition_and_persistence": {
            "minimum_dwell_sec": 300,
            "hysteresis_margin_min": 0.10,
            "change_point_override_min": 0.80,
            "transition_penalty": 0.12,
            "allowed_transitions": {
                "UNKNOWN": [
                    "RANGE", "LOW_VOL_COMPRESSION", "UP_TREND", "DOWN_TREND",
                    "HIGH_VOL_CHOP", "BREAKOUT", "REVERSAL_WATCH", "PANIC_SPIKE",
                ],
                "RANGE": ["RANGE", "LOW_VOL_COMPRESSION", "BREAKOUT", "HIGH_VOL_CHOP"],
                "LOW_VOL_COMPRESSION": ["LOW_VOL_COMPRESSION", "RANGE", "BREAKOUT"],
                "BREAKOUT": ["BREAKOUT", "UP_TREND", "DOWN_TREND", "HIGH_VOL_CHOP", "RANGE"],
                "UP_TREND": ["UP_TREND", "REVERSAL_WATCH", "HIGH_VOL_CHOP", "RANGE"],
                "DOWN_TREND": ["DOWN_TREND", "REVERSAL_WATCH", "HIGH_VOL_CHOP", "RANGE"],
                "REVERSAL_WATCH": ["REVERSAL_WATCH", "RANGE", "UP_TREND", "DOWN_TREND", "HIGH_VOL_CHOP"],
                "HIGH_VOL_CHOP": ["HIGH_VOL_CHOP", "RANGE", "UP_TREND", "DOWN_TREND", "PANIC_SPIKE"],
                "PANIC_SPIKE": ["PANIC_SPIKE", "HIGH_VOL_CHOP", "RANGE"],
            },
            "canonical_application_enabled": True,
            "observation_only": False,
        },
        # MR-F3_EXPLAINABLE_CANDIDATE_SCORING_2026_07_12
        "explainable_candidate_scoring": {
            "volatility_reference_bps": 20.0,
            "spread_stress_bps": 8.0,
            "contradictory_support_max": 0.20,
            "label_selection_min_available_weight": 0.65,
            "label_selection_min_top_score": 0.55,
            "label_selection_min_margin": 0.08,
            "label_selection_required_feature_groups": [
                "price_structure",
                "volatility",
                "liquidity",
                "source_quality",
            ],
            "label_selection_observation_only": True,
        },
    })
    weights: Mapping[str, float] = field(default_factory=lambda: {
        "price_structure": 0.25,
        "volatility": 0.20,
        "liquidity": 0.18,
        "orderflow": 0.17,
        "cross_venue": 0.12,
        "source_quality": 0.08,
    })
    read_only: bool = True
    non_executing: bool = True
    live_parameter_apply_allowed: bool = False
    gpt_parameter_proposal_allowed: bool = True
    human_review_required_before_apply: bool = True
    broker_private_api_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    ledger_append_allowed: bool = False
    runtime_artifact_write_allowed: bool = False

    def with_status(self, status: str, *, change_reason: str) -> "MarketRegimeParameterSet":
        return replace(self, status=status, change_reason=change_reason)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parameter_set_id": self.parameter_set_id,
            "version": self.version,
            "status": self.status,
            "created_by": self.created_by,
            "change_reason": self.change_reason,
            "supported_horizons_sec": list(self.supported_horizons_sec),
            "required_feature_groups": [group.value for group in self.required_feature_groups],
            "thresholds": dict(self.thresholds),
            "weights": dict(self.weights),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "live_parameter_apply_allowed": self.live_parameter_apply_allowed,
            "gpt_parameter_proposal_allowed": self.gpt_parameter_proposal_allowed,
            "human_review_required_before_apply": self.human_review_required_before_apply,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "runtime_artifact_write_allowed": self.runtime_artifact_write_allowed,
        }


def build_default_market_regime_parameter_set() -> MarketRegimeParameterSet:
    return MarketRegimeParameterSet()
