# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_operator_shell_once_run_cli_skeleton.py
# desc: PS-Q16N disabled operator-shell once-run CLI skeleton/dry-run wrapper contract. It validates a PS-Q16M implementation skeleton and declares future CLI boundaries only; it never creates locks, invokes refresh runners, writes status/runtime artifacts, registers schedulers, triggers WarRoom UI, mutates parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_guarded_once_run_implementation_skeleton import (
    GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_VERSION,
)
from .prediction_warroom_guarded_once_run_execution_plan_packet import LOCK_RELATIVE_PATH
from .prediction_warroom_non_ui_scheduled_producer_contract import (
    PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
    RECOMMENDED_CADENCE_SEC,
)

DISABLED_OPERATOR_SHELL_ONCE_RUN_CLI_SKELETON_VERSION = (
    "prediction_warroom_disabled_operator_shell_once_run_cli_skeleton.ps_q16n.v1"
)

CLI_SKELETON_SEQUENCE: Tuple[str, ...] = (
    "consume_ps_q16m_implementation_skeleton_packet_only",
    "require_ps_q16m_skeleton_ready",
    "require_explicit_human_cli_skeleton_record",
    "declare_operator_shell_cli_name_only",
    "declare_default_disabled_and_dry_run_only",
    "declare_argument_contract_without_parsing_runtime_args",
    "declare_lock_status_refresh_boundaries_without_io",
    "declare_no_scheduler_no_loop_no_warroom_ui_trigger",
    "declare_no_autotrade_broker_ledger_parameter_behavior",
    "return_disabled_cli_skeleton_packet_only",
)

FUTURE_CLI_CONTRACT: Tuple[str, ...] = (
    "future_cli_name=check_phase4a_prediction_system_ps_q16n_disabled_operator_shell_once_run_cli.py",
    "future_cli_default=disabled",
    "future_cli_operator_shell_only=true",
    "future_cli_default_mode=dry_run_only",
    "future_cli_requires_explicit_execution_approval=false_in_ps_q16n",
    "future_cli_requires_clean_tree=true",
    "future_cli_requires_fresh_ps_q16j_dry_run=true",
    "future_cli_requires_no_existing_lock=true",
    "future_cli_must_not_register_scheduler=true",
    "future_cli_must_not_be_invoked_from_warroom_ui=true",
)

FUTURE_ARGUMENT_CONTRACT: Tuple[str, ...] = (
    "future_arg_hot_root=read_only_observation_root",
    "future_arg_allow_dirty=diagnostics_only_default_false",
    "future_arg_execute=not_available_in_ps_q16n",
    "future_arg_create_lock=not_available_in_ps_q16n",
    "future_arg_write_status=not_available_in_ps_q16n",
    "future_arg_refresh_latest=not_available_in_ps_q16n",
)

FORBIDDEN_REQUEST_NAMES: Tuple[str, ...] = (
    "request_enable_cli",
    "request_execute_cli",
    "request_execute_once_run",
    "request_execute_manual_refresh",
    "request_latest_prediction_refresh",
    "request_status_artifact_write",
    "request_runtime_artifact_write",
    "request_lock_file_create",
    "request_lock_file_delete",
    "request_scheduler_enable",
    "request_os_scheduler_registration",
    "request_scheduled_loop_enable",
    "request_generate_enablement_command",
    "request_warroom_ui_trigger",
    "request_parameter_apply",
    "request_parameter_staging_write",
    "request_approval_or_ledger_or_autotrade_or_broker",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _requested_flags(**flags: bool) -> tuple[str, ...]:
    return tuple(name for name, requested in flags.items() if requested)


@dataclass(frozen=True)
class PredictionWarRoomDisabledOperatorShellOnceRunCliSkeletonPacket:
    cli_skeleton_version: str
    cli_skeleton_id: str
    cli_skeleton_state: str
    cli_skeleton_sequence: Tuple[str, ...] = CLI_SKELETON_SEQUENCE
    future_cli_contract: Tuple[str, ...] = FUTURE_CLI_CONTRACT
    future_argument_contract: Tuple[str, ...] = FUTURE_ARGUMENT_CONTRACT
    implementation_skeleton_supplied: bool = False
    implementation_skeleton_version: str = ""
    implementation_skeleton_ready: bool = False
    human_cli_skeleton_record_present: bool = False
    human_cli_skeleton_source: str = ""
    lock_relative_path: str = LOCK_RELATIVE_PATH
    status_artifact_relative_path: str = PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH
    recommended_cadence_sec: int = RECOMMENDED_CADENCE_SEC
    requested_forbidden_flags: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    ready_for_future_disabled_operator_shell_dry_run_cli_slice: bool = False
    ready_for_execution_enablement: bool = False
    cli_enabled: bool = False
    implementation_enabled: bool = False
    execution_enabled: bool = False
    cli_skeleton_only: bool = True
    dry_run_wrapper_only: bool = True
    operator_shell_only: bool = True
    read_only: bool = True
    non_executing: bool = True
    manual_refresh_invoked_by_this_cli_skeleton: bool = False
    latest_prediction_refresh_performed_by_this_cli_skeleton: bool = False
    status_artifact_write_performed_by_this_cli_skeleton: bool = False
    runtime_artifact_write_performed_by_this_cli_skeleton: bool = False
    lock_file_created_by_this_cli_skeleton: bool = False
    lock_file_deleted_by_this_cli_skeleton: bool = False
    wrapper_enabled: bool = False
    scheduler_enabled: bool = False
    os_scheduler_registration_performed: bool = False
    scheduled_loop_enabled: bool = False
    enablement_command_generated: bool = False
    warroom_ui_trigger_enabled: bool = False
    ui_triggered_runner_execution: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    parameter_apply_allowed: bool = False
    parameter_staging_write_allowed: bool = False
    would_send_to_broker: bool = False
    would_write_collector_state: bool = False
    freshness_bypass_added: bool = False
    force_ready_added: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cli_skeleton_version": self.cli_skeleton_version,
            "cli_skeleton_id": self.cli_skeleton_id,
            "cli_skeleton_state": self.cli_skeleton_state,
            "cli_skeleton_sequence": list(self.cli_skeleton_sequence),
            "future_cli_contract": list(self.future_cli_contract),
            "future_argument_contract": list(self.future_argument_contract),
            "implementation_skeleton_supplied": self.implementation_skeleton_supplied,
            "implementation_skeleton_version": self.implementation_skeleton_version,
            "implementation_skeleton_ready": self.implementation_skeleton_ready,
            "human_cli_skeleton_record_present": self.human_cli_skeleton_record_present,
            "human_cli_skeleton_source": self.human_cli_skeleton_source,
            "lock_relative_path": self.lock_relative_path,
            "status_artifact_relative_path": self.status_artifact_relative_path,
            "recommended_cadence_sec": self.recommended_cadence_sec,
            "requested_forbidden_flags": list(self.requested_forbidden_flags),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "ready_for_future_disabled_operator_shell_dry_run_cli_slice": self.ready_for_future_disabled_operator_shell_dry_run_cli_slice,
            "ready_for_execution_enablement": self.ready_for_execution_enablement,
            "cli_enabled": self.cli_enabled,
            "implementation_enabled": self.implementation_enabled,
            "execution_enabled": self.execution_enabled,
            "cli_skeleton_only": self.cli_skeleton_only,
            "dry_run_wrapper_only": self.dry_run_wrapper_only,
            "operator_shell_only": self.operator_shell_only,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "manual_refresh_invoked_by_this_cli_skeleton": self.manual_refresh_invoked_by_this_cli_skeleton,
            "latest_prediction_refresh_performed_by_this_cli_skeleton": self.latest_prediction_refresh_performed_by_this_cli_skeleton,
            "status_artifact_write_performed_by_this_cli_skeleton": self.status_artifact_write_performed_by_this_cli_skeleton,
            "runtime_artifact_write_performed_by_this_cli_skeleton": self.runtime_artifact_write_performed_by_this_cli_skeleton,
            "lock_file_created_by_this_cli_skeleton": self.lock_file_created_by_this_cli_skeleton,
            "lock_file_deleted_by_this_cli_skeleton": self.lock_file_deleted_by_this_cli_skeleton,
            "wrapper_enabled": self.wrapper_enabled,
            "scheduler_enabled": self.scheduler_enabled,
            "os_scheduler_registration_performed": self.os_scheduler_registration_performed,
            "scheduled_loop_enabled": self.scheduled_loop_enabled,
            "enablement_command_generated": self.enablement_command_generated,
            "warroom_ui_trigger_enabled": self.warroom_ui_trigger_enabled,
            "ui_triggered_runner_execution": self.ui_triggered_runner_execution,
            "approval_or_authorization_allowed": self.approval_or_authorization_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "parameter_apply_allowed": self.parameter_apply_allowed,
            "parameter_staging_write_allowed": self.parameter_staging_write_allowed,
            "would_send_to_broker": self.would_send_to_broker,
            "would_write_collector_state": self.would_write_collector_state,
            "freshness_bypass_added": self.freshness_bypass_added,
            "force_ready_added": self.force_ready_added,
        }


def build_prediction_warroom_disabled_operator_shell_once_run_cli_skeleton(
    *,
    ps_q16m_implementation_skeleton_packet: Mapping[str, Any] | Any | None = None,
    human_cli_skeleton_record_present: bool = False,
    human_cli_skeleton_source: str = "",
    request_enable_cli: bool = False,
    request_execute_cli: bool = False,
    request_execute_once_run: bool = False,
    request_execute_manual_refresh: bool = False,
    request_latest_prediction_refresh: bool = False,
    request_status_artifact_write: bool = False,
    request_runtime_artifact_write: bool = False,
    request_lock_file_create: bool = False,
    request_lock_file_delete: bool = False,
    request_scheduler_enable: bool = False,
    request_os_scheduler_registration: bool = False,
    request_scheduled_loop_enable: bool = False,
    request_generate_enablement_command: bool = False,
    request_warroom_ui_trigger: bool = False,
    request_parameter_apply: bool = False,
    request_parameter_staging_write: bool = False,
    request_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> PredictionWarRoomDisabledOperatorShellOnceRunCliSkeletonPacket:
    """Return a disabled operator-shell CLI skeleton packet without executing or writing anything."""
    skeleton = _as_mapping(ps_q16m_implementation_skeleton_packet)
    requested = _requested_flags(
        request_enable_cli=request_enable_cli,
        request_execute_cli=request_execute_cli,
        request_execute_once_run=request_execute_once_run,
        request_execute_manual_refresh=request_execute_manual_refresh,
        request_latest_prediction_refresh=request_latest_prediction_refresh,
        request_status_artifact_write=request_status_artifact_write,
        request_runtime_artifact_write=request_runtime_artifact_write,
        request_lock_file_create=request_lock_file_create,
        request_lock_file_delete=request_lock_file_delete,
        request_scheduler_enable=request_scheduler_enable,
        request_os_scheduler_registration=request_os_scheduler_registration,
        request_scheduled_loop_enable=request_scheduled_loop_enable,
        request_generate_enablement_command=request_generate_enablement_command,
        request_warroom_ui_trigger=request_warroom_ui_trigger,
        request_parameter_apply=request_parameter_apply,
        request_parameter_staging_write=request_parameter_staging_write,
        request_approval_or_ledger_or_autotrade_or_broker=request_approval_or_ledger_or_autotrade_or_broker,
    )
    blockers: list[str] = ["forbidden_request_in_ps_q16n:" + item for item in requested]
    warnings: list[str] = []
    if not skeleton:
        blockers.append("ps_q16m_implementation_skeleton_packet_required")
    else:
        if skeleton.get("skeleton_version") != GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_VERSION:
            blockers.append("ps_q16m_implementation_skeleton_version_mismatch")
        if skeleton.get("ready_for_future_disabled_once_run_operator_shell_cli_slice") is not True:
            blockers.append("ps_q16m_implementation_skeleton_not_ready_for_cli_skeleton")
        if skeleton.get("skeleton_only") is not True or skeleton.get("read_only") is not True or skeleton.get("non_executing") is not True:
            blockers.append("ps_q16m_implementation_skeleton_safety_flags_missing")
        if skeleton.get("lock_relative_path") != LOCK_RELATIVE_PATH:
            blockers.append("ps_q16m_lock_relative_path_mismatch")
        for key in (
            "ready_for_execution_enablement",
            "implementation_enabled",
            "execution_enabled",
            "manual_refresh_invoked_by_this_skeleton",
            "latest_prediction_refresh_performed_by_this_skeleton",
            "status_artifact_write_performed_by_this_skeleton",
            "runtime_artifact_write_performed_by_this_skeleton",
            "lock_file_created_by_this_skeleton",
            "lock_file_deleted_by_this_skeleton",
            "scheduler_enabled",
            "os_scheduler_registration_performed",
            "scheduled_loop_enabled",
            "warroom_ui_trigger_enabled",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
            "parameter_apply_allowed",
            "parameter_staging_write_allowed",
            "freshness_bypass_added",
            "force_ready_added",
        ):
            if skeleton.get(key) is not False:
                blockers.append("ps_q16m_" + key + "_must_remain_false")
    if not human_cli_skeleton_record_present:
        blockers.append("human_cli_skeleton_record_required_for_ps_q16n")
    if human_cli_skeleton_record_present and not str(human_cli_skeleton_source or "").strip():
        warnings.append("human_cli_skeleton_source_not_supplied")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = bool(not unique_blockers)
    state = "disabled_operator_shell_once_run_cli_skeleton_ready_for_future_dry_run_wrapper" if ready else "disabled_operator_shell_once_run_cli_skeleton_blocked"
    return PredictionWarRoomDisabledOperatorShellOnceRunCliSkeletonPacket(
        cli_skeleton_version=DISABLED_OPERATOR_SHELL_ONCE_RUN_CLI_SKELETON_VERSION,
        cli_skeleton_id=f"{DISABLED_OPERATOR_SHELL_ONCE_RUN_CLI_SKELETON_VERSION}:{state}",
        cli_skeleton_state=state,
        implementation_skeleton_supplied=bool(skeleton),
        implementation_skeleton_version=str(skeleton.get("skeleton_version") or ""),
        implementation_skeleton_ready=bool(skeleton.get("ready_for_future_disabled_once_run_operator_shell_cli_slice") is True),
        human_cli_skeleton_record_present=bool(human_cli_skeleton_record_present),
        human_cli_skeleton_source=str(human_cli_skeleton_source or ""),
        requested_forbidden_flags=requested,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        ready_for_future_disabled_operator_shell_dry_run_cli_slice=ready,
    )
