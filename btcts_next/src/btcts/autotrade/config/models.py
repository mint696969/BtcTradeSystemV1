# path: ./btcts_next/src/btcts/autotrade/config/models.py
# desc: Immutable AutoTrade parameter-set models and defaults schema.

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from typing import Any, Dict, Tuple


class ParameterSetStatus(str, Enum):
    DRAFT = "draft"
    SHADOW = "shadow"
    PAPER = "paper"
    LIVE_ACTIVE = "live_active"
    RETIRED = "retired"
    ROLLBACK_CANDIDATE = "rollback_candidate"


class AggressivenessProfile(str, Enum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    OPPORTUNISTIC = "opportunistic"


class RegimeParameterSetStatus(str, Enum):
    DRAFT = "draft"
    SHADOW = "shadow"
    PAPER = "paper"
    LIVE_ACTIVE = "live_active"
    RETIRED = "retired"
    ROLLBACK_CANDIDATE = "rollback_candidate"


@dataclass(frozen=True)
class RegimeThresholds:
    trend_strength_min: float = 0.65
    range_score_min: float = 0.60
    volatility_spike_threshold: float = 0.75
    liquidity_thin_threshold: float = 0.70
    spread_wide_threshold: float = 0.65
    min_data_freshness_score: float = 0.90


@dataclass(frozen=True)
class RegimeParameterSet:
    regime_parameter_set_id: str
    parent_regime_parameter_set_id: str | None
    status: RegimeParameterSetStatus
    product_type: "ProductType"
    exchange: str
    symbol: str
    created_at: str
    created_by: str
    change_reason: str
    logic_version: str
    thresholds: RegimeThresholds = field(default_factory=RegimeThresholds)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["product_type"] = self.product_type.value
        data["kind"] = "regime"
        return data

    def activate_shadow(self) -> "RegimeParameterSet":
        return replace(self, status=RegimeParameterSetStatus.SHADOW)

    def retire(self) -> "RegimeParameterSet":
        return replace(self, status=RegimeParameterSetStatus.RETIRED)


class ProductType(str, Enum):
    FX = "FX"


@dataclass(frozen=True)
class MarginPolicy:
    leverage_cap: float = 2.0
    normal_margin_target_pct: float = 200.0
    green_margin_buffer_pct: float = 220.0
    caution_margin_threshold_pct: float = 180.0
    attack_caution_threshold_pct: float = 170.0
    attack_margin_floor_pct: float = 150.0
    hard_block_margin_pct: float = 150.0


@dataclass(frozen=True)
class ExposurePolicy:
    live_min_size: str = "broker_product_minimum_confirm_before_live"
    max_open_orders_live_min_size: int = 1
    max_positions_live_min_size: int = 1
    max_add_count_live_min_size: int = 0
    max_add_count_live_controlled_initial: int = 1
    min_spacing_between_adds_sec: int = 180
    no_averaging_down: bool = True
    no_pyramiding_live_min_size: bool = True


@dataclass(frozen=True)
class LossLimits:
    max_loss_per_trade_pct_of_margin: float = 0.25
    max_loss_per_session_pct_of_margin: float = 0.75
    max_loss_per_day_pct_of_margin: float = 1.0
    max_consecutive_losses: int = 3
    max_drawdown_from_daily_peak_pct: float = 1.5
    hard_stop_loss_enabled: bool = True
    time_stop_sec: int = 180
    max_hold_sec: int = 600


@dataclass(frozen=True)
class FreshnessThresholds:
    max_board_age_sec: int = 5
    max_trade_age_sec: int = 10
    max_l4_age_sec: int = 60
    max_account_state_age_sec: int = 5
    max_order_state_age_sec: int = 5
    max_position_state_age_sec: int = 5
    max_heartbeat_age_sec: int = 10
    max_temporal_feature_age_sec: int = 10


@dataclass(frozen=True)
class EntryQualityThresholds:
    live_threshold_balanced: int = 75
    live_threshold_conservative: int = 82
    live_threshold_opportunistic: int = 68
    watch_threshold: int = 55
    paper_threshold: int = 60


@dataclass(frozen=True)
class ParticipationPolicy:
    min_candidate_per_hour_shadow: int = 3
    review_if_allowed_entry_count_zero_for_session: bool = True
    missed_opportunity_tracking: bool = True
    near_miss_setup_library: bool = True
    exploration_quota_shadow_per_session: int = 10
    exploration_quota_paper_per_session: int = 5
    exploration_quota_live: int = 0


@dataclass(frozen=True)
class ForecastPolicy:
    horizon_sec: int = 300
    min_confidence_for_entry_support: str = "medium"
    min_confidence_for_add: str = "medium"
    min_confidence_for_hold_extension: str = "medium"
    low_confidence_can_only_tighten: bool = True
    unknown_adds_no_permission: bool = True


@dataclass(frozen=True)
class TemporalFlowPolicy:
    windows_sec: Tuple[int, ...] = (15, 30, 60, 180, 300)
    min_points_per_window: int = 3
    use_temporal_liquidity_flow: bool = True
    use_temporal_price_flow: bool = True
    use_temporal_pressure_flow: bool = True
    use_temporal_pattern_flags: bool = True
    feature_groups: Tuple[str, ...] = (
        "temporal_liquidity_flow",
        "temporal_price_flow",
        "temporal_pressure_flow",
        "temporal_pattern_flags",
    )


@dataclass(frozen=True)
class CancelRepricePolicy:
    cancel_after_ms: int = 4000
    reprice_after_ms: int = 2500
    cancel_on_forecast_volatile: bool = True
    cancel_on_spread_widening: bool = True
    cancel_on_wall_flip: bool = True
    reprice_on_best_price_move: bool = True


@dataclass(frozen=True)
class AttackModePolicy:
    enabled_default: bool = False
    requires_manual_confirmation: bool = True
    allowed_initially: str = "shadow_paper_only"
    live_requires_live_controlled: bool = True
    margin_floor_pct: float = 150.0
    max_add_count_initial: int = 1
    min_forecast_confidence: str = "medium"
    min_entry_quality: int = 82


@dataclass(frozen=True)
class CostModelPolicy:
    use_spread_cost: bool = True
    use_fee_estimate: bool = True
    use_slippage_buffer: bool = True
    minimum_required_edge_formula: str = "spread_cost + fee_estimate + slippage_buffer + profile_min_edge"


@dataclass(frozen=True)
class AutoManualPolicy:
    manual_approve_required_live_min_size: bool = True
    auto_allowed_shadow: bool = True
    auto_allowed_paper: bool = True
    auto_allowed_armed_dry_run_read_reconcile_only: bool = True
    auto_allowed_live_min_size_default: bool = False


@dataclass(frozen=True)
class ParameterSet:
    parameter_set_id: str
    parent_parameter_set_id: str | None
    status: ParameterSetStatus
    product_type: ProductType
    exchange: str
    symbol: str
    created_at: str
    created_by: str
    change_reason: str
    logic_version: str
    aggressiveness: AggressivenessProfile = AggressivenessProfile.BALANCED
    margin_policy: MarginPolicy = field(default_factory=MarginPolicy)
    exposure_policy: ExposurePolicy = field(default_factory=ExposurePolicy)
    loss_limits: LossLimits = field(default_factory=LossLimits)
    freshness: FreshnessThresholds = field(default_factory=FreshnessThresholds)
    entry_quality: EntryQualityThresholds = field(default_factory=EntryQualityThresholds)
    participation: ParticipationPolicy = field(default_factory=ParticipationPolicy)
    forecast: ForecastPolicy = field(default_factory=ForecastPolicy)
    temporal_flow: TemporalFlowPolicy = field(default_factory=TemporalFlowPolicy)
    cancel_reprice: CancelRepricePolicy = field(default_factory=CancelRepricePolicy)
    attack_mode: AttackModePolicy = field(default_factory=AttackModePolicy)
    cost_model: CostModelPolicy = field(default_factory=CostModelPolicy)
    auto_manual: AutoManualPolicy = field(default_factory=AutoManualPolicy)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["product_type"] = self.product_type.value
        data["aggressiveness"] = self.aggressiveness.value
        return data

    def activate_shadow(self) -> "ParameterSet":
        return replace(self, status=ParameterSetStatus.SHADOW)

    def retire(self) -> "ParameterSet":
        return replace(self, status=ParameterSetStatus.RETIRED)


@dataclass(frozen=True)
class ParameterSetRegistry:
    active_live_parameter_set_id: str | None = None
    active_shadow_parameter_set_ids: Tuple[str, ...] = ()
    last_known_good_parameter_set_id: str | None = None
    rollback_parameter_set_id: str | None = None
    retired_parameter_set_ids: Tuple[str, ...] = ()
    pending_draft_parameter_set_id: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ParameterSetBundleStatus(str, Enum):
    DRAFT = "draft"
    SHADOW = "shadow"
    PAPER = "paper"
    LIVE_ACTIVE = "live_active"
    RETIRED = "retired"
    ROLLBACK_CANDIDATE = "rollback_candidate"


@dataclass(frozen=True)
class ParameterSetBundle:
    parameter_bundle_id: str
    parent_parameter_bundle_id: str | None
    status: ParameterSetBundleStatus
    regime_parameter_set: RegimeParameterSet
    trade_parameter_set: ParameterSet
    created_at: str
    created_by: str
    change_reason: str
    market_uid: str
    product_code: str
    logic_version: str
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        regime_data = self.regime_parameter_set.to_dict()
        trade_data = self.trade_parameter_set.to_dict()
        trade_data["kind"] = "trade"
        return {
            "schema_version": "autotrade_parameter_bundle.v1",
            "parameter_bundle_id": self.parameter_bundle_id,
            "parent_parameter_bundle_id": self.parent_parameter_bundle_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "change_reason": self.change_reason,
            "market_uid": self.market_uid,
            "product_code": self.product_code,
            "logic_version": self.logic_version,
            "regime_parameter_set": regime_data,
            "trade_parameter_set": trade_data,
            "notes": self.notes,
        }

    @property
    def regime_parameter_set_id(self) -> str:
        return self.regime_parameter_set.regime_parameter_set_id

    @property
    def trade_parameter_set_id(self) -> str:
        return self.trade_parameter_set.parameter_set_id


@dataclass(frozen=True)
class ParameterSetBundleRegistry:
    active_shadow_bundle_id: str | None = None
    active_paper_bundle_id: str | None = None
    active_live_bundle_id: str | None = None
    last_known_good_bundle_id: str | None = None
    rollback_bundle_id: str | None = None
    pending_draft_bundle_id: str | None = None
    retired_bundle_ids: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["schema_version"] = "autotrade_parameter_bundle_registry.v1"
        return data

