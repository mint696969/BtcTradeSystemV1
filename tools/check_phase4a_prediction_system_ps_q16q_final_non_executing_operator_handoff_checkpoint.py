# path: ./tools/check_phase4a_prediction_system_ps_q16q_final_non_executing_operator_handoff_checkpoint.py
# desc: PS-Q16Q final non-executing operator handoff checkpoint. It consumes a PS-Q16P handoff report and returns a ledger-free readiness summary only; it never reads D-hot, creates locks, invokes refresh runners, writes status/runtime artifacts, appends ledgers, registers schedulers, triggers WarRoom UI, mutates parameters, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

from collections.abc import Callable
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard import (
    CHECKER_VERSION as PS_Q16P_CHECKER_VERSION,
    build_report as build_ps_q16p_report,
)

CHECKER = "ps_q16q_final_non_executing_operator_handoff_checkpoint"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q16q_final_non_executing_operator_handoff_checkpoint.v1"
Q16P_REPORT_BUILDER = "check_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard.build_report"
ReportBuilder = Callable[[], Mapping[str, Any]]


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _q16p_boundary_failures(report: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    if report.get("checker_version") != PS_Q16P_CHECKER_VERSION:
        failures.append("q16p_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q16p_report_not_ok")
    for key in (
        "dry_run_report_integration_only",
        "operator_handoff_summary_only",
        "no_hot_data_read",
        "no_runtime_write",
        "no_lock_io",
        "no_refresh_invocation",
        "no_scheduler_or_ui_trigger",
    ):
        if report.get(key) is not True:
            failures.append(f"q16p_report_{key}_must_remain_true")
    for key in (
        "ready_for_execution_enablement",
        "cli_enabled",
        "implementation_enabled",
        "execution_enabled",
        "manual_refresh_invoked",
        "latest_prediction_refresh_performed",
        "status_artifact_write_performed",
        "runtime_artifact_write_performed",
        "lock_file_created",
        "lock_file_deleted",
        "scheduler_enabled",
        "os_scheduler_registration_performed",
        "scheduled_loop_enabled",
        "enablement_command_generated",
        "warroom_ui_trigger_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        if report.get(key) is not False:
            failures.append(f"q16p_report_{key}_must_remain_false")
    return failures


def build_report(
    *,
    supplied_q16p_report: Mapping[str, Any] | Any | None = None,
    q16p_report_builder: ReportBuilder = build_ps_q16p_report,
    human_final_checkpoint_record_present: bool = True,
    human_final_checkpoint_source: str = "ps_q16q_final_non_executing_operator_handoff_checkpoint",
    request_enable_cli: bool = False,
    request_execute_cli: bool = False,
    request_status_artifact_write: bool = False,
    request_lock_file_create: bool = False,
    request_scheduler_enable: bool = False,
    request_ledger_append: bool = False,
    request_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> dict[str, Any]:
    """Return a final non-executing handoff checkpoint without writing a ledger or doing runtime IO."""
    q16p_report = _as_mapping(supplied_q16p_report) or _as_mapping(q16p_report_builder())
    requested = tuple(
        name
        for name, value in {
            "request_enable_cli": request_enable_cli,
            "request_execute_cli": request_execute_cli,
            "request_status_artifact_write": request_status_artifact_write,
            "request_lock_file_create": request_lock_file_create,
            "request_scheduler_enable": request_scheduler_enable,
            "request_ledger_append": request_ledger_append,
            "request_approval_or_ledger_or_autotrade_or_broker": request_approval_or_ledger_or_autotrade_or_broker,
        }.items()
        if value
    )
    blockers = ["forbidden_request_in_ps_q16q:" + item for item in requested]
    if not human_final_checkpoint_record_present:
        blockers.append("human_final_checkpoint_record_required_for_ps_q16q")
    blockers.extend(_q16p_boundary_failures(q16p_report))
    warnings: list[str] = []
    if human_final_checkpoint_record_present and not str(human_final_checkpoint_source or "").strip():
        warnings.append("human_final_checkpoint_source_not_supplied")
    unique_blockers = list(dict.fromkeys(item for item in blockers if item))
    unique_warnings = list(dict.fromkeys(item for item in warnings if item))
    ok = bool(not unique_blockers)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "stage": "final_non_executing_operator_handoff_checkpoint_ledger_free",
        "q16p_report_builder": Q16P_REPORT_BUILDER,
        "q16p_report_checker_version": q16p_report.get("checker_version", ""),
        "q16p_report_ok": q16p_report.get("ok") is True,
        "q16p_report_stage": q16p_report.get("stage", ""),
        "q16p_ready_for_future_operator_handoff_summary_slice": q16p_report.get("ready_for_future_operator_handoff_summary_slice") is True,
        "human_final_checkpoint_record_present": bool(human_final_checkpoint_record_present),
        "human_final_checkpoint_source": str(human_final_checkpoint_source or ""),
        "requested_forbidden_flags": list(requested),
        "blocked_reasons": unique_blockers,
        "warning_reasons": unique_warnings,
        "final_handoff_checkpoint_only": True,
        "ledger_free_summary_only": True,
        "operator_review_summary_only": True,
        "no_hot_data_read": True,
        "no_runtime_write": True,
        "no_status_write": True,
        "no_ledger_append": True,
        "no_lock_io": True,
        "no_refresh_invocation": True,
        "no_scheduler_or_ui_trigger": True,
        "ready_for_human_review_checkpoint": ok,
        "ready_for_execution_enablement": False,
        "cli_enabled": False,
        "implementation_enabled": False,
        "execution_enabled": False,
        "manual_refresh_invoked": False,
        "latest_prediction_refresh_performed": False,
        "status_artifact_write_performed": False,
        "runtime_artifact_write_performed": False,
        "lock_file_created": False,
        "lock_file_deleted": False,
        "scheduler_enabled": False,
        "os_scheduler_registration_performed": False,
        "scheduled_loop_enabled": False,
        "enablement_command_generated": False,
        "warroom_ui_trigger_enabled": False,
        "approval_or_authorization_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "freshness_bypass_added": False,
        "force_ready_added": False,
        "operator_note": "PS-Q16Q is the final non-executing operator handoff checkpoint for the disabled CLI/report path. It is ledger-free and performs no D-hot reads, writes, lock IO, refresh invocation, scheduler registration, WarRoom UI trigger, AutoTrade, broker, ledger, or parameter behavior.",
        "next_action": "human_review_checkpoint_only; separate explicit approval slice required before any execution/write/lock behavior",
    }


def main() -> int:
    payload = build_report()
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
