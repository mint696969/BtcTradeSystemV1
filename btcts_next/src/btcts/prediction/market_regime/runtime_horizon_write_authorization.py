# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_write_authorization.py
# desc: MR-F9.19I read-only limited D-hot one-shot authorization package. No writer invocation.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from btcts.prediction.market_regime.runtime_horizon_write_approval import (
    validate_runtime_horizon_write_approval_token,
)

RUNTIME_HORIZON_WRITE_AUTHORIZATION_VERSION = (
    "prediction.market_regime.runtime_horizon_write_authorization.mr_f9_19i.v1"
)
MAX_AUTHORIZATION_TTL_SEC = 300


def _json_native(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_native(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_native(item) for item in value]
    return value


def _digest(value: Any) -> str:
    text = json.dumps(
        _json_native(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_utc(value: str, field: str) -> str:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"runtime_horizon_write_authorization_timestamp_invalid:{field}") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"runtime_horizon_write_authorization_timestamp_timezone_missing:{field}")
    return (
        parsed.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _parse_utc(value: str, field: str) -> datetime:
    canonical = _canonical_utc(value, field)
    return datetime.fromisoformat(canonical.replace("Z", "+00:00"))


def build_runtime_horizon_write_authorization_package(
    *,
    token: Mapping[str, Any],
    readiness: Mapping[str, Any],
    plan: Mapping[str, Any],
    created_at: str,
    ttl_sec: int = 300,
    expected_dhot_root: str | Path,
) -> Mapping[str, Any]:
    if not isinstance(token, Mapping):
        raise ValueError("runtime_horizon_write_authorization_token_invalid")
    if not isinstance(readiness, Mapping):
        raise ValueError("runtime_horizon_write_authorization_readiness_invalid")
    if not isinstance(plan, Mapping):
        raise ValueError("runtime_horizon_write_authorization_plan_invalid")
    if type(ttl_sec) is not int or ttl_sec <= 0 or ttl_sec > MAX_AUTHORIZATION_TTL_SEC:
        raise ValueError("runtime_horizon_write_authorization_ttl_invalid")

    validate_runtime_horizon_write_approval_token(
        token=token,
        readiness=readiness,
        plan=plan,
    )

    destination = Path(str(token.get("destination_root") or "")).resolve()
    expected_root = Path(expected_dhot_root).resolve()
    if destination != expected_root:
        raise ValueError("runtime_horizon_write_authorization_destination_not_dhot")
    if Path(str(readiness.get("destination_root") or "")).resolve() != expected_root:
        raise ValueError("runtime_horizon_write_authorization_readiness_root_mismatch")
    if readiness.get("ready") is not True or tuple(readiness.get("blockers") or ()):
        raise ValueError("runtime_horizon_write_authorization_readiness_not_ready")

    created = _parse_utc(created_at, "created_at")
    prediction_origin = _parse_utc(
        str(token.get("prediction_origin") or ""),
        "prediction_origin",
    )
    origin_age_sec = (created - prediction_origin).total_seconds()
    if origin_age_sec < 0:
        raise ValueError("runtime_horizon_write_authorization_created_before_origin")
    if origin_age_sec > MAX_AUTHORIZATION_TTL_SEC:
        raise PermissionError("runtime_horizon_write_authorization_origin_too_old")

    expires = created + timedelta(seconds=ttl_sec)
    created_text = created.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    expires_text = expires.replace(microsecond=0).isoformat().replace("+00:00", "Z")

    write_order = tuple(str(item) for item in (token.get("write_order") or ()))
    if len(write_order) != 9 or not write_order[-1].endswith("/manifest.json"):
        raise ValueError("runtime_horizon_write_authorization_write_order_invalid")
    artifact_bindings = tuple(token.get("artifact_bindings") or ())
    if len(artifact_bindings) != 8:
        raise ValueError("runtime_horizon_write_authorization_artifact_bindings_invalid")

    operator_id = str(token.get("operator_id") or "").strip()
    run_id = str(token.get("run_id") or "")
    approval_sha = str(token.get("approval_token_sha256") or "")
    if not operator_id or not run_id or len(approval_sha) != 64:
        raise ValueError("runtime_horizon_write_authorization_identity_invalid")

    authorization_text = (
        f"AUTHORIZE MR-F9 ONE-SHOT D-HOT WRITE run_id={run_id} "
        f"approval_token_sha256={approval_sha} operator_id={operator_id} paths=9"
    )
    package_body = {
        "schema_version": RUNTIME_HORIZON_WRITE_AUTHORIZATION_VERSION,
        "artifact_kind": "market_regime_runtime_horizon_write_authorization_package",
        "destination_root": str(expected_root),
        "run_id": run_id,
        "prediction_origin": str(token.get("prediction_origin") or ""),
        "origin_age_sec_at_package_creation": int(origin_age_sec),
        "operator_id": operator_id,
        "created_at": created_text,
        "expires_at": expires_text,
        "ttl_sec": ttl_sec,
        "approval_token_sha256": approval_sha,
        "readiness_sha256": str(token.get("readiness_sha256") or ""),
        "artifact_bindings": artifact_bindings,
        "manifest_binding": dict(token.get("manifest_binding") or {}),
        "write_order": write_order,
        "manifest_written_last_required": True,
        "expected_authorization_text": authorization_text,
        "expected_authorization_text_sha256": hashlib.sha256(authorization_text.encode("utf-8")).hexdigest(),
        "human_authorized": False,
        "awaiting_explicit_human_authorization": True,
        "writer_invoked": False,
        "writes_dhot": False,
        "writer_registered": False,
        "latest_pointer_created": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "websocket_opened": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
        "post_write_verification_requirements": (
            "written_or_duplicate_count_equals_9",
            "manifest_written_last",
            "all_payload_digests_match",
            "manifest_semantic_bindings_match",
            "second_execution_duplicate_count_equals_9",
            "conflict_probe_fails_closed",
            "latest_pointer_absent",
            "writer_not_registered",
            "scheduler_loop_ws_ui_execution_disabled",
        ),
    }
    return {**package_body, "authorization_package_sha256": _digest(package_body)}


def validate_runtime_horizon_write_authorization_package(
    *,
    package: Mapping[str, Any],
    token: Mapping[str, Any],
    readiness: Mapping[str, Any],
    plan: Mapping[str, Any],
    now: str,
    expected_dhot_root: str | Path,
) -> None:
    if not isinstance(package, Mapping):
        raise ValueError("runtime_horizon_write_authorization_package_invalid")
    rebuilt = build_runtime_horizon_write_authorization_package(
        token=token,
        readiness=readiness,
        plan=plan,
        created_at=str(package.get("created_at") or ""),
        ttl_sec=int(package.get("ttl_sec") or 0),
        expected_dhot_root=expected_dhot_root,
    )
    if _json_native(package) != _json_native(rebuilt):
        raise ValueError("runtime_horizon_write_authorization_package_mismatch")

    now_dt = _parse_utc(now, "now")
    created_dt = _parse_utc(str(package.get("created_at") or ""), "created_at")
    expires_dt = _parse_utc(str(package.get("expires_at") or ""), "expires_at")
    if now_dt < created_dt:
        raise ValueError("runtime_horizon_write_authorization_not_yet_valid")
    if now_dt > expires_dt:
        raise PermissionError("runtime_horizon_write_authorization_expired")
