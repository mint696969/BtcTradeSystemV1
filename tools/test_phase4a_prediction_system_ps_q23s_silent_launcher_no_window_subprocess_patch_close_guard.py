# path: ./tools/test_phase4a_prediction_system_ps_q23s_silent_launcher_no_window_subprocess_patch_close_guard.py
# desc: Close guard for PS-Q23S Q22X subprocess no-window patch.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q23S_SILENT_LAUNCHER_NO_WINDOW_SUBPROCESS_PATCH_2026-06-29.md",
    "tools/run_phase4a_prediction_system_ps_q22x_silent_q22s_launcher.py",
    "tools/test_phase4a_prediction_system_ps_q23s_silent_launcher_no_window_subprocess_patch.py",
    "tools/test_phase4a_prediction_system_ps_q23s_silent_launcher_no_window_subprocess_patch_close_guard.py",
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
        "guard": "ps_q23s_silent_launcher_no_window_subprocess_patch_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED),
        "contract": {
            "scheduler_action_changed": False,
            "q22x_pythonw_action_retained": True,
            "subprocess_child_console_windows_suppressed": True,
            "latest_artifact_behavior_changed": False,
            "broker_autotrade": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
