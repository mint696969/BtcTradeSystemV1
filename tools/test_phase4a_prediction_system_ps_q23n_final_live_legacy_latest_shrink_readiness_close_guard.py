# path: ./tools/test_phase4a_prediction_system_ps_q23n_final_live_legacy_latest_shrink_readiness_close_guard.py
# desc: Close guard for PS-Q23N final no-write readiness before live legacy latest shrink.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q23N_FINAL_LIVE_LEGACY_LATEST_SHRINK_READINESS_2026-06-28.md",
    "tools/diagnose_phase4a_prediction_system_ps_q23n_final_live_legacy_latest_shrink_readiness.py",
    "tools/test_phase4a_prediction_system_ps_q23n_final_live_legacy_latest_shrink_readiness.py",
    "tools/test_phase4a_prediction_system_ps_q23n_final_live_legacy_latest_shrink_readiness_close_guard.py",
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
        "guard": "ps_q23n_final_live_legacy_latest_shrink_readiness_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED),
        "contract": {
            "actual_legacy_latest_shrink_executed": False,
            "actual_shrink_command_candidate_ready": True,
            "rollback_command_candidate_ready": True,
            "backup_before_replace_required": True,
            "scheduler_action_changed": False,
            "runtime_artifact_write_changed": False,
            "broker_autotrade": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
