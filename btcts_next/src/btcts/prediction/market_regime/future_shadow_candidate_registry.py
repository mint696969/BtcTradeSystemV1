# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_candidate_registry.py
# desc: Immutable two-candidate registry for MR-F5 operational shadow comparison; no live apply or auto promotion.

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Tuple


@dataclass(frozen=True)
class FutureShadowCandidateParameters:
    parameter_set_id: str
    short_horizon_minimum_top: float
    short_horizon_minimum_margin: float
    long_horizon_minimum_top: float
    long_horizon_minimum_margin: float
    transition_prior_fraction_of_top: float
    registry_state: str = "shadow"
    live_parameter_apply_allowed: bool = False
    auto_promotion_allowed: bool = False
    canonical_replacement_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.parameter_set_id.strip():
            raise ValueError("future_shadow_candidate_parameter_set_id_missing")
        if self.registry_state not in ("active", "candidate", "shadow"):
            raise ValueError("future_shadow_candidate_registry_state_invalid")
        for name, value in (
            ("short_horizon_minimum_top", self.short_horizon_minimum_top),
            ("short_horizon_minimum_margin", self.short_horizon_minimum_margin),
            ("long_horizon_minimum_top", self.long_horizon_minimum_top),
            ("long_horizon_minimum_margin", self.long_horizon_minimum_margin),
            ("transition_prior_fraction_of_top", self.transition_prior_fraction_of_top),
        ):
            number = float(value)
            if not 0.0 <= number <= 1.0:
                raise ValueError(f"future_shadow_candidate_threshold_invalid:{name}")
        if not 0.0 < float(self.transition_prior_fraction_of_top) < 1.0:
            raise ValueError("future_shadow_candidate_transition_prior_fraction_invalid")
        if self.live_parameter_apply_allowed is not False:
            raise ValueError("future_shadow_candidate_live_apply_not_allowed")
        if self.auto_promotion_allowed is not False:
            raise ValueError("future_shadow_candidate_auto_promotion_not_allowed")
        if self.canonical_replacement_allowed is not False:
            raise ValueError("future_shadow_candidate_canonical_replacement_not_allowed")

    def thresholds_for_horizon(self, horizon_sec: int) -> Tuple[float, float]:
        if int(horizon_sec) <= 3600:
            return (
                float(self.short_horizon_minimum_top),
                float(self.short_horizon_minimum_margin),
            )
        return (
            float(self.long_horizon_minimum_top),
            float(self.long_horizon_minimum_margin),
        )

    def to_dict(self) -> Mapping[str, object]:
        return MappingProxyType({
            "parameter_set_id": self.parameter_set_id,
            "short_horizon_minimum_top": self.short_horizon_minimum_top,
            "short_horizon_minimum_margin": self.short_horizon_minimum_margin,
            "long_horizon_minimum_top": self.long_horizon_minimum_top,
            "long_horizon_minimum_margin": self.long_horizon_minimum_margin,
            "transition_prior_fraction_of_top": self.transition_prior_fraction_of_top,
            "registry_state": self.registry_state,
            "live_parameter_apply_allowed": False,
            "auto_promotion_allowed": False,
            "canonical_replacement_allowed": False,
        })


BASELINE_CANDIDATE = FutureShadowCandidateParameters(
    parameter_set_id="market_regime.future.transparent_baseline.params.v1",
    short_horizon_minimum_top=0.34,
    short_horizon_minimum_margin=0.08,
    long_horizon_minimum_top=0.30,
    long_horizon_minimum_margin=0.06,
    transition_prior_fraction_of_top=0.20,
    registry_state="active",
)

CONSERVATIVE_CANDIDATE = FutureShadowCandidateParameters(
    parameter_set_id="market_regime.future.transparent_baseline.params.conservative.v1",
    short_horizon_minimum_top=0.40,
    short_horizon_minimum_margin=0.12,
    long_horizon_minimum_top=0.36,
    long_horizon_minimum_margin=0.10,
    transition_prior_fraction_of_top=0.10,
    registry_state="shadow",
)


def build_default_future_shadow_candidate_registry() -> Tuple[FutureShadowCandidateParameters, ...]:
    return (BASELINE_CANDIDATE, CONSERVATIVE_CANDIDATE)


def validate_future_shadow_candidate_registry(
    candidates: Tuple[FutureShadowCandidateParameters, ...],
) -> Mapping[str, object]:
    ids = tuple(item.parameter_set_id for item in candidates)
    failures = []
    if len(candidates) < 2:
        failures.append("fewer_than_two_candidates")
    if len(ids) != len(set(ids)):
        failures.append("duplicate_parameter_set_id")
    if sum(1 for item in candidates if item.registry_state == "active") != 1:
        failures.append("active_candidate_count_not_one")
    return MappingProxyType({
        "ok": not failures,
        "candidate_count": len(candidates),
        "parameter_set_ids": ids,
        "failures": tuple(failures),
        "live_parameter_apply_allowed": False,
        "auto_promotion_allowed": False,
        "canonical_replacement_allowed": False,
    })
