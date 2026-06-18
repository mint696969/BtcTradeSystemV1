# path: ./btcts_next/src/btcts/prediction/feature_registry.py
# desc: Non-executing feature registry contracts for prediction foundation extensibility.

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Tuple

from .contracts import PredictionFamily

LOGIC_VERSION = "prediction_feature_registry.s125.v1"
DEFAULT_HORIZONS_SEC: Tuple[int, ...] = (15, 30, 60, 180, 300, 900, 1800, 3600, 14400, 86400)


class FeatureFamily(str, Enum):
    OHLCV = "ohlcv"
    VOLATILITY = "volatility"
    LIQUIDITY = "liquidity"
    ORDERBOOK_PRESSURE = "orderbook_pressure"
    TRADEFLOW = "tradeflow"
    SPOT_FX_BASIS = "spot_fx_basis"
    CROSS_VENUE = "cross_venue"
    HUMAN_TECHNICAL = "human_technical"
    MACRO_CONTEXT = "macro_context"
    ALGORITHMIC_FOOTPRINT = "algorithmic_footprint"
    OPPORTUNITY = "opportunity"


@dataclass(frozen=True)
class FeatureSpec:
    feature_id: str
    feature_family: FeatureFamily
    version: str = "0.1.0"
    supported_horizons_sec: Tuple[int, ...] = DEFAULT_HORIZONS_SEC
    required_source_families: Tuple[str, ...] = ()
    used_by_prediction_families: Tuple[PredictionFamily, ...] = ()
    description: str = ""
    read_only: bool = True
    non_executing: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["feature_family"] = self.feature_family.value
        data["supported_horizons_sec"] = list(self.supported_horizons_sec)
        data["required_source_families"] = list(self.required_source_families)
        data["used_by_prediction_families"] = [family.value for family in self.used_by_prediction_families]
        data["logic_version"] = LOGIC_VERSION
        return data


@dataclass(frozen=True)
class FeatureRegistryEntry:
    spec: FeatureSpec
    enabled_by_default: bool = True
    implementation_status: str = "contract_only"
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spec": self.spec.to_dict(),
            "enabled_by_default": self.enabled_by_default,
            "implementation_status": self.implementation_status,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
        }


def build_default_feature_registry() -> Tuple[FeatureRegistryEntry, ...]:
    rows = (
        ("ohlcv_multi_timeframe", FeatureFamily.OHLCV, ("provided_or_canonical_trade_rows",), (PredictionFamily.MARKET_REGIME, PredictionFamily.HUMAN_TECHNICAL_STRUCTURE, PredictionFamily.BREAKOUT_FALSE_BREAK), "multi-timeframe candle structure"),
        ("realized_volatility_atr", FeatureFamily.VOLATILITY, ("ohlcv",), (PredictionFamily.VOLATILITY_RISK, PredictionFamily.MARKET_REGIME), "volatility, ATR, and range width"),
        ("liquidity_execution_quality", FeatureFamily.LIQUIDITY, ("bitflyer_fx_public_board",), (PredictionFamily.LIQUIDITY_EXECUTION_QUALITY,), "spread, depth, slippage, and book stability"),
        ("orderbook_pressure", FeatureFamily.ORDERBOOK_PRESSURE, ("public_orderbook",), (PredictionFamily.TREND_BIAS, PredictionFamily.MARKET_REGIME), "imbalance, wall ratio, and pressure"),
        ("tradeflow_dynamics", FeatureFamily.TRADEFLOW, ("public_trades",), (PredictionFamily.TREND_BIAS,), "trade delta, trade density, and aggressive flow"),
        ("spot_fx_basis", FeatureFamily.SPOT_FX_BASIS, ("bitflyer_spot_public", "bitflyer_fx_public"), (PredictionFamily.MARKET_REGIME, PredictionFamily.CROSS_VENUE_CONFIRMATION), "spot-FX divergence and basis"),
        ("cross_venue_confirmation", FeatureFamily.CROSS_VENUE, ("external_public_market_data",), (PredictionFamily.CROSS_VENUE_CONFIRMATION, PredictionFamily.BREAKOUT_FALSE_BREAK), "global venue agreement and lead/lag"),
        ("human_technical_structure", FeatureFamily.HUMAN_TECHNICAL, ("ohlcv",), (PredictionFamily.HUMAN_TECHNICAL_STRUCTURE, PredictionFamily.REVERSAL_ZONE), "support/resistance, VWAP, MA, wick/retest structure"),
        ("macro_risk_context", FeatureFamily.MACRO_CONTEXT, ("macro_public_context",), (PredictionFamily.MACRO_RISK_CONTEXT,), "risk-on/off and event-window context"),
        ("algorithmic_participant_footprint", FeatureFamily.ALGORITHMIC_FOOTPRINT, ("public_orderbook", "public_trades", "cross_venue"), (PredictionFamily.ALGORITHMIC_PARTICIPANT_FOOTPRINT,), "wall vanish, stop-run, crowding, and reaction-speed footprints"),
        ("opportunity_participation", FeatureFamily.OPPORTUNITY, ("decision_and_outcome_ledgers",), (PredictionFamily.OPPORTUNITY_PARTICIPATION,), "near-miss and wait-too-much diagnostics"),
    )
    return tuple(
        FeatureRegistryEntry(
            spec=FeatureSpec(
                feature_id=feature_id,
                feature_family=family,
                required_source_families=source_families,
                used_by_prediction_families=prediction_families,
                description=description,
            )
        )
        for feature_id, family, source_families, prediction_families, description in rows
    )


def feature_registry_by_id() -> Dict[str, FeatureRegistryEntry]:
    return {entry.spec.feature_id: entry for entry in build_default_feature_registry()}
