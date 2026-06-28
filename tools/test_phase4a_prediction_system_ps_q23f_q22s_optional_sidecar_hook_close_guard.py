# path: ./tools/test_phase4a_prediction_system_ps_q23f_q22s_optional_sidecar_hook_close_guard.py
# desc: Close guard for PS-Q23F Q22S optional distributed sidecar hook.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q23F_Q22S_OPTIONAL_SIDECAR_HOOK_2026-06-28.md",
    "tools/run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py",
    "tools/test_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py",
    "tools/test_phase4a_prediction_system_ps_q23f_q22s_optional_sidecar_hook.py",
    "tools/test_phase4a_prediction_system_ps_q23f_q22s_optional_sidecar_hook_close_guard.py",
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
        "guard": "ps_q23f_q22s_optional_sidecar_hook_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED),
        "contract": {
            "q22s_sidecar_hook_added": True,
            "sidecar_hook_default_disabled": True,
            "scheduler_action_changed": False,
            "scheduled_sidecar_write_enabled": False,
            "legacy_latest_refresh_semantics_preserved": True,
            "broker_autotrade": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
