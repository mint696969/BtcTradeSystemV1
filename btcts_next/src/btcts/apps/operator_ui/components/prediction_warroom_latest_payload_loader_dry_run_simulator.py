# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_loader_dry_run_simulator.py
# desc: Dry-run simulator for a future Prediction WarRoom latest-payload loader. Uses supplied metadata only; no file access, payload decode, rendering, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_latest_payload_loader_permission_contract import (
    LOADER_PERMISSION_CONTRACT_VERSION,
    build_prediction_warroom_latest_payload_loader_permission_contract,
)
from .prediction_warroom_latest_payload_preflight_status import (
    PREFLIGHT_STATUS_VERSION,
    build_prediction_warroom_latest_payload_preflight_status_contract,
)

LOADER_DRY_RUN_SIMULATOR_VERSION = "prediction_warroom_latest_payload_loader_dry_run_simulator.ps_q6c.v1"

_PATH_BLOCK_STATES = {"not_supplied", "outside_hot_latest_root", "unexpected_path", "missing_path_hint"}
_EXTENSION_BLOCK_STATES = {"not_json"}
_SIZE_BLOCK_STATES = {"too_large"}
_FRESHNESS_BLOCK_STATES = {"missing", "stale", "expired", "unknown_required"}
_SCHEMA_BLOCK_STATES = {"invalid", "failed", "schema_blocked"}


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadLoaderDryRunArtifactEvaluation:
    artifact_role: str
    artifact_contract_id: str
    required: bool
    supplied_by_metadata_input: bool = False
    allowed_root_hint: str | None = None
    allowed_path_hint: str | None = None
    observed_path_hint: str | None = None
    allowed_extension: str = ".json"
    max_file_size_bytes: int | None = None
    observed_file_size_bytes: int | None = None
    freshness_max_age_sec: int | None = None
    observed_age_sec: int | None = None
    path_scope_status: str = "not_supplied"
    extension_status: str = "not_supplied"
    file_size_status: str = "not_supplied"
    freshness_status: str = "missing"
    schema_validation_status: str = "not_available"
    schema_validation_valid: bool | None = None
    dry_run_outcome: str = "blocked_missing_metadata"
    candidate_for_future_guarded_loader: bool = False
    blocker_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    actual_file_read_allowed_by_this_contract: bool = False
    actual_payload_decode_allowed_by_this_contract: bool = False
    read_by_this_slice: bool = False
    loaded_in_this_slice: bool = False
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    dry_run_only: bool = True
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
            "required": self.required,
            "supplied_by_metadata_input": self.supplied_by_metadata_input,
            "allowed_root_hint": self.allowed_root_hint,
            "allowed_path_hint": self.allowed_path_hint,
            "observed_path_hint": self.observed_path_hint,
            "allowed_extension": self.allowed_extension,
            "max_file_size_bytes": self.max_file_size_bytes,
            "observed_file_size_bytes": self.observed_file_size_bytes,
            "freshness_max_age_sec": self.freshness_max_age_sec,
            "observed_age_sec": self.observed_age_sec,
            "path_scope_status": self.path_scope_status,
            "extension_status": self.extension_status,
            "file_size_status": self.file_size_status,
            "freshness_status": self.freshness_status,
            "schema_validation_status": self.schema_validation_status,
            "schema_validation_valid": self.schema_validation_valid,
            "dry_run_outcome": self.dry_run_outcome,
            "candidate_for_future_guarded_loader": self.candidate_for_future_guarded_loader,
            "blocker_reasons": list(self.blocker_reasons),
            "warning_reasons": list(self.warning_reasons),
            "actual_file_read_allowed_by_this_contract": self.actual_file_read_allowed_by_this_contract,
            "actual_payload_decode_allowed_by_this_contract": self.actual_payload_decode_allowed_by_this_contract,
            "read_by_this_slice": self.read_by_this_slice,
            "loaded_in_this_slice": self.loaded_in_this_slice,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "dry_run_only": self.dry_run_only,
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
class PredictionWarRoomLatestPayloadLoaderDryRunSimulationPacket:
    simulation_version: str
    simulation_id: str
    simulation_state: str
    hot_latest_root_hint: str
    loader_permission_contract_version: str
    preflight_status_contract_version: str
    permission_contract: Mapping[str, Any] = field(default_factory=dict)
    preflight_status: Mapping[str, Any] = field(default_factory=dict)
    artifact_evaluations: Tuple[PredictionWarRoomLatestPayloadLoaderDryRunArtifactEvaluation, ...] = ()
    simulated_preflight_ready_for_payload_handoff: bool = False
    candidate_artifact_count: int = 0
    evaluation_blocker_count: int = 0
    evaluation_warning_count: int = 0
    actual_loader_execution_allowed: bool = False
    actual_file_read_allowed_by_this_contract: bool = False
    actual_payload_decode_allowed_by_this_contract: bool = False
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    handoff_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    dry_run_only: bool = True
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
            "simulation_version": self.simulation_version,
            "simulation_id": self.simulation_id,
            "simulation_state": self.simulation_state,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "loader_permission_contract_version": self.loader_permission_contract_version,
            "preflight_status_contract_version": self.preflight_status_contract_version,
            "permission_contract": dict(self.permission_contract),
            "preflight_status": dict(self.preflight_status),
            "artifact_evaluations": [item.to_dict() for item in self.artifact_evaluations],
            "simulated_preflight_ready_for_payload_handoff": self.simulated_preflight_ready_for_payload_handoff,
            "candidate_artifact_count": self.candidate_artifact_count,
            "evaluation_blocker_count": self.evaluation_blocker_count,
            "evaluation_warning_count": self.evaluation_warning_count,
            "actual_loader_execution_allowed": self.actual_loader_execution_allowed,
            "actual_file_read_allowed_by_this_contract": self.actual_file_read_allowed_by_this_contract,
            "actual_payload_decode_allowed_by_this_contract": self.actual_payload_decode_allowed_by_this_contract,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "handoff_summary": dict(self.handoff_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "dry_run_only": self.dry_run_only,
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


def _metadata_by_role(artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None) -> dict[str, Mapping[str, Any]]:
    by_role: dict[str, Mapping[str, Any]] = {}
    for raw in artifact_metadata_inputs or ():
        item = _as_mapping(raw)
        role = str(item.get("artifact_role") or "")
        if role:
            by_role[role] = item
    return by_role


def _starts_under_root(path_hint: str, root_hint: str) -> bool:
    path = path_hint.replace("/", "\\").rstrip("\\")
    root = root_hint.replace("/", "\\").rstrip("\\")
    return path == root or path.startswith(root + "\\")


def _int_or_none(value: Any) -> int | None:
    return int(value) if isinstance(value, int) else None


def _evaluate_artifact(rule: Mapping[str, Any], metadata: Mapping[str, Any]) -> PredictionWarRoomLatestPayloadLoaderDryRunArtifactEvaluation:
    role = str(rule.get("artifact_role") or "unknown")
    required = bool(rule.get("required", True))
    supplied = bool(
        metadata.get("supplied_by_metadata_input")
        or metadata.get("metadata_supplied")
        or metadata.get("supplied")
        or metadata.get("artifact_available")
        or metadata.get("payload_supplied")
    )
    allowed_root = str(rule.get("allowed_root_hint") or "")
    allowed_path = str(rule.get("allowed_path_hint") or "")
    observed_path = str(metadata.get("observed_path_hint") or metadata.get("path_hint") or metadata.get("expected_path_hint") or "")
    allowed_extension = str(rule.get("allowed_extension") or ".json")
    max_bytes = _int_or_none(rule.get("max_file_size_bytes"))
    observed_bytes = _int_or_none(metadata.get("observed_file_size_bytes", metadata.get("file_size_bytes")))
    freshness_max_age = _int_or_none(rule.get("freshness_max_age_sec"))
    observed_age = _int_or_none(metadata.get("observed_age_sec"))
    freshness_status = str(metadata.get("freshness_status") or ("missing" if not supplied else "not_checked"))
    schema_status = str(metadata.get("schema_validation_status") or ("not_available" if not supplied else "not_run"))
    schema_valid = _bool_or_none(metadata.get("schema_validation_valid"))
    blockers: list[str] = []
    warnings: list[str] = []

    if not supplied:
        path_scope_status = "not_supplied"
        extension_status = "not_supplied"
        file_size_status = "not_supplied"
        if required:
            blockers.append("required_artifact_metadata_not_supplied")
        else:
            warnings.append("optional_artifact_metadata_not_supplied")
    else:
        if not observed_path:
            path_scope_status = "missing_path_hint"
            blockers.append("path_hint_missing_before_read")
        elif not _starts_under_root(observed_path, allowed_root):
            path_scope_status = "outside_hot_latest_root"
            blockers.append("path_scope_not_under_hot_latest_root")
        elif observed_path.replace("/", "\\") != allowed_path.replace("/", "\\"):
            path_scope_status = "unexpected_path"
            blockers.append("path_does_not_match_expected_artifact_ref")
        else:
            path_scope_status = "passed"

        if not observed_path:
            extension_status = "missing_path_hint"
        elif not observed_path.lower().endswith(allowed_extension.lower()):
            extension_status = "not_json"
            blockers.append("extension_not_allowed")
        else:
            extension_status = "passed"

        if observed_bytes is None:
            file_size_status = "not_checked"
            warnings.append("future_loader_must_check_file_size_before_parse")
        elif max_bytes is not None and observed_bytes > max_bytes:
            file_size_status = "too_large"
            blockers.append("file_size_exceeds_max_before_parse")
        else:
            file_size_status = "passed"

        if freshness_status in _FRESHNESS_BLOCK_STATES:
            if required:
                blockers.append(f"freshness_status_{freshness_status}")
            else:
                warnings.append(f"optional_freshness_status_{freshness_status}")
        if schema_status in _SCHEMA_BLOCK_STATES or schema_valid is False:
            blockers.append("schema_validation_blocked")
        if freshness_status == "not_checked":
            warnings.append("future_loader_must_check_freshness_before_display")
        if schema_status == "not_run":
            warnings.append("future_loader_must_run_schema_validation_before_display")

    blocker_set = tuple(dict.fromkeys(blockers))
    warning_set = tuple(dict.fromkeys(warnings))
    candidate = supplied and not blocker_set
    if candidate:
        dry_run_outcome = "metadata_would_be_candidate_after_future_guarded_loader"
    elif supplied:
        dry_run_outcome = "would_block_before_runtime_read"
    elif required:
        dry_run_outcome = "blocked_missing_required_metadata"
    else:
        dry_run_outcome = "optional_metadata_not_supplied"
    return PredictionWarRoomLatestPayloadLoaderDryRunArtifactEvaluation(
        artifact_role=role,
        artifact_contract_id=str(rule.get("artifact_contract_id") or metadata.get("artifact_contract_id") or "unknown"),
        required=required,
        supplied_by_metadata_input=supplied,
        allowed_root_hint=allowed_root,
        allowed_path_hint=allowed_path,
        observed_path_hint=observed_path or None,
        allowed_extension=allowed_extension,
        max_file_size_bytes=max_bytes,
        observed_file_size_bytes=observed_bytes,
        freshness_max_age_sec=freshness_max_age,
        observed_age_sec=observed_age,
        path_scope_status=path_scope_status,
        extension_status=extension_status,
        file_size_status=file_size_status,
        freshness_status=freshness_status,
        schema_validation_status=schema_status,
        schema_validation_valid=schema_valid,
        dry_run_outcome=dry_run_outcome,
        candidate_for_future_guarded_loader=candidate,
        blocker_reasons=blocker_set,
        warning_reasons=warning_set,
    )


def build_prediction_warroom_latest_payload_loader_dry_run_simulation(
    *,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomLatestPayloadLoaderDryRunSimulationPacket:
    """Simulate future latest-payload loader decisions from supplied metadata only, without file access."""
    permission = build_prediction_warroom_latest_payload_loader_permission_contract(hot_latest_root_hint=hot_latest_root_hint).to_dict()
    preflight = build_prediction_warroom_latest_payload_preflight_status_contract(
        artifact_status_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    metadata_by_role = _metadata_by_role(artifact_metadata_inputs)
    evaluations = tuple(
        _evaluate_artifact(rule, metadata_by_role.get(str(rule.get("artifact_role") or ""), {}))
        for rule in _list(permission.get("path_rules"))
    )
    candidate_count = sum(1 for item in evaluations if item.candidate_for_future_guarded_loader)
    evaluation_blocker_count = sum(len(item.blocker_reasons) for item in evaluations)
    evaluation_warning_count = sum(len(item.warning_reasons) for item in evaluations)
    preflight_ready = bool(preflight.get("preflight_ready_for_payload_handoff"))
    blocked_reasons: list[str] = [str(item) for item in _list(preflight.get("blocked_reasons"))]
    warning_reasons: list[str] = [str(item) for item in _list(preflight.get("warning_reasons"))]
    for item in evaluations:
        blocked_reasons.extend(item.blocker_reasons)
        warning_reasons.extend(item.warning_reasons)
    blocked_reasons.extend(_list(permission.get("blocked_reasons_when_contract_only")))
    if preflight_ready and candidate_count:
        simulation_state = "simulated_metadata_handoff_ready_actual_loader_disabled"
    else:
        simulation_state = "simulated_loader_blocked_or_waiting_for_metadata"
    return PredictionWarRoomLatestPayloadLoaderDryRunSimulationPacket(
        simulation_version=LOADER_DRY_RUN_SIMULATOR_VERSION,
        simulation_id=f"{LOADER_DRY_RUN_SIMULATOR_VERSION}:latest:{'candidate' if candidate_count else 'waiting'}",
        simulation_state=simulation_state,
        hot_latest_root_hint=str(hot_latest_root_hint),
        loader_permission_contract_version=LOADER_PERMISSION_CONTRACT_VERSION,
        preflight_status_contract_version=PREFLIGHT_STATUS_VERSION,
        permission_contract=permission,
        preflight_status=preflight,
        artifact_evaluations=evaluations,
        simulated_preflight_ready_for_payload_handoff=preflight_ready,
        candidate_artifact_count=candidate_count,
        evaluation_blocker_count=evaluation_blocker_count,
        evaluation_warning_count=evaluation_warning_count,
        blocked_reasons=tuple(dict.fromkeys(str(item) for item in blocked_reasons if item)),
        warning_reasons=tuple(dict.fromkeys(str(item) for item in warning_reasons if item)),
        handoff_summary={
            "simulation_boundary": "metadata_only_latest_payload_loader_dry_run",
            "hot_latest_root_preference": str(hot_latest_root_hint),
            "loader_permission_contract_version": LOADER_PERMISSION_CONTRACT_VERSION,
            "preflight_status_contract_version": PREFLIGHT_STATUS_VERSION,
            "artifact_evaluation_count": len(evaluations),
            "candidate_artifact_count": candidate_count,
            "simulated_preflight_ready_for_payload_handoff": preflight_ready,
            "actual_loader_execution_allowed": False,
            "actual_file_read_allowed_by_this_contract": False,
            "actual_payload_decode_allowed_by_this_contract": False,
            "runtime_file_read_enabled": False,
            "runtime_artifact_write_enabled": False,
            "autotrade_trigger_enabled": False,
        },
    )
