# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_scheduler_design_packet.py
# desc: PS-Q16G design-only packet for a future disabled-by-default non-UI scheduler wrapper. It emits runbook/checkpoint structure only and never schedules, loops, refreshes artifacts, writes files, mutates parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_non_ui_scheduled_producer_contract import (
    FRESHNESS_MAX_AGE_SEC,
    LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH,
    MAXIMUM_CADENCE_SEC,
    MINIMUM_CADENCE_SEC,
    PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
    RECOMMENDED_CADENCE_SEC,
)

DISABLED_SCHEDULER_DESIGN_PACKET_VERSION = "prediction_warroom_disabled_scheduler_design_packet.ps_q16g.v1"

DESIGN_SEQUENCE: Tuple[str, ...] = (
    "consume_ps_q16f_preflight_report_or_summary_only",
    "require_explicit_human_decision_record_for_design_slice",
    "declare_disabled_by_default_wrapper_boundary",
    "declare_clean_tree_and_preflight_recheck_before_any_future_run",
    "declare_single_run_lock_and_no_overlap_policy",
    "declare_status_first_failure_visibility_policy",
    "declare_disable_rollback_before_any_enablement",
    "declare_no_scheduler_enablement_in_ps_q16g",
    "declare_no_runtime_write_automation_in_ps_q16g",
    "declare_no_command_generation_in_ps_q16g",
    "return_design_packet_only",
)

RUNBOOK_STEPS: Tuple[str, ...] = (
    "future_slice_must_recheck_clean_tree_and_ps_q16f_preflight",
    "future_slice_must_start_disabled_by_default",
    "future_slice_must_use_operator_shell_only_entrypoint",
    "future_slice_must_use_single_run_lock_and_skip_on_overlap",
    "future_slice_must_call_bounded_manual_refresh_runner_only_after_gates",
    "future_slice_must_write_status_on_success_and_failure",
    "future_slice_must_keep_warroom_ui_read_only_observer",
    "future_slice_must_have_disable_rollback_before_enablement",
    "future_slice_must_require_separate_human_enablement_record",
)

FORBIDDEN_REQUEST_NAMES: Tuple[str, ...] = (
    "request_scheduler_enable",
    "request_scheduled_loop_enable",
    "request_runtime_artifact_write_automation_enable",
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
class PredictionWarRoomDisabledSchedulerDesignPacket:
    design_version: str
    design_id: str
    design_state: str
    design_sequence: Tuple[str, ...] = DESIGN_SEQUENCE
    runbook_steps: Tuple[str, ...] = RUNBOOK_STEPS
    preflight_report_supplied: bool = False
    preflight_passed: bool = False
    human_decision_record_present: bool = False
    human_decision_source: str = ""
    latest_prediction_run_id: str = ""
    latest_prediction_generated_at: str = ""
    latest_prediction_age_sec: int | None = None
    producer_status_state: str = ""
    producer_status_last_success_at: str = ""
    producer_status_last_success_generated_at: str = ""
    producer_status_last_prediction_run_id: str = ""
    recommended_cadence_sec: int = RECOMMENDED_CADENCE_SEC
    minimum_cadence_sec: int = MINIMUM_CADENCE_SEC
    maximum_cadence_sec: int = MAXIMUM_CADENCE_SEC
    freshness_max_age_sec: int = FRESHNESS_MAX_AGE_SEC
    latest_prediction_artifact_relative_path: str = LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH
    producer_status_artifact_relative_path: str = PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH
    requested_forbidden_flags: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    ready_for_disabled_scheduler_wrapper_slice: bool = False
    ready_for_scheduler_enablement: bool = False
    ready_for_runtime_artifact_write_automation: bool = False
    scheduler_enablement_command_generated: bool = False
    scheduler_registration_performed: bool = False
    scheduled_loop_enabled: bool = False
    runtime_artifact_write_automation_enabled: bool = False
    latest_prediction_refresh_performed_by_this_design: bool = False
    status_artifact_write_performed_by_this_design: bool = False
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
    design_only: bool = True
    read_only: bool = True
    non_executing: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "design_version": self.design_version,
            "design_id": self.design_id,
            "design_state": self.design_state,
            "design_sequence": list(self.design_sequence),
            "runbook_steps": list(self.runbook_steps),
            "preflight_report_supplied": self.preflight_report_supplied,
            "preflight_passed": self.preflight_passed,
            "human_decision_record_present": self.human_decision_record_present,
            "human_decision_source": self.human_decision_source,
            "latest_prediction_run_id": self.latest_prediction_run_id,
            "latest_prediction_generated_at": self.latest_prediction_generated_at,
            "latest_prediction_age_sec": self.latest_prediction_age_sec,
            "producer_status_state": self.producer_status_state,
            "producer_status_last_success_at": self.producer_status_last_success_at,
            "producer_status_last_success_generated_at": self.producer_status_last_success_generated_at,
            "producer_status_last_prediction_run_id": self.producer_status_last_prediction_run_id,
            "recommended_cadence_sec": self.recommended_cadence_sec,
            "minimum_cadence_sec": self.minimum_cadence_sec,
            "maximum_cadence_sec": self.maximum_cadence_sec,
            "freshness_max_age_sec": self.freshness_max_age_sec,
            "latest_prediction_artifact_relative_path": self.latest_prediction_artifact_relative_path,
            "producer_status_artifact_relative_path": self.producer_status_artifact_relative_path,
            "requested_forbidden_flags": list(self.requested_forbidden_flags),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "ready_for_disabled_scheduler_wrapper_slice": self.ready_for_disabled_scheduler_wrapper_slice,
            "ready_for_scheduler_enablement": self.ready_for_scheduler_enablement,
            "ready_for_runtime_artifact_write_automation": self.ready_for_runtime_artifact_write_automation,
            "scheduler_enablement_command_generated": self.scheduler_enablement_command_generated,
            "scheduler_registration_performed": self.scheduler_registration_performed,
            "scheduled_loop_enabled": self.scheduled_loop_enabled,
            "runtime_artifact_write_automation_enabled": self.runtime_artifact_write_automation_enabled,
            "latest_prediction_refresh_performed_by_this_design": self.latest_prediction_refresh_performed_by_this_design,
            "status_artifact_write_performed_by_this_design": self.status_artifact_write_performed_by_this_design,
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
            "design_only": self.design_only,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
        }


def build_prediction_warroom_disabled_scheduler_design_packet(
    *,
    ps_q16f_preflight_report: Mapping[str, Any] | Any | None = None,
    human_decision_record_present: bool = False,
    human_decision_source: str = "",
    request_scheduler_enable: bool = False,
    request_scheduled_loop_enable: bool = False,
    request_runtime_artifact_write_automation_enable: bool = False,
    request_generate_enablement_command: bool = False,
    request_warroom_ui_trigger: bool = False,
    request_parameter_apply: bool = False,
    request_parameter_staging_write: bool = False,
    request_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> PredictionWarRoomDisabledSchedulerDesignPacket:
    """Return a design-only packet for a future disabled scheduler wrapper slice.

    This function performs no IO, never generates an enablement command, and never enables
    a scheduler. A ready packet only means a future disabled wrapper design slice may start.
    """
    report = _as_mapping(ps_q16f_preflight_report)
    latest = _as_mapping(report.get("latest_prediction"))
    status = _as_mapping(report.get("producer_status"))
    blockers: list[str] = []
    warnings: list[str] = []
    requested = _requested_flags(
        request_scheduler_enable=request_scheduler_enable,
        request_scheduled_loop_enable=request_scheduled_loop_enable,
        request_runtime_artifact_write_automation_enable=request_runtime_artifact_write_automation_enable,
        request_generate_enablement_command=request_generate_enablement_command,
        request_warroom_ui_trigger=request_warroom_ui_trigger,
        request_parameter_apply=request_parameter_apply,
        request_parameter_staging_write=request_parameter_staging_write,
        request_approval_or_ledger_or_autotrade_or_broker=request_approval_or_ledger_or_autotrade_or_broker,
    )
    for item in requested:
        blockers.append("forbidden_request_in_ps_q16g:" + item)
    if not report:
        blockers.append("ps_q16f_preflight_report_required")
    elif report.get("preflight_passed") is not True or report.get("ok") is not True:
        blockers.append("ps_q16f_preflight_not_passed")
    if report and report.get("ready_for_scheduler_enablement") is not False:
        blockers.append("ps_q16f_ready_for_scheduler_enablement_must_remain_false")
    if report and report.get("scheduler_registration_performed") is not False:
        blockers.append("ps_q16f_scheduler_registration_must_remain_false")
    if report and report.get("scheduled_loop_enabled") is not False:
        blockers.append("ps_q16f_scheduled_loop_must_remain_false")
    if not human_decision_record_present:
        blockers.append("human_decision_record_required_for_ps_q16g_design")
    if human_decision_record_present and not str(human_decision_source or "").strip():
        warnings.append("human_decision_source_not_supplied")
    if _int(latest.get("age_sec")) > FRESHNESS_MAX_AGE_SEC:
        blockers.append("latest_prediction_too_stale_for_disabled_scheduler_design")
    for item in report.get("warning_reasons", []) if isinstance(report.get("warning_reasons", []), list) else []:
        warnings.append("preflight_warning:" + str(item))
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = bool(not unique_blockers)
    state = "disabled_scheduler_design_ready_for_future_wrapper_slice" if ready else "disabled_scheduler_design_blocked"
    return PredictionWarRoomDisabledSchedulerDesignPacket(
        design_version=DISABLED_SCHEDULER_DESIGN_PACKET_VERSION,
        design_id=f"{DISABLED_SCHEDULER_DESIGN_PACKET_VERSION}:{state}",
        design_state=state,
        preflight_report_supplied=bool(report),
        preflight_passed=bool(report.get("preflight_passed") is True and report.get("ok") is True),
        human_decision_record_present=bool(human_decision_record_present),
        human_decision_source=str(human_decision_source or ""),
        latest_prediction_run_id=str(latest.get("prediction_run_id") or ""),
        latest_prediction_generated_at=str(latest.get("generated_at") or ""),
        latest_prediction_age_sec=latest.get("age_sec") if isinstance(latest.get("age_sec"), int) else None,
        producer_status_state=str(status.get("producer_state") or ""),
        producer_status_last_success_at=str(status.get("last_success_at") or ""),
        producer_status_last_success_generated_at=str(status.get("last_success_generated_at") or ""),
        producer_status_last_prediction_run_id=str(status.get("last_prediction_run_id") or ""),
        requested_forbidden_flags=requested,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        ready_for_disabled_scheduler_wrapper_slice=ready,
    )
