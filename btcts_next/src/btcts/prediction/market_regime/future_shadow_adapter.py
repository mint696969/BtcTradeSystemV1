# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_adapter.py
# desc: Pure MR-F5.4 adapter from explicit feature bundle and signal-score report to shadow-only future MarketRegime forecasts. No reads, writes, UI, scheduler, broker, or AutoTrade behavior.

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from types import MappingProxyType
from typing import Any, Dict, Mapping, Tuple

from .contracts import FeatureGroup, MarketRegimeCode
from .features import MarketRegimeFeatureBundle
from .future_baseline_model import (
    MARKET_REGIME_FUTURE_BASELINE_LOGIC_VERSION,
    MARKET_REGIME_FUTURE_BASELINE_MODEL_ID,
    FutureBaselineEvidence,
    forecast_future_market_regime_baseline,
)
from .future_forecast_contract import (
    FUTURE_MARKET_REGIME_HORIZONS_SEC,
    FutureForecastStatus,
    MarketRegimeFutureForecast,
    validate_future_forecast_set,
)
from .future_target_definition import future_target_definitions_by_horizon
from .future_shadow_candidate_registry import BASELINE_CANDIDATE, FutureShadowCandidateParameters

MARKET_REGIME_FUTURE_SHADOW_ADAPTER_VERSION = "prediction.market_regime.future_shadow_adapter.mr_f5_4.v2"
MARKET_REGIME_FUTURE_SHADOW_PACKET_VERSION = "prediction.market_regime.future_shadow_packet.mr_f5_4.v2"


@dataclass(frozen=True)
class MarketRegimeFutureShadowPacket:
    generated_at: str
    origin_current_state: MarketRegimeCode
    feature_snapshot_ref: str
    forecasts: Tuple[MarketRegimeFutureForecast, ...]
    adapter_version: str = MARKET_REGIME_FUTURE_SHADOW_ADAPTER_VERSION
    packet_version: str = MARKET_REGIME_FUTURE_SHADOW_PACKET_VERSION

    def __post_init__(self) -> None:
        if not self.generated_at.strip() or not self.feature_snapshot_ref.strip():
            raise ValueError("future_shadow_packet_identity_missing")
        if not isinstance(self.origin_current_state, MarketRegimeCode):
            raise ValueError("future_shadow_packet_origin_state_invalid")
        validate_future_forecast_set(self.forecasts)
        if any(item.origin_timestamp != self.generated_at for item in self.forecasts):
            raise ValueError("future_shadow_packet_origin_timestamp_mismatch")
        if any(item.origin_current_state is not self.origin_current_state for item in self.forecasts):
            raise ValueError("future_shadow_packet_origin_state_mismatch")
        if any(item.feature_snapshot_ref != self.feature_snapshot_ref for item in self.forecasts):
            raise ValueError("future_shadow_packet_feature_snapshot_mismatch")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "packet_version": self.packet_version,
            "adapter_version": self.adapter_version,
            "generated_at": self.generated_at,
            "origin_current_state": self.origin_current_state.value,
            "feature_snapshot_ref": self.feature_snapshot_ref,
            "shadow_only": True,
            "canonical_replacement": False,
            "forecast_count": len(self.forecasts),
            "forecasts": [item.to_dict() for item in self.forecasts],
            "safety": {
                "read_only": True,
                "writes_dhot": False,
                "ui_behavior_change": False,
                "canonical_future_label_replacement": False,
                "broker_private_api_allowed": False,
                "autotrade_trigger_allowed": False,
                "order_submission_allowed": False,
                "parameter_auto_promotion_allowed": False,
                "live_parameter_apply_allowed": False,
            },
        }


def market_regime_feature_snapshot_ref(bundle: MarketRegimeFeatureBundle) -> str:
    if not isinstance(bundle, MarketRegimeFeatureBundle):
        raise ValueError("future_shadow_feature_bundle_invalid")
    parts = [bundle.generated_at, bundle.logic_version, str(bundle.source_snapshot_ok)]
    for item in sorted(bundle.coverage, key=lambda row: row.feature_group.value):
        parts.extend((item.feature_group.value, str(item.available), item.freshness_state.value, *item.used_sources, *item.missing_sources))
    for signal in sorted(bundle.signals, key=lambda row: (row.feature_group.value, row.name)):
        parts.extend((signal.feature_group.value, signal.name, str(signal.available), repr(signal.value), *signal.source_refs))
    digest = sha256("|".join(parts).encode("utf-8")).hexdigest()
    return f"market_regime_feature_snapshot:{digest}"


def _available_feature_families(bundle: MarketRegimeFeatureBundle) -> Tuple[str, ...]:
    available = {item.feature_group.value for item in bundle.coverage if item.available}
    available.update(signal.feature_group.value for signal in bundle.signals if signal.available)
    available_signal_names = {signal.name.strip() for signal in bundle.signals if signal.available and signal.name.strip()}
    # MR-F5 target names that map to existing feature groups or explicit signal names.
    if FeatureGroup.LIQUIDITY.value in available:
        available.add("microprice")
    for explicit_family in ("session_context", "macro_context", "orderflow", "cross_venue", "change_point"):
        if explicit_family in available_signal_names:
            available.add(explicit_family)
    return tuple(sorted(available))


def _rows_by_horizon(signal_score_report: Mapping[str, Any]) -> Mapping[int, Mapping[str, Any]]:
    rows: dict[int, Mapping[str, Any]] = {}
    for raw in signal_score_report.get("horizons", ()):
        if not isinstance(raw, Mapping):
            raise ValueError("future_shadow_signal_row_not_mapping")
        horizon = int(raw.get("horizon_sec") or 0)
        if horizon not in FUTURE_MARKET_REGIME_HORIZONS_SEC:
            raise ValueError(f"future_shadow_unsupported_horizon:{horizon}")
        expected_key = f"{horizon}s"
        if str(raw.get("horizon_key") or "") != expected_key:
            raise ValueError(
                f"future_shadow_horizon_key_mismatch:{horizon}:"
                f"expected={expected_key}:actual={raw.get('horizon_key')}"
            )
        if horizon in rows:
            raise ValueError(f"future_shadow_duplicate_horizon:{horizon}")
        rows[horizon] = raw
    return MappingProxyType(rows)


def _scores(row: Mapping[str, Any]) -> Mapping[MarketRegimeCode, float]:
    raw_scores = row.get("regime_scores")
    if not isinstance(raw_scores, Mapping):
        raise ValueError("future_shadow_regime_scores_missing")
    result: dict[MarketRegimeCode, float] = {}
    for key, value in raw_scores.items():
        try:
            regime = key if isinstance(key, MarketRegimeCode) else MarketRegimeCode(str(key))
        except ValueError as exc:
            raise ValueError(f"future_shadow_regime_code_invalid:{key}") from exc
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"future_shadow_regime_score_invalid:{regime.value}:non_numeric") from exc
        if not isfinite(numeric) or numeric < 0.0:
            raise ValueError(f"future_shadow_regime_score_invalid:{regime.value}:{numeric!r}")
        result[regime] = numeric
    return MappingProxyType(result)


def _invalid_score_abstain(
    *,
    origin_timestamp: str,
    origin_current_state: MarketRegimeCode,
    target_horizon_sec: int,
    feature_snapshot_ref: str,
    candidate: FutureShadowCandidateParameters,
    blocker: str,
) -> MarketRegimeFutureForecast:
    definition = future_target_definitions_by_horizon()[int(target_horizon_sec)]
    return MarketRegimeFutureForecast(
        origin_timestamp=origin_timestamp,
        origin_current_state=origin_current_state,
        target_horizon_sec=target_horizon_sec,
        predicted_future_state=MarketRegimeCode.UNKNOWN,
        status=FutureForecastStatus.ABSTAIN,
        transition_path_candidate=(),
        raw_model_score_or_probability=None,
        feature_snapshot_ref=feature_snapshot_ref,
        model_id=MARKET_REGIME_FUTURE_BASELINE_MODEL_ID,
        logic_version=MARKET_REGIME_FUTURE_BASELINE_LOGIC_VERSION,
        parameter_set_id=candidate.parameter_set_id,
        target_definition_version=definition.target_definition_version,
        invalidation_conditions=(blocker,),
        abstain_reason="invalid_regime_score",
        metadata={
            "shadow_only": True,
            "canonical_replacement": False,
            "candidate_registry_state": candidate.registry_state,
            "blockers": [blocker],
        },
    )


def build_market_regime_future_shadow_packet(
    *,
    feature_bundle: MarketRegimeFeatureBundle,
    signal_score_report: Mapping[str, Any],
    origin_current_state: MarketRegimeCode,
    origin_timestamp_epoch_sec: float,
    source_timestamp_epoch_sec: float,
    candidate: FutureShadowCandidateParameters = BASELINE_CANDIDATE,
) -> MarketRegimeFutureShadowPacket:
    if not feature_bundle.source_snapshot_ok:
        raise ValueError("future_shadow_source_snapshot_not_ok")
    if str(signal_score_report.get("market_regime_only") or "").lower() not in ("true", "1") and signal_score_report.get("market_regime_only") is not True:
        raise ValueError("future_shadow_signal_report_not_market_regime_only")
    rows = _rows_by_horizon(signal_score_report)
    feature_snapshot_ref = market_regime_feature_snapshot_ref(feature_bundle)
    available_families = _available_feature_families(feature_bundle)
    forecasts = []
    for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC:
        row = rows.get(horizon)
        if row is None:
            raise ValueError(f"future_shadow_horizon_score_missing:{horizon}")
        try:
            regime_scores = _scores(row)
        except ValueError as exc:
            blocker = str(exc)
            if not blocker.startswith("future_shadow_regime_score_invalid:"):
                raise
            forecasts.append(
                _invalid_score_abstain(
                    origin_timestamp=feature_bundle.generated_at,
                    origin_current_state=origin_current_state,
                    target_horizon_sec=horizon,
                    feature_snapshot_ref=feature_snapshot_ref,
                    candidate=candidate,
                    blocker=blocker,
                )
            )
            continue
        evidence = FutureBaselineEvidence(
            origin_timestamp=feature_bundle.generated_at,
            origin_current_state=origin_current_state,
            target_horizon_sec=horizon,
            feature_snapshot_ref=feature_snapshot_ref,
            regime_scores=regime_scores,
            available_feature_families=available_families,
            source_timestamp_epoch_sec=source_timestamp_epoch_sec,
            origin_timestamp_epoch_sec=origin_timestamp_epoch_sec,
            invalidation_conditions=tuple(feature_bundle.warnings) + tuple(feature_bundle.missing_sources),
        )
        forecasts.append(forecast_future_market_regime_baseline(evidence, candidate=candidate))
    return MarketRegimeFutureShadowPacket(
        generated_at=feature_bundle.generated_at,
        origin_current_state=origin_current_state,
        feature_snapshot_ref=feature_snapshot_ref,
        forecasts=tuple(forecasts),
    )
