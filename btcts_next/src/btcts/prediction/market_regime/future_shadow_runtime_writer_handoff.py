# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_runtime_writer_handoff.py
# desc: MR-F8.9 pure schema adapter from verified runtime preflight output to the guarded writer report contract.

from __future__ import annotations

from collections.abc import Mapping as MappingABC, Sequence
from types import MappingProxyType
from typing import Any, Mapping

from .future_shadow_runtime_preflight_bridge import (
    MARKET_REGIME_FUTURE_SHADOW_RUNTIME_PREFLIGHT_BRIDGE_VERSION,
)
from .tools.shadow_runtime_preflight_once import MR_F8_RUNTIME_PREFLIGHT_ONCE_TOOL_VERSION

MR_F8_RUNTIME_WRITER_HANDOFF_VERSION = (
    "prediction.market_regime.future_shadow_runtime_writer_handoff.mr_f8_9.v1"
)
WRITER_REPORT_SCHEMA = "market_regime_shadow_pair_once_report.mr_f8_6.v1"
EXPECTED_RUNTIME_PAIR_COUNT = 7


def _mapping(value: Any, error: str) -> Mapping[str, Any]:
    if not isinstance(value, MappingABC):
        raise ValueError(error)
    return value


def _sequence(value: Any, error: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(error)
    return value


def _validate_outer_safety(report: Mapping[str, Any]) -> None:
    required_true = ("source_snapshot_ok", "preflight_only")
    required_false = (
        "writer_invoked",
        "writes_dhot",
        "scheduler_enabled",
        "producer_loop_enabled",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
        "auto_promotion_allowed",
        "live_parameter_apply_allowed",
    )
    for field in required_true:
        if report.get(field) is not True:
            raise ValueError(f"mr_f8_writer_handoff_outer_safety_invalid:{field}")
    for field in required_false:
        if report.get(field) is not False:
            raise ValueError(f"mr_f8_writer_handoff_outer_safety_invalid:{field}")


def _validate_preflight_safety(report: Mapping[str, Any]) -> None:
    if report.get("runtime_source_ready") is not True:
        raise ValueError("mr_f8_writer_handoff_runtime_source_not_ready")
    if report.get("preflight_only") is not True:
        raise ValueError("mr_f8_writer_handoff_preflight_only_missing")
    for field in (
        "writer_invoked",
        "writes_dhot",
        "scheduler_enabled",
        "auto_promotion_allowed",
        "live_parameter_apply_allowed",
        "canonical_replacement_allowed",
    ):
        if report.get(field) is not False:
            raise ValueError(f"mr_f8_writer_handoff_preflight_safety_invalid:{field}")


def _validate_pair(pair: Mapping[str, Any], *, index: int) -> None:
    if pair.get("artifact_kind") != "future_shadow_candidate_pair":
        raise ValueError(f"mr_f8_writer_handoff_pair_kind_invalid:{index}")
    pair_id = str(pair.get("pair_id") or "").strip()
    source_bundle_id = str(pair.get("source_bundle_id") or "").strip()
    if not pair_id or not source_bundle_id:
        raise ValueError(f"mr_f8_writer_handoff_pair_identity_missing:{index}")
    if pair.get("candidate_count") != 2:
        raise ValueError(f"mr_f8_writer_handoff_candidate_count_invalid:{index}")
    forecasts = _sequence(pair.get("forecasts"), f"mr_f8_writer_handoff_forecasts_invalid:{index}")
    if len(forecasts) != 2:
        raise ValueError(f"mr_f8_writer_handoff_forecast_count_invalid:{index}")
    trace_plan = _mapping(pair.get("trace_plan"), f"mr_f8_writer_handoff_trace_plan_missing:{index}")
    if trace_plan.get("trace_count") != 2:
        raise ValueError(f"mr_f8_writer_handoff_trace_count_invalid:{index}")
    persistence = _mapping(
        trace_plan.get("persistence_plan"),
        f"mr_f8_writer_handoff_persistence_plan_missing:{index}",
    )
    if persistence.get("would_write") is not False:
        raise ValueError(f"mr_f8_writer_handoff_write_enabled:{index}")


def build_runtime_writer_handoff_report(*, runtime_preflight_result: Mapping[str, Any]) -> Mapping[str, Any]:
    outer = _mapping(runtime_preflight_result, "mr_f8_writer_handoff_outer_invalid")
    if outer.get("schema_version") != MR_F8_RUNTIME_PREFLIGHT_ONCE_TOOL_VERSION:
        raise ValueError("mr_f8_writer_handoff_outer_schema_invalid")
    if outer.get("artifact_kind") != "mr_f8_runtime_preflight_once_result":
        raise ValueError("mr_f8_writer_handoff_outer_kind_invalid")
    _validate_outer_safety(outer)

    preflight = _mapping(
        outer.get("preflight_report"),
        "mr_f8_writer_handoff_preflight_report_invalid",
    )
    if preflight.get("schema_version") != MARKET_REGIME_FUTURE_SHADOW_RUNTIME_PREFLIGHT_BRIDGE_VERSION:
        raise ValueError("mr_f8_writer_handoff_preflight_schema_invalid")
    if preflight.get("artifact_kind") != "future_shadow_runtime_preflight_report":
        raise ValueError("mr_f8_writer_handoff_preflight_kind_invalid")
    _validate_preflight_safety(preflight)

    pairs = _sequence(preflight.get("pairs"), "mr_f8_writer_handoff_pairs_invalid")
    if len(pairs) != EXPECTED_RUNTIME_PAIR_COUNT:
        raise ValueError(f"mr_f8_writer_handoff_pair_count_invalid:{len(pairs)}")
    if outer.get("pair_count") != len(pairs) or preflight.get("pair_count") != len(pairs):
        raise ValueError("mr_f8_writer_handoff_pair_count_mismatch")

    normalized_pairs: list[dict[str, Any]] = []
    pair_ids: set[str] = set()
    source_bundle_ids: set[str] = set()
    for index, value in enumerate(pairs):
        pair = _mapping(value, f"mr_f8_writer_handoff_pair_invalid:{index}")
        _validate_pair(pair, index=index)
        pair_id = str(pair["pair_id"])
        source_bundle_id = str(pair["source_bundle_id"])
        if pair_id in pair_ids:
            raise ValueError(f"mr_f8_writer_handoff_pair_duplicate:{pair_id}")
        if source_bundle_id in source_bundle_ids:
            raise ValueError(f"mr_f8_writer_handoff_source_bundle_duplicate:{source_bundle_id}")
        pair_ids.add(pair_id)
        source_bundle_ids.add(source_bundle_id)
        normalized_pairs.append(dict(pair))

    return MappingProxyType({
        "schema_version": WRITER_REPORT_SCHEMA,
        "artifact_kind": "mr_f8_runtime_writer_handoff_report",
        "handoff_schema_version": MR_F8_RUNTIME_WRITER_HANDOFF_VERSION,
        "ok": True,
        "runtime_derived": True,
        "fixture_derived": False,
        "prediction_origin": preflight.get("prediction_origin"),
        "feature_snapshot_ref": preflight.get("feature_snapshot_ref"),
        "pair_count": len(normalized_pairs),
        "pair_ids": tuple(sorted(pair_ids)),
        "source_bundle_ids": tuple(sorted(source_bundle_ids)),
        "pairs": tuple(normalized_pairs),
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
    })
