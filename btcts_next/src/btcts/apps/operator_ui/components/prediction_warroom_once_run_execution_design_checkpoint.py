# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_once_run_execution_design_checkpoint.py
# desc: PS-Q16K once-run execution design checkpoint. It validates PS-Q16J dry-run evidence and records the future execution design boundary only; it never invokes manual refresh, writes status/runtime artifacts, creates locks, registers schedulers, enables loops, triggers WarRoom UI, mutates parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_disabled_once_run_checker import DISABLED_ONCE_RUN_CHECKER_VERSION
from .prediction_warroom_non_ui_scheduled_producer_contract import FRESHNESS_MAX_AGE_SEC, RECOMMENDED_CADENCE_SEC

ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION = "prediction_warroom_once_run_execution_design_checkpoint.ps_q16k.v1"

CHECKPOINT_SEQUENCE: Tuple[str, ...] = (
    "consume_ps_q16j_dry_run_report_only",
    "require_ps_q16j_ok_true",
    "require_decision_ready_no_lock_no_execution",
    "require_lock_absent_in_dry_run_evidence",
    "require_status_ready_in_dry_run_evidence",
    "require_explicit_human_execution_design_record",
    "declare_future_execution_requires_separate_later_approval",
    "declare_future_lock_create_status_write_refresh_sequence_but_do_not_execute",
    "declare_disable_rollback_before_any_future_execution",
    "return_execution_design_checkpoint_packet_only",
)

FUTURE_EXECUTION_BOUNDARY: Tuple[str, ...] = (
    "future_slice_requires_clean_tree=true",
    "future_slice_requires_fresh_ps_q16j_dry_run=true",
    "future_slice_requires_operator_acknowledgement=true",
    "future_slice_requires_lock_absent_before_start=true",
    "future_slice_may_create_lock_only_after_separate_approval=false_in_ps_q16k",
    "future_slice_may_invoke_manual_refresh_only_after_separate_approval=false_in_ps_q16k",
    "future_slice_may_write_status_only_after_separate_approval=false_in_ps_q16k",
    "future_slice_must_delete_or_release_lock_on_failure_in_future_design=true",
    "future_slice_scheduler_registration_allowed=false",
    "future_slice_warroom_ui_trigger_allowed=false",
    "future_slice_autotrade_broker_ledger_parameter_allowed=false",
)

FORBIDDEN_REQUEST_NAMES: Tuple[str, ...] = (
    "request_execute_manual_refresh",
    "request_latest_prediction_refresh",
    "request_status_artifact_write",
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


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class PredictionWarRoomOnceRunExecutionDesignCheckpointPacket:
    checkpoint_version: str
    checkpoint_id: str
    checkpoint_state: str
    checkpoint_sequence: Tuple[str, ...] = CHECKPOINT_SEQUENCE
    future_execution_boundary: Tuple[str, ...] = FUTURE_EXECUTION_BOUNDARY
    ps_q16j_report_supplied: bool = False
    ps_q16j_ok: bool = False
    decision_checker_version: str = ""
    decision_state: str = ""
    decision_simulated_decision: str = ""
    decision_preflight_latest_age_sec: int | None = None
    lock_present_in_dry_run: bool = False
    status_ready_in_dry_run: bool = False
    human_execution_design_record_present: bool = False
    human_execution_design_source: str = ""
    recommended_cadence_sec: int = RECOMMENDED_CADENCE_SEC
    freshness_max_age_sec: int = FRESHNESS_MAX_AGE_SEC
    requested_forbidden_flags: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    ready_for_future_guarded_once_run_execution_design_slice: bool = False
    ready_for_execution_enablement: bool = False
    execution_enabled: bool = False
    manual_refresh_invoked_by_this_checkpoint: bool = False
    latest_prediction_refresh_performed_by_this_checkpoint: bool = False
    status_artifact_write_performed_by_this_checkpoint: bool = False
    runtime_artifact_write_performed_by_this_checkpoint: bool = False
    lock_file_created_by_this_checkpoint: bool = False
    lock_file_deleted_by_this_checkpoint: bool = False
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
    checkpoint_only: bool = True
    read_only: bool = True
    non_executing: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_version": self.checkpoint_version,
            "checkpoint_id": self.checkpoint_id,
            "checkpoint_state": self.checkpoint_state,
            "checkpoint_sequence": list(self.checkpoint_sequence),
            "future_execution_boundary": list(self.future_execution_boundary),
            "ps_q16j_report_supplied": self.ps_q16j_report_supplied,
            "ps_q16j_ok": self.ps_q16j_ok,
            "decision_checker_version": self.decision_checker_version,
            "decision_state": self.decision_state,
            "decision_simulated_decision": self.decision_simulated_decision,
            "decision_preflight_latest_age_sec": self.decision_preflight_latest_age_sec,
            "lock_present_in_dry_run": self.lock_present_in_dry_run,
            "status_ready_in_dry_run": self.status_ready_in_dry_run,
            "human_execution_design_record_present": self.human_execution_design_record_present,
            "human_execution_design_source": self.human_execution_design_source,
            "recommended_cadence_sec": self.recommended_cadence_sec,
            "freshness_max_age_sec": self.freshness_max_age_sec,
            "requested_forbidden_flags": list(self.requested_forbidden_flags),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "ready_for_future_guarded_once_run_execution_design_slice": self.ready_for_future_guarded_once_run_execution_design_slice,
            "ready_for_execution_enablement": self.ready_for_execution_enablement,
            "execution_enabled": self.execution_enabled,
            "manual_refresh_invoked_by_this_checkpoint": self.manual_refresh_invoked_by_this_checkpoint,
            "latest_prediction_refresh_performed_by_this_checkpoint": self.latest_prediction_refresh_performed_by_this_checkpoint,
            "status_artifact_write_performed_by_this_checkpoint": self.status_artifact_write_performed_by_this_checkpoint,
            "runtime_artifact_write_performed_by_this_checkpoint": self.runtime_artifact_write_performed_by_this_checkpoint,
            "lock_file_created_by_this_checkpoint": self.lock_file_created_by_this_checkpoint,
            "lock_file_deleted_by_this_checkpoint": self.lock_file_deleted_by_this_checkpoint,
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
            "checkpoint_only": self.checkpoint_only,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
        }


def build_prediction_warroom_once_run_execution_design_checkpoint(
    *,
    ps_q16j_dry_run_report: Mapping[str, Any] | Any | None = None,
    human_execution_design_record_present: bool = False,
    human_execution_design_source: str = "",
    request_execute_manual_refresh: bool = False,
    request_latest_prediction_refresh: bool = False,
    request_status_artifact_write: bool = False,
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
) -> PredictionWarRoomOnceRunExecutionDesignCheckpointPacket:
    """Return a PS-Q16K execution design checkpoint packet without executing anything."""
    report = _as_mapping(ps_q16j_dry_run_report)
    decision = _as_mapping(report.get("decision"))
    lock = _as_mapping(report.get("lock_observation"))
    status = _as_mapping(report.get("status_observation"))
    requested = _requested_flags(
        request_execute_manual_refresh=request_execute_manual_refresh,
        request_latest_prediction_refresh=request_latest_prediction_refresh,
        request_status_artifact_write=request_status_artifact_write,
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
    blockers: list[str] = ["forbidden_request_in_ps_q16k:" + item for item in requested]
    warnings: list[str] = []
    if not report:
        blockers.append("ps_q16j_dry_run_report_required")
    else:
        if report.get("ok") is not True:
            blockers.append("ps_q16j_dry_run_not_ok")
        if report.get("dry_run_only") is not True:
            blockers.append("ps_q16j_dry_run_only_flag_missing")
        if decision.get("checker_version") != DISABLED_ONCE_RUN_CHECKER_VERSION:
            blockers.append("ps_q16j_decision_checker_version_mismatch")
        if decision.get("simulated_decision") != "ready_no_lock_no_execution":
            blockers.append("ps_q16j_decision_not_ready_no_lock_no_execution")
        if decision.get("blocker_count") not in (0, None):
            blockers.append("ps_q16j_decision_has_blockers")
        if decision.get("ready_for_future_disabled_once_run_checker_implementation") is not True:
            blockers.append("ps_q16j_decision_not_ready_for_future_disabled_once_run_checker")
        if lock.get("lock_present") is not False or decision.get("lock_present") is not False:
            blockers.append("ps_q16j_lock_present_or_unconfirmed_absent")
        if status.get("status_ready") is not True or decision.get("status_ready") is not True:
            blockers.append("ps_q16j_status_not_ready")
        latest_age = _int_or_none(decision.get("preflight_latest_age_sec"))
        if latest_age is None:
            blockers.append("ps_q16j_latest_age_missing")
        elif latest_age > FRESHNESS_MAX_AGE_SEC:
            blockers.append("ps_q16j_latest_age_stale")
        for key in (
            "manual_refresh_invoked_by_this_checker",
            "latest_prediction_refresh_performed_by_this_checker",
            "status_artifact_write_performed_by_this_checker",
            "lock_file_created_by_this_checker",
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
            if decision.get(key) is not False:
                blockers.append("ps_q16j_" + key + "_must_remain_false")
    if not human_execution_design_record_present:
        blockers.append("human_execution_design_record_required_for_ps_q16k")
    if human_execution_design_record_present and not str(human_execution_design_source or "").strip():
        warnings.append("human_execution_design_source_not_supplied")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = bool(not unique_blockers)
    state = "once_run_execution_design_checkpoint_ready_for_future_guarded_slice" if ready else "once_run_execution_design_checkpoint_blocked"
    return PredictionWarRoomOnceRunExecutionDesignCheckpointPacket(
        checkpoint_version=ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION,
        checkpoint_id=f"{ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION}:{state}",
        checkpoint_state=state,
        ps_q16j_report_supplied=bool(report),
        ps_q16j_ok=bool(report.get("ok") is True),
        decision_checker_version=str(decision.get("checker_version") or ""),
        decision_state=str(decision.get("checker_state") or ""),
        decision_simulated_decision=str(decision.get("simulated_decision") or ""),
        decision_preflight_latest_age_sec=_int_or_none(decision.get("preflight_latest_age_sec")),
        lock_present_in_dry_run=bool(lock.get("lock_present") is True or decision.get("lock_present") is True),
        status_ready_in_dry_run=bool(status.get("status_ready") is True and decision.get("status_ready") is True),
        human_execution_design_record_present=bool(human_execution_design_record_present),
        human_execution_design_source=str(human_execution_design_source or ""),
        requested_forbidden_flags=requested,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        ready_for_future_guarded_once_run_execution_design_slice=ready,
    )
