# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_loader_authorization_request.py
# desc: Explicit authorization-request contract for a future Prediction WarRoom latest-payload loader. Request metadata only; no loader execution, file access, payload decode, rendering, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_latest_payload_loader_permission_contract import (
    FAILURE_BEHAVIOR_SEQUENCE,
    LOADER_PERMISSION_CONTRACT_VERSION,
    VALIDATION_SEQUENCE,
    build_prediction_warroom_latest_payload_loader_permission_contract,
)
from .prediction_warroom_latest_payload_preflight_status import PREFLIGHT_STATUS_VERSION
from .prediction_warroom_payload_schema_validator import VALIDATOR_VERSION

LOADER_AUTHORIZATION_REQUEST_VERSION = "prediction_warroom_latest_payload_loader_authorization_request.ps_q7a.v1"
AUTHORIZATION_REVIEW_SEQUENCE = (
    "review_q6b_permission_contract",
    "verify_hot_latest_root_scope_is_d_btc_ts_hot",
    "verify_expected_artifact_roles_and_json_extensions",
    "verify_file_size_check_required_before_payload_parse",
    "verify_freshness_check_required_before_display",
    "verify_q5c_schema_validation_required_before_display",
    "verify_q6a_preflight_status_update_required",
    "verify_fail_closed_keep_last_good_packet_on_failure",
    "verify_no_runtime_write_no_autotrade_no_broker",
    "approve_future_loader_implementation_slice_separately",
)
AUTHORIZATION_FAILURE_BEHAVIOR_SEQUENCE = (
    "do_not_execute_loader",
    "do_not_read_hot_latest_file",
    "do_not_decode_payload",
    "return_authorization_request_not_granted",
    "keep_q6a_preflight_blocked_or_waiting",
    "show_loader_not_authorized_status_only",
    "do_not_render_unvalidated_payload",
    "do_not_write_runtime_artifact",
    "do_not_trigger_autotrade",
    "do_not_send_to_broker",
)
_DANGEROUS_FALSE_FIELDS = (
    "actual_loader_execution_allowed",
    "actual_file_read_allowed_by_this_contract",
    "actual_payload_decode_allowed_by_this_contract",
    "would_load_hot_latest_artifacts",
    "would_read_runtime_file",
    "would_collect_public_source",
    "would_write_runtime_artifact",
    "would_write_collector_state",
    "would_send_to_broker",
    "broker_execution_requested",
    "mode_apply_requested",
    "command_ledger_append_requested",
    "approval_append_requested",
    "approval_granted_by_this_contract",
    "authorization_granted_by_this_contract",
)


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadLoaderAuthorizationRequestPacket:
    authorization_request_version: str
    authorization_request_id: str
    authorization_request_state: str
    authorization_request_kind: str
    permission_contract_version: str
    permission_contract_id: str | None = None
    loader_permission_state: str | None = None
    hot_latest_root_hint: str | None = None
    requested_loader_scope: str = "single_cycle_latest_prediction_payload_read_after_separate_approval"
    requested_artifact_roles: Tuple[str, ...] = ()
    requested_path_rule_count: int = 0
    required_artifact_count: int = 0
    optional_artifact_count: int = 0
    authorization_review_sequence: Tuple[str, ...] = AUTHORIZATION_REVIEW_SEQUENCE
    authorization_failure_behavior_sequence: Tuple[str, ...] = AUTHORIZATION_FAILURE_BEHAVIOR_SEQUENCE
    inherited_validation_sequence: Tuple[str, ...] = VALIDATION_SEQUENCE
    inherited_failure_behavior_sequence: Tuple[str, ...] = FAILURE_BEHAVIOR_SEQUENCE
    authorization_gates: Mapping[str, Any] = field(default_factory=dict)
    approval_contract: Mapping[str, Any] = field(default_factory=dict)
    permission_contract_summary: Mapping[str, Any] = field(default_factory=dict)
    boundaries: Mapping[str, Any] = field(default_factory=dict)
    request_ready_for_human_review: bool = True
    permission_contract_safe_for_request: bool = True
    future_loader_implementation_required: bool = True
    future_loader_requires_separate_guard: bool = True
    future_loader_requires_separate_commit: bool = True
    future_loader_requires_human_approval_before_actual_read: bool = True
    approval_granted_by_this_contract: bool = False
    authorization_granted_by_this_contract: bool = False
    actual_loader_execution_allowed: bool = False
    actual_file_read_allowed_by_this_contract: bool = False
    actual_payload_decode_allowed_by_this_contract: bool = False
    read_only: bool = True
    non_executing: bool = True
    authorization_request_only: bool = True
    contract_only: bool = True
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
            "authorization_request_version": self.authorization_request_version,
            "authorization_request_id": self.authorization_request_id,
            "authorization_request_state": self.authorization_request_state,
            "authorization_request_kind": self.authorization_request_kind,
            "permission_contract_version": self.permission_contract_version,
            "permission_contract_id": self.permission_contract_id,
            "loader_permission_state": self.loader_permission_state,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "requested_loader_scope": self.requested_loader_scope,
            "requested_artifact_roles": list(self.requested_artifact_roles),
            "requested_path_rule_count": self.requested_path_rule_count,
            "required_artifact_count": self.required_artifact_count,
            "optional_artifact_count": self.optional_artifact_count,
            "authorization_review_sequence": list(self.authorization_review_sequence),
            "authorization_failure_behavior_sequence": list(self.authorization_failure_behavior_sequence),
            "inherited_validation_sequence": list(self.inherited_validation_sequence),
            "inherited_failure_behavior_sequence": list(self.inherited_failure_behavior_sequence),
            "authorization_gates": dict(self.authorization_gates),
            "approval_contract": dict(self.approval_contract),
            "permission_contract_summary": dict(self.permission_contract_summary),
            "boundaries": dict(self.boundaries),
            "request_ready_for_human_review": self.request_ready_for_human_review,
            "permission_contract_safe_for_request": self.permission_contract_safe_for_request,
            "future_loader_implementation_required": self.future_loader_implementation_required,
            "future_loader_requires_separate_guard": self.future_loader_requires_separate_guard,
            "future_loader_requires_separate_commit": self.future_loader_requires_separate_commit,
            "future_loader_requires_human_approval_before_actual_read": self.future_loader_requires_human_approval_before_actual_read,
            "approval_granted_by_this_contract": self.approval_granted_by_this_contract,
            "authorization_granted_by_this_contract": self.authorization_granted_by_this_contract,
            "actual_loader_execution_allowed": self.actual_loader_execution_allowed,
            "actual_file_read_allowed_by_this_contract": self.actual_file_read_allowed_by_this_contract,
            "actual_payload_decode_allowed_by_this_contract": self.actual_payload_decode_allowed_by_this_contract,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "authorization_request_only": self.authorization_request_only,
            "contract_only": self.contract_only,
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


def _safe_flags() -> Dict[str, Any]:
    return {
        "read_only": True,
        "non_executing": True,
        "authorization_request_only": True,
        "contract_only": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "approval_granted_by_this_contract": False,
        "authorization_granted_by_this_contract": False,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
        "would_load_hot_latest_artifacts": False,
        "would_read_runtime_file": False,
        "would_collect_public_source": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
    }


def _permission_contract_is_safe(packet: Mapping[str, Any]) -> bool:
    if packet.get("contract_version") != LOADER_PERMISSION_CONTRACT_VERSION:
        return False
    for key in _DANGEROUS_FALSE_FIELDS:
        if key in packet and packet.get(key) is not False:
            return False
    for rule in _list(packet.get("path_rules")):
        item = _as_mapping(rule)
        for key in ("actual_file_read_allowed_by_this_contract", "would_load_hot_latest_artifacts", "would_read_runtime_file", "would_write_runtime_artifact", "would_send_to_broker"):
            if item.get(key) is not False:
                return False
    return True


def _permission_summary(packet: Mapping[str, Any]) -> Mapping[str, Any]:
    path_rules = [_as_mapping(item) for item in _list(packet.get("path_rules"))]
    return {
        "permission_contract_version": packet.get("contract_version"),
        "permission_contract_id": packet.get("contract_id"),
        "loader_permission_state": packet.get("loader_permission_state"),
        "hot_latest_root_hint": packet.get("hot_latest_root_hint"),
        "path_rule_count": len(path_rules),
        "required_artifact_count": packet.get("required_artifact_count"),
        "optional_artifact_count": packet.get("optional_artifact_count"),
        "requested_artifact_roles": [str(item.get("artifact_role") or "unknown") for item in path_rules],
        "allowed_path_hints": [str(item.get("allowed_path_hint") or "") for item in path_rules],
        "validation_sequence": list(_list(packet.get("validation_sequence"))),
        "failure_behavior_sequence": list(_list(packet.get("failure_behavior_sequence"))),
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
        "runtime_file_read_enabled": False,
        "runtime_artifact_write_enabled": False,
        "autotrade_trigger_enabled": False,
    }


def build_prediction_warroom_latest_payload_loader_authorization_request(
    *,
    permission_contract: Mapping[str, Any] | Any | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomLatestPayloadLoaderAuthorizationRequestPacket:
    """Build an explicit authorization-request packet before any future latest-payload loader implementation."""
    permission = dict(_as_mapping(permission_contract)) if permission_contract is not None else build_prediction_warroom_latest_payload_loader_permission_contract(hot_latest_root_hint=hot_latest_root_hint).to_dict()
    safe = _permission_contract_is_safe(permission)
    summary = _permission_summary(permission)
    roles = tuple(str(item) for item in _list(summary.get("requested_artifact_roles")))
    request_state = "prepared_for_human_review_actual_read_disabled" if safe else "blocked_permission_contract_unsafe"
    gates = {
        "permission_contract_version_required": LOADER_PERMISSION_CONTRACT_VERSION,
        "permission_contract_safe_for_request": safe,
        "preflight_status_contract_required": PREFLIGHT_STATUS_VERSION,
        "schema_validator_contract_required": VALIDATOR_VERSION,
        "path_scope_check_required_before_read": True,
        "expected_artifact_role_check_required": True,
        "extension_json_check_required": True,
        "file_size_check_required_before_payload_parse": True,
        "freshness_check_required_before_display": True,
        "schema_validation_required_before_display": True,
        "q6a_preflight_status_update_required": True,
        "fail_closed_required": True,
        "keep_last_good_packet_on_failure_required": True,
        "separate_loader_implementation_slice_required": True,
        "separate_loader_guard_required": True,
        **_safe_flags(),
    }
    approval_contract = {
        "approval_contract_version": LOADER_AUTHORIZATION_REQUEST_VERSION,
        "approval_kind": "future_loader_implementation_authorization_request_only",
        "human_review_required": True,
        "human_approval_required_before_actual_read": True,
        "approval_granted_by_this_contract": False,
        "authorization_granted_by_this_contract": False,
        "future_approval_must_reference_permission_contract_version": LOADER_PERMISSION_CONTRACT_VERSION,
        "future_approval_must_reference_authorization_request_id": True,
        "future_approval_must_define_single_read_window": True,
        "future_approval_must_not_enable_autotrade_or_broker": True,
        "future_loader_must_ship_in_separate_commit": True,
        **_safe_flags(),
    }
    boundaries = {
        "boundary": "authorization_request_before_latest_payload_loader_implementation",
        "request_can_be_displayed_for_review": True,
        "request_can_enable_loader": False,
        "request_can_read_files": False,
        "request_can_decode_payloads": False,
        "request_can_write_runtime_artifacts": False,
        "request_can_trigger_autotrade": False,
        "request_can_send_to_broker": False,
        **_safe_flags(),
    }
    return PredictionWarRoomLatestPayloadLoaderAuthorizationRequestPacket(
        authorization_request_version=LOADER_AUTHORIZATION_REQUEST_VERSION,
        authorization_request_id=f"{LOADER_AUTHORIZATION_REQUEST_VERSION}:{summary.get('permission_contract_id') or 'unknown'}",
        authorization_request_state=request_state,
        authorization_request_kind="prediction_warroom_latest_payload_loader_authorization_request",
        permission_contract_version=str(summary.get("permission_contract_version") or "unknown"),
        permission_contract_id=str(summary.get("permission_contract_id")) if summary.get("permission_contract_id") else None,
        loader_permission_state=str(summary.get("loader_permission_state")) if summary.get("loader_permission_state") else None,
        hot_latest_root_hint=str(summary.get("hot_latest_root_hint") or hot_latest_root_hint),
        requested_artifact_roles=roles,
        requested_path_rule_count=int(summary.get("path_rule_count") or 0),
        required_artifact_count=int(summary.get("required_artifact_count") or 0),
        optional_artifact_count=int(summary.get("optional_artifact_count") or 0),
        authorization_gates=gates,
        approval_contract=approval_contract,
        permission_contract_summary=summary,
        boundaries=boundaries,
        request_ready_for_human_review=safe,
        permission_contract_safe_for_request=safe,
    )


def build_prediction_warroom_latest_payload_loader_authorization_request_index(
    *,
    permission_contract: Mapping[str, Any] | Any | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> Dict[str, Any]:
    """Return a compact read-only index for the latest-payload loader authorization request."""
    request = build_prediction_warroom_latest_payload_loader_authorization_request(
        permission_contract=permission_contract,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    return {
        "authorization_request_index_version": LOADER_AUTHORIZATION_REQUEST_VERSION,
        "authorization_request_id": request.get("authorization_request_id"),
        "authorization_request_state": request.get("authorization_request_state"),
        "authorization_request_kind": request.get("authorization_request_kind"),
        "permission_contract_version": request.get("permission_contract_version"),
        "permission_contract_id": request.get("permission_contract_id"),
        "hot_latest_root_hint": request.get("hot_latest_root_hint"),
        "request_ready_for_human_review": request.get("request_ready_for_human_review"),
        "permission_contract_safe_for_request": request.get("permission_contract_safe_for_request"),
        "requested_loader_scope": request.get("requested_loader_scope"),
        "requested_artifact_roles": list(request.get("requested_artifact_roles") or ()),
        "requested_path_rule_count": request.get("requested_path_rule_count"),
        "required_artifact_count": request.get("required_artifact_count"),
        "optional_artifact_count": request.get("optional_artifact_count"),
        "authorization_review_sequence": list(request.get("authorization_review_sequence") or ()),
        "authorization_failure_behavior_sequence": list(request.get("authorization_failure_behavior_sequence") or ()),
        "authorization_gates": dict(_as_mapping(request.get("authorization_gates"))),
        "approval_contract": dict(_as_mapping(request.get("approval_contract"))),
        "boundaries": dict(_as_mapping(request.get("boundaries"))),
        **_safe_flags(),
    }
