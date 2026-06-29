# path: ./tools/test_phase4a_prediction_system_ps_q23r_closeout_steady_state_guard_sync_close_guard.py
# desc: Close guard for PS-Q23R closeout and steady-state guard sync slice.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q23R_CLOSEOUT_AND_STEADY_STATE_GUARD_SYNC_2026-06-29.md",
    "tools/diagnose_phase4a_prediction_system_ps_q23r_closeout_steady_state_guard_sync.py",
    "tools/test_phase4a_prediction_system_ps_q23r_closeout_steady_state_guard_sync.py",
    "tools/test_phase4a_prediction_system_ps_q23r_closeout_steady_state_guard_sync_close_guard.py",
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
        "ok": dirty == EXPECTED_DIRTY,
        "guard": "ps_q23r_closeout_steady_state_guard_sync_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED_DIRTY - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY),
        "contract": {
            "canonical_reentry": "PS_Q23R_AFTER_SCHEDULED_COMPACT_LEGACY_STEADY_STATE",
            "room_focus_synced": True,
            "legacy_latest_compact_after_scheduled_tick": True,
            "latest_manifest_full_sidecars_retained": True,
            "read_only_diagnostic": True,
            "scheduler_action_changed": False,
            "runtime_artifact_write_changed": False,
            "broker_autotrade": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
