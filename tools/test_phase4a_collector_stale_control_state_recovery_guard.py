# path: ./tools/test_phase4a_collector_stale_control_state_recovery_guard.py
# desc: Guard stale Collector control state recovery after PC reboot.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from btcts.collector_vnext import stack_control as sc


class _FakeCollectorConfig:
    def __init__(self, root: Path):
        self._state = root / "state" / "collector_vnext"
        self.data_root = root / "data"
        self.logs_root = root / "logs"
        self.state_root = root / "state"
        self._state.mkdir(parents=True, exist_ok=True)

    def roots(self):
        return {"state": self._state}


class _FakeArchiveConfig:
    def __init__(self, root: Path):
        self.hot_root = root


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        cfg = _FakeCollectorConfig(root)
        archive_cfg = _FakeArchiveConfig(root)
        state = cfg.roots()["state"]
        now = _now()

        _write(state / "unified_supervisor.lock.json", {"pid": 999991, "command": "python -m btcts.collector_vnext.unified_watchdog"})
        _write(state / "unified_daemon.lock.json", {"pid": 999992, "command": "python -m btcts.collector_vnext.unified_daemon"})
        _write(state / "archive_worker.lock.json", {"pid": 999993, "command": "python -m btcts.collector_vnext.archive.worker"})
        _write(state / "unified_supervisor_request.json", {"action": "stop_stack", "requested_at": now})
        _write(state / "archive_stop_request.json", {"action": "stop", "requested_at": now})
        _write(
            state / "unified_supervisor_status.json",
            {"ts": now, "mode": "ARCHIVE_DRAINING", "supervisor_pid": 999991, "daemon_pid": None, "last_seen_ts": now},
        )
        _write(state / "archive_copy_state.json", {"ts": now, "mode": "RUNNING", "current_phase": "copy_executing"})
        _write(state / "archive_gc_state.json", {"ts": now, "mode": "RUNNING", "current_phase": "gc_executing"})

        original_load_config = sc.load_config
        original_load_archive_config = sc.load_archive_config
        original_is_pid_alive = sc.is_pid_alive
        try:
            sc.load_config = lambda: cfg
            sc.load_archive_config = lambda: archive_cfg
            sc.is_pid_alive = lambda pid: False

            snapshot = sc.stack_runtime_snapshot()
        finally:
            sc.load_config = original_load_config
            sc.load_archive_config = original_load_archive_config
            sc.is_pid_alive = original_is_pid_alive

        assert snapshot["stale_control_state_recovered"] is True, snapshot
        assert snapshot["stack_active"] is False, snapshot
        assert snapshot["supervisor_active"] is False, snapshot
        assert snapshot["archive_active"] is False, snapshot
        assert snapshot["pending_action"] == "", snapshot
        assert snapshot["supervisor_mode"] == "STOPPED", snapshot
        assert snapshot["archive_copy_mode"] == "STOPPED", snapshot
        assert snapshot["archive_gc_mode"] == "STOPPED", snapshot
        assert not (state / "unified_supervisor.lock.json").exists()
        assert not (state / "unified_daemon.lock.json").exists()
        assert not (state / "archive_worker.lock.json").exists()
        assert not (state / "unified_supervisor_request.json").exists()
        assert not (state / "archive_stop_request.json").exists()
        backup_dir = snapshot.get("stale_control_state_backup_dir")
        assert backup_dir and Path(backup_dir).exists(), snapshot

    print(json.dumps({"ok": True, "guard": "collector_stale_control_state_recovery"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
