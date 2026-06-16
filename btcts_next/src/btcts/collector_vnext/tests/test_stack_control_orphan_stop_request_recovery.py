# path: ./btcts_next/src/btcts/collector_vnext/tests/test_stack_control_orphan_stop_request_recovery.py
# desc: Pytest-free guard for orphan stop_stack request recovery in stack_control.

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.collector_vnext import stack_control  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="btcts_stack_recovery_") as td:
        state_dir = Path(td) / "state" / "collector_vnext"
        state_dir.mkdir(parents=True, exist_ok=True)
        (state_dir / "unified_supervisor_request.json").write_text(
            json.dumps(
                {
                    "request_id": "unit-stop",
                    "action": "stop_stack",
                    "requested_at": "2026-06-14T00:00:00Z",
                    "requested_by": "operator_ui",
                    "reason": "maintenance_safe_stop",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (state_dir / "unified_supervisor_status.json").write_text(
            json.dumps(
                {
                    "mode": "FAILED",
                    "last_action": "restart",
                    "last_error": "too_many_failures=10",
                    "supervisor_pid": 99999999,
                    "daemon_pid": 99999998,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        result = stack_control._reconcile_stale_control_state_if_safe(
            state_dir=state_dir,
            supervisor_status={
                "mode": "FAILED",
                "last_action": "restart",
                "last_error": "too_many_failures=10",
                "supervisor_pid": 99999999,
                "daemon_pid": 99999998,
            },
            supervisor_request={
                "request_id": "unit-stop",
                "action": "stop_stack",
                "requested_at": "2026-06-14T00:00:00Z",
                "requested_by": "operator_ui",
            },
            archive_copy_state={"mode": "STOPPED"},
            archive_gc_state={"mode": "STOPPED"},
            supervisor_lock={},
            daemon_lock={},
            archive_lock={},
        )

        assert result["stale_control_state_recovered"] is True, result
        assert result["orphan_stop_stack_request_recovered"] is True, result
        assert not (state_dir / "unified_supervisor_request.json").exists()
        status = json.loads((state_dir / "unified_supervisor_status.json").read_text(encoding="utf-8"))
        assert status["mode"] == "STOPPED", status
        assert status["last_action"] == "auto_stale_control_state_recovery", status

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
