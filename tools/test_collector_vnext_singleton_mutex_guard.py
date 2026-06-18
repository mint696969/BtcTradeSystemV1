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


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _safe_info(info: dict) -> dict:
    return {k: v for k, v in info.items() if k != "handle"}


def _normal_mutex_name(suffix: str) -> str:
    return "Local" + chr(92) + suffix


def _doubled_mutex_name(suffix: str) -> str:
    return "Local" + chr(92) + chr(92) + suffix


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
        "lock_has_name_normalizer": "def _normalize_windows_mutex_name" in lock_text,
        "lock_has_kernel32_mutex_prototypes": "def _kernel32_for_mutex" in lock_text,
        "lock_uses_create_mutex": "CreateMutexW" in lock_text and "ERROR_ALREADY_EXISTS" in lock_text,
        "lock_sets_win_handle_prototypes": "CreateMutexW.restype = wintypes.HANDLE" in lock_text and "CloseHandle.argtypes = (wintypes.HANDLE,)" in lock_text,
        "watchdog_imports_mutex": "acquire_process_singleton_mutex" in watchdog_text and "release_process_singleton_mutex" in watchdog_text,
        "daemon_imports_mutex": "acquire_process_singleton_mutex" in daemon_text and "release_process_singleton_mutex" in daemon_text,
        "archive_imports_mutex": "acquire_process_singleton_mutex" in archive_text and "release_process_singleton_mutex" in archive_text,
        "watchdog_mutex_suffix_present": "BTCTS_COLLECTOR_VNEXT_UNIFIED_WATCHDOG" in watchdog_text,
        "daemon_mutex_suffix_present": "BTCTS_COLLECTOR_VNEXT_UNIFIED_DAEMON" in daemon_text,
        "archive_mutex_suffix_present": "BTCTS_COLLECTOR_VNEXT_ARCHIVE_WORKER" in archive_text,
        "watchdog_releases_on_file_lock_failure": "release_process_singleton_mutex(singleton_info)" in watchdog_text,
        "daemon_releases_on_file_lock_failure": "release_process_singleton_mutex(singleton_info)" in daemon_text,
        "archive_releases_on_file_lock_failure": "release_process_singleton_mutex(singleton_info)" in archive_text,
    }
    failures.extend(f"check failed: {name}" for name, ok in static_checks.items() if not ok)

    mutex_name = _normal_mutex_name(f"BTCTS_COLLECTOR_VNEXT_SINGLETON_GUARD_{os.getpid()}")
    ok1, info1 = acquire_process_singleton_mutex(mutex_name)
    ok2, info2 = acquire_process_singleton_mutex(mutex_name)
    release_process_singleton_mutex(info1)
    ok3, info3 = acquire_process_singleton_mutex(mutex_name)
    release_process_singleton_mutex(info2)
    release_process_singleton_mutex(info3)

    doubled_mutex_name = _doubled_mutex_name(f"BTCTS_COLLECTOR_VNEXT_SINGLETON_GUARD_DOUBLE_{os.getpid()}")
    ok4, info4 = acquire_process_singleton_mutex(doubled_mutex_name)
    ok5, info5 = acquire_process_singleton_mutex(doubled_mutex_name)
    release_process_singleton_mutex(info4)
    ok6, info6 = acquire_process_singleton_mutex(doubled_mutex_name)
    release_process_singleton_mutex(info5)
    release_process_singleton_mutex(info6)

    runtime_checks = {
        "first_acquire_ok": ok1 is True,
        "second_acquire_blocked_on_windows": (ok2 is False and info2.get("already_running") is True) if os.name == "nt" else ok2 is True,
        "reacquire_after_release_ok": ok3 is True,
        "normal_mutex_no_invalid_name_123": info1.get("last_error") != 123 and info2.get("last_error") != 123 and info3.get("last_error") != 123,
        "doubled_separator_normalized_first_acquire_ok": ok4 is True,
        "doubled_separator_no_invalid_name_123": info4.get("last_error") != 123 and info5.get("last_error") != 123 and info6.get("last_error") != 123,
        "doubled_separator_second_acquire_blocked_on_windows": (ok5 is False and info5.get("already_running") is True) if os.name == "nt" else ok5 is True,
        "doubled_separator_reacquire_after_release_ok": ok6 is True,
        "doubled_separator_normalized_mutex_name_visible": str(info4.get("mutex_name") or "").count(chr(92)) == 1 if os.name == "nt" else True,
    }
    failures.extend(f"check failed: {name}" for name, ok in runtime_checks.items() if not ok)

    payload = {
        "ok": not failures,
        "phase": "collector_vnext_singleton_mutex_guard",
        "status": "closed" if not failures else "open",
        "contract": static_checks | runtime_checks,
        "sample": {
            "mutex_name": mutex_name,
            "first": _safe_info(info1),
            "second": _safe_info(info2),
            "third": _safe_info(info3),
            "doubled_mutex_name": doubled_mutex_name,
            "doubled_first": _safe_info(info4),
            "doubled_second": _safe_info(info5),
            "doubled_third": _safe_info(info6),
        },
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_collector_vnext_singleton_mutex_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
