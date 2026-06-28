# path: ./tools/test_phase4a_prediction_system_ps_q22x_silent_scheduler_launcher_close_guard.py
# desc: Close guard for PS-Q22X silent launcher repo patch.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q22X_SILENT_SCHEDULER_LAUNCHER_2026-06-28.md",
    "tools/run_phase4a_prediction_system_ps_q22x_silent_q22s_launcher.py",
    "tools/run_phase4a_prediction_system_ps_q22x_switch_scheduler_action_to_silent_once.py",
    "tools/test_phase4a_prediction_system_ps_q22x_silent_scheduler_launcher.py",
    "tools/test_phase4a_prediction_system_ps_q22x_silent_scheduler_launcher_close_guard.py",
    "tools/diagnose_phase4a_prediction_system_ps_q22v_post_enablement_tick_readiness.py",
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
        "guard": "ps_q22x_silent_scheduler_launcher_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED),
        "contract": {
            "uses_pythonw_exe": True,
            "redirects_stdout_stderr_to_log": True,
            "scheduler_action_replacement_explicit_only": True,
            "trigger_addition_executed": False,
            "latest_prediction_artifact_written_by_patch": False,
            "would_send_to_broker": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


def test_ps_q22x_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
