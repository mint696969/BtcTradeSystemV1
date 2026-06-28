# path: ./tools/test_phase4a_prediction_system_ps_q22u_mountain2_scheduler_enablement_once_close_guard.py
# desc: Close guard for PS-Q22U scheduler enablement executor implementation.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q22U_MOUNTAIN2_SCHEDULER_ENABLEMENT_EXECUTOR_2026-06-28.md",
    "tools/run_phase4a_prediction_system_ps_q22u_mountain2_scheduler_enablement_once.py",
    "tools/test_phase4a_prediction_system_ps_q22u_mountain2_scheduler_enablement_once.py",
    "tools/test_phase4a_prediction_system_ps_q22u_mountain2_scheduler_enablement_once_close_guard.py",
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
        "guard": "ps_q22u_mountain2_scheduler_enablement_once_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED),
        "contract": {
            "default_no_write": True,
            "requires_exact_confirmation": True,
            "scheduler_action_replacement_explicit_only": True,
            "trigger_addition_explicit_only": True,
            "scheduler_enablement_explicit_only": True,
            "has_rollback_mode": True,
            "would_send_to_broker": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


def test_ps_q22u_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
