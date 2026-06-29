# path: ./tools/test_phase4a_prediction_system_ps_q23q_scheduled_tick_compact_legacy_after_sidecars_close_guard.py
# desc: Close guard for PS-Q23Q scheduled tick compact legacy latest after sidecars.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q23Q_SCHEDULED_TICK_COMPACT_LEGACY_AFTER_SIDECARS_2026-06-29.md",
    "tools/run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py",
    "tools/test_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py",
    "tools/test_phase4a_prediction_system_ps_q23q_scheduled_tick_compact_legacy_after_sidecars.py",
    "tools/test_phase4a_prediction_system_ps_q23q_scheduled_tick_compact_legacy_after_sidecars_close_guard.py",
}
FORBIDDEN = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q23P_ACTUAL_LEGACY_LATEST_SHRINK_CLOSEOUT_2026-06-28.md",
    "tools/diagnose_phase4a_prediction_system_ps_q23p_actual_legacy_latest_shrink_closeout.py",
    "tools/test_phase4a_prediction_system_ps_q23p_actual_legacy_latest_shrink_closeout.py",
    "tools/test_phase4a_prediction_system_ps_q23p_actual_legacy_latest_shrink_closeout_close_guard.py",
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
        "ok": dirty == EXPECTED and not (dirty & FORBIDDEN),
        "guard": "ps_q23q_scheduled_tick_compact_legacy_after_sidecars_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED),
        "forbidden_q23p_dirty": sorted(dirty & FORBIDDEN),
        "contract": {
            "scheduled_sidecar_dual_write_required": True,
            "compact_legacy_latest_after_sidecar": True,
            "legacy_latest_backup_per_tick": False,
            "scheduler_action_changed": False,
            "trigger_added": False,
            "broker_autotrade": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
