# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_read_only_loader.py
# desc: PS-Q9B minimal guarded read-only loader for explicitly allowed Prediction WarRoom latest JSON payloads. Performs bounded stat/read/decode only when explicitly enabled; no rendering, runtime writes, Collector runtime, AutoTrade, broker, mode, approval/grant, or ledger append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT
from .prediction_warroom_latest_payload_actual_read_preflight_contract import (
    ACTUAL_READ_PREFLIGHT_CONTRACT_VERSION,
    build_prediction_warroom_latest_payload_actual_read_preflight_contract,
)
from .prediction_warroom_payload_schema_validator import VALIDATOR_VERSION

READ_ONLY_LOADER_VERSION = "prediction_warroom_latest_payload_read_only_loader.ps_q9b.v1"
DEFAULT_ALLOWED_ARTIFACT_ROLES = ("prediction_system_result_snapshot",)


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadReadOnlyArtifactResult:
    artifact_role: str
    artifact_contract_id: str
    allowed_path_hint: str
    required: bool
    loader_state: str
    path_exists: bool = False
    observed_file_size_bytes: int | None = None
    observed_age_sec: int | None = None
    observed_last_modified_at: str | None = None
    preflight_ready_for_read: bool = False
    actual_file_read_attempted: bool = False
    actual_file_read_succeeded: bool = False
    payload_decode_attempted: bool = False
    payload_decode_succeeded: bool = False
    payload_type: str | None = None
    payload_key_count: int = 0
    payload_preview_keys: Tuple[str, ...] = ()
    blocker_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    exception_class: str | None = None
    exception_message: str | None = None
    read_only: bool = True
    non_executing: bool = True
    guarded_loader_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    would_write_runtime_artifact: bool = False
    would_write_collector_state: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False
    authorization_grant_requested: bool = False
    autotrade_trigger_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_role": self.artifact_role,
            "artifact_contract_id": self.artifact_contract_id,
            "allowed_path_hint": self.allowed_path_hint,
            "required": self.required,
            "loader_state": self.loader_state,
            "path_exists": self.path_exists,
            "observed_file_size_bytes": self.observed_file_size_bytes,
            "observed_age_sec": self.observed_age_sec,
            "observed_last_modified_at": self.observed_last_modified_at,
            "preflight_ready_for_read": self.preflight_ready_for_read,
            "actual_file_read_attempted": self.actual_file_read_attempted,
            "actual_file_read_succeeded": self.actual_file_read_succeeded,
            "payload_decode_attempted": self.payload_decode_attempted,
            "payload_decode_succeeded": self.payload_decode_succeeded,
            "payload_type": self.payload_type,
            "payload_key_count": self.payload_key_count,
            "payload_preview_keys": list(self.payload_preview_keys),
            "blocker_reasons": list(self.blocker_reasons),
            "warning_reasons": list(self.warning_reasons),
            "exception_class": self.exception_class,
            "exception_message": self.exception_message,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "guarded_loader_only": self.guarded_loader_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_write_collector_state": self.would_write_collector_state,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
            "authorization_grant_requested": self.authorization_grant_requested,
            "autotrade_trigger_enabled": self.autotrade_trigger_enabled,
        }


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadReadOnlyLoaderResult:
    loader_version: str
    loader_id: str
    loader_state: str
    hot_latest_root_hint: str
    actual_read_preflight_contract_version: str
    schema_validator_contract_version: str
    allowed_artifact_roles: Tuple[str, ...]
    preflight_contract: Mapping[str, Any] = field(default_factory=dict)
    artifact_results: Tuple[PredictionWarRoomLatestPayloadReadOnlyArtifactResult, ...] = ()
    loaded_payloads: Mapping[str, Any] = field(default_factory=dict)
    loaded_payload_count: int = 0
    blocker_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    allow_actual_read_requested: bool = False
    actual_file_read_attempted: bool = False
    actual_file_read_succeeded: bool = False
    payload_decode_attempted: bool = False
    payload_decode_succeeded: bool = False
    schema_validation_deferred_to_ps_q9c: bool = True
    read_only: bool = True
    non_executing: bool = True
    guarded_loader_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    would_write_runtime_artifact: bool = False
    would_write_collector_state: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False
    authorization_grant_requested: bool = False
    autotrade_trigger_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loader_version": self.loader_version,
            "loader_id": self.loader_id,
            "loader_state": self.loader_state,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "actual_read_preflight_contract_version": self.actual_read_preflight_contract_version,
            "schema_validator_contract_version": self.schema_validator_contract_version,
            "allowed_artifact_roles": list(self.allowed_artifact_roles),
            "preflight_contract": dict(self.preflight_contract),
            "artifact_results": [item.to_dict() for item in self.artifact_results],
            "loaded_payloads": dict(self.loaded_payloads),
            "loaded_payload_count": self.loaded_payload_count,
            "blocker_reasons": list(self.blocker_reasons),
            "warning_reasons": list(self.warning_reasons),
            "allow_actual_read_requested": self.allow_actual_read_requested,
            "actual_file_read_attempted": self.actual_file_read_attempted,
            "actual_file_read_succeeded": self.actual_file_read_succeeded,
            "payload_decode_attempted": self.payload_decode_attempted,
            "payload_decode_succeeded": self.payload_decode_succeeded,
            "schema_validation_deferred_to_ps_q9c": self.schema_validation_deferred_to_ps_q9c,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "guarded_loader_only": self.guarded_loader_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_write_collector_state": self.would_write_collector_state,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
            "authorization_grant_requested": self.authorization_grant_requested,
            "autotrade_trigger_enabled": self.autotrade_trigger_enabled,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _preview_keys(payload: Any) -> tuple[str, ...]:
    if isinstance(payload, Mapping):
        return tuple(str(key) for key in list(payload.keys())[:12])
    return ()


def _metadata_for_candidate(candidate: Mapping[str, Any], *, now: datetime) -> Mapping[str, Any]:
    path_hint = str(candidate.get("allowed_path_hint") or "")
    path = Path(path_hint)
    if not path.exists():
        return {
            "artifact_role": candidate.get("artifact_role"),
            "supplied": True,
            "path_hint": path_hint,
            "freshness_status": "missing",
            "blocker_reasons": ("actual_read_candidate_file_missing",),
        }
    stat = path.stat()
    modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    observed_age_sec = max(0, int((now - modified).total_seconds()))
    freshness_max_age_sec = int(candidate.get("freshness_max_age_sec") or 0)
    freshness_status = "fresh" if freshness_max_age_sec > 0 and observed_age_sec <= freshness_max_age_sec else "stale"
    return {
        "artifact_role": candidate.get("artifact_role"),
        "supplied": True,
        "path_hint": path_hint,
        "file_size_bytes": int(stat.st_size),
        "observed_age_sec": observed_age_sec,
        "observed_last_modified_at": modified.isoformat(),
        "freshness_status": freshness_status,
        "schema_validation_status": "planned_not_run",
    }


def _result_blocked(candidate: Mapping[str, Any], *, state: str, blockers: Iterable[str], warnings: Iterable[str] = ()) -> PredictionWarRoomLatestPayloadReadOnlyArtifactResult:
    return PredictionWarRoomLatestPayloadReadOnlyArtifactResult(
        artifact_role=str(candidate.get("artifact_role") or "unknown"),
        artifact_contract_id=str(candidate.get("artifact_contract_id") or "unknown"),
        allowed_path_hint=str(candidate.get("allowed_path_hint") or ""),
        required=bool(candidate.get("required", True)),
        loader_state=state,
        path_exists=False,
        observed_file_size_bytes=candidate.get("observed_file_size_bytes") if isinstance(candidate.get("observed_file_size_bytes"), int) else None,
        observed_age_sec=candidate.get("observed_age_sec") if isinstance(candidate.get("observed_age_sec"), int) else None,
        observed_last_modified_at=str(candidate.get("observed_last_modified_at")) if candidate.get("observed_last_modified_at") else None,
        preflight_ready_for_read=bool(candidate.get("candidate_ready_for_ps_q9b_guarded_actual_read")),
        blocker_reasons=tuple(str(item) for item in blockers if item),
        warning_reasons=tuple(str(item) for item in warnings if item),
    )


def _read_candidate_payload(candidate: Mapping[str, Any]) -> tuple[PredictionWarRoomLatestPayloadReadOnlyArtifactResult, Any | None]:
    path = Path(str(candidate.get("allowed_path_hint") or ""))
    blockers: list[str] = []
    warnings: list[str] = [str(item) for item in candidate.get("warning_reasons", ())]
    try:
        max_bytes = int(candidate.get("max_file_size_bytes") or 0)
        raw = path.read_bytes()
        if max_bytes > 0 and len(raw) > max_bytes:
            return (
                PredictionWarRoomLatestPayloadReadOnlyArtifactResult(
                    artifact_role=str(candidate.get("artifact_role") or "unknown"),
                    artifact_contract_id=str(candidate.get("artifact_contract_id") or "unknown"),
                    allowed_path_hint=str(candidate.get("allowed_path_hint") or ""),
                    required=bool(candidate.get("required", True)),
                    loader_state="blocked_file_size_exceeded_after_read_guard",
                    path_exists=True,
                    observed_file_size_bytes=len(raw),
                    observed_age_sec=candidate.get("observed_age_sec") if isinstance(candidate.get("observed_age_sec"), int) else None,
                    observed_last_modified_at=str(candidate.get("observed_last_modified_at")) if candidate.get("observed_last_modified_at") else None,
                    preflight_ready_for_read=True,
                    actual_file_read_attempted=True,
                    actual_file_read_succeeded=False,
                    payload_decode_attempted=False,
                    payload_decode_succeeded=False,
                    blocker_reasons=("file_size_exceeds_max_after_read_guard",),
                    warning_reasons=tuple(warnings),
                ),
                None,
            )
        text = raw.decode("utf-8")
    except Exception as exc:  # noqa: BLE001 - report fail-closed loader boundary
        return (
            PredictionWarRoomLatestPayloadReadOnlyArtifactResult(
                artifact_role=str(candidate.get("artifact_role") or "unknown"),
                artifact_contract_id=str(candidate.get("artifact_contract_id") or "unknown"),
                allowed_path_hint=str(candidate.get("allowed_path_hint") or ""),
                required=bool(candidate.get("required", True)),
                loader_state="blocked_file_read_failed",
                path_exists=path.exists(),
                observed_file_size_bytes=candidate.get("observed_file_size_bytes") if isinstance(candidate.get("observed_file_size_bytes"), int) else None,
                observed_age_sec=candidate.get("observed_age_sec") if isinstance(candidate.get("observed_age_sec"), int) else None,
                observed_last_modified_at=str(candidate.get("observed_last_modified_at")) if candidate.get("observed_last_modified_at") else None,
                preflight_ready_for_read=True,
                actual_file_read_attempted=True,
                actual_file_read_succeeded=False,
                payload_decode_attempted=False,
                payload_decode_succeeded=False,
                blocker_reasons=("actual_file_read_failed",),
                warning_reasons=tuple(warnings),
                exception_class=exc.__class__.__name__,
                exception_message=str(exc),
            ),
            None,
        )
    try:
        payload = json.loads(text)
    except Exception as exc:  # noqa: BLE001 - report fail-closed decode boundary
        return (
            PredictionWarRoomLatestPayloadReadOnlyArtifactResult(
                artifact_role=str(candidate.get("artifact_role") or "unknown"),
                artifact_contract_id=str(candidate.get("artifact_contract_id") or "unknown"),
                allowed_path_hint=str(candidate.get("allowed_path_hint") or ""),
                required=bool(candidate.get("required", True)),
                loader_state="blocked_payload_decode_failed",
                path_exists=True,
                observed_file_size_bytes=candidate.get("observed_file_size_bytes") if isinstance(candidate.get("observed_file_size_bytes"), int) else None,
                observed_age_sec=candidate.get("observed_age_sec") if isinstance(candidate.get("observed_age_sec"), int) else None,
                observed_last_modified_at=str(candidate.get("observed_last_modified_at")) if candidate.get("observed_last_modified_at") else None,
                preflight_ready_for_read=True,
                actual_file_read_attempted=True,
                actual_file_read_succeeded=True,
                payload_decode_attempted=True,
                payload_decode_succeeded=False,
                blocker_reasons=("payload_decode_failed",),
                warning_reasons=tuple(warnings),
                exception_class=exc.__class__.__name__,
                exception_message=str(exc),
            ),
            None,
        )
    payload_type = type(payload).__name__
    return (
        PredictionWarRoomLatestPayloadReadOnlyArtifactResult(
            artifact_role=str(candidate.get("artifact_role") or "unknown"),
            artifact_contract_id=str(candidate.get("artifact_contract_id") or "unknown"),
            allowed_path_hint=str(candidate.get("allowed_path_hint") or ""),
            required=bool(candidate.get("required", True)),
            loader_state="loaded_read_only_payload_decode_succeeded",
            path_exists=True,
            observed_file_size_bytes=candidate.get("observed_file_size_bytes") if isinstance(candidate.get("observed_file_size_bytes"), int) else None,
            observed_age_sec=candidate.get("observed_age_sec") if isinstance(candidate.get("observed_age_sec"), int) else None,
            observed_last_modified_at=str(candidate.get("observed_last_modified_at")) if candidate.get("observed_last_modified_at") else None,
            preflight_ready_for_read=True,
            actual_file_read_attempted=True,
            actual_file_read_succeeded=True,
            payload_decode_attempted=True,
            payload_decode_succeeded=True,
            payload_type=payload_type,
            payload_key_count=len(payload) if isinstance(payload, Mapping) else 0,
            payload_preview_keys=_preview_keys(payload),
            warning_reasons=tuple(dict.fromkeys(warnings + ["schema_validation_deferred_to_ps_q9c"])),
        ),
        payload,
    )


def load_prediction_warroom_latest_payload_read_only(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    allowed_artifact_roles: Iterable[str] = DEFAULT_ALLOWED_ARTIFACT_ROLES,
    allow_actual_read: bool = False,
    now: datetime | None = None,
) -> PredictionWarRoomLatestPayloadReadOnlyLoaderResult:
    """Load explicitly allowed latest prediction JSON payloads as read-only data when allow_actual_read=True."""
    now_utc = now or datetime.now(timezone.utc)
    allowed_roles = tuple(str(item) for item in allowed_artifact_roles)
    base_contract = build_prediction_warroom_latest_payload_actual_read_preflight_contract(
        hot_latest_root_hint=hot_latest_root_hint
    ).to_dict()
    base_candidates = [
        item for item in base_contract.get("allowed_candidates", ())
        if str(item.get("artifact_role")) in allowed_roles
    ]
    if not allow_actual_read:
        results = tuple(
            _result_blocked(
                candidate,
                state="blocked_actual_read_not_requested",
                blockers=("allow_actual_read_false",),
                warnings=("caller_must_explicitly_request_ps_q9b_read_only_load",),
            )
            for candidate in base_candidates
        )
        return PredictionWarRoomLatestPayloadReadOnlyLoaderResult(
            loader_version=READ_ONLY_LOADER_VERSION,
            loader_id=f"{READ_ONLY_LOADER_VERSION}:latest:blocked",
            loader_state="blocked_actual_read_not_requested",
            hot_latest_root_hint=str(hot_latest_root_hint),
            actual_read_preflight_contract_version=ACTUAL_READ_PREFLIGHT_CONTRACT_VERSION,
            schema_validator_contract_version=VALIDATOR_VERSION,
            allowed_artifact_roles=allowed_roles,
            preflight_contract=base_contract,
            artifact_results=results,
            blocker_reasons=("allow_actual_read_false",),
            warning_reasons=("caller_must_explicitly_request_ps_q9b_read_only_load",),
            allow_actual_read_requested=False,
        )

    metadata_inputs = tuple(_metadata_for_candidate(candidate, now=now_utc) for candidate in base_candidates)
    contract = build_prediction_warroom_latest_payload_actual_read_preflight_contract(
        candidate_metadata_inputs=metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    candidates = [
        item for item in contract.get("allowed_candidates", ())
        if str(item.get("artifact_role")) in allowed_roles
    ]
    results: list[PredictionWarRoomLatestPayloadReadOnlyArtifactResult] = []
    payloads: dict[str, Any] = {}
    blockers: list[str] = [str(item) for item in contract.get("blocked_reasons", ())]
    warnings: list[str] = [str(item) for item in contract.get("warning_reasons", ())]
    for candidate in candidates:
        candidate_blockers = tuple(str(item) for item in candidate.get("blocker_reasons", ()) if item)
        if not bool(candidate.get("candidate_ready_for_ps_q9b_guarded_actual_read")) or candidate_blockers:
            result = _result_blocked(
                candidate,
                state="blocked_by_q9a_preflight_contract",
                blockers=candidate_blockers or ("candidate_not_ready_for_ps_q9b_guarded_actual_read",),
                warnings=tuple(str(item) for item in candidate.get("warning_reasons", ()) if item),
            )
            results.append(result)
            continue
        result, payload = _read_candidate_payload(candidate)
        results.append(result)
        blockers.extend(result.blocker_reasons)
        warnings.extend(result.warning_reasons)
        if result.payload_decode_succeeded and payload is not None:
            payloads[result.artifact_role] = payload
    read_attempted = any(item.actual_file_read_attempted for item in results)
    read_succeeded = any(item.actual_file_read_succeeded for item in results)
    decode_attempted = any(item.payload_decode_attempted for item in results)
    decode_succeeded = any(item.payload_decode_succeeded for item in results)
    if payloads and not blockers:
        loader_state = "loaded_read_only_payload_decode_succeeded_schema_validation_deferred"
    elif read_attempted:
        loader_state = "blocked_after_read_or_decode_failure"
    else:
        loader_state = "blocked_before_actual_read"
    return PredictionWarRoomLatestPayloadReadOnlyLoaderResult(
        loader_version=READ_ONLY_LOADER_VERSION,
        loader_id=f"{READ_ONLY_LOADER_VERSION}:latest:{'loaded' if payloads else 'blocked'}",
        loader_state=loader_state,
        hot_latest_root_hint=str(hot_latest_root_hint),
        actual_read_preflight_contract_version=ACTUAL_READ_PREFLIGHT_CONTRACT_VERSION,
        schema_validator_contract_version=VALIDATOR_VERSION,
        allowed_artifact_roles=allowed_roles,
        preflight_contract=contract,
        artifact_results=tuple(results),
        loaded_payloads=payloads,
        loaded_payload_count=len(payloads),
        blocker_reasons=tuple(dict.fromkeys(item for item in blockers if item)),
        warning_reasons=tuple(dict.fromkeys(item for item in warnings if item)),
        allow_actual_read_requested=True,
        actual_file_read_attempted=read_attempted,
        actual_file_read_succeeded=read_succeeded,
        payload_decode_attempted=decode_attempted,
        payload_decode_succeeded=decode_succeeded,
    )
