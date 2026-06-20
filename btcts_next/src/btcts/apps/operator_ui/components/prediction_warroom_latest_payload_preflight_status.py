# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_preflight_status.py
# desc: Contract-only latest payload preflight status for Prediction WarRoom. Describes future loader readiness/freshness/schema status without filesystem reads, rendering, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_l4_latest_adapter import (
    ADAPTER_VERSION,
    DEFAULT_HOT_LATEST_ROOT_HINT,
    build_prediction_warroom_l4_latest_expected_artifacts,
)
from .prediction_warroom_payload_schema_validator import VALIDATOR_VERSION

PREFLIGHT_STATUS_VERSION = "prediction_warroom_latest_payload_preflight_status.ps_q6a.v1"

_FRESHNESS_BLOCK_STATES = {"missing", "stale", "expired", "unknown_required"}
_SCHEMA_BLOCK_STATES = {"invalid", "failed", "schema_blocked"}


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadPreflightArtifactStatus:
    artifact_role: str
    artifact_contract_id: str
    expected_path_hint: str | None = None
    required: bool = True
    supplied_by_preflight_input: bool = False
    future_loader_required: bool = True
    future_loader_must_check_freshness: bool = True
    future_loader_must_run_schema_validation: bool = True
    freshness_status: str = "not_checked"
    freshness_max_age_sec: int | None = None
    observed_age_sec: int | None = None
    observed_last_modified_at: str | None = None
    schema_validation_status: str = "not_run"
    schema_validation_report_version: str | None = None
    schema_validation_valid: bool | None = None
    payload_contract_version: str | None = None
    blocker_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    refresh_group_id: str | None = None
    read_by_this_slice: bool = False
    loaded_in_this_slice: bool = False
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    preflight_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    would_load_hot_latest_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_write_collector_state: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_role": self.artifact_role,
            "artifact_contract_id": self.artifact_contract_id,
            "expected_path_hint": self.expected_path_hint,
            "required": self.required,
            "supplied_by_preflight_input": self.supplied_by_preflight_input,
            "future_loader_required": self.future_loader_required,
            "future_loader_must_check_freshness": self.future_loader_must_check_freshness,
            "future_loader_must_run_schema_validation": self.future_loader_must_run_schema_validation,
            "freshness_status": self.freshness_status,
            "freshness_max_age_sec": self.freshness_max_age_sec,
            "observed_age_sec": self.observed_age_sec,
            "observed_last_modified_at": self.observed_last_modified_at,
            "schema_validation_status": self.schema_validation_status,
            "schema_validation_report_version": self.schema_validation_report_version,
            "schema_validation_valid": self.schema_validation_valid,
            "payload_contract_version": self.payload_contract_version,
            "blocker_reasons": list(self.blocker_reasons),
            "warning_reasons": list(self.warning_reasons),
            "refresh_group_id": self.refresh_group_id,
            "read_by_this_slice": self.read_by_this_slice,
            "loaded_in_this_slice": self.loaded_in_this_slice,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "preflight_only": self.preflight_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_write_collector_state": self.would_write_collector_state,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
        }


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadPreflightStatusPacket:
    preflight_status_version: str
    preflight_id: str
    preflight_state: str
    hot_latest_root_hint: str
    l4_latest_adapter_contract_version: str
    schema_validator_contract_version: str
    artifact_statuses: Tuple[PredictionWarRoomLatestPayloadPreflightArtifactStatus, ...] = ()
    required_artifact_blocker_count: int = 0
    freshness_blocker_count: int = 0
    schema_blocker_count: int = 0
    optional_artifact_warning_count: int = 0
    preflight_ready_for_payload_handoff: bool = False
    future_loader_required: bool = True
    future_loader_allowed_by_this_contract: bool = False
    future_loader_must_validate_schema_before_display: bool = True
    future_loader_must_check_freshness_before_display: bool = True
    future_loader_must_not_write_runtime_artifacts: bool = True
    future_loader_must_not_trigger_autotrade: bool = True
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    handoff_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    preflight_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    would_load_hot_latest_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_write_collector_state: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "preflight_status_version": self.preflight_status_version,
            "preflight_id": self.preflight_id,
            "preflight_state": self.preflight_state,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "l4_latest_adapter_contract_version": self.l4_latest_adapter_contract_version,
            "schema_validator_contract_version": self.schema_validator_contract_version,
            "artifact_statuses": [item.to_dict() for item in self.artifact_statuses],
            "required_artifact_blocker_count": self.required_artifact_blocker_count,
            "freshness_blocker_count": self.freshness_blocker_count,
            "schema_blocker_count": self.schema_blocker_count,
            "optional_artifact_warning_count": self.optional_artifact_warning_count,
            "preflight_ready_for_payload_handoff": self.preflight_ready_for_payload_handoff,
            "future_loader_required": self.future_loader_required,
            "future_loader_allowed_by_this_contract": self.future_loader_allowed_by_this_contract,
            "future_loader_must_validate_schema_before_display": self.future_loader_must_validate_schema_before_display,
            "future_loader_must_check_freshness_before_display": self.future_loader_must_check_freshness_before_display,
            "future_loader_must_not_write_runtime_artifacts": self.future_loader_must_not_write_runtime_artifacts,
            "future_loader_must_not_trigger_autotrade": self.future_loader_must_not_trigger_autotrade,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "handoff_summary": dict(self.handoff_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "preflight_only": self.preflight_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_write_collector_state": self.would_write_collector_state,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _bool_or_none(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None


def _artifact_status_input_by_role(artifact_status_inputs: Iterable[Mapping[str, Any]] | None) -> dict[str, Mapping[str, Any]]:
    by_role: dict[str, Mapping[str, Any]] = {}
    for raw in artifact_status_inputs or ():
        item = _as_mapping(raw)
        role = str(item.get("artifact_role") or "")
        if role:
            by_role[role] = item
    return by_role


def _build_artifact_status(ref: Any, supplied: Mapping[str, Any]) -> PredictionWarRoomLatestPayloadPreflightArtifactStatus:
    ref_data = _as_mapping(ref)
    artifact_role = str(ref_data.get("artifact_role") or "unknown")
    required = bool(ref_data.get("required", True))
    supplied_by_preflight_input = bool(
        supplied.get("supplied_by_preflight_input")
        or supplied.get("artifact_available")
        or supplied.get("payload_supplied")
        or supplied.get("supplied")
    )
    freshness_status = str(supplied.get("freshness_status") or ("not_checked" if supplied_by_preflight_input else "missing"))
    schema_validation_status = str(supplied.get("schema_validation_status") or ("not_run" if supplied_by_preflight_input else "not_available"))
    schema_validation_valid = _bool_or_none(supplied.get("schema_validation_valid"))
    schema_report_version = supplied.get("schema_validation_report_version")
    if not schema_report_version and schema_validation_status in {"valid", "invalid", "failed", "schema_blocked"}:
        schema_report_version = VALIDATOR_VERSION
    blocker_reasons: list[str] = [str(item) for item in _list(supplied.get("blocker_reasons"))]
    warning_reasons: list[str] = [str(item) for item in _list(supplied.get("warning_reasons"))]
    if required and not supplied_by_preflight_input:
        blocker_reasons.append("required_artifact_not_supplied_by_preflight_input")
    if not required and not supplied_by_preflight_input:
        warning_reasons.append("optional_artifact_not_supplied_by_preflight_input")
    if required and freshness_status in _FRESHNESS_BLOCK_STATES:
        reason = f"freshness_status_{freshness_status}"
        if reason not in blocker_reasons:
            blocker_reasons.append(reason)
    if schema_validation_status in _SCHEMA_BLOCK_STATES or schema_validation_valid is False:
        reason = "schema_validation_blocked"
        if reason not in blocker_reasons:
            blocker_reasons.append(reason)
    if supplied_by_preflight_input and freshness_status == "not_checked":
        warning_reasons.append("future_loader_must_check_freshness_before_display")
    if supplied_by_preflight_input and schema_validation_status == "not_run":
        warning_reasons.append("future_loader_must_run_schema_validation_before_display")
    return PredictionWarRoomLatestPayloadPreflightArtifactStatus(
        artifact_role=artifact_role,
        artifact_contract_id=str(ref_data.get("artifact_contract_id") or supplied.get("artifact_contract_id") or "unknown"),
        expected_path_hint=str(ref_data.get("expected_path_hint")) if ref_data.get("expected_path_hint") else None,
        required=required,
        supplied_by_preflight_input=supplied_by_preflight_input,
        future_loader_required=not supplied_by_preflight_input,
        freshness_status=freshness_status,
        freshness_max_age_sec=int(supplied["freshness_max_age_sec"]) if isinstance(supplied.get("freshness_max_age_sec"), int) else None,
        observed_age_sec=int(supplied["observed_age_sec"]) if isinstance(supplied.get("observed_age_sec"), int) else None,
        observed_last_modified_at=str(supplied.get("observed_last_modified_at")) if supplied.get("observed_last_modified_at") else None,
        schema_validation_status=schema_validation_status,
        schema_validation_report_version=str(schema_report_version) if schema_report_version else None,
        schema_validation_valid=schema_validation_valid,
        payload_contract_version=str(supplied.get("payload_contract_version")) if supplied.get("payload_contract_version") else None,
        blocker_reasons=tuple(dict.fromkeys(blocker_reasons)),
        warning_reasons=tuple(dict.fromkeys(warning_reasons)),
        refresh_group_id=str(ref_data.get("refresh_group_id")) if ref_data.get("refresh_group_id") else None,
    )


def build_prediction_warroom_latest_payload_preflight_status_contract(
    *,
    artifact_status_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
) -> PredictionWarRoomLatestPayloadPreflightStatusPacket:
    """Build a contract-only latest payload preflight status without reading hot/latest artifacts."""
    supplied_by_role = _artifact_status_input_by_role(artifact_status_inputs)
    expected_refs = build_prediction_warroom_l4_latest_expected_artifacts(hot_latest_root_hint=hot_latest_root_hint)
    statuses = tuple(_build_artifact_status(ref, supplied_by_role.get(_as_mapping(ref).get("artifact_role", ""), {})) for ref in expected_refs)
    required_blockers = sum(1 for item in statuses if item.required and any(reason.startswith("required_artifact") for reason in item.blocker_reasons))
    freshness_blockers = sum(1 for item in statuses if any(reason.startswith("freshness_status") for reason in item.blocker_reasons))
    schema_blockers = sum(1 for item in statuses if "schema_validation_blocked" in item.blocker_reasons)
    optional_warnings = sum(1 for item in statuses if "optional_artifact_not_supplied_by_preflight_input" in item.warning_reasons)
    blocked_reasons: list[str] = []
    if required_blockers:
        blocked_reasons.append("required_latest_artifact_not_supplied")
    if freshness_blockers:
        blocked_reasons.append("freshness_not_acceptable")
    if schema_blockers:
        blocked_reasons.append("schema_validation_not_acceptable")
    warning_reasons: list[str] = []
    if optional_warnings:
        warning_reasons.append("optional_latest_artifacts_not_supplied")
    if any("future_loader_must_check_freshness_before_display" in item.warning_reasons for item in statuses):
        warning_reasons.append("future_loader_must_check_freshness_before_display")
    if any("future_loader_must_run_schema_validation_before_display" in item.warning_reasons for item in statuses):
        warning_reasons.append("future_loader_must_run_schema_validation_before_display")
    ready = not blocked_reasons and any(item.supplied_by_preflight_input for item in statuses)
    preflight_state = "ready_for_payload_handoff" if ready else "blocked_waiting_for_latest_loader"
    return PredictionWarRoomLatestPayloadPreflightStatusPacket(
        preflight_status_version=PREFLIGHT_STATUS_VERSION,
        preflight_id=f"{PREFLIGHT_STATUS_VERSION}:latest:{'ready' if ready else 'waiting'}",
        preflight_state=preflight_state,
        hot_latest_root_hint=str(hot_latest_root_hint),
        l4_latest_adapter_contract_version=ADAPTER_VERSION,
        schema_validator_contract_version=VALIDATOR_VERSION,
        artifact_statuses=statuses,
        required_artifact_blocker_count=required_blockers,
        freshness_blocker_count=freshness_blockers,
        schema_blocker_count=schema_blockers,
        optional_artifact_warning_count=optional_warnings,
        preflight_ready_for_payload_handoff=ready,
        blocked_reasons=tuple(blocked_reasons),
        warning_reasons=tuple(dict.fromkeys(warning_reasons)),
        handoff_summary={
            "preflight_boundary": "latest_payload_contract_status_before_loader",
            "hot_latest_root_preference": str(hot_latest_root_hint),
            "expected_artifact_count": len(statuses),
            "required_artifact_roles": [item.artifact_role for item in statuses if item.required],
            "optional_artifact_roles": [item.artifact_role for item in statuses if not item.required],
            "schema_validator_contract_version": VALIDATOR_VERSION,
            "future_loader_required": True,
            "future_loader_allowed_by_this_contract": False,
            "loaded_in_this_slice": False,
            "runtime_file_read_enabled": False,
            "runtime_artifact_write_enabled": False,
            "autotrade_trigger_enabled": False,
        },
    )
