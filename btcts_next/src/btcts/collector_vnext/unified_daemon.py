# path: ./btcts_next/src/btcts/collector_vnext/unified_daemon.py
# desc: Unified Collector 用の常駐 daemon scaffold。U1 では REST + WS board の supervisor になる。

from __future__ import annotations

import json
import sys
import threading
import time

from ._env_utils import env_float, env_int

from .config import load_config
from .events import now_iso_utc
from .lock import (
    acquire_daemon_lock,
    acquire_process_singleton_mutex,
    release_daemon_lock,
    release_process_singleton_mutex,
)
from .unified_runtime import run_once
from .unified_state import (
    read_unified_daemon_stop_request,
    write_unified_daemon_health,
    write_unified_daemon_status,
)
from .unified_ws_board_lane import UnifiedWsBoardLane
from .unified_ws_executions_lane import UnifiedWsExecutionsLane


def _active_stop_request(cfg) -> dict:
    payload = read_unified_daemon_stop_request(cfg)
    if not isinstance(payload, dict):
        return {}

    action = str(payload.get("action") or "").strip().lower()
    if action != "stop":
        return {}

    return payload


def _write_stopping_state(
    cfg,
    *,
    cycle_no: int,
    reason: str,
    requested_by: str,
    last_error: str | None,
    last_success_ts: str | None,
) -> None:
    ts = now_iso_utc()

    write_unified_daemon_status(
        cfg,
        {
            "ts": ts,
            "collector_id": cfg.collector_id,
            "collector_role": cfg.collector_role,
            "mode": "STOPPING",
            "message": f"collector_vnext unified daemon stopping reason={reason}",
            "runtime_kind": "unified",
            "daemon": True,
            "cycle_no": cycle_no,
            "lane_health": {
                "rest_lane": "stopping",
                "ws_board_lane": "stopping",
                "ws_executions_lane": "stopping",
            },
            "stop_requested": True,
            "stop_reason": reason,
            "stop_requested_by": requested_by,
            "consecutive_failures": 0,
            "last_error": last_error,
            "last_success_ts": last_success_ts,
        },
    )
    write_unified_daemon_health(
        cfg,
        {
            "ts": ts,
            "ok": False,
            "status": "stopping",
            "runtime_kind": "unified",
            "daemon": True,
            "cycle_no": cycle_no,
            "stopping": True,
            "reason": reason,
            "requested_by": requested_by,
            "lane_failures": {
                "rest_lane": 0,
                "ws_board_lane": 0,
                "ws_executions_lane": 0,
            },
            "consecutive_failures": 0,
            "last_error": last_error,
            "last_success_ts": last_success_ts,
        },
    )


def _write_stopped_state(
    cfg,
    *,
    cycle_no: int,
    reason: str,
    requested_by: str,
    last_error: str | None,
    last_success_ts: str | None,
    consecutive_failures: int,
) -> None:
    ts = now_iso_utc()

    write_unified_daemon_status(
        cfg,
        {
            "ts": ts,
            "collector_id": cfg.collector_id,
            "collector_role": cfg.collector_role,
            "mode": "STOPPED",
            "message": f"collector_vnext unified daemon stopped reason={reason}",
            "runtime_kind": "unified",
            "daemon": True,
            "cycle_no": cycle_no,
            "lane_health": {
                "rest_lane": "stopped",
                "ws_board_lane": "stopped",
                "ws_executions_lane": "stopped",
            },
            "stop_requested": True,
            "stop_reason": reason,
            "stop_requested_by": requested_by,
            "consecutive_failures": consecutive_failures,
            "last_error": last_error,
            "last_success_ts": last_success_ts,
        },
    )
    write_unified_daemon_health(
        cfg,
        {
            "ts": ts,
            "ok": False,
            "status": "stopped",
            "runtime_kind": "unified",
            "daemon": True,
            "stopped": True,
            "reason": reason,
            "requested_by": requested_by,
            "cycle_no": cycle_no,
            "lane_failures": {
                "rest_lane": 0,
                "ws_board_lane": 0,
                "ws_executions_lane": 0,
            },
            "consecutive_failures": consecutive_failures,
            "last_error": last_error,
            "last_success_ts": last_success_ts,
        },
    )


def run_forever() -> int:
    singleton_locked, singleton_info = acquire_process_singleton_mutex(
        r"Local\BTCTS_COLLECTOR_VNEXT_UNIFIED_DAEMON"
    )
    if not singleton_locked:
        print(
            json.dumps(
                {
                    "ok": False,
                    "daemon": True,
                    "runtime_kind": "unified",
                    "already_running": True,
                    "singleton_info": singleton_info,
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2

    cfg = load_config()

    locked, lock_info = acquire_daemon_lock(cfg, runtime_family="unified")
    if not locked:
        release_process_singleton_mutex(singleton_info)
        print(
            json.dumps(
                {
                    "ok": False,
                    "daemon": True,
                    "runtime_kind": "unified",
                    "already_running": True,
                    "lock_info": lock_info,
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2

    loop_sleep_sec = max(0.05, env_float("BTCTS_UNIFIED_LOOP_SLEEP_SEC", 0.25))
    max_failures = env_int("BTCTS_UNIFIED_MAX_FAILURES", 20)
    failure_backoff_sec = max(1, env_int("BTCTS_UNIFIED_FAILURE_BACKOFF_SEC", 3))

    cycle_no = 0
    consecutive_failures = 0
    last_error: str | None = None
    last_success_ts: str | None = None
    stop_reason: str | None = None
    stop_requested_by: str = "unknown"

    ws_board_lane = UnifiedWsBoardLane()
    ws_executions_lane = UnifiedWsExecutionsLane()
    stop_event = threading.Event()

    ws_board_thread = threading.Thread(
        target=ws_board_lane.run_forever,
        args=(stop_event,),
        name="unified-ws-board-lane",
        daemon=True,
    )
    ws_executions_thread = threading.Thread(
        target=ws_executions_lane.run_forever,
        args=(stop_event,),
        name="unified-ws-executions-lane",
        daemon=True,
    )

    ws_board_thread.start()
    ws_executions_thread.start()

    try:
        while True:
            pending_stop = _active_stop_request(cfg)
            if pending_stop:
                stop_reason = str(pending_stop.get("reason") or "watchdog_requested")
                stop_requested_by = str(pending_stop.get("requested_by") or "watchdog")
                stop_event.set()
                _write_stopping_state(
                    cfg,
                    cycle_no=cycle_no,
                    reason=stop_reason,
                    requested_by=stop_requested_by,
                    last_error=last_error,
                    last_success_ts=last_success_ts,
                )
                break

            cycle_no += 1

            try:
                exit_code = run_once()
                if exit_code != 0:
                    raise RuntimeError(f"unified runtime exited with code={exit_code}")

                consecutive_failures = 0
                last_error = None
                last_success_ts = now_iso_utc()

                ws_board_snapshot = ws_board_lane.snapshot()
                ws_executions_snapshot = ws_executions_lane.snapshot()

                write_unified_daemon_status(
                    cfg,
                    {
                        "ts": now_iso_utc(),
                        "collector_id": cfg.collector_id,
                        "collector_role": cfg.collector_role,
                        "mode": "RUNNING",
                        "message": (
                            f"collector_vnext unified daemon active "
                            f"cycle={cycle_no} sleep_sec={loop_sleep_sec}"
                        ),
                        "runtime_kind": "unified",
                        "daemon": True,
                        "cycle_no": cycle_no,
                        "lane_health": {
                            "rest_lane": "running",
                            "ws_board_lane": ws_board_snapshot.get("lane_state") or "unknown",
                            "ws_executions_lane": ws_executions_snapshot.get("lane_state") or "unknown",
                        },
                        "stop_requested": False,
                        "consecutive_failures": consecutive_failures,
                        "last_error": last_error,
                        "last_success_ts": last_success_ts,
                    },
                )
                write_unified_daemon_health(
                    cfg,
                    {
                        "ts": now_iso_utc(),
                        "ok": True,
                        "status": "healthy",
                        "runtime_kind": "unified",
                        "daemon": True,
                        "cycle_no": cycle_no,
                        "lane_failures": {
                            "rest_lane": 0,
                            "ws_board_lane": ws_board_snapshot.get("restart_count") or 0,
                            "ws_executions_lane": ws_executions_snapshot.get("restart_count") or 0,
                        },
                        "consecutive_failures": consecutive_failures,
                        "last_error": last_error,
                        "last_success_ts": last_success_ts,
                    },
                )

            except KeyboardInterrupt:
                stop_reason = "keyboard_interrupt"
                stop_requested_by = "console"
                stop_event.set()
                _write_stopping_state(
                    cfg,
                    cycle_no=cycle_no,
                    reason=stop_reason,
                    requested_by=stop_requested_by,
                    last_error=last_error,
                    last_success_ts=last_success_ts,
                )
                break

            except Exception as exc:
                consecutive_failures += 1
                last_error = str(exc)

                ws_board_snapshot = ws_board_lane.snapshot()
                ws_executions_snapshot = ws_executions_lane.snapshot()

                write_unified_daemon_status(
                    cfg,
                    {
                        "ts": now_iso_utc(),
                        "collector_id": cfg.collector_id,
                        "collector_role": cfg.collector_role,
                        "mode": "DEGRADED",
                        "message": (
                            "collector_vnext unified daemon cycle failed "
                            f"failures={consecutive_failures} error={exc}"
                        ),
                        "runtime_kind": "unified",
                        "daemon": True,
                        "cycle_no": cycle_no,
                        "lane_health": {
                            "rest_lane": "degraded",
                            "ws_board_lane": ws_board_snapshot.get("lane_state") or "unknown",
                            "ws_executions_lane": ws_executions_snapshot.get("lane_state") or "unknown",
                        },
                        "consecutive_failures": consecutive_failures,
                        "last_error": last_error,
                        "last_success_ts": last_success_ts,
                    },
                )
                write_unified_daemon_health(
                    cfg,
                    {
                        "ts": now_iso_utc(),
                        "ok": False,
                        "status": "degraded",
                        "runtime_kind": "unified",
                        "daemon": True,
                        "cycle_no": cycle_no,
                        "lane_failures": {
                            "rest_lane": consecutive_failures,
                            "ws_board_lane": ws_board_snapshot.get("restart_count") or 0,
                            "ws_executions_lane": ws_executions_snapshot.get("restart_count") or 0,
                        },
                        "consecutive_failures": consecutive_failures,
                        "last_error": last_error,
                        "last_success_ts": last_success_ts,
                    },
                )

                print(
                    json.dumps(
                        {
                            "ok": False,
                            "daemon": True,
                            "runtime_kind": "unified",
                            "cycle_no": cycle_no,
                            "consecutive_failures": consecutive_failures,
                            "error": str(exc),
                        },
                        ensure_ascii=False,
                    ),
                    file=sys.stderr,
                )

                if consecutive_failures >= max_failures:
                    write_unified_daemon_status(
                        cfg,
                        {
                            "ts": now_iso_utc(),
                            "collector_id": cfg.collector_id,
                            "collector_role": cfg.collector_role,
                            "mode": "STOPPED",
                            "message": (
                                "collector_vnext unified daemon stopped after too many failures "
                                f"max_failures={max_failures}"
                            ),
                            "runtime_kind": "unified",
                            "daemon": True,
                            "cycle_no": cycle_no,
                            "lane_health": {
                                "rest_lane": "stopped",
                                "ws_board_lane": "stopped",
                                "ws_executions_lane": "stopped",
                            },
                            "consecutive_failures": consecutive_failures,
                            "last_error": last_error,
                            "last_success_ts": last_success_ts,
                        },
                    )
                    return 1

                time.sleep(failure_backoff_sec)
                continue

            time.sleep(loop_sleep_sec)

        _write_stopped_state(
            cfg,
            cycle_no=cycle_no,
            reason=stop_reason or "unknown",
            requested_by=stop_requested_by,
            last_error=last_error,
            last_success_ts=last_success_ts,
            consecutive_failures=consecutive_failures,
        )
        return 0

    finally:
        stop_event.set()
        release_daemon_lock(cfg, runtime_family="unified")
        release_process_singleton_mutex(singleton_info)


if __name__ == "__main__":
    raise SystemExit(run_forever())