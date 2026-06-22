# path: ./tools/check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool.py
# desc: PS-Q16O disabled operator-shell CLI dry-run report tool. It prints a Q16N skeleton decision only; it never reads D-hot, creates locks, invokes refresh runners, writes status/runtime artifacts, registers schedulers, triggers WarRoom UI, mutates parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_disabled_operator_shell_once_run_cli_skeleton import (  # noqa: E402
    DISABLED_OPERATOR_SHELL_ONCE_RUN_CLI_SKELETON_VERSION,
    build_prediction_warroom_disabled_operator_shell_once_run_cli_skeleton,
)
from btcts.apps.operator_ui.components.prediction_warroom_guarded_once_run_execution_plan_packet import LOCK_RELATIVE_PATH  # noqa: E402
from btcts.apps.operator_ui.components.prediction_warroom_guarded_once_run_implementation_skeleton import (  # noqa: E402
    GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_VERSION,
)

CHECKER = "ps_q16o_disabled_operator_shell_cli_dry_run_report_tool"
CHECKER_VERSION = "check_phase4a_prediction_system_ps_q16o_disabled_operator_shell_cli_dry_run_report_tool.v1"


def _synthetic_ps_q16m_skeleton(*, ready: bool = True, unsafe_write: bool = False) -> dict[str, Any]:
    return {
        "skeleton_version": GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_VERSION,
        "ready_for_future_disabled_once_run_operator_shell_cli_slice": ready,
        "skeleton_only": True,
        "read_only": True,
        "non_executing": True,
        "lock_relative_path": LOCK_RELATIVE_PATH,
        "ready_for_execution_enablement": False,
        "implementation_enabled": False,
        "execution_enabled": False,
        "manual_refresh_invoked_by_this_skeleton": False,
        "latest_prediction_refresh_performed_by_this_skeleton": False,
        "status_artifact_write_performed_by_this_skeleton": bool(unsafe_write),
        "runtime_artifact_write_performed_by_this_skeleton": False,
        "lock_file_created_by_this_skeleton": False,
        "lock_file_deleted_by_this_skeleton": False,
        "scheduler_enabled": False,
        "os_scheduler_registration_performed": False,
        "scheduled_loop_enabled": False,
        "warroom_ui_trigger_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "freshness_bypass_added": False,
        "force_ready_added": False,
    }


def _safe_flags(decision: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "dry_run_report_only_true": True,
        "cli_skeleton_only_true": decision.get("cli_skeleton_only") is True,
        "dry_run_wrapper_only_true": decision.get("dry_run_wrapper_only") is True,
        "operator_shell_only_true": decision.get("operator_shell_only") is True,
        "read_only_true": decision.get("read_only") is True,
        "non_executing_true": decision.get("non_executing") is True,
        "cli_enabled_false": decision.get("cli_enabled") is False,
        "implementation_enabled_false": decision.get("implementation_enabled") is False,
        "execution_enabled_false": decision.get("execution_enabled") is False,
        "manual_refresh_invoked_false": decision.get("manual_refresh_invoked_by_this_cli_skeleton") is False,
        "latest_prediction_refresh_performed_false": decision.get("latest_prediction_refresh_performed_by_this_cli_skeleton") is False,
        "status_artifact_write_performed_false": decision.get("status_artifact_write_performed_by_this_cli_skeleton") is False,
        "runtime_artifact_write_performed_false": decision.get("runtime_artifact_write_performed_by_this_cli_skeleton") is False,
        "lock_file_created_false": decision.get("lock_file_created_by_this_cli_skeleton") is False,
        "lock_file_deleted_false": decision.get("lock_file_deleted_by_this_cli_skeleton") is False,
        "scheduler_enabled_false": decision.get("scheduler_enabled") is False,
        "os_scheduler_registration_performed_false": decision.get("os_scheduler_registration_performed") is False,
        "scheduled_loop_enabled_false": decision.get("scheduled_loop_enabled") is False,
        "warroom_ui_trigger_enabled_false": decision.get("warroom_ui_trigger_enabled") is False,
        "autotrade_trigger_allowed_false": decision.get("autotrade_trigger_allowed") is False,
        "broker_private_api_allowed_false": decision.get("broker_private_api_allowed") is False,
        "ledger_append_allowed_false": decision.get("ledger_append_allowed") is False,
        "parameter_apply_allowed_false": decision.get("parameter_apply_allowed") is False,
        "parameter_staging_write_allowed_false": decision.get("parameter_staging_write_allowed") is False,
        "freshness_bypass_added_false": decision.get("freshness_bypass_added") is False,
        "force_ready_added_false": decision.get("force_ready_added") is False,
    }


def build_report(
    *,
    human_cli_skeleton_record_present: bool = True,
    human_cli_skeleton_source: str = "ps_q16o_disabled_operator_shell_cli_dry_run_report_tool",
    simulate_unready_ps_q16m_skeleton: bool = False,
    simulate_unsafe_ps_q16m_write: bool = False,
    request_enable_cli: bool = False,
    request_execute_cli: bool = False,
    request_execute_once_run: bool = False,
    request_execute_manual_refresh: bool = False,
    request_status_artifact_write: bool = False,
    request_lock_file_create: bool = False,
    request_scheduler_enable: bool = False,
    request_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> dict[str, Any]:
    """Build a stdout-safe Q16N decision report without reading, writing, locking, or executing anything."""
    decision = build_prediction_warroom_disabled_operator_shell_once_run_cli_skeleton(
        ps_q16m_implementation_skeleton_packet=_synthetic_ps_q16m_skeleton(
            ready=not simulate_unready_ps_q16m_skeleton,
            unsafe_write=simulate_unsafe_ps_q16m_write,
        ),
        human_cli_skeleton_record_present=human_cli_skeleton_record_present,
        human_cli_skeleton_source=human_cli_skeleton_source,
        request_enable_cli=request_enable_cli,
        request_execute_cli=request_execute_cli,
        request_execute_once_run=request_execute_once_run,
        request_execute_manual_refresh=request_execute_manual_refresh,
        request_status_artifact_write=request_status_artifact_write,
        request_lock_file_create=request_lock_file_create,
        request_scheduler_enable=request_scheduler_enable,
        request_approval_or_ledger_or_autotrade_or_broker=request_approval_or_ledger_or_autotrade_or_broker,
    ).to_dict()
    safe = _safe_flags(decision)
    ok = bool(decision.get("blocker_count") == 0 and all(safe.values()))
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": CHECKER_VERSION,
        "stage": "disabled_operator_shell_cli_dry_run_report_only",
        "dry_run_report_only": True,
        "no_hot_data_read": True,
        "no_runtime_write": True,
        "no_lock_io": True,
        "no_refresh_invocation": True,
        "no_scheduler_or_ui_trigger": True,
        "q16n_skeleton_version": DISABLED_OPERATOR_SHELL_ONCE_RUN_CLI_SKELETON_VERSION,
        "decision": decision,
        "safe_flags": safe,
        "blocked_reasons": list(decision.get("blocked_reasons") or []),
        "warning_reasons": list(decision.get("warning_reasons") or []),
        "operator_note": "PS-Q16O prints the Q16N skeleton decision only. It does not read D-hot, create locks, invoke refresh, write status/runtime artifacts, register schedulers, trigger WarRoom UI, or enable AutoTrade/broker/ledger/parameters.",
        "next_action": "review_dry_run_report_only; separate explicit slice required before any execution/write/lock behavior",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q16O disabled Q16N skeleton dry-run report tool")
    parser.add_argument("--simulate-unready-ps-q16m-skeleton", action="store_true")
    parser.add_argument("--simulate-unsafe-ps-q16m-write", action="store_true")
    parser.add_argument("--missing-human-record", action="store_true")
    parser.add_argument("--request-enable-cli", action="store_true")
    parser.add_argument("--request-execute-cli", action="store_true")
    parser.add_argument("--request-execute-once-run", action="store_true")
    parser.add_argument("--request-execute-manual-refresh", action="store_true")
    parser.add_argument("--request-status-artifact-write", action="store_true")
    parser.add_argument("--request-lock-file-create", action="store_true")
    parser.add_argument("--request-scheduler-enable", action="store_true")
    parser.add_argument("--request-approval-ledger-autotrade-broker", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    payload = build_report(
        human_cli_skeleton_record_present=not bool(args.missing_human_record),
        simulate_unready_ps_q16m_skeleton=bool(args.simulate_unready_ps_q16m_skeleton),
        simulate_unsafe_ps_q16m_write=bool(args.simulate_unsafe_ps_q16m_write),
        request_enable_cli=bool(args.request_enable_cli),
        request_execute_cli=bool(args.request_execute_cli),
        request_execute_once_run=bool(args.request_execute_once_run),
        request_execute_manual_refresh=bool(args.request_execute_manual_refresh),
        request_status_artifact_write=bool(args.request_status_artifact_write),
        request_lock_file_create=bool(args.request_lock_file_create),
        request_scheduler_enable=bool(args.request_scheduler_enable),
        request_approval_or_ledger_or_autotrade_or_broker=bool(args.request_approval_ledger_autotrade_broker),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
