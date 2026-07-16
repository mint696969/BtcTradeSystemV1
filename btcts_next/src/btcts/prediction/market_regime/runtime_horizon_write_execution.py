# path: ./btcts_next/src/btcts/prediction/market_regime/runtime_horizon_write_execution.py
# desc: MR-F9.19H limited once-only execution envelope; validates one exact approval token before calling the guarded writer.

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from btcts.prediction.market_regime.runtime_horizon_persistence import (
    persist_runtime_horizon_plan_once,
)
from btcts.prediction.market_regime.runtime_horizon_write_approval import (
    validate_runtime_horizon_write_approval_token,
)

RUNTIME_HORIZON_WRITE_EXECUTION_VERSION = (
    "prediction.market_regime.runtime_horizon_write_execution.mr_f9_19h.v1"
)
REPOSITORY_ROOT = Path(__file__).resolve().parents[5]


def classify_execution_output_root(
    output_root: str | Path,
    *,
    repository_root: str | Path = REPOSITORY_ROOT,
) -> str:
    resolved = Path(output_root).resolve()
    repo_tmp = (Path(repository_root).resolve() / "tmp").resolve()
    try:
        resolved.relative_to(repo_tmp)
    except ValueError as exc:
        raise ValueError("runtime_horizon_write_execution_output_root_not_repo_tmp") from exc
    return "repo_tmp"


def execute_runtime_horizon_write_with_approval_once(
    *,
    output_root: str | Path,
    token: Mapping[str, Any],
    readiness: Mapping[str, Any],
    plan: Mapping[str, Any],
    enabled: bool = False,
    once: bool = False,
    repository_root: str | Path = REPOSITORY_ROOT,
) -> Mapping[str, Any]:
    if any(type(value) is not bool for value in (enabled, once)):
        raise ValueError("runtime_horizon_write_execution_flags_invalid")
    if enabled is not True:
        raise PermissionError("runtime_horizon_write_execution_enabled_ack_required")
    if once is not True:
        raise PermissionError("runtime_horizon_write_execution_once_ack_required")
    if not isinstance(token, Mapping):
        raise ValueError("runtime_horizon_write_execution_token_invalid")
    if not isinstance(readiness, Mapping):
        raise ValueError("runtime_horizon_write_execution_readiness_invalid")
    if not isinstance(plan, Mapping):
        raise ValueError("runtime_horizon_write_execution_plan_invalid")

    resolved_output_root = Path(output_root).resolve()
    output_root_kind = classify_execution_output_root(
        resolved_output_root,
        repository_root=repository_root,
    )

    validate_runtime_horizon_write_approval_token(
        token=token,
        readiness=readiness,
        plan=plan,
    )

    if str(token.get("destination_root") or "") != str(resolved_output_root):
        raise ValueError("runtime_horizon_write_execution_destination_root_mismatch")
    if str(readiness.get("destination_root") or "") != str(resolved_output_root):
        raise ValueError("runtime_horizon_write_execution_readiness_root_mismatch")
    if token.get("enabled_acknowledged") is not True:
        raise PermissionError("runtime_horizon_write_execution_token_enabled_ack_required")
    if token.get("once_acknowledged") is not True:
        raise PermissionError("runtime_horizon_write_execution_token_once_ack_required")

    write_result = persist_runtime_horizon_plan_once(
        resolved_output_root,
        plan=plan,
        enabled=True,
        once=True,
    )
    for key in (
        "latest_pointer_created",
        "writer_registered",
        "producer_loop_enabled",
        "scheduler_enabled",
        "websocket_opened",
        "order_submission_allowed",
    ):
        if write_result.get(key) is not False:
            raise ValueError(f"runtime_horizon_write_execution_result_safety_invalid:{key}")

    return {
        "schema_version": RUNTIME_HORIZON_WRITE_EXECUTION_VERSION,
        "artifact_kind": "market_regime_runtime_horizon_write_execution_result",
        "output_root": str(resolved_output_root),
        "output_root_kind": output_root_kind,
        "run_id": str(token.get("run_id") or ""),
        "prediction_origin": str(token.get("prediction_origin") or ""),
        "operator_id": str(token.get("operator_id") or ""),
        "approval_token_sha256": str(token.get("approval_token_sha256") or ""),
        "approval_validated_before_writer": True,
        "explicit_enabled_acknowledged": True,
        "explicit_once_acknowledged": True,
        "write_result": dict(write_result),
        "writes_dhot": False,
        "writer_registered": False,
        "latest_pointer_created": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "websocket_opened": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
    }
