# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_write_approval.py
# desc: MR-F9.19G build-only approval token binding one readiness report to one exact persistence plan. No writes.

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from btcts.prediction.market_regime.runtime_horizon_persistence_plan import (
    EXPECTED_HORIZONS,
    RUNTIME_HORIZON_PERSISTENCE_PLAN_VERSION,
)
from btcts.prediction.market_regime.runtime_horizon_write_readiness import (
    RUNTIME_HORIZON_WRITE_READINESS_VERSION,
)

RUNTIME_HORIZON_WRITE_APPROVAL_VERSION = (
    "prediction.market_regime.runtime_horizon_write_approval.mr_f9_19g.v1"
)


def _json_native(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_native(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_native(item) for item in value]
    return value


def _digest(value: Mapping[str, Any]) -> str:
    text = json.dumps(
        _json_native(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _validate_bindings(
    *,
    readiness: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> tuple[tuple[Mapping[str, Any], ...], tuple[str, ...]]:
    if readiness.get("schema_version") != RUNTIME_HORIZON_WRITE_READINESS_VERSION:
        raise ValueError("runtime_horizon_write_approval_readiness_schema_invalid")
    if readiness.get("ready") is not True or tuple(readiness.get("blockers") or ()):
        raise ValueError("runtime_horizon_write_approval_readiness_not_ready")
    if readiness.get("build_only") is not True:
        raise ValueError("runtime_horizon_write_approval_readiness_build_only_invalid")
    for key in (
        "writer_invoked",
        "writes_dhot",
        "writer_registered",
        "latest_pointer_created",
        "scheduler_enabled",
        "producer_loop_enabled",
        "websocket_opened",
        "ui_inference_allowed",
        "ui_confidence_recalculation_allowed",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
    ):
        if readiness.get(key) is not False:
            raise ValueError(f"runtime_horizon_write_approval_readiness_safety_invalid:{key}")

    if plan.get("schema_version") != RUNTIME_HORIZON_PERSISTENCE_PLAN_VERSION:
        raise ValueError("runtime_horizon_write_approval_plan_schema_invalid")
    if int(plan.get("horizon_count") or -1) != 8:
        raise ValueError("runtime_horizon_write_approval_plan_horizon_count_invalid")
    for key in (
        "writer_registered",
        "would_write",
        "latest_pointer_created",
        "canonical_latest_replacement",
        "scheduler_enabled",
        "producer_loop_enabled",
        "websocket_opened",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
    ):
        if plan.get(key) is not False:
            raise ValueError(f"runtime_horizon_write_approval_plan_safety_invalid:{key}")

    for key in ("run_id", "prediction_origin"):
        if str(readiness.get(key) or "") != str(plan.get(key) or ""):
            raise ValueError(f"runtime_horizon_write_approval_binding_mismatch:{key}")

    artifact_rows = plan.get("horizon_artifacts")
    if not isinstance(artifact_rows, (tuple, list)) or len(artifact_rows) != 8:
        raise ValueError("runtime_horizon_write_approval_plan_artifacts_invalid")
    horizons = tuple(int(item.get("horizon_sec")) for item in artifact_rows if isinstance(item, Mapping))
    if horizons != EXPECTED_HORIZONS:
        raise ValueError("runtime_horizon_write_approval_horizon_identity_invalid")

    digest_rows_list = []
    for item in artifact_rows:
        payload = item.get("payload")
        if not isinstance(payload, Mapping):
            raise ValueError("runtime_horizon_write_approval_artifact_payload_invalid")
        recorded_digest = str(item.get("payload_sha256") or "")
        if recorded_digest != _digest(payload):
            raise ValueError("runtime_horizon_write_approval_artifact_digest_mismatch")
        digest_rows_list.append({
            "horizon_sec": int(item["horizon_sec"]),
            "trace_id": str(item.get("trace_id") or ""),
            "artifact_relpath": str(item.get("artifact_relpath") or ""),
            "payload_sha256": recorded_digest,
        })
    digest_rows = tuple(digest_rows_list)
    if any(not item["trace_id"] or len(item["payload_sha256"]) != 64 for item in digest_rows):
        raise ValueError("runtime_horizon_write_approval_artifact_binding_invalid")

    manifest_relpath = str(plan.get("manifest_relpath") or "")
    manifest_payload = plan.get("manifest_payload")
    manifest_digest = str(plan.get("manifest_payload_sha256") or "")
    if not isinstance(manifest_payload, Mapping):
        raise ValueError("runtime_horizon_write_approval_manifest_payload_invalid")
    if manifest_digest != _digest(manifest_payload):
        raise ValueError("runtime_horizon_write_approval_manifest_digest_mismatch")
    if not manifest_relpath.endswith("/manifest.json") or len(manifest_digest) != 64:
        raise ValueError("runtime_horizon_write_approval_manifest_binding_invalid")
    if manifest_payload.get("schema_version") != RUNTIME_HORIZON_PERSISTENCE_PLAN_VERSION:
        raise ValueError("runtime_horizon_write_approval_manifest_schema_invalid")
    if str(manifest_payload.get("run_id") or "") != str(plan.get("run_id") or ""):
        raise ValueError("runtime_horizon_write_approval_manifest_run_id_mismatch")
    if str(manifest_payload.get("prediction_origin") or "") != str(plan.get("prediction_origin") or ""):
        raise ValueError("runtime_horizon_write_approval_manifest_origin_mismatch")
    if int(manifest_payload.get("horizon_count") or -1) != 8:
        raise ValueError("runtime_horizon_write_approval_manifest_horizon_count_invalid")
    manifest_rows = manifest_payload.get("horizon_artifacts")
    if _json_native(manifest_rows) != _json_native(digest_rows):
        raise ValueError("runtime_horizon_write_approval_manifest_artifact_bindings_mismatch")
    if manifest_payload.get("latest_pointer_relpath") is not None:
        raise ValueError("runtime_horizon_write_approval_manifest_latest_pointer_invalid")
    for key in (
        "canonical_latest_replacement",
        "ui_inference_allowed",
        "ui_confidence_recalculation_allowed",
    ):
        if manifest_payload.get(key) is not False:
            raise ValueError(f"runtime_horizon_write_approval_manifest_safety_invalid:{key}")
    for key in ("read_only", "non_executing"):
        if manifest_payload.get(key) is not True:
            raise ValueError(f"runtime_horizon_write_approval_manifest_contract_invalid:{key}")

    write_order = tuple(str(item) for item in (plan.get("write_order") or ()))
    expected_order = tuple(item["artifact_relpath"] for item in digest_rows) + (manifest_relpath,)
    if write_order != expected_order:
        raise ValueError("runtime_horizon_write_approval_write_order_invalid")

    destination_checks = readiness.get("destination_checks")
    if not isinstance(destination_checks, (tuple, list)) or len(destination_checks) != 9:
        raise ValueError("runtime_horizon_write_approval_destination_checks_invalid")
    readiness_order = tuple(str(item.get("artifact_relpath") or "") for item in destination_checks if isinstance(item, Mapping))
    if readiness_order != write_order:
        raise ValueError("runtime_horizon_write_approval_binding_mismatch:destination_paths")
    if any(str(item.get("state") or "") not in {"missing", "duplicate"} for item in destination_checks):
        raise ValueError("runtime_horizon_write_approval_destination_state_invalid")

    source_checks = readiness.get("source_checks")
    if not isinstance(source_checks, (tuple, list)) or len(source_checks) != 8:
        raise ValueError("runtime_horizon_write_approval_source_checks_invalid")
    source_horizons = tuple(int(item.get("horizon_sec")) for item in source_checks if isinstance(item, Mapping))
    if source_horizons != EXPECTED_HORIZONS:
        raise ValueError("runtime_horizon_write_approval_source_identity_invalid")
    if any(item.get("ready") is not True for item in source_checks):
        raise ValueError("runtime_horizon_write_approval_source_not_ready")

    return digest_rows, write_order


def build_runtime_horizon_write_approval_token(
    *,
    readiness: Mapping[str, Any],
    plan: Mapping[str, Any],
    operator_id: str,
    enabled_acknowledged: bool = False,
    once_acknowledged: bool = False,
) -> Mapping[str, Any]:
    if not isinstance(readiness, Mapping) or not isinstance(plan, Mapping):
        raise ValueError("runtime_horizon_write_approval_input_invalid")
    if type(enabled_acknowledged) is not bool or type(once_acknowledged) is not bool:
        raise ValueError("runtime_horizon_write_approval_ack_flags_invalid")
    operator = str(operator_id).strip()
    if not operator:
        raise ValueError("runtime_horizon_write_approval_operator_missing")
    if enabled_acknowledged is not True:
        raise PermissionError("runtime_horizon_write_approval_enabled_ack_required")
    if once_acknowledged is not True:
        raise PermissionError("runtime_horizon_write_approval_once_ack_required")
    if readiness.get("operator_id") != operator:
        raise ValueError("runtime_horizon_write_approval_binding_mismatch:operator_id")
    if readiness.get("enabled_acknowledged") is not True or readiness.get("once_acknowledged") is not True:
        raise ValueError("runtime_horizon_write_approval_readiness_ack_invalid")

    artifact_bindings, write_order = _validate_bindings(readiness=readiness, plan=plan)
    token_body = {
        "schema_version": RUNTIME_HORIZON_WRITE_APPROVAL_VERSION,
        "artifact_kind": "market_regime_runtime_horizon_write_approval_token",
        "destination_root": str(readiness.get("destination_root") or ""),
        "prediction_origin": str(plan["prediction_origin"]),
        "run_id": str(plan["run_id"]),
        "operator_id": operator,
        "enabled_acknowledged": True,
        "once_acknowledged": True,
        "readiness_sha256": _digest(readiness),
        "artifact_bindings": artifact_bindings,
        "manifest_binding": {
            "artifact_relpath": str(plan["manifest_relpath"]),
            "payload_sha256": str(plan["manifest_payload_sha256"]),
        },
        "write_order": write_order,
        "build_only": True,
        "writer_invoked": False,
        "writes_dhot": False,
        "writer_registered": False,
        "latest_pointer_created": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "websocket_opened": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "order_submission_allowed": False,
    }
    return {**token_body, "approval_token_sha256": _digest(token_body)}


def validate_runtime_horizon_write_approval_token(
    *,
    token: Mapping[str, Any],
    readiness: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> None:
    if not isinstance(token, Mapping):
        raise ValueError("runtime_horizon_write_approval_token_invalid")
    operator = str(token.get("operator_id") or "")
    rebuilt = build_runtime_horizon_write_approval_token(
        readiness=readiness,
        plan=plan,
        operator_id=operator,
        enabled_acknowledged=token.get("enabled_acknowledged") is True,
        once_acknowledged=token.get("once_acknowledged") is True,
    )
    if _json_native(token) != _json_native(rebuilt):
        raise ValueError("runtime_horizon_write_approval_token_mismatch")
