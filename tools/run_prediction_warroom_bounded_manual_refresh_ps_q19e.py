# path: ./tools/run_prediction_warroom_bounded_manual_refresh_ps_q19e.py
# desc: PS-Q19E guarded non-UI manual refresh entrypoint for WarRoom latest prediction observation. Default dry-run/no-write; explicit ACK required to invoke existing Q16D bounded manual refresh runner. Scheduled loop remains disabled.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from btcts.apps.operator_ui.components.prediction_warroom_bounded_manual_refresh_runner import (  # noqa: E402
    PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION,
    build_prediction_warroom_bounded_manual_refresh_runner,
)
from btcts.apps.operator_ui.components.prediction_warroom_l4_latest_adapter import (  # noqa: E402
    DEFAULT_HOT_LATEST_ROOT_HINT,
)
from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_contract import (  # noqa: E402
    LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH,
    PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
)

PS_Q19E_NON_UI_REFRESH_VERSION = "prediction_warroom.ps_q19e_non_ui_manual_or_scheduled_refresh_guarded.v1"
PS_Q19E_MANUAL_REFRESH_ACK = "PS_Q19E_RUN_BOUNDED_NON_UI_MANUAL_REFRESH"

ActualExportRunner = Callable[..., Any]


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _manual_execution_authorized(*, execute_manual_refresh: bool, ack: str, request_scheduled_refresh: bool) -> bool:
    return bool(execute_manual_refresh and ack == PS_Q19E_MANUAL_REFRESH_ACK and not request_scheduled_refresh)


def build_ps_q19e_non_ui_refresh_request_packet(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    execute_manual_refresh: bool = False,
    ack: str = "",
    request_scheduled_refresh: bool = False,
    allow_guard_test_root: bool = False,
    actual_export_runner: ActualExportRunner | None = None,
) -> dict[str, Any]:
    """Build/run the PS-Q19E guarded refresh request.

    Default is a dry-run/no-write packet.  A real bounded manual refresh can only
    occur when execute_manual_refresh is true and the exact ACK is supplied.  A
    scheduled refresh request is explicitly represented but remains disabled.
    """
    explicit_ack_matched = ack == PS_Q19E_MANUAL_REFRESH_ACK
    manual_authorized = _manual_execution_authorized(
        execute_manual_refresh=execute_manual_refresh,
        ack=ack,
        request_scheduled_refresh=request_scheduled_refresh,
    )
    requested_but_not_authorized = bool(execute_manual_refresh and not manual_authorized)
    scheduled_blockers: list[str] = []
    if request_scheduled_refresh:
        scheduled_blockers.append("scheduled_refresh_loop_not_enabled_in_ps_q19e")

    runner = build_prediction_warroom_bounded_manual_refresh_runner(
        hot_latest_root_hint=str(hot_latest_root_hint),
        operator_acknowledged=explicit_ack_matched,
        execute_manual_refresh=manual_authorized,
        allow_actual_read=manual_authorized,
        allow_prediction_build=manual_authorized,
        allow_export_preflight=manual_authorized,
        allow_latest_payload_export=manual_authorized,
        allow_runtime_artifact_write=manual_authorized,
        allow_status_artifact_write=manual_authorized,
        execute_status_artifact_write=manual_authorized,
        allow_guard_test_root=allow_guard_test_root,
        actual_export_runner=actual_export_runner,
        request_scheduler_enable=bool(request_scheduled_refresh),
        request_warroom_ui_trigger=False,
        request_parameter_apply=False,
        request_parameter_staging_write=False,
        request_approval_or_ledger_or_autotrade_or_broker=False,
    ).to_dict()

    blocked_reasons = list(dict.fromkeys([*scheduled_blockers, *[str(item) for item in runner.get("blocked_reasons", [])]]))
    warning_reasons = list(dict.fromkeys([str(item) for item in runner.get("warning_reasons", [])]))
    latest_written = bool(runner.get("latest_prediction_artifact_written"))
    status_written = bool(runner.get("status_artifact_written"))
    dry_run_no_write = bool(not execute_manual_refresh and not request_scheduled_refresh and not latest_written and not status_written)
    executed_ok = bool(manual_authorized and latest_written and status_written and not blocked_reasons)
    blocked_ok = bool(request_scheduled_refresh and not latest_written and not runner.get("actual_export_runner_invoked"))
    ok = bool(dry_run_no_write or executed_ok or blocked_ok)
    if requested_but_not_authorized:
        ok = False

    if executed_ok:
        request_state = "bounded_manual_refresh_executed"
    elif dry_run_no_write:
        request_state = "dry_run_no_write"
    elif request_scheduled_refresh:
        request_state = "scheduled_refresh_requested_but_disabled"
    else:
        request_state = "manual_refresh_blocked"

    packet: dict[str, Any] = {
        "ok": ok,
        "ps_q19e_version": PS_Q19E_NON_UI_REFRESH_VERSION,
        "request_state": request_state,
        "hot_latest_root_hint": str(hot_latest_root_hint),
        "latest_prediction_artifact_relative_path": LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH,
        "producer_status_artifact_relative_path": PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
        "q16d_runner_version": PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION,
        "q16d_runner_state": str(runner.get("runner_state") or ""),
        "q16d_runner_packet": runner,
        "explicit_ack_required": True,
        "explicit_ack_matched": explicit_ack_matched,
        "execute_manual_refresh_requested": bool(execute_manual_refresh),
        "manual_execution_authorized": manual_authorized,
        "request_scheduled_refresh": bool(request_scheduled_refresh),
        "scheduled_refresh_declared": True,
        "scheduled_loop_enabled": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "warroom_ui_trigger_enabled": False,
        "actual_export_runner_invoked": bool(runner.get("actual_export_runner_invoked")),
        "latest_prediction_artifact_written": latest_written,
        "status_artifact_written": status_written,
        "latest_prediction_artifact_path": str(runner.get("latest_prediction_artifact_path") or ""),
        "status_artifact_path": str(runner.get("status_artifact_path") or ""),
        "prediction_run_id": str(runner.get("prediction_run_id") or ""),
        "generated_at": str(runner.get("generated_at") or ""),
        "blocked_reasons": blocked_reasons,
        "warning_reasons": warning_reasons,
        "default_dry_run_no_write": dry_run_no_write,
        "non_ui_runner_only": True,
        "bounded_manual_run_only": manual_authorized,
        "manual_runtime_artifact_write_gate_declared": True,
        "runtime_artifact_write_performed_by_this_request": latest_written,
        "status_artifact_write_performed_by_this_request": status_written,
        "runtime_behavior_changed_by_patch": False,
        "collector_data_collection_changed": False,
        "ui_triggered_runner_execution": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "authorization_grant_requested": False,
        "autotrade_trigger_enabled": False,
    }
    return packet


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q19E guarded non-UI latest prediction refresh request")
    parser.add_argument("--root", default=DEFAULT_HOT_LATEST_ROOT_HINT, help="Hot latest root. Default: D:/btc_ts_hot")
    parser.add_argument("--execute-manual-refresh", action="store_true", help="Run one bounded non-UI manual refresh if ACK matches.")
    parser.add_argument("--ack", default="", help=f"Required ACK for execution: {PS_Q19E_MANUAL_REFRESH_ACK}")
    parser.add_argument("--request-scheduled-refresh", action="store_true", help="Represent scheduled refresh request. It remains disabled in PS-Q19E.")
    parser.add_argument("--allow-guard-test-root", action="store_true", help="Allow non-D root for tests only.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    packet = build_ps_q19e_non_ui_refresh_request_packet(
        hot_latest_root_hint=str(args.root),
        execute_manual_refresh=bool(args.execute_manual_refresh),
        ack=str(args.ack or ""),
        request_scheduled_refresh=bool(args.request_scheduled_refresh),
        allow_guard_test_root=bool(args.allow_guard_test_root),
    )
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if packet.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
