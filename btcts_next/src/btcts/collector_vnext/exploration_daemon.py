# path: ./btcts_next/src/btcts/collector_vnext/exploration_daemon.py
# desc: Exploration Runtime 用の常駐 daemon。smoke daemon と分離して高密度運転を継続する。

from __future__ import annotations

import json
import os
import sys
import time

from .config import load_config
from .events import now_iso_utc
from .exploration_runtime import run_once
from .exploration_state import (
    write_exploration_daemon_health,
    write_exploration_daemon_status,
)
from .lock import acquire_daemon_lock, release_daemon_lock


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

    locked, lock_info = acquire_daemon_lock(cfg)
    if not locked:
        print(
            json.dumps(
                {
                    "ok": False,
                    "daemon": True,
                    "runtime_kind": "exploration",
                    "already_running": True,
                    "lock_info": lock_info,
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2

    loop_sleep_sec = max(0.05, _env_float("BTCTS_EXPLORATION_LOOP_SLEEP_SEC", 0.25))
    max_failures = _env_int("BTCTS_EXPLORATION_MAX_FAILURES", 20)
    failure_backoff_sec = max(1, _env_int("BTCTS_EXPLORATION_FAILURE_BACKOFF_SEC", 3))

    cycle_no = 0
    consecutive_failures = 0
    last_error: str | None = None
    last_success_ts: str | None = None

    try:
        while True:
            cycle_no += 1

            try:
                exit_code = run_once()
                if exit_code != 0:
                    raise RuntimeError(f"exploration runtime exited with code={exit_code}")

                consecutive_failures = 0
                last_error = None
                last_success_ts = now_iso_utc()

                write_exploration_daemon_status(
                    cfg,
                    {
                        "ts": now_iso_utc(),
                        "collector_id": cfg.collector_id,
                        "collector_role": cfg.collector_role,
                        "mode": "RUNNING",
                        "message": (
                            f"collector_vnext exploration daemon active "
                            f"cycle={cycle_no} sleep_sec={loop_sleep_sec}"
                        ),
                        "runtime_kind": "exploration",
                        "daemon": True,
                        "cycle_no": cycle_no,
                        "consecutive_failures": consecutive_failures,
                        "last_error": last_error,
                        "last_success_ts": last_success_ts,
                    },
                )
                write_exploration_daemon_health(
                    cfg,
                    {
                        "ts": now_iso_utc(),
                        "ok": True,
                        "status": "healthy",
                        "runtime_kind": "exploration",
                        "daemon": True,
                        "cycle_no": cycle_no,
                        "consecutive_failures": consecutive_failures,
                        "last_error": last_error,
                        "last_success_ts": last_success_ts,
                    },
                )

            except KeyboardInterrupt:
                write_exploration_daemon_status(
                    cfg,
                    {
                        "ts": now_iso_utc(),
                        "collector_id": cfg.collector_id,
                        "collector_role": cfg.collector_role,
                        "mode": "STOPPED",
                        "message": "collector_vnext exploration daemon stopped by keyboard interrupt",
                        "runtime_kind": "exploration",
                        "daemon": True,
                        "cycle_no": cycle_no,
                        "consecutive_failures": consecutive_failures,
                        "last_error": last_error,
                        "last_success_ts": last_success_ts,
                    },
                )
                write_exploration_daemon_health(
                    cfg,
                    {
                        "ts": now_iso_utc(),
                        "ok": False,
                        "status": "stopped",
                        "runtime_kind": "exploration",
                        "daemon": True,
                        "stopped": True,
                        "reason": "keyboard_interrupt",
                        "cycle_no": cycle_no,
                        "consecutive_failures": consecutive_failures,
                        "last_error": last_error,
                        "last_success_ts": last_success_ts,
                    },
                )
                return 0

            except Exception as exc:
                consecutive_failures += 1
                last_error = str(exc)

                write_exploration_daemon_status(
                    cfg,
                    {
                        "ts": now_iso_utc(),
                        "collector_id": cfg.collector_id,
                        "collector_role": cfg.collector_role,
                        "mode": "DEGRADED",
                        "message": (
                            "collector_vnext exploration daemon cycle failed "
                            f"failures={consecutive_failures} error={exc}"
                        ),
                        "runtime_kind": "exploration",
                        "daemon": True,
                        "cycle_no": cycle_no,
                        "consecutive_failures": consecutive_failures,
                        "last_error": last_error,
                        "last_success_ts": last_success_ts,
                    },
                )
                write_exploration_daemon_health(
                    cfg,
                    {
                        "ts": now_iso_utc(),
                        "ok": False,
                        "status": "degraded",
                        "runtime_kind": "exploration",
                        "daemon": True,
                        "cycle_no": cycle_no,
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
                            "runtime_kind": "exploration",
                            "cycle_no": cycle_no,
                            "consecutive_failures": consecutive_failures,
                            "error": str(exc),
                        },
                        ensure_ascii=False,
                    ),
                    file=sys.stderr,
                )

                if consecutive_failures >= max_failures:
                    write_exploration_daemon_status(
                        cfg,
                        {
                            "ts": now_iso_utc(),
                            "collector_id": cfg.collector_id,
                            "collector_role": cfg.collector_role,
                            "mode": "STOPPED",
                            "message": (
                                "collector_vnext exploration daemon stopped after too many failures "
                                f"max_failures={max_failures}"
                            ),
                            "runtime_kind": "exploration",
                            "daemon": True,
                            "cycle_no": cycle_no,
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
        release_daemon_lock(cfg)


if __name__ == "__main__":
    raise SystemExit(run_forever())