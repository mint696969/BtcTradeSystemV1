# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_runtime_outcome_intake.py
# desc: MR-F8.10 pure intake from verified runtime-pair trace rows and explicit point-in-time observations to immutable outcome rows.

from __future__ import annotations

from collections.abc import Mapping as MappingABC, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from .contracts import MarketRegimeCode
from .future_forecast_contract import FutureForecastStatus
from .future_shadow_outcome import (
    FutureShadowOutcomeEvidence,
    resolve_market_regime_future_shadow_outcome,
)
from .future_target_definition import future_target_definitions_by_horizon
from .future_trace_identity import MarketRegimeFutureTraceIdentity

MARKET_REGIME_FUTURE_SHADOW_RUNTIME_OUTCOME_INTAKE_VERSION = (
    "prediction.market_regime.future_shadow_runtime_outcome_intake.mr_f8_10.v1"
)
EXPECTED_PAIR_COUNT = 7


@dataclass(frozen=True)
class FutureShadowPointObservation:
    target_horizon_sec: int
    observed_at: str
    observed_future_state: MarketRegimeCode
    observation_source_ref: str
    observation_available: bool = True
    invalidated: bool = False
    invalidation_reason: str = ""

    def __post_init__(self) -> None:
        horizon = int(self.target_horizon_sec)
        if horizon not in future_target_definitions_by_horizon():
            raise ValueError(f"runtime_outcome_observation_horizon_invalid:{horizon}")
        if not isinstance(self.observed_future_state, MarketRegimeCode):
            raise ValueError("runtime_outcome_observation_state_invalid")
        if self.observation_available:
            if not self.observed_at.strip():
                raise ValueError("runtime_outcome_observed_at_missing")
            if not self.observation_source_ref.strip():
                raise ValueError("runtime_outcome_source_ref_missing")
        if self.invalidated and not self.invalidation_reason.strip():
            raise ValueError("runtime_outcome_invalidation_reason_missing")


def _mapping(value: Any, error: str) -> Mapping[str, Any]:
    if not isinstance(value, MappingABC):
        raise ValueError(error)
    return value


def _sequence(value: Any, error: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(error)
    return value


def _trace_from_row(row: Mapping[str, Any]) -> MarketRegimeFutureTraceIdentity:
    return MarketRegimeFutureTraceIdentity(
        trace_id=str(row.get("trace_id") or ""),
        origin_timestamp=str(row.get("origin_timestamp") or ""),
        expiry_at=str(row.get("expiry_at") or ""),
        target_horizon_sec=int(row.get("target_horizon_sec") or 0),
        target_horizon_key=str(row.get("target_horizon_key") or ""),
        target_definition_version=str(row.get("target_definition_version") or ""),
        model_id=str(row.get("model_id") or ""),
        logic_version=str(row.get("logic_version") or ""),
        parameter_set_id=str(row.get("parameter_set_id") or ""),
        feature_snapshot_ref=str(row.get("feature_snapshot_ref") or ""),
        predicted_future_state=MarketRegimeCode(str(row.get("predicted_future_state") or "UNKNOWN")),
        forecast_status=FutureForecastStatus(str(row.get("forecast_status") or "")),
    )


def build_runtime_outcome_intake_report(
    *,
    runtime_preflight_result: Mapping[str, Any],
    observations_by_horizon: Mapping[int, FutureShadowPointObservation],
    resolved_at: str,
) -> Mapping[str, Any]:
    outer = _mapping(runtime_preflight_result, "runtime_outcome_outer_invalid")
    preflight = _mapping(outer.get("preflight_report"), "runtime_outcome_preflight_invalid")
    pairs = _sequence(preflight.get("pairs"), "runtime_outcome_pairs_invalid")
    if len(pairs) != EXPECTED_PAIR_COUNT:
        raise ValueError(f"runtime_outcome_pair_count_invalid:{len(pairs)}")
    if outer.get("source_snapshot_ok") is not True or preflight.get("runtime_source_ready") is not True:
        raise ValueError("runtime_outcome_runtime_source_not_ready")
    for field in ("writer_invoked", "writes_dhot", "scheduler_enabled", "auto_promotion_allowed", "live_parameter_apply_allowed"):
        if outer.get(field) is not False:
            raise ValueError(f"runtime_outcome_outer_safety_invalid:{field}")

    known_horizons = set(future_target_definitions_by_horizon())
    if set(int(key) for key in observations_by_horizon) - known_horizons:
        raise ValueError("runtime_outcome_unknown_observation_horizon")

    outcome_rows: list[Mapping[str, Any]] = []
    status_counts: dict[str, int] = {}
    observed_horizons: set[int] = set()
    unresolved_horizons: set[int] = set()
    seen_trace_ids: set[str] = set()

    for pair_index, raw_pair in enumerate(pairs):
        pair = _mapping(raw_pair, f"runtime_outcome_pair_invalid:{pair_index}")
        trace_plan = _mapping(pair.get("trace_plan"), f"runtime_outcome_trace_plan_invalid:{pair_index}")
        persistence = _mapping(trace_plan.get("persistence_plan"), f"runtime_outcome_persistence_invalid:{pair_index}")
        trace_rows = _sequence(persistence.get("rows"), f"runtime_outcome_trace_rows_invalid:{pair_index}")
        if len(trace_rows) != 2:
            raise ValueError(f"runtime_outcome_trace_count_invalid:{pair_index}")
        pair_horizon = int(_mapping(pair.get("slot_identity"), "runtime_outcome_slot_invalid").get("target_horizon_sec") or 0)
        observation = observations_by_horizon.get(pair_horizon)
        if observation is not None and int(observation.target_horizon_sec) != pair_horizon:
            raise ValueError("runtime_outcome_observation_horizon_mismatch")

        for raw_trace in trace_rows:
            trace = _trace_from_row(_mapping(raw_trace, "runtime_outcome_trace_invalid"))
            if trace.trace_id in seen_trace_ids:
                raise ValueError(f"runtime_outcome_duplicate_trace:{trace.trace_id}")
            seen_trace_ids.add(trace.trace_id)
            if trace.target_horizon_sec != pair_horizon:
                raise ValueError("runtime_outcome_trace_pair_horizon_mismatch")
            evidence = (
                FutureShadowOutcomeEvidence(
                    resolved_at=resolved_at,
                    observation_available=False,
                )
                if observation is None
                else FutureShadowOutcomeEvidence(
                    resolved_at=resolved_at,
                    observation_available=observation.observation_available,
                    observed_at=observation.observed_at,
                    observed_future_state=observation.observed_future_state,
                    invalidated=observation.invalidated,
                    invalidation_reason=observation.invalidation_reason,
                    observation_source_ref=observation.observation_source_ref,
                )
            )
            outcome = resolve_market_regime_future_shadow_outcome(trace=trace, evidence=evidence)
            row = dict(outcome.to_evaluation_row())
            row["pair_id"] = str(pair.get("pair_id") or "")
            row["source_bundle_id"] = str(pair.get("source_bundle_id") or "")
            outcome_rows.append(MappingProxyType(row))
            status_counts[outcome.status.value] = status_counts.get(outcome.status.value, 0) + 1
            if outcome.status.value == "UNRESOLVED":
                unresolved_horizons.add(pair_horizon)
            else:
                observed_horizons.add(pair_horizon)

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_RUNTIME_OUTCOME_INTAKE_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_runtime_outcome_intake_report",
        "prediction_origin": preflight.get("prediction_origin"),
        "feature_snapshot_ref": preflight.get("feature_snapshot_ref"),
        "resolved_at": resolved_at,
        "pair_count": len(pairs),
        "trace_count": len(outcome_rows),
        "observed_horizon_count": len(observed_horizons),
        "unresolved_horizon_count": len(unresolved_horizons),
        "observed_horizons": tuple(sorted(observed_horizons)),
        "unresolved_horizons": tuple(sorted(unresolved_horizons)),
        "status_counts": MappingProxyType(dict(sorted(status_counts.items()))),
        "outcome_rows": tuple(outcome_rows),
        "comparison_input_ready": len(observed_horizons) > 0,
        "full_horizon_window_complete": len(observed_horizons) == EXPECTED_PAIR_COUNT,
        "safety": MappingProxyType({
            "explicit_observation_required": True,
            "historical_state_inference_forbidden": True,
            "read_only_inputs": True,
            "writes_dhot": False,
            "writer_invoked": False,
            "scheduler_enabled": False,
            "auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
            "human_gate_required": True,
        }),
    })
