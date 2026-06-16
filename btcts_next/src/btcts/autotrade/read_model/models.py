# path: ./btcts_next/src/btcts/autotrade/read_model/models.py
# desc: Non-UI AutoTrade snapshot, temporal-flow, and 5-minute forecast data contracts.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, Tuple


class GroundDirection(str, Enum):
    BUY_LEANING = "buy_leaning"
    SELL_LEANING = "sell_leaning"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ForecastDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    RANGE = "range"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"


class ForecastExpectedChange(str, Enum):
    STRENGTHEN_BUY = "strengthen_buy"
    STRENGTHEN_SELL = "strengthen_sell"
    MEAN_REVERT = "mean_revert"
    BREAKOUT_RISK = "breakout_risk"
    FADE = "fade"
    UNKNOWN = "unknown"


class ForecastOutcomeResult(str, Enum):
    HIT = "hit"
    PARTIAL = "partial"
    MISS = "miss"
    UNSCORABLE = "unscorable"


@dataclass(frozen=True)
class GroundState:
    direction: GroundDirection = GroundDirection.UNKNOWN
    confidence: Confidence = Confidence.LOW
    reason_codes: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["direction"] = self.direction.value
        data["confidence"] = self.confidence.value
        return data


@dataclass(frozen=True)
class SnapshotUsability:
    regime: bool = False
    liquidity: bool = False
    trade: bool = False
    l4: bool = False
    temporal: bool = False

    @property
    def live_inputs_usable(self) -> bool:
        return self.regime and self.liquidity and self.trade and self.temporal

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["live_inputs_usable"] = self.live_inputs_usable
        return data


@dataclass(frozen=True)
class CurrentMarketInputs:
    spread: float | None = None
    imbalance: float | None = None
    wall_ratio: float | None = None
    wall_side: str | None = None
    trade_delta: float | None = None
    price: float | None = None
    mid_price: float | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TemporalFlowFeatures:
    windows_sec: Tuple[int, ...] = (15, 30, 60, 180, 300)
    generated_at: str | None = None
    source_snapshot_ids: Tuple[str, ...] = ()
    max_feature_age_sec: float | None = None
    usable: bool = False
    blocked_by: Tuple[str, ...] = ()
    temporal_liquidity_flow: Dict[str, Any] = field(default_factory=dict)
    temporal_price_flow: Dict[str, Any] = field(default_factory=dict)
    temporal_pressure_flow: Dict[str, Any] = field(default_factory=dict)
    temporal_pattern_flags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AutoTradeSnapshot:
    snapshot_id: str
    created_at: str
    market_uid: str
    parameter_set_id: str
    logic_version: str
    effective_event_ts: str | None
    ground: GroundState
    usability: SnapshotUsability
    inputs: CurrentMarketInputs
    temporal_flow: TemporalFlowFeatures
    source_refs: Dict[str, Any] = field(default_factory=dict)
    stale_reasons: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["ground"] = self.ground.to_dict()
        data["usability"] = self.usability.to_dict()
        data["inputs"] = self.inputs.to_dict()
        data["temporal_flow"] = self.temporal_flow.to_dict()
        return data


@dataclass(frozen=True)
class Forecast5m:
    forecast_id: str
    created_at: str
    target_ts: str
    horizon_sec: int
    source_snapshot_id: str
    parameter_set_id: str
    logic_version: str
    base_ground_at_forecast: GroundState
    forecast_direction: ForecastDirection
    expected_change: ForecastExpectedChange
    confidence: Confidence
    drivers: Tuple[str, ...] = ()
    blocked_by: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["base_ground_at_forecast"] = self.base_ground_at_forecast.to_dict()
        data["forecast_direction"] = self.forecast_direction.value
        data["expected_change"] = self.expected_change.value
        data["confidence"] = self.confidence.value
        return data


@dataclass(frozen=True)
class ActualFiveMinuteChange:
    direction_change: str = "unknown"
    price_move: float | None = None
    spread_change: float | None = None
    imbalance_change: float | None = None
    wall_ratio_change: float | None = None
    trade_delta_change: float | None = None
    volatility_change: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ForecastScore:
    result: ForecastOutcomeResult
    direction_hit: bool = False
    change_type_hit: bool = False
    confidence_calibration: str = "unknown"
    usefulness: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["result"] = self.result.value
        return data


@dataclass(frozen=True)
class ForecastOutcome:
    forecast_id: str
    resolved_at: str
    target_ts: str
    actual_snapshot_id: str | None
    actual_ground: GroundState
    actual_change: ActualFiveMinuteChange
    score: ForecastScore
    divergence_reasons: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["actual_ground"] = self.actual_ground.to_dict()
        data["actual_change"] = self.actual_change.to_dict()
        data["score"] = self.score.to_dict()
        return data
