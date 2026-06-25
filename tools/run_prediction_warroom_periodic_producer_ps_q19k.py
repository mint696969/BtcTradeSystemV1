# path: ./tools/run_prediction_warroom_periodic_producer_ps_q19k.py
# desc: PS-Q19K guarded non-UI periodic prediction producer. Default dry-run/no-write. With explicit ACK, runs bounded cycles via existing Q16D refresh runner. No scheduler install, WarRoom UI trigger, AutoTrade, broker, parameter, ledger, or daemon install.

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_bounded_manual_refresh_runner import (  # noqa: E402
    PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION,
    build_prediction_warroom_bounded_manual_refresh_runner,
)
from btcts.apps.operator_ui.components.prediction_warroom_l4_latest_adapter import (  # noqa: E402
    DEFAULT_HOT_LATEST_ROOT_HINT,
)
from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_contract import (  # noqa: E402
    LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH,
    MAXIMUM_CADENCE_SEC,
    MINIMUM_CADENCE_SEC,
    PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
    RECOMMENDED_CADENCE_SEC,
)

PS_Q19K_PERIODIC_PRODUCER_VERSION = "prediction_warroom.ps_q19k_non_ui_periodic_producer.v1"
PS_Q19K_PERIODIC_PRODUCER_ACK = "PS_Q19K_RUN_BOUNDED_PERIODIC_PREDICTION_PRODUCER"
DEFAULT_MAX_CYCLES = 1
MAX_ALLOWED_CYCLES = 288
LOCK_RELATIVE_PATH = "prediction/status/periodic_producer_ps_q19k.lock"
STOP_RELATIVE_PATH = "prediction/status/stop_periodic_producer_ps_q19k.flag"

ActualExportRunner = Callable[..., Any]
SleepFunc = Callable[[float], Any]


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _root(root: str) -> Path:
    return Path(str(root).rstrip("\\/"))


def _lock_path(root: str) -> Path:
    return _root(root) / LOCK_RELATIVE_PATH


def _stop_path(root: str) -> Path:
    return _root(root) / STOP_RELATIVE_PATH


def _valid_root(root: str, *, allow_guard_test_root: bool) -> bool:
    normalized = str(root).rstrip("\\/").lower().replace("/", "\\")
    return normalized == "d:\\btc_ts_hot" or bool(allow_guard_test_root and normalized)


def _bounded_int(value: int, *, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(value)))


def _safe_cycle_projection(cycle: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "cycle_index": cycle.get("cycle_index"),
        "runner_state": cycle.get("runner_state"),
        "latest_prediction_artifact_written": cycle.get("latest_prediction_artifact_written"),
        "status_artifact_written": cycle.get("status_artifact_written"),
        "latest_prediction_artifact_path": cycle.get("latest_prediction_artifact_path"),
        "status_artifact_path": cycle.get("status_artifact_path"),
        "prediction_run_id": cycle.get("prediction_run_id"),
        "generated_at": cycle.get("generated_at"),
        "blocker_count": cycle.get("blocker_count"),
        "warning_count": cycle.get("warning_count"),
        "blocked_reasons": list(cycle.get("blocked_reasons") or []),
        "warning_reasons": list(cycle.get("warning_reasons") or []),
        "autotrade_trigger_allowed": cycle.get("autotrade_trigger_allowed"),
        "broker_private_api_allowed": cycle.get("broker_private_api_allowed"),
        "would_send_to_broker": cycle.get("would_send_to_broker"),
    }


def build_ps_q19k_periodic_producer_packet(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    execute_periodic_producer: bool = False,
    ack: str = "",
    max_cycles: int = DEFAULT_MAX_CYCLES,
    interval_sec: int = RECOMMENDED_CADENCE_SEC,
    allow_guard_test_root: bool = False,
    actual_export_runner: ActualExportRunner | None = None,
    sleep_func: SleepFunc = time.sleep,
) -> dict[str, Any]:
    """Run a bounded foreground non-UI prediction producer only with explicit ACK.

    This is not a scheduler install and not a daemon. It runs at most max_cycles in
    the current foreground process, uses a lock file to avoid overlap, and reuses
    the existing Q16D bounded refresh runner for each cycle.
    """
    root = str(hot_latest_root_hint)
    root_valid = _valid_root(root, allow_guard_test_root=allow_guard_test_root)
    ack_matched = ack == PS_Q19K_PERIODIC_PRODUCER_ACK
    requested_cycles = int(max_cycles)
    cycles = _bounded_int(requested_cycles, lo=1, hi=MAX_ALLOWED_CYCLES)
    requested_interval = int(interval_sec)
    min_interval = 0 if allow_guard_test_root else MINIMUM_CADENCE_SEC
    interval = _bounded_int(requested_interval, lo=min_interval, hi=MAXIMUM_CADENCE_SEC)
    blockers: list[str] = []
    warnings: list[str] = []

    if not root_valid:
        blockers.append("target_root_invalid_for_ps_q19k_periodic_producer")
    if execute_periodic_producer and not ack_matched:
        blockers.append("explicit_ps_q19k_periodic_producer_ack_required")
    if requested_cycles != cycles:
        warnings.append("max_cycles_clamped_to_allowed_bounds")
    if requested_interval != interval:
        warnings.append("interval_sec_clamped_to_cadence_policy_bounds")

    dry_run = not execute_periodic_producer
    lock_path = _lock_path(root)
    stop_path = _stop_path(root)
    cycle_packets: list[dict[str, Any]] = []
    lock_created = False
    stopped_by_stop_file = False

    if dry_run:
        request_state = "dry_run_no_write"
    elif blockers:
        request_state = "periodic_producer_blocked_before_start"
    else:
        request_state = "periodic_producer_running_bounded_cycles"
        if lock_path.exists():
            blockers.append("periodic_producer_lock_exists")
            request_state = "periodic_producer_blocked_lock_exists"
        else:
            try:
                lock_path.parent.mkdir(parents=True, exist_ok=True)
                lock_path.write_text(
                    json.dumps(
                        {
                            "version": PS_Q19K_PERIODIC_PRODUCER_VERSION,
                            "started_at": _iso_now(),
                            "root": root,
                            "max_cycles": cycles,
                            "interval_sec": interval,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ) + "\n",
                    encoding="utf-8",
                )
                lock_created = True
                for cycle_index in range(cycles):
                    if stop_path.exists():
                        stopped_by_stop_file = True
                        request_state = "periodic_producer_stopped_by_stop_file"
                        break
                    result = build_prediction_warroom_bounded_manual_refresh_runner(
                        hot_latest_root_hint=root,
                        operator_acknowledged=True,
                        execute_manual_refresh=True,
                        allow_actual_read=True,
                        allow_prediction_build=True,
                        allow_export_preflight=True,
                        allow_latest_payload_export=True,
                        allow_runtime_artifact_write=True,
                        allow_status_artifact_write=True,
                        execute_status_artifact_write=True,
                        allow_guard_test_root=allow_guard_test_root,
                        actual_export_runner=actual_export_runner,
                        request_scheduler_enable=False,
                        request_warroom_ui_trigger=False,
                        request_parameter_apply=False,
                        request_parameter_staging_write=False,
                        request_approval_or_ledger_or_autotrade_or_broker=False,
                    ).to_dict()
                    result = dict(result)
                    result["cycle_index"] = cycle_index
                    cycle_packets.append(result)
                    if result.get("blocked_reasons"):
                        request_state = "periodic_producer_cycle_blocked"
                        break
                    if cycle_index < cycles - 1:
                        sleep_func(float(interval))
                if request_state == "periodic_producer_running_bounded_cycles":
                    request_state = "periodic_producer_completed_bounded_cycles"
            except Exception as exc:  # noqa: BLE001 - fail closed and expose diagnostic
                blockers.append("periodic_producer_runtime_exception:" + exc.__class__.__name__)
                warnings.append(str(exc))
                request_state = "periodic_producer_failed_closed"
            finally:
                if lock_created:
                    try:
                        lock_path.unlink(missing_ok=True)
                    except Exception as exc:  # noqa: BLE001
                        warnings.append("periodic_producer_lock_cleanup_failed:" + exc.__class__.__name__)

    latest_written_count = sum(1 for cycle in cycle_packets if cycle.get("latest_prediction_artifact_written") is True)
    status_written_count = sum(1 for cycle in cycle_packets if cycle.get("status_artifact_written") is True)
    cycle_blockers = [str(item) for cycle in cycle_packets for item in (cycle.get("blocked_reasons") or [])]
    cycle_warnings = [str(item) for cycle in cycle_packets for item in (cycle.get("warning_reasons") or [])]
    all_blockers = list(dict.fromkeys([*blockers, *cycle_blockers]))
    all_warnings = list(dict.fromkeys([*warnings, *cycle_warnings]))
    executed_ok = bool(
        execute_periodic_producer
        and ack_matched
        and cycle_packets
        and latest_written_count == len(cycle_packets)
        and status_written_count == len(cycle_packets)
        and not all_blockers
    )
    ok = bool(dry_run or executed_ok or stopped_by_stop_file)

    return {
        "ok": ok,
        "ps_q19k_version": PS_Q19K_PERIODIC_PRODUCER_VERSION,
        "request_state": request_state,
        "hot_latest_root_hint": root,
        "latest_prediction_artifact_relative_path": LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH,
        "producer_status_artifact_relative_path": PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
        "q16d_runner_version": PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION,
        "explicit_ack_required": True,
        "explicit_ack_matched": ack_matched,
        "execute_periodic_producer_requested": bool(execute_periodic_producer),
        "default_dry_run_no_write": dry_run,
        "requested_max_cycles": requested_cycles,
        "effective_max_cycles": cycles,
        "requested_interval_sec": requested_interval,
        "effective_interval_sec": interval,
        "lock_relative_path": LOCK_RELATIVE_PATH,
        "stop_relative_path": STOP_RELATIVE_PATH,
        "lock_created_by_this_request": lock_created,
        "stopped_by_stop_file": stopped_by_stop_file,
        "cycle_count": len(cycle_packets),
        "latest_prediction_artifact_written_count": latest_written_count,
        "status_artifact_written_count": status_written_count,
        "cycle_packets": [_safe_cycle_projection(cycle) for cycle in cycle_packets],
        "blocked_reasons": all_blockers,
        "warning_reasons": all_warnings,
        "non_ui_runner_only": True,
        "bounded_periodic_loop_only": True,
        "scheduler_install_performed": False,
        "scheduler_enabled": False,
        "scheduled_loop_enabled": False,
        "producer_enabled": bool(execute_periodic_producer and ack_matched and not dry_run),
        "warroom_ui_trigger_enabled": False,
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


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q19K guarded non-UI periodic prediction producer")
    parser.add_argument("--root", default=DEFAULT_HOT_LATEST_ROOT_HINT)
    parser.add_argument("--execute-periodic-producer", action="store_true")
    parser.add_argument("--ack", default="")
    parser.add_argument("--max-cycles", type=int, default=DEFAULT_MAX_CYCLES)
    parser.add_argument("--interval-sec", type=int, default=RECOMMENDED_CADENCE_SEC)
    parser.add_argument("--allow-guard-test-root", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    packet = build_ps_q19k_periodic_producer_packet(
        hot_latest_root_hint=str(args.root),
        execute_periodic_producer=bool(args.execute_periodic_producer),
        ack=str(args.ack or ""),
        max_cycles=int(args.max_cycles),
        interval_sec=int(args.interval_sec),
        allow_guard_test_root=bool(args.allow_guard_test_root),
    )
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if packet.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
