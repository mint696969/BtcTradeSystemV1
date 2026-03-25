# path: ./btcts_next/src/btcts/collector_vnext/unified_daemon.py
# desc: Unified Collector 用の常駐 daemon scaffold。U1 では REST + WS board の supervisor になる。

from __future__ import annotations

import json
import os
import sys
import threading
import time

from .config import load_config
from .events import now_iso_utc
from .lock import acquire_daemon_lock, release_daemon_lock
from .unified_runtime import run_once
from .unified_state import (
    write_unified_daemon_health,
    write_unified_daemon_status,
)
from .unified_ws_board_lane import UnifiedWsBoardLane
from .unified_ws_executions_lane import UnifiedWsExecutionsLane


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except Exception:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except Exception:
        return default


def run_forever() -> int:
    cfg = load_config()

    locked, lock_info = acquire_daemon_lock(cfg, runtime_family="unified")
    if not locked:
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

    loop_sleep_sec = max(0.05, _env_float("BTCTS_UNIFIED_LOOP_SLEEP_SEC", 0.25))
    max_failures = _env_int("BTCTS_UNIFIED_MAX_FAILURES", 20)
    failure_backoff_sec = max(1, _env_int("BTCTS_UNIFIED_FAILURE_BACKOFF_SEC", 3))

    cycle_no = 0
    consecutive_failures = 0
    last_error: str | None = None
    last_success_ts: str | None = None

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
                stop_event.set()

                write_unified_daemon_status(
                    cfg,
                    {
                        "ts": now_iso_utc(),
                        "collector_id": cfg.collector_id,
                        "collector_role": cfg.collector_role,
                        "mode": "STOPPED",
                        "message": "collector_vnext unified daemon stopped by keyboard interrupt",
                        "runtime_kind": "unified",
                        "daemon": True,
                        "cycle_no": cycle_no,
                        "lane_health": {
                            "rest_lane": "stopped",
                            "ws_board_lane": "stopped",
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
                        "status": "stopped",
                        "runtime_kind": "unified",
                        "daemon": True,
                        "stopped": True,
                        "reason": "keyboard_interrupt",
                        "cycle_no": cycle_no,
                        "lane_failures": {
                            "rest_lane": 0,
                            "ws_board_lane": 0,
                        },
                        "consecutive_failures": consecutive_failures,
                        "last_error": last_error,
                        "last_success_ts": last_success_ts,
                    },
                )
                return 0

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
                                "ws_board_lane": "not_started",
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

    finally:
        stop_event.set()
        release_daemon_lock(cfg, runtime_family="unified")


if __name__ == "__main__":
    raise SystemExit(run_forever())