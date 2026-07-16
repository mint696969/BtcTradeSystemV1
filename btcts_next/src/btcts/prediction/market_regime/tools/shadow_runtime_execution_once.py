# path: ./btcts_next/src/btcts/prediction/market_regime/tools/shadow_runtime_execution_once.py
# desc: MR-F9.14 read-only one-shot tool from explicit preflight and observation JSON to execution evidence JSON.

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping as MappingABC
from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from btcts.prediction.market_regime.future_execution_evidence import (
    FutureInferenceMode,
    RawOutputSemantics,
)
from btcts.prediction.market_regime.future_shadow_execution_fact_builder import (
    FutureExecutionObservation,
    build_future_shadow_execution_facts,
)
from btcts.prediction.market_regime.future_shadow_runtime_execution_bridge import (
    build_future_shadow_runtime_execution_bridge,
)

MR_F9_RUNTIME_EXECUTION_ONCE_TOOL_VERSION = (
    "prediction.market_regime.tools.shadow_runtime_execution_once.mr_f9_14.v1"
)


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _mapping(value: Any, error: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(error)
    return value


def _sequence(value: Any, error: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(error)
    return value


def _preflight_report(payload: Any) -> Mapping[str, Any]:
    root = _mapping(payload, "mr_f9_execution_once_preflight_payload_invalid")
    if root.get("artifact_kind") == "mr_f8_runtime_preflight_once_result":
        report = root.get("preflight_report")
    else:
        report = root
    return _mapping(report, "mr_f9_execution_once_preflight_report_invalid")


def _observations(payload: Any) -> tuple[FutureExecutionObservation, ...]:
    root = _mapping(payload, "mr_f9_execution_once_observation_payload_invalid")
    if root.get("artifact_kind") != "future_shadow_execution_observation_batch":
        raise ValueError("mr_f9_execution_once_observation_kind_invalid")
    rows = _sequence(root.get("rows"), "mr_f9_execution_once_observation_rows_invalid")
    if not rows:
        raise ValueError("mr_f9_execution_once_observation_rows_empty")
    observations = []
    for raw in rows:
        row = _mapping(raw, "mr_f9_execution_once_observation_row_invalid")
        try:
            inference_mode = FutureInferenceMode(str(row.get("inference_mode") or ""))
        except ValueError as exc:
            raise ValueError("mr_f9_execution_once_inference_mode_invalid") from exc
        try:
            raw_semantics = RawOutputSemantics(str(row.get("raw_output_semantics") or ""))
        except ValueError as exc:
            raise ValueError("mr_f9_execution_once_raw_output_semantics_invalid") from exc
        observations.append(
            FutureExecutionObservation(
                trace_id=str(row.get("trace_id") or ""),
                prediction_origin=str(row.get("prediction_origin") or ""),
                feature_snapshot_ref=str(row.get("feature_snapshot_ref") or ""),
                target_horizon_sec=int(row.get("target_horizon_sec") or 0),
                parameter_set_id=str(row.get("parameter_set_id") or ""),
                inference_mode=inference_mode,
                raw_output_semantics=raw_semantics,
                source_freshness_state=str(row.get("source_freshness_state") or ""),
                source_age_sec=(
                    None
                    if row.get("source_age_sec") is None
                    else float(row.get("source_age_sec"))
                ),
                fallback_reason=str(row.get("fallback_reason") or ""),
                fallback_source_ref=str(row.get("fallback_source_ref") or ""),
            )
        )
    return tuple(observations)


def build_shadow_runtime_execution_once_report(
    *,
    preflight_payload: Any,
    observation_payload: Any,
) -> Mapping[str, Any]:
    preflight = _preflight_report(preflight_payload)
    observations = _observations(observation_payload)
    fact_report = build_future_shadow_execution_facts(
        preflight_report=preflight,
        observations=observations,
    )
    execution_report = build_future_shadow_runtime_execution_bridge(
        preflight_report=preflight,
        facts_by_trace_id=fact_report["facts_by_trace_id"],
    )
    return {
        "schema_version": MR_F9_RUNTIME_EXECUTION_ONCE_TOOL_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "mr_f9_runtime_execution_once_result",
        "prediction_origin": execution_report["prediction_origin"],
        "feature_snapshot_ref": execution_report["feature_snapshot_ref"],
        "pair_count": execution_report["pair_count"],
        "trace_count": execution_report["trace_count"],
        "evidence_count": execution_report["evidence_count"],
        "fact_build_report": _json_native(fact_report),
        "execution_report": _json_native(execution_report),
        "preflight_only": True,
        "writer_invoked": False,
        "writes_dhot": False,
        "writes_repository": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
    }


def _json_native(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _json_native(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, (MappingProxyType, MappingABC)):
        return {str(key): _json_native(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_native(item) for item in value]
    if hasattr(value, "to_dict"):
        return _json_native(value.to_dict())
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"mr_f9_execution_once_json_type_unsupported:{type(value).__name__}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build MR-F9 runtime execution evidence from explicit preflight and "
            "observation JSON without writes."
        )
    )
    parser.add_argument("--preflight-json", required=True)
    parser.add_argument("--observations-json", required=True)
    parser.add_argument("--preflight", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not args.preflight:
        parser.error("--preflight is required; writer and scheduler are unavailable")
    result = build_shadow_runtime_execution_once_report(
        preflight_payload=_load_json(args.preflight_json),
        observation_payload=_load_json(args.observations_json),
    )
    print(json.dumps(_json_native(result), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
