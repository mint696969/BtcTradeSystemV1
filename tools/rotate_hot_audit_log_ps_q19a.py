# path: ./tools/rotate_hot_audit_log_ps_q19a.py
# desc: PS-Q19A guarded maintenance tool to rotate the active D-hot audit.jsonl into an archive path and create a small active audit marker file. Dry-run by default; no delete/compress.

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

ACK = "PS_Q19A_ROTATE_HOT_AUDIT_LOG"
DEFAULT_ROOT = Path(r"D:\btc_ts_hot")
DEFAULT_MIN_SIZE_BYTES = 1024 * 1024 * 1024  # 1 GiB


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _safe_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _date_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _as_root(path_text: str) -> Path:
    return Path(path_text).expanduser().resolve()


def _validate_root(root: Path, *, allow_test_root: bool) -> list[str]:
    blockers: list[str] = []
    expected = DEFAULT_ROOT.resolve()
    if root != expected and not allow_test_root:
        blockers.append(f"root_must_be_D_btc_ts_hot_or_allow_test_root: {root}")
    if root.anchor and root.drive and str(root.drive).upper() != "D:" and not allow_test_root:
        blockers.append(f"root_drive_must_be_D: {root}")
    return blockers


@contextmanager
def _file_lock(target_path: Path, *, timeout_sec: float = 10.0, stale_sec: float = 60.0):
    lock_path = Path(str(target_path) + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + float(timeout_sec)
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            try:
                os.write(fd, f"pid={os.getpid()} ts={time.time()}\n".encode("utf-8"))
                os.fsync(fd)
            finally:
                os.close(fd)
            break
        except FileExistsError:
            try:
                age = time.time() - lock_path.stat().st_mtime
                if age >= float(stale_sec):
                    lock_path.unlink(missing_ok=True)
                    continue
            except Exception:
                pass
            if time.time() >= deadline:
                raise TimeoutError(f"lock timeout: {lock_path}")
            time.sleep(0.05)
    try:
        yield
    finally:
        try:
            lock_path.unlink(missing_ok=True)
        except Exception:
            pass


def _marker_row(*, archive_path: Path, original_size: int, dry_run: bool) -> dict:
    return {
        "ts": _utc_iso(),
        "mode": "NORMAL",
        "event": "audit.rotation.ps_q19a.completed" if not dry_run else "audit.rotation.ps_q19a.dry_run",
        "feature": "audit_retention",
        "level": "INFO",
        "actor": "tools.rotate_hot_audit_log_ps_q19a",
        "site": "tools.rotate_hot_audit_log_ps_q19a.main",
        "trace_id": f"ps_q19a_{_safe_stamp()}",
        "payload": {
            "ok": not dry_run,
            "dry_run": dry_run,
            "archive_path": str(archive_path),
            "original_size_bytes": original_size,
            "delete_performed": False,
            "compress_performed": False,
            "would_send_to_broker": False,
        },
        "meta": {"pid": os.getpid(), "host": os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or ""},
    }


def rotate_hot_audit(
    *,
    root: Path,
    execute: bool,
    ack: str,
    min_size_bytes: int,
    allow_test_root: bool,
) -> dict:
    blockers = _validate_root(root, allow_test_root=allow_test_root)
    audit_path = root / "logs" / "audit.jsonl"
    archive_dir = root / "logs" / "audit" / "archive" / f"date={_date_key()}"
    archive_path = archive_dir / f"audit_{_safe_stamp()}.jsonl"

    exists = audit_path.exists()
    size = audit_path.stat().st_size if exists else 0
    dry_run = not execute

    if not exists:
        blockers.append(f"active_audit_missing: {audit_path}")
    if size < int(min_size_bytes):
        blockers.append(f"active_audit_below_min_size_bytes: size={size} min={int(min_size_bytes)}")
    if execute and ack != ACK:
        blockers.append("explicit_ack_required")
    if archive_path.exists():
        blockers.append(f"archive_path_already_exists: {archive_path}")

    result = {
        "ok": not blockers,
        "tool": "rotate_hot_audit_log_ps_q19a",
        "dry_run": dry_run,
        "execute_requested": execute,
        "root": str(root),
        "active_audit_path": str(audit_path),
        "active_audit_exists": exists,
        "active_audit_size_bytes": size,
        "archive_path": str(archive_path),
        "min_size_bytes": int(min_size_bytes),
        "delete_performed": False,
        "compress_performed": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "would_send_to_broker": False,
        "blockers": blockers,
    }

    if blockers or dry_run:
        return result

    with _file_lock(audit_path, timeout_sec=10.0):
        # Re-check inside lock to avoid racing the live appender.
        if not audit_path.exists():
            result["ok"] = False
            result["blockers"] = [f"active_audit_missing_after_lock: {audit_path}"]
            return result
        size_after_lock = audit_path.stat().st_size
        if size_after_lock < int(min_size_bytes):
            result["ok"] = False
            result["blockers"] = [
                f"active_audit_below_min_size_bytes_after_lock: size={size_after_lock} min={int(min_size_bytes)}"
            ]
            result["active_audit_size_bytes"] = size_after_lock
            return result

        archive_dir.mkdir(parents=True, exist_ok=True)
        audit_path.replace(archive_path)
        marker = _marker_row(archive_path=archive_path, original_size=size_after_lock, dry_run=False)
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        with open(audit_path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(marker, ensure_ascii=False, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())

    result.update(
        {
            "ok": True,
            "active_audit_size_bytes_after": audit_path.stat().st_size if audit_path.exists() else None,
            "archive_exists_after": archive_path.exists(),
            "archive_size_bytes_after": archive_path.stat().st_size if archive_path.exists() else None,
            "marker_written": True,
        }
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q19A guarded hot audit rotation tool")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="hot root; default D:\\btc_ts_hot")
    parser.add_argument("--execute", action="store_true", help="perform rotation; omitted means dry-run")
    parser.add_argument("--ack", default="", help=f"required for --execute: {ACK}")
    parser.add_argument("--min-size-bytes", type=int, default=DEFAULT_MIN_SIZE_BYTES)
    parser.add_argument("--allow-test-root", action="store_true", help="only for tests/guards")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = rotate_hot_audit(
        root=_as_root(args.root),
        execute=bool(args.execute),
        ack=str(args.ack or ""),
        min_size_bytes=int(args.min_size_bytes),
        allow_test_root=bool(args.allow_test_root),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
