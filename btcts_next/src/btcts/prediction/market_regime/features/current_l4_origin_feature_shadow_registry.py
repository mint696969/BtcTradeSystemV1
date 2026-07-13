# path: ./btcts_next/src/btcts/prediction/market_regime/features/current_l4_origin_feature_shadow_registry.py
# desc: MR-F6.10 immutable shadow-only registry for analysis-backed current-L4 origin feature parameters.

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Tuple

from .current_l4_origin_features import CurrentL4OriginFeatureParameters

CURRENT_L4_ORIGIN_FEATURE_SHADOW_REGISTRY_VERSION = (
    "prediction.market_regime.current_l4_origin_feature_shadow_registry.mr_f6_10.v1"
)
ANALYSIS_EVIDENCE_REF = "docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_10_ORIGIN_FEATURE_PARAMETER_ANALYSIS_EVIDENCE_2026-07-14.md"
ANALYSIS_WINDOW_REF = "2026-06-29T07:38:00Z..2026-07-13T23:05:00Z"
ANALYSIS_SOURCE_ROW_COUNT = 20160
ANALYSIS_ROLLING_VOLATILITY_SAMPLE_COUNT = 10516
ANALYSIS_USABLE_SEGMENT_COUNT = 71


@dataclass(frozen=True)
class CurrentL4OriginFeatureShadowCandidate:
    candidate_id: str
    parameters: CurrentL4OriginFeatureParameters
    ma_analysis_sample_count: int
    ma_sign_change_rate: float
    volatility_band_id: str
    registry_state: str = "shadow"
    selected_for_runtime: bool = False
    live_parameter_apply_allowed: bool = False
    auto_promotion_allowed: bool = False
    canonical_replacement_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("current_l4_origin_shadow_candidate_id_missing")
        if not isinstance(self.parameters, CurrentL4OriginFeatureParameters):
            raise ValueError("current_l4_origin_shadow_parameters_invalid")
        if self.registry_state != "shadow":
            raise ValueError("current_l4_origin_shadow_registry_state_invalid")
        if isinstance(self.ma_analysis_sample_count, bool) or int(self.ma_analysis_sample_count) <= 0:
            raise ValueError("current_l4_origin_shadow_ma_sample_count_invalid")
        rate = float(self.ma_sign_change_rate)
        if not 0.0 <= rate <= 1.0:
            raise ValueError("current_l4_origin_shadow_sign_change_rate_invalid")
        if self.volatility_band_id not in ("interquartile", "central_80_percent"):
            raise ValueError("current_l4_origin_shadow_volatility_band_invalid")
        if self.selected_for_runtime is not False:
            raise ValueError("current_l4_origin_shadow_runtime_selection_not_allowed")
        if self.live_parameter_apply_allowed is not False:
            raise ValueError("current_l4_origin_shadow_live_apply_not_allowed")
        if self.auto_promotion_allowed is not False:
            raise ValueError("current_l4_origin_shadow_auto_promotion_not_allowed")
        if self.canonical_replacement_allowed is not False:
            raise ValueError("current_l4_origin_shadow_canonical_replacement_not_allowed")

    def to_dict(self) -> Mapping[str, object]:
        return MappingProxyType({
            "candidate_id": self.candidate_id,
            "parameter_set_id": self.parameters.parameter_set_id,
            "fast_ma_window_rows": self.parameters.fast_ma_window_rows,
            "slow_ma_window_rows": self.parameters.slow_ma_window_rows,
            "low_volatility_threshold_bps": self.parameters.low_volatility_threshold_bps,
            "high_volatility_threshold_bps": self.parameters.high_volatility_threshold_bps,
            "ma_analysis_sample_count": self.ma_analysis_sample_count,
            "ma_sign_change_rate": self.ma_sign_change_rate,
            "volatility_band_id": self.volatility_band_id,
            "registry_state": "shadow",
            "selected_for_runtime": False,
            "live_parameter_apply_allowed": False,
            "auto_promotion_allowed": False,
            "canonical_replacement_allowed": False,
            "analysis_evidence_ref": ANALYSIS_EVIDENCE_REF,
            "analysis_window_ref": ANALYSIS_WINDOW_REF,
        })


_MA_CANDIDATES = (
    ("ma_3_10", 3, 10, 17161, 0.12575758),
    ("ma_5_20", 5, 20, 14951, 0.06334448),
    ("ma_10_30", 10, 30, 13341, 0.03770615),
    ("ma_15_60", 15, 60, 10516, 0.02063718),
)
_VOLATILITY_BANDS = (
    ("interquartile", 4.47257112, 7.35462997),
    ("central_80_percent", 3.79525581, 10.04311125),
)


def _build_candidates() -> Tuple[CurrentL4OriginFeatureShadowCandidate, ...]:
    result = []
    for ma_id, fast, slow, sample_count, sign_change_rate in _MA_CANDIDATES:
        for band_id, low, high in _VOLATILITY_BANDS:
            candidate_id = f"market_regime.origin_feature.shadow.{ma_id}.{band_id}.v1"
            result.append(CurrentL4OriginFeatureShadowCandidate(
                candidate_id=candidate_id,
                parameters=CurrentL4OriginFeatureParameters(
                    parameter_set_id=candidate_id,
                    fast_ma_window_rows=fast,
                    slow_ma_window_rows=slow,
                    low_volatility_threshold_bps=low,
                    high_volatility_threshold_bps=high,
                ),
                ma_analysis_sample_count=sample_count,
                ma_sign_change_rate=sign_change_rate,
                volatility_band_id=band_id,
            ))
    return tuple(result)


DEFAULT_CURRENT_L4_ORIGIN_FEATURE_SHADOW_REGISTRY = _build_candidates()


def build_default_current_l4_origin_feature_shadow_registry() -> Tuple[CurrentL4OriginFeatureShadowCandidate, ...]:
    return DEFAULT_CURRENT_L4_ORIGIN_FEATURE_SHADOW_REGISTRY


def get_current_l4_origin_feature_shadow_candidate(
    candidate_id: str,
) -> CurrentL4OriginFeatureShadowCandidate:
    requested = str(candidate_id or "").strip()
    if not requested:
        raise ValueError("current_l4_origin_shadow_explicit_candidate_id_required")
    matches = tuple(
        item for item in DEFAULT_CURRENT_L4_ORIGIN_FEATURE_SHADOW_REGISTRY
        if item.candidate_id == requested
    )
    if len(matches) != 1:
        raise KeyError(f"current_l4_origin_shadow_candidate_not_found:{requested}")
    return matches[0]


def validate_current_l4_origin_feature_shadow_registry(
    candidates: Tuple[CurrentL4OriginFeatureShadowCandidate, ...],
) -> Mapping[str, object]:
    failures = []
    ids = tuple(item.candidate_id for item in candidates)
    parameter_ids = tuple(item.parameters.parameter_set_id for item in candidates)
    if len(candidates) != 8:
        failures.append("candidate_count_not_eight")
    if len(ids) != len(set(ids)):
        failures.append("duplicate_candidate_id")
    if len(parameter_ids) != len(set(parameter_ids)):
        failures.append("duplicate_parameter_set_id")
    if any(item.registry_state != "shadow" for item in candidates):
        failures.append("non_shadow_candidate_present")
    if any(item.selected_for_runtime for item in candidates):
        failures.append("runtime_selected_candidate_present")
    return MappingProxyType({
        "schema_version": CURRENT_L4_ORIGIN_FEATURE_SHADOW_REGISTRY_VERSION,
        "ok": not failures,
        "candidate_count": len(candidates),
        "candidate_ids": ids,
        "failures": tuple(failures),
        "analysis_evidence_ref": ANALYSIS_EVIDENCE_REF,
        "analysis_window_ref": ANALYSIS_WINDOW_REF,
        "analysis_source_row_count": ANALYSIS_SOURCE_ROW_COUNT,
        "analysis_rolling_volatility_sample_count": ANALYSIS_ROLLING_VOLATILITY_SAMPLE_COUNT,
        "analysis_usable_segment_count": ANALYSIS_USABLE_SEGMENT_COUNT,
        "active_candidate_count": 0,
        "runtime_selected_candidate_count": 0,
        "live_parameter_apply_allowed": False,
        "auto_promotion_allowed": False,
        "canonical_replacement_allowed": False,
    })
