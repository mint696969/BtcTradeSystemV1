# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_once_run_checker.py
# desc: PS-Q16I disabled operator-shell once-run checker. It evaluates preflight/skeleton/lock/status decision inputs in memory only; it never schedules, loops, refreshes artifacts, writes files, creates locks, triggers WarRoom UI, mutates parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_disabled_scheduler_wrapper_skeleton import (
    DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION,
)
from .prediction_warroom_non_ui_scheduled_producer_contract import (
    FRESHNESS_MAX_AGE_SEC,
    RECOMMENDED_CADENCE_SEC,
)

DISABLED_ONCE_RUN_CHECKER_VERSION = "prediction_warroom_disabled_once_run_checker.ps_q16i.v1"

CHECKER_SEQUENCE: Tuple[str, ...] = (
    "consume_ps_q16h_wrapper_skeleton_packet_only",
    "consume_ps_q16f_preflight_report_summary_only",
    "consume_supplied_lock_observation_without_reading_or_creating_lock",
    "consume_supplied_status_observation_without_writing_status",
    "simulate_skip_when_lock_present",
    "simulate_block_when_preflight_not_passed_or_stale",
    "declare_no_manual_refresh_execution_in_ps_q16i",
    "declare_no_status_write_in_ps_q16i",
    "declare_no_lock_creation_in_ps_q16i",
    "return_disabled_once_run_checker_packet_only",
)

DECISION_STATES: Tuple[str, ...] = (
    "once_run_checker_disabled_ready_no_lock",
    "once_run_checker_disabled_skip_existing_lock",
    "once_run_checker_disabled_blocked",
)

FORBIDDEN_REQUEST_NAMES: Tuple[str, ...] = (
    "request_enable_wrapper",
    "request_scheduler_enable",
    "request_os_scheduler_registration",
    "request_scheduled_loop_enable",
    "request_execute_manual_refresh",
    "request_latest_prediction_refresh",
    "request_status_artifact_write",
    "request_lock_file_create",
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


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


@dataclass(frozen=True)
class PredictionWarRoomDisabledOnceRunCheckerPacket:
    checker_version: str
    checker_id: str
    checker_state: str
    checker_sequence: Tuple[str, ...] = CHECKER_SEQUENCE
    decision_states: Tuple[str, ...] = DECISION_STATES
    skeleton_packet_supplied: bool = False
    skeleton_version: str = ""
    skeleton_ready: bool = False
    preflight_report_supplied: bool = False
    preflight_passed: bool = False
    preflight_latest_age_sec: int | None = None
    lock_observation_supplied: bool = False
    lock_present: bool = False
    lock_reason: str = ""
    status_observation_supplied: bool = False
    status_ready: bool = False
    status_last_success_at: str = ""
    recommended_cadence_sec: int = RECOMMENDED_CADENCE_SEC
    freshness_max_age_sec: int = FRESHNESS_MAX_AGE_SEC
    requested_forbidden_flags: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    simulated_decision: str = "blocked"
    would_skip_due_to_existing_lock: bool = False
    ready_for_future_disabled_once_run_checker_implementation: bool = False
    wrapper_enabled: bool = False
    scheduler_enabled: bool = False
    os_scheduler_registration_performed: bool = False
    scheduled_loop_enabled: bool = False
    enablement_command_generated: bool = False
    manual_refresh_invoked_by_this_checker: bool = False
    latest_prediction_refresh_performed_by_this_checker: bool = False
    status_artifact_write_performed_by_this_checker: bool = False
    lock_file_created_by_this_checker: bool = False
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
    checker_only: bool = True
    read_only: bool = True
    non_executing: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checker_version": self.checker_version,
            "checker_id": self.checker_id,
            "checker_state": self.checker_state,
            "checker_sequence": list(self.checker_sequence),
            "decision_states": list(self.decision_states),
            "skeleton_packet_supplied": self.skeleton_packet_supplied,
            "skeleton_version": self.skeleton_version,
            "skeleton_ready": self.skeleton_ready,
            "preflight_report_supplied": self.preflight_report_supplied,
            "preflight_passed": self.preflight_passed,
            "preflight_latest_age_sec": self.preflight_latest_age_sec,
            "lock_observation_supplied": self.lock_observation_supplied,
            "lock_present": self.lock_present,
            "lock_reason": self.lock_reason,
            "status_observation_supplied": self.status_observation_supplied,
            "status_ready": self.status_ready,
            "status_last_success_at": self.status_last_success_at,
            "recommended_cadence_sec": self.recommended_cadence_sec,
            "freshness_max_age_sec": self.freshness_max_age_sec,
            "requested_forbidden_flags": list(self.requested_forbidden_flags),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "simulated_decision": self.simulated_decision,
            "would_skip_due_to_existing_lock": self.would_skip_due_to_existing_lock,
            "ready_for_future_disabled_once_run_checker_implementation": self.ready_for_future_disabled_once_run_checker_implementation,
            "wrapper_enabled": self.wrapper_enabled,
            "scheduler_enabled": self.scheduler_enabled,
            "os_scheduler_registration_performed": self.os_scheduler_registration_performed,
            "scheduled_loop_enabled": self.scheduled_loop_enabled,
            "enablement_command_generated": self.enablement_command_generated,
            "manual_refresh_invoked_by_this_checker": self.manual_refresh_invoked_by_this_checker,
            "latest_prediction_refresh_performed_by_this_checker": self.latest_prediction_refresh_performed_by_this_checker,
            "status_artifact_write_performed_by_this_checker": self.status_artifact_write_performed_by_this_checker,
            "lock_file_created_by_this_checker": self.lock_file_created_by_this_checker,
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
            "checker_only": self.checker_only,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
        }


def build_prediction_warroom_disabled_once_run_checker(
    *,
    ps_q16h_wrapper_skeleton_packet: Mapping[str, Any] | Any | None = None,
    ps_q16f_preflight_report: Mapping[str, Any] | Any | None = None,
    supplied_lock_observation: Mapping[str, Any] | Any | None = None,
    supplied_status_observation: Mapping[str, Any] | Any | None = None,
    request_enable_wrapper: bool = False,
    request_scheduler_enable: bool = False,
    request_os_scheduler_registration: bool = False,
    request_scheduled_loop_enable: bool = False,
    request_execute_manual_refresh: bool = False,
    request_latest_prediction_refresh: bool = False,
    request_status_artifact_write: bool = False,
    request_lock_file_create: bool = False,
    request_generate_enablement_command: bool = False,
    request_warroom_ui_trigger: bool = False,
    request_parameter_apply: bool = False,
    request_parameter_staging_write: bool = False,
    request_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> PredictionWarRoomDisabledOnceRunCheckerPacket:
    """Evaluate disabled once-run decision inputs in memory without executing anything."""
    skeleton = _as_mapping(ps_q16h_wrapper_skeleton_packet)
    preflight = _as_mapping(ps_q16f_preflight_report)
    lock = _as_mapping(supplied_lock_observation)
    status = _as_mapping(supplied_status_observation)
    requested = _requested_flags(
        request_enable_wrapper=request_enable_wrapper,
        request_scheduler_enable=request_scheduler_enable,
        request_os_scheduler_registration=request_os_scheduler_registration,
        request_scheduled_loop_enable=request_scheduled_loop_enable,
        request_execute_manual_refresh=request_execute_manual_refresh,
        request_latest_prediction_refresh=request_latest_prediction_refresh,
        request_status_artifact_write=request_status_artifact_write,
        request_lock_file_create=request_lock_file_create,
        request_generate_enablement_command=request_generate_enablement_command,
        request_warroom_ui_trigger=request_warroom_ui_trigger,
        request_parameter_apply=request_parameter_apply,
        request_parameter_staging_write=request_parameter_staging_write,
        request_approval_or_ledger_or_autotrade_or_broker=request_approval_or_ledger_or_autotrade_or_broker,
    )
    blockers: list[str] = ["forbidden_request_in_ps_q16i:" + item for item in requested]
    warnings: list[str] = []
    if not skeleton:
        blockers.append("ps_q16h_wrapper_skeleton_packet_required")
    else:
        if skeleton.get("skeleton_version") != DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION:
            blockers.append("ps_q16h_wrapper_skeleton_version_mismatch")
        if skeleton.get("ready_for_future_disabled_operator_shell_wrapper_implementation") is not True:
            blockers.append("ps_q16h_wrapper_skeleton_not_ready")
        for key in ("wrapper_enabled", "scheduler_enabled", "os_scheduler_registration_performed", "scheduled_loop_enabled", "enablement_command_generated"):
            if skeleton.get(key) is not False:
                blockers.append("ps_q16h_" + key + "_must_remain_false")
    if not preflight:
        blockers.append("ps_q16f_preflight_report_required")
    else:
        if preflight.get("ok") is not True or preflight.get("preflight_passed") is not True:
            blockers.append("ps_q16f_preflight_not_passed")
        if preflight.get("ready_for_scheduler_enablement") is not False:
            blockers.append("ps_q16f_ready_for_scheduler_enablement_must_remain_false")
    latest = _as_mapping(preflight.get("latest_prediction"))
    latest_age = latest.get("age_sec") if isinstance(latest.get("age_sec"), int) else None
    if latest_age is None and preflight:
        blockers.append("ps_q16f_latest_age_missing")
    elif isinstance(latest_age, int) and latest_age > FRESHNESS_MAX_AGE_SEC:
        blockers.append("ps_q16f_latest_prediction_stale")
    if not lock:
        warnings.append("lock_observation_not_supplied_assuming_no_lock_for_simulation")
    lock_present = bool(lock.get("lock_present") is True)
    lock_reason = str(lock.get("lock_reason") or ("supplied_lock_present" if lock_present else ""))
    if lock_present:
        warnings.append("simulated_skip_due_to_existing_lock")
    status_ready = bool(status.get("status_ready") is True) if status else False
    if not status:
        warnings.append("status_observation_not_supplied")
    elif not status_ready:
        warnings.append("status_observation_not_ready")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    if unique_blockers:
        state = "once_run_checker_disabled_blocked"
        decision = "blocked"
    elif lock_present:
        state = "once_run_checker_disabled_skip_existing_lock"
        decision = "skip_existing_lock"
    else:
        state = "once_run_checker_disabled_ready_no_lock"
        decision = "ready_no_lock_no_execution"
    return PredictionWarRoomDisabledOnceRunCheckerPacket(
        checker_version=DISABLED_ONCE_RUN_CHECKER_VERSION,
        checker_id=f"{DISABLED_ONCE_RUN_CHECKER_VERSION}:{state}",
        checker_state=state,
        skeleton_packet_supplied=bool(skeleton),
        skeleton_version=str(skeleton.get("skeleton_version") or ""),
        skeleton_ready=bool(skeleton.get("ready_for_future_disabled_operator_shell_wrapper_implementation") is True),
        preflight_report_supplied=bool(preflight),
        preflight_passed=bool(preflight.get("ok") is True and preflight.get("preflight_passed") is True),
        preflight_latest_age_sec=latest_age,
        lock_observation_supplied=bool(lock),
        lock_present=lock_present,
        lock_reason=lock_reason,
        status_observation_supplied=bool(status),
        status_ready=status_ready,
        status_last_success_at=str(status.get("last_success_at") or ""),
        requested_forbidden_flags=requested,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        simulated_decision=decision,
        would_skip_due_to_existing_lock=lock_present and not unique_blockers,
        ready_for_future_disabled_once_run_checker_implementation=not unique_blockers,
    )
