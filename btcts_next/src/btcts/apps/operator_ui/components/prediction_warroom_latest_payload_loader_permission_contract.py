# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_loader_permission_contract.py
# desc: Dry-run permission contract for a future Prediction WarRoom latest-payload loader. Defines allowed path scope, max sizes, freshness/schema sequence, and failure behavior without reading files, rendering UI, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT, build_prediction_warroom_l4_latest_expected_artifacts
from .prediction_warroom_latest_payload_preflight_status import PREFLIGHT_STATUS_VERSION
from .prediction_warroom_payload_schema_validator import VALIDATOR_VERSION

LOADER_PERMISSION_CONTRACT_VERSION = "prediction_warroom_latest_payload_loader_permission_contract.ps_q6b.v1"
DEFAULT_REQUIRED_ARTIFACT_MAX_BYTES = 8_000_000
DEFAULT_OPTIONAL_ARTIFACT_MAX_BYTES = 2_000_000
DEFAULT_REQUIRED_ARTIFACT_FRESHNESS_MAX_AGE_SEC = 3_600
DEFAULT_OPTIONAL_ARTIFACT_FRESHNESS_MAX_AGE_SEC = 180

VALIDATION_SEQUENCE = (
    "path_scope_check_under_hot_latest_root",
    "expected_artifact_role_check",
    "extension_json_check",
    "file_size_check_before_payload_parse",
    "freshness_check_before_display",
    "payload_decode_after_explicit_loader_authorization",
    "schema_validation_with_q5c",
    "q6a_preflight_status_update",
    "handoff_only_when_preflight_ready",
)
FAILURE_BEHAVIOR_SEQUENCE = (
    "return_blocked_preflight_status",
    "show_stale_or_blocked_badge_keep_last_good_packet",
    "do_not_render_unvalidated_payload",
    "do_not_write_runtime_artifact",
    "do_not_trigger_autotrade",
    "do_not_send_to_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadLoaderPathRule:
    artifact_role: str
    artifact_contract_id: str
    allowed_root_hint: str
    allowed_path_hint: str
    required: bool = True
    allowed_extension: str = ".json"
    max_file_size_bytes: int = DEFAULT_REQUIRED_ARTIFACT_MAX_BYTES
    freshness_max_age_sec: int = DEFAULT_REQUIRED_ARTIFACT_FRESHNESS_MAX_AGE_SEC
    must_be_under_hot_latest_root: bool = True
    must_match_expected_artifact_ref: bool = True
    future_loader_must_check_path_scope_before_read: bool = True
    future_loader_must_check_size_before_parse: bool = True
    future_loader_must_check_freshness_before_display: bool = True
    future_loader_must_run_schema_validation_before_display: bool = True
    schema_validator_contract_version: str = VALIDATOR_VERSION
    preflight_status_contract_version: str = PREFLIGHT_STATUS_VERSION
    actual_file_read_allowed_by_this_contract: bool = False
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
            "allowed_root_hint": self.allowed_root_hint,
            "allowed_path_hint": self.allowed_path_hint,
            "required": self.required,
            "allowed_extension": self.allowed_extension,
            "max_file_size_bytes": self.max_file_size_bytes,
            "freshness_max_age_sec": self.freshness_max_age_sec,
            "must_be_under_hot_latest_root": self.must_be_under_hot_latest_root,
            "must_match_expected_artifact_ref": self.must_match_expected_artifact_ref,
            "future_loader_must_check_path_scope_before_read": self.future_loader_must_check_path_scope_before_read,
            "future_loader_must_check_size_before_parse": self.future_loader_must_check_size_before_parse,
            "future_loader_must_check_freshness_before_display": self.future_loader_must_check_freshness_before_display,
            "future_loader_must_run_schema_validation_before_display": self.future_loader_must_run_schema_validation_before_display,
            "schema_validator_contract_version": self.schema_validator_contract_version,
            "preflight_status_contract_version": self.preflight_status_contract_version,
            "actual_file_read_allowed_by_this_contract": self.actual_file_read_allowed_by_this_contract,
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
class PredictionWarRoomLatestPayloadLoaderPermissionContractPacket:
    contract_version: str
    contract_id: str
    loader_permission_state: str
    hot_latest_root_hint: str
    preflight_status_contract_version: str
    schema_validator_contract_version: str
    path_rules: Tuple[PredictionWarRoomLatestPayloadLoaderPathRule, ...] = ()
    validation_sequence: Tuple[str, ...] = VALIDATION_SEQUENCE
    failure_behavior_sequence: Tuple[str, ...] = FAILURE_BEHAVIOR_SEQUENCE
    required_artifact_count: int = 0
    optional_artifact_count: int = 0
    actual_file_read_allowed_by_this_contract: bool = False
    actual_payload_decode_allowed_by_this_contract: bool = False
    future_loader_implementation_required: bool = True
    future_loader_requires_separate_guard: bool = True
    future_loader_requires_human_approval_before_actual_read: bool = True
    future_loader_must_not_expand_allowed_roots_silently: bool = True
    future_loader_must_validate_schema_before_display: bool = True
    future_loader_must_check_freshness_before_display: bool = True
    future_loader_must_fail_closed_on_validation_error: bool = True
    future_loader_must_keep_last_good_packet_on_failure: bool = True
    future_loader_must_not_write_runtime_artifacts: bool = True
    future_loader_must_not_trigger_autotrade: bool = True
    blocked_reasons_when_contract_only: Tuple[str, ...] = ("actual_latest_payload_loader_not_implemented", "actual_file_read_not_allowed_by_ps_q6b_contract")
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
            "contract_version": self.contract_version,
            "contract_id": self.contract_id,
            "loader_permission_state": self.loader_permission_state,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "preflight_status_contract_version": self.preflight_status_contract_version,
            "schema_validator_contract_version": self.schema_validator_contract_version,
            "path_rules": [item.to_dict() for item in self.path_rules],
            "validation_sequence": list(self.validation_sequence),
            "failure_behavior_sequence": list(self.failure_behavior_sequence),
            "required_artifact_count": self.required_artifact_count,
            "optional_artifact_count": self.optional_artifact_count,
            "actual_file_read_allowed_by_this_contract": self.actual_file_read_allowed_by_this_contract,
            "actual_payload_decode_allowed_by_this_contract": self.actual_payload_decode_allowed_by_this_contract,
            "future_loader_implementation_required": self.future_loader_implementation_required,
            "future_loader_requires_separate_guard": self.future_loader_requires_separate_guard,
            "future_loader_requires_human_approval_before_actual_read": self.future_loader_requires_human_approval_before_actual_read,
            "future_loader_must_not_expand_allowed_roots_silently": self.future_loader_must_not_expand_allowed_roots_silently,
            "future_loader_must_validate_schema_before_display": self.future_loader_must_validate_schema_before_display,
            "future_loader_must_check_freshness_before_display": self.future_loader_must_check_freshness_before_display,
            "future_loader_must_fail_closed_on_validation_error": self.future_loader_must_fail_closed_on_validation_error,
            "future_loader_must_keep_last_good_packet_on_failure": self.future_loader_must_keep_last_good_packet_on_failure,
            "future_loader_must_not_write_runtime_artifacts": self.future_loader_must_not_write_runtime_artifacts,
            "future_loader_must_not_trigger_autotrade": self.future_loader_must_not_trigger_autotrade,
            "blocked_reasons_when_contract_only": list(self.blocked_reasons_when_contract_only),
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


def _path_rule_from_expected_ref(ref: Any, *, hot_latest_root_hint: str, required_max_bytes: int, optional_max_bytes: int, required_freshness_sec: int, optional_freshness_sec: int) -> PredictionWarRoomLatestPayloadLoaderPathRule:
    item = _as_mapping(ref)
    required = bool(item.get("required", True))
    return PredictionWarRoomLatestPayloadLoaderPathRule(
        artifact_role=str(item.get("artifact_role") or "unknown"),
        artifact_contract_id=str(item.get("artifact_contract_id") or "unknown"),
        allowed_root_hint=str(hot_latest_root_hint),
        allowed_path_hint=str(item.get("expected_path_hint") or ""),
        required=required,
        max_file_size_bytes=required_max_bytes if required else optional_max_bytes,
        freshness_max_age_sec=required_freshness_sec if required else optional_freshness_sec,
    )


def build_prediction_warroom_latest_payload_loader_permission_contract(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    required_artifact_max_bytes: int = DEFAULT_REQUIRED_ARTIFACT_MAX_BYTES,
    optional_artifact_max_bytes: int = DEFAULT_OPTIONAL_ARTIFACT_MAX_BYTES,
    required_artifact_freshness_max_age_sec: int = DEFAULT_REQUIRED_ARTIFACT_FRESHNESS_MAX_AGE_SEC,
    optional_artifact_freshness_max_age_sec: int = DEFAULT_OPTIONAL_ARTIFACT_FRESHNESS_MAX_AGE_SEC,
) -> PredictionWarRoomLatestPayloadLoaderPermissionContractPacket:
    """Build a dry-run-only permission contract for a future latest-payload loader without reading files."""
    expected_refs = build_prediction_warroom_l4_latest_expected_artifacts(hot_latest_root_hint=hot_latest_root_hint)
    rules = tuple(
        _path_rule_from_expected_ref(
            ref,
            hot_latest_root_hint=hot_latest_root_hint,
            required_max_bytes=required_artifact_max_bytes,
            optional_max_bytes=optional_artifact_max_bytes,
            required_freshness_sec=required_artifact_freshness_max_age_sec,
            optional_freshness_sec=optional_artifact_freshness_max_age_sec,
        )
        for ref in expected_refs
    )
    required_count = sum(1 for item in rules if item.required)
    optional_count = len(rules) - required_count
    return PredictionWarRoomLatestPayloadLoaderPermissionContractPacket(
        contract_version=LOADER_PERMISSION_CONTRACT_VERSION,
        contract_id=f"{LOADER_PERMISSION_CONTRACT_VERSION}:latest:dry_run_only",
        loader_permission_state="contract_only_actual_read_not_allowed",
        hot_latest_root_hint=str(hot_latest_root_hint),
        preflight_status_contract_version=PREFLIGHT_STATUS_VERSION,
        schema_validator_contract_version=VALIDATOR_VERSION,
        path_rules=rules,
        required_artifact_count=required_count,
        optional_artifact_count=optional_count,
        handoff_summary={
            "loader_boundary": "latest_payload_loader_permission_contract_before_implementation",
            "hot_latest_root_preference": str(hot_latest_root_hint),
            "path_rule_count": len(rules),
            "required_artifact_roles": [item.artifact_role for item in rules if item.required],
            "optional_artifact_roles": [item.artifact_role for item in rules if not item.required],
            "validation_sequence": list(VALIDATION_SEQUENCE),
            "failure_behavior_sequence": list(FAILURE_BEHAVIOR_SEQUENCE),
            "preflight_status_contract_version": PREFLIGHT_STATUS_VERSION,
            "schema_validator_contract_version": VALIDATOR_VERSION,
            "actual_file_read_allowed_by_this_contract": False,
            "actual_payload_decode_allowed_by_this_contract": False,
            "future_loader_requires_separate_guard": True,
            "loaded_in_this_slice": False,
            "runtime_file_read_enabled": False,
            "runtime_artifact_write_enabled": False,
            "autotrade_trigger_enabled": False,
        },
    )
