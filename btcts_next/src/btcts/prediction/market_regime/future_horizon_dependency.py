# path: ./btcts_next/src/btcts/prediction/market_regime/future_horizon_dependency.py
# desc: MR-F9.18A7 pure causal dependency contract for sequential horizon re-evaluation. No scoring, writes, scheduler, UI, WS, broker, or AutoTrade behavior.

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .future_forecast_contract import FUTURE_MARKET_REGIME_HORIZONS_SEC

MARKET_REGIME_FUTURE_HORIZON_DEPENDENCY_VERSION = "prediction.market_regime.future_horizon_dependency.mr_f9_18a7.v1"


@dataclass(frozen=True)
class HorizonDependencyContext:
    target_horizon_sec: int
    direct_predecessor_horizon_sec: int | None
    upstream_horizons_sec: Tuple[int, ...]
    predecessor_distribution: Mapping[str, float]
    predecessor_status: str
    predecessor_margin: float | None
    predecessor_transition_path: Tuple[Mapping[str, Any], ...]
    predecessor_uncertainty_state: str
    re_evaluation_required: bool
    reason_codes: Tuple[str, ...]

    def __post_init__(self) -> None:
        if int(self.target_horizon_sec) not in FUTURE_MARKET_REGIME_HORIZONS_SEC:
            raise ValueError("future_horizon_dependency_target_invalid")
        expected = tuple(h for h in FUTURE_MARKET_REGIME_HORIZONS_SEC if h < int(self.target_horizon_sec))
        if tuple(self.upstream_horizons_sec) != expected:
            raise ValueError("future_horizon_dependency_upstream_mismatch")
        if self.direct_predecessor_horizon_sec is None:
            if expected:
                raise ValueError("future_horizon_dependency_predecessor_missing")
        elif int(self.direct_predecessor_horizon_sec) != expected[-1]:
            raise ValueError("future_horizon_dependency_predecessor_mismatch")
        normalized = {str(k): float(v) for k, v in self.predecessor_distribution.items()}
        if any(v < 0.0 for v in normalized.values()):
            raise ValueError("future_horizon_dependency_distribution_invalid")
        object.__setattr__(self, "predecessor_distribution", MappingProxyType(normalized))
        object.__setattr__(self, "predecessor_transition_path", tuple(MappingProxyType(dict(item)) for item in self.predecessor_transition_path))

    def to_dict(self) -> Mapping[str, Any]:
        return MappingProxyType({
            "schema_version": MARKET_REGIME_FUTURE_HORIZON_DEPENDENCY_VERSION,
            "target_horizon_sec": int(self.target_horizon_sec),
            "direct_predecessor_horizon_sec": self.direct_predecessor_horizon_sec,
            "upstream_horizons_sec": tuple(self.upstream_horizons_sec),
            "predecessor_distribution": dict(self.predecessor_distribution),
            "predecessor_status": self.predecessor_status,
            "predecessor_margin": self.predecessor_margin,
            "predecessor_transition_path": tuple(dict(item) for item in self.predecessor_transition_path),
            "predecessor_uncertainty_state": self.predecessor_uncertainty_state,
            "re_evaluation_required": self.re_evaluation_required,
            "reason_codes": tuple(self.reason_codes),
            "label_copy_allowed": False,
            "distribution_context_only": True,
            "runtime_activation_allowed": False,
        })


def build_horizon_dependency_contexts(
    *,
    horizon_results: Mapping[int, Mapping[str, Any]],
    changed_horizon_sec: int | None = None,
) -> Tuple[HorizonDependencyContext, ...]:
    missing = tuple(h for h in FUTURE_MARKET_REGIME_HORIZONS_SEC if h not in horizon_results)
    if missing:
        raise ValueError("future_horizon_dependency_results_missing:" + ",".join(str(x) for x in missing))
    if changed_horizon_sec is not None and int(changed_horizon_sec) not in FUTURE_MARKET_REGIME_HORIZONS_SEC:
        raise ValueError("future_horizon_dependency_changed_horizon_invalid")

    contexts = []
    for index, horizon in enumerate(FUTURE_MARKET_REGIME_HORIZONS_SEC):
        predecessor = None if index == 0 else FUTURE_MARKET_REGIME_HORIZONS_SEC[index - 1]
        upstream = tuple(FUTURE_MARKET_REGIME_HORIZONS_SEC[:index])
        source = {} if predecessor is None else dict(horizon_results[predecessor])
        should_re_evaluate = changed_horizon_sec is not None and int(changed_horizon_sec) < int(horizon)
        reasons = () if not should_re_evaluate else ("upstream_horizon_changed", f"changed_horizon:{int(changed_horizon_sec)}")
        contexts.append(HorizonDependencyContext(
            target_horizon_sec=horizon,
            direct_predecessor_horizon_sec=predecessor,
            upstream_horizons_sec=upstream,
            predecessor_distribution=source.get("probability_by_state") or source.get("score_distribution") or {},
            predecessor_status=str(source.get("status") or "ORIGIN_ONLY"),
            predecessor_margin=source.get("score_margin"),
            predecessor_transition_path=tuple(source.get("transition_path_candidate") or ()),
            predecessor_uncertainty_state=str(source.get("uncertainty_state") or source.get("abstain_reason") or "UNSPECIFIED"),
            re_evaluation_required=should_re_evaluate,
            reason_codes=reasons,
        ))
    return tuple(contexts)
