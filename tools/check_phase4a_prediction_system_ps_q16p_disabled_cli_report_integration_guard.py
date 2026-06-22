# path: ./tools/check_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard.py
# desc: PS-Q16P disabled CLI report integration guard. It consumes a PS-Q16O dry-run report and returns an operator handoff summary only; it never reads D-hot, creates locks, invokes refresh runners, writes status/runtime artifacts, registers schedulers, triggers WarRoom UI, mutates parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

from collections.abc import Callable
import json
from typing import Any, Mapping

from check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool import (
    CHECKER_VERSION as PS_Q16O_CHECKER_VERSION,
    build_report as build_ps_q16o_report,
)

CHECKER = "ps_q16p_disabled_cli_report_integration_guard"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q16p_disabled_cli_report_integration_guard.v1"
Q16O_REPORT_BUILDER = "check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool.build_report"
ReportBuilder = Callable[[], Mapping[str, Any]]


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _decision_false_boundary_failures(decision: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    for key in (
        "ready_for_execution_enablement",
        "cli_enabled",
        "implementation_enabled",
        "execution_enabled",
        "manual_refresh_invoked_by_this_cli_skeleton",
        "latest_prediction_refresh_performed_by_this_cli_skeleton",
        "status_artifact_write_performed_by_this_cli_skeleton",
        "runtime_artifact_write_performed_by_this_cli_skeleton",
        "lock_file_created_by_this_cli_skeleton",
        "lock_file_deleted_by_this_cli_skeleton",
        "wrapper_enabled",
        "scheduler_enabled",
        "os_scheduler_registration_performed",
        "scheduled_loop_enabled",
        "enablement_command_generated",
        "warroom_ui_trigger_enabled",
        "ui_triggered_runner_execution",
        "approval_or_authorization_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "would_send_to_broker",
        "would_write_collector_state",
        "freshness_bypass_added",
        "force_ready_added",
    ):
        if decision.get(key) is not False:
            failures.append(f"q16o_decision_{key}_must_remain_false")
    for key in ("cli_skeleton_only", "dry_run_wrapper_only", "operator_shell_only", "read_only", "non_executing"):
        if decision.get(key) is not True:
            failures.append(f"q16o_decision_{key}_must_remain_true")
    return failures


def _report_boundary_failures(report: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    for key in (
        "dry_run_report_only",
        "no_hot_data_read",
        "no_runtime_write",
        "no_lock_io",
        "no_refresh_invocation",
        "no_scheduler_or_ui_trigger",
    ):
        if report.get(key) is not True:
            failures.append(f"q16o_report_{key}_must_remain_true")
    if report.get("checker_version") != PS_Q16O_CHECKER_VERSION:
        failures.append("q16o_checker_version_mismatch")
    if report.get("ok") is not True:
        failures.append("q16o_report_not_ok")
    decision = _as_mapping(report.get("decision"))
    if not decision:
        failures.append("q16o_decision_required")
    else:
        failures.extend(_decision_false_boundary_failures(decision))
    return failures


def build_report(
    *,
    supplied_q16o_report: Mapping[str, Any] | Any | None = None,
    q16o_report_builder: ReportBuilder = build_ps_q16o_report,
    human_handoff_record_present: bool = True,
    human_handoff_source: str = "ps_q16p_disabled_cli_report_integration_guard",
    request_enable_cli: bool = False,
    request_execute_cli: bool = False,
    request_status_artifact_write: bool = False,
    request_lock_file_create: bool = False,
    request_scheduler_enable: bool = False,
    request_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> dict[str, Any]:
    """Integrate a PS-Q16O dry-run report into a handoff summary without executing or writing anything."""
    q16o_report = _as_mapping(supplied_q16o_report) or _as_mapping(q16o_report_builder())
    requested = tuple(
        name
        for name, value in {
            "request_enable_cli": request_enable_cli,
            "request_execute_cli": request_execute_cli,
            "request_status_artifact_write": request_status_artifact_write,
            "request_lock_file_create": request_lock_file_create,
            "request_scheduler_enable": request_scheduler_enable,
            "request_approval_or_ledger_or_autotrade_or_broker": request_approval_or_ledger_or_autotrade_or_broker,
        }.items()
        if value
    )
    blockers = ["forbidden_request_in_ps_q16p:" + item for item in requested]
    if not human_handoff_record_present:
        blockers.append("human_handoff_record_required_for_ps_q16p")
    blockers.extend(_report_boundary_failures(q16o_report))
    warnings: list[str] = []
    if human_handoff_record_present and not str(human_handoff_source or "").strip():
        warnings.append("human_handoff_source_not_supplied")
    unique_blockers = list(dict.fromkeys(item for item in blockers if item))
    unique_warnings = list(dict.fromkeys(item for item in warnings if item))
    ok = bool(not unique_blockers)
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "stage": "disabled_cli_report_integration_guard_handoff_only",
        "q16o_report_builder": Q16O_REPORT_BUILDER,
        "q16o_report_checker_version": q16o_report.get("checker_version", ""),
        "q16o_report_ok": q16o_report.get("ok") is True,
        "q16o_report_stage": q16o_report.get("stage", ""),
        "q16o_decision_state": _as_mapping(q16o_report.get("decision")).get("cli_skeleton_state", ""),
        "q16o_ready_for_future_disabled_operator_shell_dry_run_cli_slice": _as_mapping(q16o_report.get("decision")).get("ready_for_future_disabled_operator_shell_dry_run_cli_slice") is True,
        "human_handoff_record_present": bool(human_handoff_record_present),
        "human_handoff_source": str(human_handoff_source or ""),
        "requested_forbidden_flags": list(requested),
        "blocked_reasons": unique_blockers,
        "warning_reasons": unique_warnings,
        "dry_run_report_integration_only": True,
        "operator_handoff_summary_only": True,
        "no_hot_data_read": True,
        "no_runtime_write": True,
        "no_lock_io": True,
        "no_refresh_invocation": True,
        "no_scheduler_or_ui_trigger": True,
        "ready_for_future_operator_handoff_summary_slice": ok,
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
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "freshness_bypass_added": False,
        "force_ready_added": False,
        "operator_note": "PS-Q16P integrates the PS-Q16O dry-run report into an operator handoff summary only. It performs no D-hot reads, writes, lock IO, refresh invocation, scheduler registration, WarRoom UI trigger, AutoTrade, broker, ledger, or parameter behavior.",
        "next_action": "review_handoff_summary_only; separate explicit slice required before any execution/write/lock behavior",
    }


def main() -> int:
    payload = build_report()
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
