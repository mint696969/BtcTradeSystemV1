# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_maturation_cycle.py
# desc: MR-F9.5 pure expiry-gated maturation plan from origin receipt and explicit point observations.

from __future__ import annotations

from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from .future_shadow_runtime_outcome_intake import (
    FutureShadowPointObservation,
    build_runtime_outcome_intake_report,
)

MARKET_REGIME_FUTURE_SHADOW_MATURATION_CYCLE_VERSION = (
    "prediction.market_regime.future_shadow_maturation_cycle.mr_f9_5.v1"
)


def _parse_utc(value: str, error: str) -> datetime:
    text = str(value or "")
    if not text.endswith("Z"):
        raise ValueError(error)
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(error) from exc
    if parsed.tzinfo != timezone.utc or parsed.isoformat().replace("+00:00", "Z") != text:
        raise ValueError(error)
    return parsed


def _mapping(value: Any, error: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(error)
    return value


def _sequence(value: Any, error: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(error)
    return value


def build_future_shadow_maturation_cycle(
    *,
    origin_receipt: Mapping[str, Any],
    observations_by_horizon: Mapping[int, FutureShadowPointObservation],
    polled_at: str,
) -> Mapping[str, Any]:
    receipt = _mapping(origin_receipt, "future_shadow_maturation_receipt_invalid")
    if receipt.get("artifact_kind") != "future_shadow_origin_receipt":
        raise ValueError("future_shadow_maturation_receipt_kind_invalid")
    effective = _parse_utc(polled_at, "future_shadow_maturation_polled_at_invalid")
    trace_plans = _sequence(
        receipt.get("trace_persistence_plans"),
        "future_shadow_maturation_trace_plans_invalid",
    )
    if len(trace_plans) != int(receipt.get("pair_count") or 0):
        raise ValueError("future_shadow_maturation_pair_count_mismatch")
    if not isinstance(observations_by_horizon, Mapping):
        raise ValueError("future_shadow_maturation_observations_invalid")

    pairs = []
    expired_horizons: set[int] = set()
    pending_horizons: set[int] = set()
    seen_trace_ids: set[str] = set()

    for index, raw_plan in enumerate(trace_plans):
        plan = _mapping(raw_plan, f"future_shadow_maturation_trace_plan_invalid:{index}")
        persistence = _mapping(
            plan.get("persistence_plan"),
            f"future_shadow_maturation_persistence_plan_invalid:{index}",
        )
        rows = _sequence(
            persistence.get("rows"),
            f"future_shadow_maturation_trace_rows_invalid:{index}",
        )
        if len(rows) != 2:
            raise ValueError(f"future_shadow_maturation_trace_count_invalid:{index}")
        mapped_rows = tuple(_mapping(row, "future_shadow_maturation_trace_row_invalid") for row in rows)
        horizons = {int(row.get("target_horizon_sec") or 0) for row in mapped_rows}
        expiries = {str(row.get("expiry_at") or "") for row in mapped_rows}
        origins = {str(row.get("origin_timestamp") or "") for row in mapped_rows}
        if len(horizons) != 1 or len(expiries) != 1 or len(origins) != 1:
            raise ValueError("future_shadow_maturation_pair_identity_mismatch")
        horizon = next(iter(horizons))
        expiry_at = next(iter(expiries))
        origin = next(iter(origins))
        expiry = _parse_utc(expiry_at, "future_shadow_maturation_expiry_invalid")
        trace_ids = tuple(str(row.get("trace_id") or "") for row in mapped_rows)
        if any(not trace_id for trace_id in trace_ids):
            raise ValueError("future_shadow_maturation_trace_id_missing")
        if any(trace_id in seen_trace_ids for trace_id in trace_ids):
            raise ValueError("future_shadow_maturation_duplicate_trace_id")
        seen_trace_ids.update(trace_ids)
        if origin != str(receipt.get("prediction_origin") or ""):
            raise ValueError("future_shadow_maturation_origin_mismatch")
        if effective >= expiry:
            expired_horizons.add(horizon)
        else:
            pending_horizons.add(horizon)
        pairs.append({
            "pair_id": str(plan.get("pair_id") or ""),
            "source_bundle_id": str(receipt.get("suite_id") or ""),
            "slot_identity": {
                "origin_timestamp": origin,
                "target_horizon_sec": horizon,
                "feature_snapshot_ref": str(receipt.get("feature_snapshot_ref") or ""),
            },
            "trace_plan": {"persistence_plan": persistence},
        })

    observation_horizons = {int(key) for key in observations_by_horizon.keys()}
    known_horizons = expired_horizons | pending_horizons
    unknown_observations = tuple(sorted(observation_horizons - known_horizons))
    if unknown_observations:
        raise ValueError(
            "future_shadow_maturation_unknown_observation_horizon:"
            + ",".join(str(item) for item in unknown_observations)
        )
    unexpired_observations = tuple(sorted(observation_horizons & pending_horizons))
    if unexpired_observations:
        raise ValueError(
            "future_shadow_maturation_observation_before_expiry:"
            + ",".join(str(item) for item in unexpired_observations)
        )

    runtime_preflight_result = {
        "source_snapshot_ok": True,
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "preflight_report": {
            "runtime_source_ready": True,
            "prediction_origin": str(receipt.get("prediction_origin") or ""),
            "feature_snapshot_ref": str(receipt.get("feature_snapshot_ref") or ""),
            "pairs": tuple(pairs),
        },
    }
    intake = build_runtime_outcome_intake_report(
        runtime_preflight_result=runtime_preflight_result,
        observations_by_horizon=observations_by_horizon,
        resolved_at=polled_at,
    )
    if tuple(sorted(seen_trace_ids)) != tuple(receipt.get("trace_ids") or ()):
        raise ValueError("future_shadow_maturation_trace_set_mismatch")
    if int(intake.get("trace_count") or 0) != len(seen_trace_ids):
        raise ValueError("future_shadow_maturation_outcome_count_mismatch")

    return MappingProxyType({
        "schema_version": MARKET_REGIME_FUTURE_SHADOW_MATURATION_CYCLE_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "future_shadow_maturation_cycle",
        "receipt_id": str(receipt.get("receipt_id") or ""),
        "suite_id": str(receipt.get("suite_id") or ""),
        "prediction_origin": str(receipt.get("prediction_origin") or ""),
        "polled_at": polled_at,
        "expired_horizons": tuple(sorted(expired_horizons)),
        "pending_horizons": tuple(sorted(pending_horizons)),
        "observation_horizons": tuple(sorted(observation_horizons)),
        "trace_count": len(seen_trace_ids),
        "outcome_intake_report": intake,
        "would_write": False,
        "safety": MappingProxyType({
            "explicit_observation_required": True,
            "observation_before_expiry_forbidden": True,
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
