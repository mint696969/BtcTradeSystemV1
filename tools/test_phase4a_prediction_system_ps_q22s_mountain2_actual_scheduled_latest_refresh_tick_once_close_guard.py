# path: ./tools/test_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once_close_guard.py
# desc: Close guard for PS-Q22S actual Mountain2 one-tick runner no scheduler enablement.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q22S_MOUNTAIN2_ACTUAL_TICK_RUNNER_NO_SCHEDULER_ENABLEMENT_2026-06-28.md",
    "tools/run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py",
    "tools/test_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py",
    "tools/test_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once_close_guard.py",
}


def _dirty() -> set[str]:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        path = line[3:].strip().replace(chr(92), "/")
        if path.startswith("tmp/work/") or path.startswith("tmp/gpt_room/") or path.endswith(".pyc") or "/__pycache__/" in path:
            continue
        out.add(path)
    return out


def main_guard() -> int:
    dirty = _dirty()
    result = {
        "ok": dirty == EXPECTED,
        "guard": "ps_q22s_mountain2_actual_tick_runner_no_scheduler_enablement_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED),
        "contract": {
            "actual_tick_runner_implemented": True,
            "post_refresh_q22e_design_packet": True,
            "default_no_write": True,
            "lock_acquire_explicit_only": True,
            "latest_prediction_artifact_write_explicit_only": True,
            "status_artifact_write_explicit_only": True,
            "scheduler_action_replacement_executed": False,
            "scheduler_enabled": False,
            "trigger_added": False,
            "recurring_enablement_allowed_now": False,
            "periodic_execution_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "would_send_to_broker": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


def test_ps_q22s_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
