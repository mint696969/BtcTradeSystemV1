# path: ./btcts_next/src/btcts/collector_vnext/archive/worker.py
# desc: Background archive worker for safe hot->cold copy.

from __future__ import annotations

import json
import os
import socket
import sys
import time

from btcts.collector_vnext.events import now_iso_utc

from .audit import append_archive_audit
from .config import load_archive_config
from .gc_job import build_gc_plan, execute_gc_plan
from .health_summary import (
    build_archive_transfer_health_summary,
    write_archive_transfer_health_summary,
)
from .planner import build_copy_plan, execute_copy_plan
from .state import (
    acquire_archive_worker_lock,
    clear_archive_stop_request,
    read_archive_stop_request,
    release_archive_worker_lock,
    write_archive_copy_state,
    write_archive_gc_state,
)


def _active_stop_request(cfg) -> dict:
    payload = read_archive_stop_request(cfg)
    if not isinstance(payload, dict):
        return {}
    action = str(payload.get("action") or "").strip().lower()
    if action != "stop":
        return {}
    return payload


def run_forever() -> int:
    cfg = load_archive_config()

    locked, lock_info = acquire_archive_worker_lock(cfg)
    if not locked:
        print(
            json.dumps(
                {
                    "ok": False,
                    "archive_worker": True,
                    "already_running": True,
                    "lock_info": lock_info,
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2

    worker_started_at = now_iso_utc()

    append_archive_audit(
        cfg,
        "archive.worker.start",
        extra={
            "pid": os.getpid(),
            "host_name": socket.gethostname(),
            "hot_root": str(cfg.hot_root),
            "cold_root": str(cfg.cold_root),
            "copy_prefixes": cfg.resolved_copy_prefixes(),
            "gc_prefixes": cfg.resolved_gc_prefixes(),
        },
    )

    write_archive_copy_state(
        cfg,
        {
            "mode": "RUNNING",
            "current_phase": "startup",
            "started_at": worker_started_at,
            "last_error": None,
            "last_plan_count": 0,
            "last_copied_files": 0,
            "last_copied_bytes": 0,
        },
    )
    write_archive_gc_state(
        cfg,
        {
            "mode": "IDLE",
            "current_phase": "startup",
            "started_at": worker_started_at,
            "last_error": None,
            "last_plan_count": 0,
            "last_deleted_files": 0,
            "last_deleted_bytes": 0,
            "enabled": cfg.gc_enabled,
            "dry_run": cfg.gc_dry_run,
        },
    )

    try:
        while True:
            stop_req = _active_stop_request(cfg)
            if stop_req:
                stop_reason = stop_req.get("reason") or "archive_stop_request"
                write_archive_copy_state(
                    cfg,
                    {
                        "mode": "STOPPING",
                        "current_phase": "stopping",
                        "started_at": worker_started_at,
                        "last_error": None,
                        "stop_reason": stop_reason,
                    },
                )
                write_archive_gc_state(
                    cfg,
                    {
                        "mode": "STOPPING",
                        "current_phase": "stopping",
                        "started_at": worker_started_at,
                        "dry_run": cfg.gc_dry_run,
                        "enabled": cfg.gc_enabled,
                        "last_error": None,
                        "stop_reason": stop_reason,
                        "last_scan_ts": now_iso_utc(),
                    },
                )
                break

            write_archive_copy_state(
                cfg,
                {
                    "mode": "RUNNING",
                    "current_phase": "copy_planning",
                    "started_at": worker_started_at,
                    "last_error": None,
                },
            )
            plan = build_copy_plan(cfg)
            plan_sample = [
                {
                    "kind": x.kind,
                    "src": str(x.src),
                    "dst": str(x.dst),
                    "size_bytes": x.size_bytes,
                }
                for x in plan[:10]
            ]

            if plan:
                append_archive_audit(
                    cfg,
                    "archive.copy.begin",
                    extra={
                        "plan_count": len(plan),
                        "plan_sample": plan_sample,
                    },
                )

            write_archive_copy_state(
                cfg,
                {
                    "mode": "RUNNING",
                    "current_phase": "copy_executing",
                    "started_at": worker_started_at,
                    "last_error": None,
                    "last_plan_count": len(plan),
                    "plan_sample": plan_sample,
                },
            )
            result = execute_copy_plan(plan)

            if result["error_count"]:
                append_archive_audit(
                    cfg,
                    "archive.copy.error",
                    level="WARN",
                    extra={
                        "plan_count": len(plan),
                        **result,
                    },
                )
            elif plan:
                append_archive_audit(
                    cfg,
                    "archive.copy.completed",
                    extra={
                        "plan_count": len(plan),
                        **result,
                    },
                )

            write_archive_copy_state(
                cfg,
                {
                    "mode": "RUNNING",
                    "current_phase": "copy_executing",
                    "started_at": worker_started_at,
                    "last_error": None if result["error_count"] == 0 else "copy_error",
                    "last_scan_ts": now_iso_utc(),
                    "last_plan_count": len(plan),
                    "last_copied_files": result["copied_files"],
                    "last_copied_dirs": result["copied_dirs"],
                    "last_copied_bytes": result["copied_bytes"],
                    "error_count": result["error_count"],
                    "plan_sample": plan_sample,
                },
            )

            write_archive_gc_state(
                cfg,
                {
                    "mode": "RUNNING" if cfg.gc_enabled else "IDLE",
                    "current_phase": "gc_planning" if cfg.gc_enabled else "sleeping",
                    "started_at": worker_started_at,
                    "dry_run": cfg.gc_dry_run,
                    "enabled": cfg.gc_enabled,
                    "last_error": None,
                },
            )
            gc_plan = build_gc_plan(cfg) if cfg.gc_enabled else []
            gc_plan_sample = [
                {
                    "hot_path": str(x.hot_path),
                    "cold_path": str(x.cold_path),
                    "size_bytes": x.size_bytes,
                }
                for x in gc_plan[:10]
            ]

            if gc_plan:
                append_archive_audit(
                    cfg,
                    "archive.gc.begin",
                    extra={
                        "dry_run": cfg.gc_dry_run,
                        "plan_count": len(gc_plan),
                        "plan_sample": gc_plan_sample,
                    },
                )

            if cfg.gc_enabled:
                write_archive_gc_state(
                    cfg,
                    {
                        "mode": "RUNNING",
                        "current_phase": "gc_executing",
                        "started_at": worker_started_at,
                        "dry_run": cfg.gc_dry_run,
                        "enabled": cfg.gc_enabled,
                        "last_error": None,
                        "last_plan_count": len(gc_plan),
                        "plan_sample": gc_plan_sample,
                    },
                )

            gc_result = execute_gc_plan(gc_plan, dry_run=cfg.gc_dry_run) if gc_plan else {
                "deleted_files": 0,
                "deleted_bytes": 0,
                "error_count": 0,
                "errors_sample": [],
            }

            transfer_health_summary = build_archive_transfer_health_summary(
                cfg,
                copy_items=plan,
                copy_result=result,
                gc_items=gc_plan,
                gc_result=gc_result,
            )
            transfer_health_summary_path = write_archive_transfer_health_summary(cfg, transfer_health_summary)
            append_archive_audit(
                cfg,
                "archive.transfer_health_summary.updated",
                level="WARN" if transfer_health_summary.get("status") in {"warn", "crit"} else "INFO",
                extra={
                    "status": transfer_health_summary.get("status"),
                    "severity": transfer_health_summary.get("severity"),
                    "summary_path": str(transfer_health_summary_path),
                    "bad_file_count": len(transfer_health_summary.get("bad_files") or []),
                    "mismatch_count": (transfer_health_summary.get("integrity") or {}).get("mismatch_count"),
                    "missing_count": (transfer_health_summary.get("integrity") or {}).get("missing_count"),
                },
            )
            if gc_result["error_count"]:
                append_archive_audit(
                    cfg,
                    "archive.gc.error",
                    level="WARN",
                    extra={
                        "dry_run": cfg.gc_dry_run,
                        "plan_count": len(gc_plan),
                        **gc_result,
                    },
                )
            elif gc_plan:
                append_archive_audit(
                    cfg,
                    "archive.gc.completed",
                    extra={
                        "dry_run": cfg.gc_dry_run,
                        "plan_count": len(gc_plan),
                        **gc_result,
                    },
                )

            write_archive_gc_state(
                cfg,
                {
                    "mode": "RUNNING" if cfg.gc_enabled else "IDLE",
                    "current_phase": "gc_executing" if cfg.gc_enabled else "sleeping",
                    "started_at": worker_started_at,
                    "dry_run": cfg.gc_dry_run,
                    "enabled": cfg.gc_enabled,
                    "last_error": None if gc_result["error_count"] == 0 else "gc_error",
                    "last_scan_ts": now_iso_utc(),
                    "last_plan_count": len(gc_plan),
                    "last_deleted_files": gc_result["deleted_files"],
                    "last_deleted_bytes": gc_result["deleted_bytes"],
                    "error_count": gc_result["error_count"],
                    "plan_sample": gc_plan_sample,
                },
            )

            write_archive_copy_state(
                cfg,
                {
                    "mode": "RUNNING",
                    "current_phase": "sleeping",
                    "started_at": worker_started_at,
                    "last_error": None if result["error_count"] == 0 else "copy_error",
                    "last_scan_ts": now_iso_utc(),
                    "last_plan_count": len(plan),
                    "last_copied_files": result["copied_files"],
                    "last_copied_dirs": result["copied_dirs"],
                    "last_copied_bytes": result["copied_bytes"],
                    "error_count": result["error_count"],
                    "plan_sample": plan_sample,
                },
            )
            write_archive_gc_state(
                cfg,
                {
                    "mode": "RUNNING" if cfg.gc_enabled else "IDLE",
                    "current_phase": "sleeping",
                    "started_at": worker_started_at,
                    "dry_run": cfg.gc_dry_run,
                    "enabled": cfg.gc_enabled,
                    "last_error": None if gc_result["error_count"] == 0 else "gc_error",
                    "last_scan_ts": now_iso_utc(),
                    "last_plan_count": len(gc_plan),
                    "last_deleted_files": gc_result["deleted_files"],
                    "last_deleted_bytes": gc_result["deleted_bytes"],
                    "error_count": gc_result["error_count"],
                    "plan_sample": gc_plan_sample,
                },
            )

            time.sleep(cfg.scan_interval_sec)

        append_archive_audit(cfg, "archive.worker.stop", extra={"reason": "stop_requested"})
        write_archive_copy_state(
            cfg,
            {
                "mode": "STOPPED",
                "current_phase": "stopped",
                "started_at": worker_started_at,
                "last_error": None,
                "last_scan_ts": now_iso_utc(),
            },
        )
        write_archive_gc_state(
            cfg,
            {
                "mode": "STOPPED",
                "current_phase": "stopped",
                "started_at": worker_started_at,
                "dry_run": cfg.gc_dry_run,
                "enabled": cfg.gc_enabled,
                "last_error": None,
                "last_scan_ts": now_iso_utc(),
            },
        )
        return 0

    except KeyboardInterrupt:
        append_archive_audit(cfg, "archive.worker.stop", extra={"reason": "keyboard_interrupt"})
        write_archive_copy_state(
            cfg,
            {
                "mode": "STOPPED",
                "current_phase": "stopped",
                "started_at": worker_started_at,
                "last_error": None,
                "last_scan_ts": now_iso_utc(),
            },
        )
        write_archive_gc_state(
            cfg,
            {
                "mode": "STOPPED",
                "current_phase": "stopped",
                "started_at": worker_started_at,
                "dry_run": cfg.gc_dry_run,
                "enabled": cfg.gc_enabled,
                "last_error": None,
                "last_scan_ts": now_iso_utc(),
            },
        )
        return 0

    except Exception as exc:
        append_archive_audit(
            cfg,
            "archive.worker.exception",
            level="ERROR",
            extra={"error": str(exc)},
        )
        write_archive_copy_state(
            cfg,
            {
                "mode": "FAILED",
                "current_phase": "failed",
                "started_at": worker_started_at,
                "last_error": str(exc),
                "last_scan_ts": now_iso_utc(),
            },
        )
        write_archive_gc_state(
            cfg,
            {
                "mode": "FAILED",
                "current_phase": "failed",
                "started_at": worker_started_at,
                "dry_run": cfg.gc_dry_run,
                "enabled": cfg.gc_enabled,
                "last_error": str(exc),
                "last_scan_ts": now_iso_utc(),
            },
        )
        raise

    finally:
        clear_archive_stop_request(cfg)
        release_archive_worker_lock(cfg)


def main() -> int:
    code = run_forever()
    print(json.dumps({"ok": code == 0, "archive_worker": True, "exit_code": code}, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())