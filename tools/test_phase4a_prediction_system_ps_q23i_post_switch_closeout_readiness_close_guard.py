# path: ./tools/test_phase4a_prediction_system_ps_q23i_post_switch_closeout_readiness_close_guard.py
# desc: Close guard for PS-Q23I post-switch closeout/readiness diagnostic.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q23I_POST_SWITCH_CLOSEOUT_READINESS_2026-06-28.md",
    "tools/diagnose_phase4a_prediction_system_ps_q23i_post_switch_closeout_readiness.py",
    "tools/test_phase4a_prediction_system_ps_q23i_post_switch_closeout_readiness.py",
    "tools/test_phase4a_prediction_system_ps_q23i_post_switch_closeout_readiness_close_guard.py",
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
        "guard": "ps_q23i_post_switch_closeout_readiness_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED),
        "contract": {
            "read_only_closeout": True,
            "rollback_plan_only": True,
            "reader_default_change_ready_check_only": True,
            "scheduler_action_changed_by_this_tool": False,
            "writes_d_hot_runtime_artifacts": False,
            "broker_autotrade": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
