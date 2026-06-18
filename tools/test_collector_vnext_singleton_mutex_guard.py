# path: ./tools/test_collector_vnext_singleton_mutex_guard.py
# desc: Guard collector_vnext archive/watchdog/daemon use OS-level singleton mutexes to prevent duplicate .venv/system-Python stacks.

from __future__ import annotations

import ast
import json
import os
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

from btcts.collector_vnext.lock import (
    acquire_process_singleton_mutex,
    release_process_singleton_mutex,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
LOCK = REPO_ROOT / "btcts_next/src/btcts/collector_vnext/lock.py"
WATCHDOG = REPO_ROOT / "btcts_next/src/btcts/collector_vnext/unified_watchdog.py"
DAEMON = REPO_ROOT / "btcts_next/src/btcts/collector_vnext/unified_daemon.py"
ARCHIVE = REPO_ROOT / "btcts_next/src/btcts/collector_vnext/archive/worker.py"
EXPECTED_MUTEX_NAMES = {
    "watchdog": r"Local\BTCTS_COLLECTOR_VNEXT_UNIFIED_WATCHDOG",
    "daemon": r"Local\BTCTS_COLLECTOR_VNEXT_UNIFIED_DAEMON",
    "archive": r"Local\BTCTS_COLLECTOR_VNEXT_ARCHIVE_WORKER",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    for target in (LOCK, WATCHDOG, DAEMON, ARCHIVE):
        try:
            ast.parse(_text(target), filename=str(target))
            compile(_text(target), str(target), "exec")
        except Exception as exc:
            failures.append(f"syntax/compile failed: {target.relative_to(REPO_ROOT)}: {exc}")

    lock_text = _text(LOCK)
    watchdog_text = _text(WATCHDOG)
    daemon_text = _text(DAEMON)
    archive_text = _text(ARCHIVE)
    static_checks = {
        "lock_has_acquire_helper": "def acquire_process_singleton_mutex" in lock_text,
        "lock_has_release_helper": "def release_process_singleton_mutex" in lock_text,
        "lock_uses_create_mutex": "CreateMutexW" in lock_text and "ERROR_ALREADY_EXISTS" in lock_text,
        "lock_sets_win_handle_prototypes": "CreateMutexW.restype = wintypes.HANDLE" in lock_text and "CloseHandle.argtypes = (wintypes.HANDLE,)" in lock_text,
        "watchdog_imports_mutex": "acquire_process_singleton_mutex" in watchdog_text and "release_process_singleton_mutex" in watchdog_text,
        "daemon_imports_mutex": "acquire_process_singleton_mutex" in daemon_text and "release_process_singleton_mutex" in daemon_text,
        "archive_imports_mutex": "acquire_process_singleton_mutex" in archive_text and "release_process_singleton_mutex" in archive_text,
        "watchdog_mutex_name": EXPECTED_MUTEX_NAMES["watchdog"] in watchdog_text,
        "daemon_mutex_name": EXPECTED_MUTEX_NAMES["daemon"] in daemon_text,
        "archive_mutex_name": EXPECTED_MUTEX_NAMES["archive"] in archive_text,
        "watchdog_releases_on_file_lock_failure": "release_process_singleton_mutex(singleton_info)" in watchdog_text,
        "daemon_releases_on_file_lock_failure": "release_process_singleton_mutex(singleton_info)" in daemon_text,
        "archive_releases_on_file_lock_failure": "release_process_singleton_mutex(singleton_info)" in archive_text,
    }
    failures.extend(f"check failed: {name}" for name, ok in static_checks.items() if not ok)

    mutex_name = rf"Local\BTCTS_COLLECTOR_VNEXT_SINGLETON_GUARD_{os.getpid()}"
    ok1, info1 = acquire_process_singleton_mutex(mutex_name)
    ok2, info2 = acquire_process_singleton_mutex(mutex_name)
    release_process_singleton_mutex(info1)
    ok3, info3 = acquire_process_singleton_mutex(mutex_name)
    release_process_singleton_mutex(info2)
    release_process_singleton_mutex(info3)

    runtime_checks = {
        "first_acquire_ok": ok1 is True,
        "second_acquire_blocked_on_windows": (ok2 is False and info2.get("already_running") is True) if os.name == "nt" else ok2 is True,
        "reacquire_after_release_ok": ok3 is True,
    }
    failures.extend(f"check failed: {name}" for name, ok in runtime_checks.items() if not ok)

    payload = {
        "ok": not failures,
        "phase": "collector_vnext_singleton_mutex_guard",
        "status": "closed" if not failures else "open",
        "contract": static_checks | runtime_checks,
        "sample": {
            "mutex_name": mutex_name,
            "first": {k: v for k, v in info1.items() if k != "handle"},
            "second": {k: v for k, v in info2.items() if k != "handle"},
            "third": {k: v for k, v in info3.items() if k != "handle"},
        },
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_collector_vnext_singleton_mutex_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
