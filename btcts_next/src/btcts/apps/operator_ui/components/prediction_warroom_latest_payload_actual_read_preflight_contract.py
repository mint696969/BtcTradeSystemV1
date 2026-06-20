# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_actual_read_preflight_contract.py
# desc: PS-Q9A final preflight contract for a future guarded Prediction WarRoom latest-payload actual-read loader. Contract/readiness only; no filesystem access, payload decode, rendering, Collector runtime, AutoTrade, broker, mode, approval/grant, or ledger append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_l4_latest_adapter import (
    DEFAULT_HOT_LATEST_ROOT_HINT,
    build_prediction_warroom_l4_latest_expected_artifacts,
)
from .prediction_warroom_latest_payload_loader_permission_contract import (
    DEFAULT_OPTIONAL_ARTIFACT_FRESHNESS_MAX_AGE_SEC,
    DEFAULT_OPTIONAL_ARTIFACT_MAX_BYTES,
    DEFAULT_REQUIRED_ARTIFACT_FRESHNESS_MAX_AGE_SEC,
    DEFAULT_REQUIRED_ARTIFACT_MAX_BYTES,
    LOADER_PERMISSION_CONTRACT_VERSION,
    build_prediction_warroom_latest_payload_loader_permission_contract,
)
from .prediction_warroom_latest_payload_preflight_status import PREFLIGHT_STATUS_VERSION
from .prediction_warroom_payload_schema_validator import VALIDATOR_VERSION

ACTUAL_READ_PREFLIGHT_CONTRACT_VERSION = "prediction_warroom_latest_payload_actual_read_preflight_contract.ps_q9a.v1"

ACTUAL_READ_PREFLIGHT_SEQUENCE = (
    "q6b_permission_contract_path_rules_loaded_as_contract_data",
    "allowed_hot_latest_root_check_under_d_btc_ts_hot",
    "expected_artifact_role_and_path_match_check",
    "json_extension_check_before_any_read",
    "file_size_metadata_check_before_any_read",
    "freshness_metadata_check_before_any_read",
    "schema_validation_plan_with_q5c_after_ps_q9b_decode",
    "ps_q9b_guarded_actual_read_requires_separate_guard",
    "ps_q9c_loaded_payload_validation_panel_before_display",
    "fail_closed_keep_runtime_disconnected_on_any_blocker",
)

PS_Q9B_ENTRY_REQUIREMENTS = (
    "ps_q9a_contract_committed_and_guarded",
    "working_tree_clean_before_ps_q9b",
    "only_explicit_allowed_json_candidates_under_hot_latest_root",
    "required_prediction_system_result_snapshot_metadata_ready",
    "path_scope_extension_size_freshness_metadata_all_ready",
    "q5c_schema_validation_plan_declared_before_decode",
    "human_review_required_before_actual_read_attempt",
    "actual_read_slice_must_remain_read_only_and_guarded",
)

FAIL_CLOSED_BEHAVIOR = (
    "return_blocked_actual_read_preflight_contract",
    "do_not_attempt_file_read",
    "do_not_decode_payload",
    "do_not_render_unvalidated_prediction_cards",
    "do_not_mutate_warroom_page",
    "do_not_write_runtime_artifact",
    "do_not_append_decision_or_command_ledger",
    "do_not_trigger_autotrade",
    "do_not_send_to_broker",
)

_PATH_BLOCK_STATES = {"not_supplied", "missing_path_hint", "outside_hot_latest_root", "unexpected_path"}
_EXTENSION_BLOCK_STATES = {"not_supplied", "missing_path_hint", "not_json"}
_SIZE_BLOCK_STATES = {"not_supplied", "not_checked", "too_large"}
_FRESHNESS_BLOCK_STATES = {"missing", "stale", "expired", "unknown_required", "not_checked"}
_SCHEMA_BLOCK_STATES = {"invalid", "failed", "schema_blocked"}


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadActualReadCandidate:
    artifact_role: str
    artifact_contract_id: str
    allowed_root_hint: str
    allowed_path_hint: str
    required: bool
    allowed_extension: str = ".json"
    max_file_size_bytes: int = DEFAULT_REQUIRED_ARTIFACT_MAX_BYTES
    freshness_max_age_sec: int = DEFAULT_REQUIRED_ARTIFACT_FRESHNESS_MAX_AGE_SEC
    supplied_by_candidate_metadata: bool = False
    observed_path_hint: str | None = None
    observed_file_size_bytes: int | None = None
    observed_age_sec: int | None = None
    observed_last_modified_at: str | None = None
    path_scope_status: str = "not_supplied"
    extension_status: str = "not_supplied"
    file_size_status: str = "not_supplied"
    freshness_status: str = "missing"
    schema_validation_status: str = "planned_not_run"
    schema_validation_report_version: str | None = None
    candidate_ready_for_ps_q9b_guarded_actual_read: bool = False
    blocker_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    preflight_only: bool = True
    actual_file_read_allowed_by_this_contract: bool = False
    actual_payload_decode_allowed_by_this_contract: bool = False
    loader_execution_allowed_by_this_contract: bool = False
    read_by_this_slice: bool = False
    decoded_in_this_slice: bool = False
    loaded_in_this_slice: bool = False
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
    authorization_grant_requested: bool = False
    autotrade_trigger_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_role": self.artifact_role,
            "artifact_contract_id": self.artifact_contract_id,
            "allowed_root_hint": self.allowed_root_hint,
            "allowed_path_hint": self.allowed_path_hint,
            "required": self.required,
            "allowed_extension": self.allowed_extension,
            "max_file_size_bytes": self.max_file_size_bytes,
            "freshness_max_age_sec": self.freshness_max_age_sec,
            "supplied_by_candidate_metadata": self.supplied_by_candidate_metadata,
            "observed_path_hint": self.observed_path_hint,
            "observed_file_size_bytes": self.observed_file_size_bytes,
            "observed_age_sec": self.observed_age_sec,
            "observed_last_modified_at": self.observed_last_modified_at,
            "path_scope_status": self.path_scope_status,
            "extension_status": self.extension_status,
            "file_size_status": self.file_size_status,
            "freshness_status": self.freshness_status,
            "schema_validation_status": self.schema_validation_status,
            "schema_validation_report_version": self.schema_validation_report_version,
            "candidate_ready_for_ps_q9b_guarded_actual_read": self.candidate_ready_for_ps_q9b_guarded_actual_read,
            "blocker_reasons": list(self.blocker_reasons),
            "warning_reasons": list(self.warning_reasons),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "preflight_only": self.preflight_only,
            "actual_file_read_allowed_by_this_contract": self.actual_file_read_allowed_by_this_contract,
            "actual_payload_decode_allowed_by_this_contract": self.actual_payload_decode_allowed_by_this_contract,
            "loader_execution_allowed_by_this_contract": self.loader_execution_allowed_by_this_contract,
            "read_by_this_slice": self.read_by_this_slice,
            "decoded_in_this_slice": self.decoded_in_this_slice,
            "loaded_in_this_slice": self.loaded_in_this_slice,
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
            "authorization_grant_requested": self.authorization_grant_requested,
            "autotrade_trigger_enabled": self.autotrade_trigger_enabled,
        }


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadActualReadPreflightContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    hot_latest_root_hint: str
    q6a_preflight_status_contract_version: str
    q6b_loader_permission_contract_version: str
    schema_validator_contract_version: str
    allowed_candidates: Tuple[PredictionWarRoomLatestPayloadActualReadCandidate, ...] = ()
    actual_read_preflight_sequence: Tuple[str, ...] = ACTUAL_READ_PREFLIGHT_SEQUENCE
    ps_q9b_entry_requirements: Tuple[str, ...] = PS_Q9B_ENTRY_REQUIREMENTS
    fail_closed_behavior: Tuple[str, ...] = FAIL_CLOSED_BEHAVIOR
    required_candidate_count: int = 0
    optional_candidate_count: int = 0
    ready_candidate_count: int = 0
    blocker_count: int = 0
    warning_count: int = 0
    ready_for_ps_q9b_guarded_actual_read: bool = False
    operator_visible_readiness_state: str = "blocked_waiting_for_candidate_metadata"
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    handoff_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    preflight_only: bool = True
    actual_file_read_allowed_by_this_contract: bool = False
    actual_payload_decode_allowed_by_this_contract: bool = False
    loader_execution_allowed_by_this_contract: bool = False
    approval_granted: bool = False
    authorization_granted: bool = False
    read_by_this_slice: bool = False
    decoded_in_this_slice: bool = False
    loaded_in_this_slice: bool = False
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
    authorization_grant_requested: bool = False
    autotrade_trigger_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "contract_id": self.contract_id,
            "contract_state": self.contract_state,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "q6a_preflight_status_contract_version": self.q6a_preflight_status_contract_version,
            "q6b_loader_permission_contract_version": self.q6b_loader_permission_contract_version,
            "schema_validator_contract_version": self.schema_validator_contract_version,
            "allowed_candidates": [item.to_dict() for item in self.allowed_candidates],
            "actual_read_preflight_sequence": list(self.actual_read_preflight_sequence),
            "ps_q9b_entry_requirements": list(self.ps_q9b_entry_requirements),
            "fail_closed_behavior": list(self.fail_closed_behavior),
            "required_candidate_count": self.required_candidate_count,
            "optional_candidate_count": self.optional_candidate_count,
            "ready_candidate_count": self.ready_candidate_count,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "ready_for_ps_q9b_guarded_actual_read": self.ready_for_ps_q9b_guarded_actual_read,
            "operator_visible_readiness_state": self.operator_visible_readiness_state,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "handoff_summary": dict(self.handoff_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "preflight_only": self.preflight_only,
            "actual_file_read_allowed_by_this_contract": self.actual_file_read_allowed_by_this_contract,
            "actual_payload_decode_allowed_by_this_contract": self.actual_payload_decode_allowed_by_this_contract,
            "loader_execution_allowed_by_this_contract": self.loader_execution_allowed_by_this_contract,
            "approval_granted": self.approval_granted,
            "authorization_granted": self.authorization_granted,
            "read_by_this_slice": self.read_by_this_slice,
            "decoded_in_this_slice": self.decoded_in_this_slice,
            "loaded_in_this_slice": self.loaded_in_this_slice,
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
            "authorization_grant_requested": self.authorization_grant_requested,
            "autotrade_trigger_enabled": self.autotrade_trigger_enabled,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _int_or_none(value: Any) -> int | None:
    return int(value) if isinstance(value, int) else None


def _bool_or_none(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None


def _metadata_by_role(candidate_metadata_inputs: Iterable[Mapping[str, Any]] | None) -> dict[str, Mapping[str, Any]]:
    by_role: dict[str, Mapping[str, Any]] = {}
    for raw in candidate_metadata_inputs or ():
        item = _as_mapping(raw)
        role = str(item.get("artifact_role") or "")
        if role:
            by_role[role] = item
    return by_role


def _starts_under_root(path_hint: str, root_hint: str) -> bool:
    path = path_hint.replace("/", "\\").rstrip("\\")
    root = root_hint.replace("/", "\\").rstrip("\\")
    return path == root or path.startswith(root + "\\")


def _path_scope_status(observed_path: str, allowed_root: str, allowed_path: str) -> tuple[str, tuple[str, ...]]:
    if not observed_path:
        return "missing_path_hint", ("path_hint_missing_before_actual_read",)
    normalized_observed = observed_path.replace("/", "\\")
    normalized_allowed = allowed_path.replace("/", "\\")
    if not _starts_under_root(normalized_observed, allowed_root):
        return "outside_hot_latest_root", ("path_scope_not_under_hot_latest_root",)
    if normalized_observed != normalized_allowed:
        return "unexpected_path", ("path_does_not_match_expected_artifact_ref",)
    return "passed", ()


def _extension_status(observed_path: str, allowed_extension: str) -> tuple[str, tuple[str, ...]]:
    if not observed_path:
        return "missing_path_hint", ("extension_check_missing_path_hint",)
    if not observed_path.lower().endswith(allowed_extension.lower()):
        return "not_json", ("extension_not_allowed_before_actual_read",)
    return "passed", ()


def _file_size_status(observed_bytes: int | None, max_bytes: int) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    if observed_bytes is None:
        return "not_checked", ("file_size_metadata_not_checked_before_actual_read",), ()
    if observed_bytes > max_bytes:
        return "too_large", ("file_size_exceeds_max_before_actual_read",), ()
    return "passed", (), ()


def _freshness_status(raw_status: str, required: bool) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    status = raw_status or "missing"
    if status in _FRESHNESS_BLOCK_STATES:
        reason = f"freshness_status_{status}_before_actual_read"
        if required:
            return status, (reason,), ()
        return status, (), (f"optional_{reason}",)
    return status, (), ()


def _schema_plan_status(raw_status: str, schema_valid: bool | None) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    status = raw_status or "planned_not_run"
    if status in _SCHEMA_BLOCK_STATES or schema_valid is False:
        return status, ("schema_validation_known_blocked_before_actual_read",), ()
    if status in {"not_run", "planned_not_run", "not_available"}:
        return status, (), ("ps_q9b_must_decode_then_ps_q9c_must_validate_with_q5c_before_display",)
    return status, (), ()


def _candidate_from_rule(rule: Mapping[str, Any], metadata: Mapping[str, Any]) -> PredictionWarRoomLatestPayloadActualReadCandidate:
    role = str(rule.get("artifact_role") or "unknown")
    required = bool(rule.get("required", True))
    supplied = bool(
        metadata.get("supplied_by_candidate_metadata")
        or metadata.get("supplied_by_metadata_input")
        or metadata.get("metadata_supplied")
        or metadata.get("supplied")
        or metadata.get("artifact_available")
        or metadata.get("payload_supplied")
    )
    allowed_root = str(rule.get("allowed_root_hint") or DEFAULT_HOT_LATEST_ROOT_HINT)
    allowed_path = str(rule.get("allowed_path_hint") or "")
    allowed_extension = str(rule.get("allowed_extension") or ".json")
    max_bytes = _int_or_none(rule.get("max_file_size_bytes")) or (
        DEFAULT_REQUIRED_ARTIFACT_MAX_BYTES if required else DEFAULT_OPTIONAL_ARTIFACT_MAX_BYTES
    )
    freshness_max_age = _int_or_none(rule.get("freshness_max_age_sec")) or (
        DEFAULT_REQUIRED_ARTIFACT_FRESHNESS_MAX_AGE_SEC if required else DEFAULT_OPTIONAL_ARTIFACT_FRESHNESS_MAX_AGE_SEC
    )
    observed_path = str(
        metadata.get("observed_path_hint")
        or metadata.get("path_hint")
        or metadata.get("expected_path_hint")
        or ""
    )
    observed_bytes = _int_or_none(metadata.get("observed_file_size_bytes", metadata.get("file_size_bytes")))
    observed_age = _int_or_none(metadata.get("observed_age_sec"))
    observed_last_modified_at = metadata.get("observed_last_modified_at")
    schema_valid = _bool_or_none(metadata.get("schema_validation_valid"))
    blockers: list[str] = [str(item) for item in _list(metadata.get("blocker_reasons"))]
    warnings: list[str] = [str(item) for item in _list(metadata.get("warning_reasons"))]

    if not supplied:
        path_status = "not_supplied"
        extension_status = "not_supplied"
        size_status = "not_supplied"
        freshness_status = "missing"
        schema_status = "planned_not_run"
        if required:
            blockers.append("required_actual_read_candidate_metadata_not_supplied")
        else:
            warnings.append("optional_actual_read_candidate_metadata_not_supplied")
    else:
        path_status, path_blockers = _path_scope_status(observed_path, allowed_root, allowed_path)
        extension_status, extension_blockers = _extension_status(observed_path, allowed_extension)
        size_status, size_blockers, size_warnings = _file_size_status(observed_bytes, max_bytes)
        freshness_status, freshness_blockers, freshness_warnings = _freshness_status(
            str(metadata.get("freshness_status") or "not_checked"),
            required,
        )
        schema_status, schema_blockers, schema_warnings = _schema_plan_status(
            str(metadata.get("schema_validation_status") or "planned_not_run"),
            schema_valid,
        )
        blockers.extend(path_blockers)
        blockers.extend(extension_blockers)
        blockers.extend(size_blockers)
        blockers.extend(freshness_blockers)
        blockers.extend(schema_blockers)
        warnings.extend(size_warnings)
        warnings.extend(freshness_warnings)
        warnings.extend(schema_warnings)
        if observed_age is None:
            warnings.append("observed_age_metadata_not_supplied_before_actual_read")

    blocker_set = tuple(dict.fromkeys(item for item in blockers if item))
    warning_set = tuple(dict.fromkeys(item for item in warnings if item))
    ready = supplied and not blocker_set
    return PredictionWarRoomLatestPayloadActualReadCandidate(
        artifact_role=role,
        artifact_contract_id=str(rule.get("artifact_contract_id") or metadata.get("artifact_contract_id") or "unknown"),
        allowed_root_hint=allowed_root,
        allowed_path_hint=allowed_path,
        required=required,
        allowed_extension=allowed_extension,
        max_file_size_bytes=max_bytes,
        freshness_max_age_sec=freshness_max_age,
        supplied_by_candidate_metadata=supplied,
        observed_path_hint=observed_path or None,
        observed_file_size_bytes=observed_bytes,
        observed_age_sec=observed_age,
        observed_last_modified_at=str(observed_last_modified_at) if observed_last_modified_at else None,
        path_scope_status=path_status,
        extension_status=extension_status,
        file_size_status=size_status,
        freshness_status=freshness_status,
        schema_validation_status=schema_status,
        schema_validation_report_version=VALIDATOR_VERSION if schema_status in {"valid", "invalid", "failed", "schema_blocked"} else None,
        candidate_ready_for_ps_q9b_guarded_actual_read=ready,
        blocker_reasons=blocker_set,
        warning_reasons=warning_set,
    )


def build_prediction_warroom_latest_payload_actual_read_preflight_contract(
    *,
    candidate_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
) -> PredictionWarRoomLatestPayloadActualReadPreflightContractPacket:
    """Build the PS-Q9A final preflight contract without reading or decoding hot/latest payloads."""
    permission = build_prediction_warroom_latest_payload_loader_permission_contract(
        hot_latest_root_hint=hot_latest_root_hint
    ).to_dict()
    metadata_by_role = _metadata_by_role(candidate_metadata_inputs)
    rules = _list(permission.get("path_rules"))
    if not rules:
        rules = [
            {
                "artifact_role": ref.artifact_role,
                "artifact_contract_id": ref.artifact_contract_id,
                "allowed_root_hint": hot_latest_root_hint,
                "allowed_path_hint": ref.expected_path_hint,
                "required": ref.required,
                "allowed_extension": ".json",
            }
            for ref in build_prediction_warroom_l4_latest_expected_artifacts(hot_latest_root_hint=hot_latest_root_hint)
        ]
    candidates = tuple(
        _candidate_from_rule(rule, metadata_by_role.get(str(rule.get("artifact_role") or ""), {}))
        for rule in rules
    )
    required_count = sum(1 for item in candidates if item.required)
    optional_count = len(candidates) - required_count
    ready_count = sum(1 for item in candidates if item.candidate_ready_for_ps_q9b_guarded_actual_read)
    blocker_reasons: list[str] = []
    warning_reasons: list[str] = []
    for item in candidates:
        blocker_reasons.extend(item.blocker_reasons)
        warning_reasons.extend(item.warning_reasons)
    required_candidates = [item for item in candidates if item.required]
    required_ready = bool(required_candidates) and all(
        item.candidate_ready_for_ps_q9b_guarded_actual_read for item in required_candidates
    )
    ready_for_q9b = required_ready and not blocker_reasons
    if not ready_for_q9b:
        contract_state = "blocked_waiting_for_ps_q9b_actual_read_candidate_metadata"
        operator_state = "blocked"
    else:
        contract_state = "ready_for_ps_q9b_guarded_actual_read_contract_handoff"
        operator_state = "ready_for_ps_q9b_guarded_actual_read"
        warning_reasons.append("actual_read_still_not_allowed_by_ps_q9a_contract")
        warning_reasons.append("ps_q9b_must_be_separate_read_only_guarded_slice")
    return PredictionWarRoomLatestPayloadActualReadPreflightContractPacket(
        contract_version=ACTUAL_READ_PREFLIGHT_CONTRACT_VERSION,
        contract_id=f"{ACTUAL_READ_PREFLIGHT_CONTRACT_VERSION}:latest:{'ready' if ready_for_q9b else 'blocked'}",
        contract_state=contract_state,
        hot_latest_root_hint=str(hot_latest_root_hint),
        q6a_preflight_status_contract_version=PREFLIGHT_STATUS_VERSION,
        q6b_loader_permission_contract_version=LOADER_PERMISSION_CONTRACT_VERSION,
        schema_validator_contract_version=VALIDATOR_VERSION,
        allowed_candidates=candidates,
        required_candidate_count=required_count,
        optional_candidate_count=optional_count,
        ready_candidate_count=ready_count,
        blocker_count=len(tuple(dict.fromkeys(blocker_reasons))),
        warning_count=len(tuple(dict.fromkeys(warning_reasons))),
        ready_for_ps_q9b_guarded_actual_read=ready_for_q9b,
        operator_visible_readiness_state=operator_state,
        blocked_reasons=tuple(dict.fromkeys(blocker_reasons)),
        warning_reasons=tuple(dict.fromkeys(warning_reasons)),
        handoff_summary={
            "contract_boundary": "ps_q9a_actual_read_preflight_final_contract_only",
            "responsibility": "declare allowed candidates and exact pre-read readiness conditions for PS-Q9B",
            "hot_latest_root_preference": str(hot_latest_root_hint),
            "allowed_candidate_count": len(candidates),
            "required_artifact_roles": [item.artifact_role for item in candidates if item.required],
            "optional_artifact_roles": [item.artifact_role for item in candidates if not item.required],
            "actual_read_preflight_sequence": list(ACTUAL_READ_PREFLIGHT_SEQUENCE),
            "ps_q9b_entry_requirements": list(PS_Q9B_ENTRY_REQUIREMENTS),
            "fail_closed_behavior": list(FAIL_CLOSED_BEHAVIOR),
            "ready_for_ps_q9b_guarded_actual_read": ready_for_q9b,
            "actual_file_read_allowed_by_this_contract": False,
            "actual_payload_decode_allowed_by_this_contract": False,
            "loader_execution_allowed_by_this_contract": False,
            "approval_granted": False,
            "authorization_granted": False,
            "runtime_file_read_enabled": False,
            "runtime_artifact_write_enabled": False,
            "autotrade_trigger_enabled": False,
            "broker_private_api_enabled": False,
        },
    )
