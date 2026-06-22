# path: ./tools/check_phase4a_prediction_system_ps_q16j_operator_shell_once_run_dry_run_cli.py
# desc: PS-Q16J operator-shell once-run dry-run CLI. It reads/observes D-hot preflight/status/lock state read-only and prints the PS-Q16I disabled once-run decision; it never executes refresh, writes status/runtime artifacts, creates locks, registers schedulers, enables loops, triggers WarRoom UI, mutates parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_disabled_once_run_checker import (  # noqa: E402
    DISABLED_ONCE_RUN_CHECKER_VERSION,
    build_prediction_warroom_disabled_once_run_checker,
)
from btcts.apps.operator_ui.components.prediction_warroom_disabled_scheduler_design_packet import (  # noqa: E402
    build_prediction_warroom_disabled_scheduler_design_packet,
)
from btcts.apps.operator_ui.components.prediction_warroom_disabled_scheduler_wrapper_skeleton import (  # noqa: E402
    DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION,
    build_prediction_warroom_disabled_scheduler_wrapper_skeleton,
)
from check_phase4a_prediction_system_ps_q16f_scheduler_enablement_preflight import (  # noqa: E402
    HOT_ROOT,
    build_report as build_ps_q16f_preflight_report,
)

CHECKER = "ps_q16j_operator_shell_once_run_dry_run_cli"
LOCK_RELATIVE_PATH = "prediction/status/non_ui_scheduled_producer.lock"
PreflightBuilder = Callable[..., Mapping[str, Any]]


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _utc_now() -> str:
    return _format_utc(datetime.now(timezone.utc))


def _lock_observation(*, hot_root: str) -> dict[str, Any]:
    lock_path = Path(str(hot_root).rstrip("\\/")) / LOCK_RELATIVE_PATH
    exists = lock_path.exists()
    stat = lock_path.stat() if exists else None
    return {
        "lock_relative_path": LOCK_RELATIVE_PATH,
        "lock_path": str(lock_path),
        "lock_present": bool(exists),
        "lock_reason": "d_hot_lock_file_present" if exists else "d_hot_lock_file_absent",
        "lock_size_bytes": int(stat.st_size) if stat is not None else None,
        "lock_mtime_utc": _format_utc(datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)) if stat is not None else "",
        "lock_read_attempted": False,
        "lock_write_attempted": False,
        "lock_create_attempted": False,
        "lock_delete_attempted": False,
    }


def _status_observation(preflight: Mapping[str, Any]) -> dict[str, Any]:
    status = _as_mapping(preflight.get("producer_status"))
    ready = bool(
        preflight.get("ok") is True
        and preflight.get("preflight_passed") is True
        and status.get("panel_state") == "producer_status_panel_loaded"
        and status.get("payload_decode_succeeded") is True
        and status.get("producer_enabled") is False
        and status.get("scheduler_enabled") is False
        and int(status.get("last_blocker_count") or 0) == 0
        and bool(status.get("last_success_at"))
    )
    return {
        "status_ready": ready,
        "status_artifact_relative_path": status.get("status_artifact_relative_path"),
        "panel_state": status.get("panel_state"),
        "payload_decode_succeeded": status.get("payload_decode_succeeded"),
        "last_success_at": status.get("last_success_at") or "",
        "last_success_generated_at": status.get("last_success_generated_at") or "",
        "last_prediction_run_id": status.get("last_prediction_run_id") or "",
        "last_blocker_count": status.get("last_blocker_count"),
        "producer_enabled": status.get("producer_enabled"),
        "scheduler_enabled": status.get("scheduler_enabled"),
        "status_read_via_ps_q16f_preflight": True,
        "status_write_attempted": False,
    }


def _safe_flags(decision: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "dry_run_only_true": True,
        "read_only_true": decision.get("read_only") is True,
        "non_executing_true": decision.get("non_executing") is True,
        "wrapper_enabled_false": decision.get("wrapper_enabled") is False,
        "scheduler_enabled_false": decision.get("scheduler_enabled") is False,
        "os_scheduler_registration_performed_false": decision.get("os_scheduler_registration_performed") is False,
        "scheduled_loop_enabled_false": decision.get("scheduled_loop_enabled") is False,
        "enablement_command_generated_false": decision.get("enablement_command_generated") is False,
        "manual_refresh_invoked_false": decision.get("manual_refresh_invoked_by_this_checker") is False,
        "latest_prediction_refresh_performed_false": decision.get("latest_prediction_refresh_performed_by_this_checker") is False,
        "status_artifact_write_performed_false": decision.get("status_artifact_write_performed_by_this_checker") is False,
        "lock_file_created_false": decision.get("lock_file_created_by_this_checker") is False,
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
    hot_root: str = HOT_ROOT,
    preflight_builder: PreflightBuilder = build_ps_q16f_preflight_report,
    lock_observation_builder: Callable[..., Mapping[str, Any]] | None = None,
    require_clean_tree: bool = True,
    allow_guard_test_root: bool = False,
) -> dict[str, Any]:
    """Build a read-only operator-shell dry-run report for the disabled once-run path."""
    preflight = dict(
        preflight_builder(
            hot_root=str(hot_root),
            require_clean_tree=require_clean_tree,
            human_approval_record_present=True,
            allow_guard_test_root=allow_guard_test_root,
        )
    )
    design_packet = build_prediction_warroom_disabled_scheduler_design_packet(
        ps_q16f_preflight_report=preflight,
        human_decision_record_present=True,
        human_decision_source="ps_q16j_operator_shell_dry_run_cli",
    ).to_dict()
    skeleton_packet = build_prediction_warroom_disabled_scheduler_wrapper_skeleton(
        ps_q16g_design_packet=design_packet,
        human_wrapper_skeleton_record_present=True,
        human_wrapper_skeleton_source="ps_q16j_operator_shell_dry_run_cli",
    ).to_dict()
    lock_builder = lock_observation_builder or _lock_observation
    lock = dict(lock_builder(hot_root=str(hot_root)))
    status = _status_observation(preflight)
    decision = build_prediction_warroom_disabled_once_run_checker(
        ps_q16h_wrapper_skeleton_packet=skeleton_packet,
        ps_q16f_preflight_report=preflight,
        supplied_lock_observation=lock,
        supplied_status_observation=status,
    ).to_dict()
    safe = _safe_flags(decision)
    ok = bool(decision.get("blocker_count") == 0 and all(safe.values()))
    return {
        "ok": ok,
        "checker": CHECKER,
        "checker_version": DISABLED_ONCE_RUN_CHECKER_VERSION,
        "stage": "operator_shell_once_run_dry_run_read_only",
        "observed_at_utc": _utc_now(),
        "hot_root": str(hot_root),
        "dry_run_only": True,
        "decision": decision,
        "preflight_summary": {
            "ok": preflight.get("ok"),
            "preflight_passed": preflight.get("preflight_passed"),
            "git_status_short": preflight.get("git_status_short"),
            "latest_prediction": preflight.get("latest_prediction"),
            "producer_status": preflight.get("producer_status"),
            "blocked_reasons": preflight.get("blocked_reasons"),
            "warning_reasons": preflight.get("warning_reasons"),
        },
        "design_summary": {
            "design_state": design_packet.get("design_state"),
            "ready_for_disabled_scheduler_wrapper_slice": design_packet.get("ready_for_disabled_scheduler_wrapper_slice"),
            "ready_for_scheduler_enablement": design_packet.get("ready_for_scheduler_enablement"),
            "scheduler_registration_performed": design_packet.get("scheduler_registration_performed"),
            "scheduled_loop_enabled": design_packet.get("scheduled_loop_enabled"),
        },
        "skeleton_summary": {
            "skeleton_version": DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION,
            "skeleton_state": skeleton_packet.get("skeleton_state"),
            "ready_for_future_disabled_operator_shell_wrapper_implementation": skeleton_packet.get("ready_for_future_disabled_operator_shell_wrapper_implementation"),
            "wrapper_enabled": skeleton_packet.get("wrapper_enabled"),
            "scheduler_enabled": skeleton_packet.get("scheduler_enabled"),
            "os_scheduler_registration_performed": skeleton_packet.get("os_scheduler_registration_performed"),
            "scheduled_loop_enabled": skeleton_packet.get("scheduled_loop_enabled"),
        },
        "lock_observation": lock,
        "status_observation": status,
        "safe_flags": safe,
        "blocked_reasons": list(decision.get("blocked_reasons") or []),
        "warning_reasons": list(dict.fromkeys(list(preflight.get("warning_reasons") or []) + list(decision.get("warning_reasons") or []))),
        "operator_note": "PS-Q16J is a read-only dry-run CLI. It prints decisions only and does not execute refresh, write status, create locks, register schedulers, or enable automation.",
        "next_action": "review_dry_run_decision_only; separate explicit slice required before any execution/write/lock/scheduler behavior",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q16J read-only operator-shell once-run dry-run CLI")
    parser.add_argument("--hot-root", default=HOT_ROOT)
    parser.add_argument("--allow-dirty", action="store_true", help="Allow dirty tree for diagnostics only; default requires Q16F clean-tree preflight.")
    parser.add_argument("--allow-guard-test-root", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    payload = build_report(
        hot_root=str(args.hot_root),
        require_clean_tree=not bool(args.allow_dirty),
        allow_guard_test_root=bool(args.allow_guard_test_root),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
