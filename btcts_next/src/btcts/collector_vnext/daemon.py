# path: ./btcts_next/src/btcts/collector_vnext/daemon.py
# desc: Smoke daemon for Collector vNext that repeats qualification cycles and refreshes vNext state files.

from __future__ import annotations

import json
import os
import sys
import time

from pathlib import Path

from .app import main as run_once_main
from .config import load_config
from .events import now_iso_utc
from .lock import acquire_daemon_lock, release_daemon_lock
from .run_smoke import build_status
from .state import write_daemon_health, write_status


def _load_runtime_status(cfg) -> dict:
    path = Path(cfg.roots()["state"]) / "status.json"
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_runtime_health(cfg) -> dict:
    path = Path(cfg.roots()["state"]) / "health.json"
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_rate_state(cfg) -> dict:
    path = Path(cfg.roots()["state"]) / "rate_state.json"
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _summarize_rate_state(rate_state: dict) -> dict:
    items = rate_state.get("items") if isinstance(rate_state, dict) else {}
    if not isinstance(items, dict) or not items:
        return {
            "summary_state": "NORMAL",
            "engaged": False,
            "reason": "",
            "wait_ms": 0,
            "util_ratio": 0.0,
            "last_429_ts": None,
            "recovery_phase": "steady",
        }

    best = {
        "rank": -1,
        "summary_state": "NORMAL",
        "engaged": False,
        "reason": "",
        "wait_ms": 0,
        "util_ratio": 0.0,
        "last_429_ts": None,
        "recovery_phase": "steady",
    }
    rank_map = {"NORMAL": 0, "WARN": 1, "CRIT": 2}

    for _, item in items.items():
        if not isinstance(item, dict):
            continue

        mode = str(item.get("summary_state") or "NORMAL").upper()
        rank = rank_map.get(mode, 0)
        if rank > best["rank"]:
            best = {
                "rank": rank,
                "summary_state": mode,
                "engaged": bool(item.get("engaged", False)),
                "reason": str(item.get("reason") or ""),
                "wait_ms": int(item.get("wait_ms") or 0),
                "util_ratio": float(item.get("util_ratio") or 0.0),
                "last_429_ts": item.get("last_429_ts"),
                "recovery_phase": str(item.get("recovery_phase") or "steady"),
            }

    return {
        "summary_state": best["summary_state"],
        "engaged": best["engaged"],
        "reason": best["reason"],
        "wait_ms": best["wait_ms"],
        "util_ratio": best["util_ratio"],
        "last_429_ts": best["last_429_ts"],
        "recovery_phase": best["recovery_phase"],
    }


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except Exception:
        return default


def _emit_loop_status(
    cfg,
    cycle_no: int,
    interval_sec: int,
    *,
    consecutive_failures: int = 0,
    last_error: str | None = None,
    last_success_ts: str | None = None,
    ws_trades_warn_streak: int = 0,
    rate_summary: dict | None = None,
    origin_continuity: dict | None = None,
) -> None:
    if consecutive_failures > 0:
        mode = "RECOVERING"
        daemon_ok = False
        daemon_status = "recovering"
    elif ws_trades_warn_streak >= 2:
        mode = "DEGRADED"
        daemon_ok = False
        daemon_status = "degraded"
    else:
        mode = "RUNNING"
        daemon_ok = True
        daemon_status = "healthy"

    write_status(
        cfg,
        build_status(
            mode=mode,
            message=(
                f"collector_vnext smoke daemon active cycle={cycle_no} "
                f"interval_sec={interval_sec} failures={consecutive_failures}"
            ),
            session_id=f"{cfg.collector_id}-daemon",
            stream_session_id=f"{cfg.collector_id}-daemon-loop",
            consecutive_failures=consecutive_failures,
            last_error=last_error,
            last_success_ts=last_success_ts,
            ws_trades_warn_streak=ws_trades_warn_streak,
            rate_control=rate_summary or {},
            origin_continuity=origin_continuity or {},
        ),
    )

    write_daemon_health(
        cfg,
        {
            "ts": now_iso_utc(),
            "ok": daemon_ok,
            "status": daemon_status,
            "collector_vnext": True,
            "daemon": True,
            "cycle_no": cycle_no,
            "interval_sec": interval_sec,
            "consecutive_failures": consecutive_failures,
            "last_error": last_error,
            "last_success_ts": last_success_ts,
            "ws_trades_warn_streak": ws_trades_warn_streak,
            "rate_control": rate_summary or {},
        },
    )


def run_forever() -> int:
    cfg = load_config()

    locked, lock_info = acquire_daemon_lock(cfg)
    if not locked:
        print(
            json.dumps(
                {
                    "ok": False,
                    "daemon": True,
                    "already_running": True,
                    "lock_info": lock_info,
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2

    interval_sec = _env_int("BTCTS_LOOP_INTERVAL_SEC", 15)
    max_failures = _env_int("BTCTS_MAX_FAILURES", 10)
    failure_backoff_sec = _env_int("BTCTS_FAILURE_BACKOFF_SEC", 10)

    consecutive_failures = 0
    cycle_no = 0
    last_error: str | None = None
    last_success_ts: str | None = None
    ws_trades_warn_streak = 0
    rate_summary: dict = {}

    try:
        while True:
            cycle_no += 1

            try:
                exit_code = run_once_main()

                if exit_code != 0:
                    raise RuntimeError(f"collector_vnext app exited with code={exit_code}")

                runtime_status = _load_runtime_status(cfg)
                health = _load_runtime_health(cfg)
                rate_state = _load_rate_state(cfg)
                rate_summary = _summarize_rate_state(rate_state)
                checks = health.get("checks") or []
                origin_continuity = runtime_status.get("origin_continuity") or {}

                ws_trade_warn = any(
                    check.get("name") == "bitflyer_ws_executions"
                    and check.get("result") == "warn"
                    for check in checks
                )

                if ws_trade_warn:
                    ws_trades_warn_streak += 1
                else:
                    ws_trades_warn_streak = 0

                consecutive_failures = 0
                last_success_ts = now_iso_utc()

                if ws_trades_warn_streak >= 2:
                    last_error = "bitflyer_ws_executions warn streak"
                else:
                    last_error = None

                _emit_loop_status(
                    cfg,
                    cycle_no,
                    interval_sec,
                    consecutive_failures=consecutive_failures,
                    last_error=last_error,
                    last_success_ts=last_success_ts,
                    ws_trades_warn_streak=ws_trades_warn_streak,
                    rate_summary=rate_summary,
                    origin_continuity=origin_continuity,
                )

            except KeyboardInterrupt:
                runtime_status = _load_runtime_status(cfg)
                origin_continuity = runtime_status.get("origin_continuity") or {}

                write_status(
                    cfg,
                    build_status(
                        mode="STOPPED",
                        message="collector_vnext smoke daemon stopped by keyboard interrupt",
                        session_id=f"{cfg.collector_id}-daemon",
                        stream_session_id=f"{cfg.collector_id}-daemon-loop",
                        consecutive_failures=consecutive_failures,
                        last_error=last_error,
                        last_success_ts=last_success_ts,
                        ws_trades_warn_streak=ws_trades_warn_streak,
                        rate_control=rate_summary or {},
                        origin_continuity=origin_continuity,
                    ),
                )
                write_daemon_health(
                    cfg,
                    {
                        "ts": now_iso_utc(),
                        "ok": False,
                        "status": "stopped",
                        "collector_vnext": True,
                        "daemon": True,
                        "stopped": True,
                        "reason": "keyboard_interrupt",
                        "cycle_no": cycle_no,
                        "last_error": last_error,
                        "last_success_ts": last_success_ts,
                        "ws_trades_warn_streak": ws_trades_warn_streak,
                        "rate_control": rate_summary or {},
                    },
                )
                return 0

            except Exception as exc:
                consecutive_failures += 1
                last_error = str(exc)
                runtime_status = _load_runtime_status(cfg)
                origin_continuity = runtime_status.get("origin_continuity") or {}

                write_status(
                    cfg,
                    build_status(
                        mode="DEGRADED",
                        message=(
                            "collector_vnext smoke daemon cycle failed "
                            f"failures={consecutive_failures} error={exc}"
                        ),
                        session_id=f"{cfg.collector_id}-daemon",
                        stream_session_id=f"{cfg.collector_id}-daemon-loop",
                        consecutive_failures=consecutive_failures,
                        last_error=str(exc),
                        last_success_ts=last_success_ts,
                        ws_trades_warn_streak=ws_trades_warn_streak,
                        rate_control=rate_summary or {},
                        origin_continuity=origin_continuity,
                    ),
                )
                write_daemon_health(
                    cfg,
                    {
                        "ts": now_iso_utc(),
                        "ok": False,
                        "status": "degraded",
                        "collector_vnext": True,
                        "daemon": True,
                        "cycle_no": cycle_no,
                        "consecutive_failures": consecutive_failures,
                        "error": str(exc),
                        "last_error": str(exc),
                        "last_success_ts": last_success_ts,
                        "ws_trades_warn_streak": ws_trades_warn_streak,
                        "rate_control": rate_summary or {},
                    },
                )

                print(
                    json.dumps(
                        {
                            "ok": False,
                            "daemon": True,
                            "cycle_no": cycle_no,
                            "consecutive_failures": consecutive_failures,
                            "error": str(exc),
                        },
                        ensure_ascii=False,
                    ),
                    file=sys.stderr,
                )

                if consecutive_failures >= max_failures:
                    write_status(
                        cfg,
                        build_status(
                            mode="STOPPED",
                            message=(
                                "collector_vnext smoke daemon stopped after too many failures "
                                f"max_failures={max_failures}"
                            ),
                            session_id=f"{cfg.collector_id}-daemon",
                            stream_session_id=f"{cfg.collector_id}-daemon-loop",
                            consecutive_failures=consecutive_failures,
                            last_error=last_error,
                            last_success_ts=last_success_ts,
                            ws_trades_warn_streak=ws_trades_warn_streak,
                            rate_control=rate_summary or {},
                            origin_continuity=origin_continuity,
                        ),
                    )
                    return 1

                time.sleep(failure_backoff_sec)
                continue

            time.sleep(interval_sec)
    finally:
        release_daemon_lock(cfg)


if __name__ == "__main__":
    raise SystemExit(run_forever())