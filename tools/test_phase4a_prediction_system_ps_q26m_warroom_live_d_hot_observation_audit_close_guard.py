# path: ./tools/test_phase4a_prediction_system_ps_q26m_warroom_live_d_hot_observation_audit_close_guard.py
# desc: Close guard for PS-Q26M WarRoom live D-hot observation audit.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q26M_WARROOM_LIVE_D_HOT_OBSERVATION_AUDIT_2026-07-01.md",
    "tools/diagnose_phase4a_prediction_system_ps_q26m_warroom_live_d_hot_observation_audit.py",
    "tools/test_phase4a_prediction_system_ps_q26m_warroom_live_d_hot_observation_audit.py",
    "tools/test_phase4a_prediction_system_ps_q26m_warroom_live_d_hot_observation_audit_close_guard.py",
}


def _dirty() -> set[str]:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    paths: set[str] = set()
    for line in proc.stdout.splitlines():
        path = line[3:].strip().replace(chr(92), "/")
        if path.startswith("tmp/work/") or path.startswith("tmp/gpt_room/") or "/__pycache__/" in path or path.endswith(".pyc"):
            continue
        paths.add(path)
    return paths


def main_guard() -> int:
    dirty = _dirty()
    result = {
        "ok": dirty == EXPECTED_DIRTY,
        "guard": "ps_q26m_warroom_live_d_hot_observation_audit_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED_DIRTY - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY),
        "contract": {
            "selected_human_lane": "B_WARROOM_DATA_FRESHNESS_LIVE_D_HOT_OBSERVATION_AUDIT",
            "production_ui_code_changed": False,
            "warroom_ui_cleanup_deferred": True,
            "ready_for_ui_visual_cleanup_intake": True,
            "read_only": True,
            "display_only": True,
            "non_executing": True,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "ledger_append": False,
            "mode_apply": False,
            "parameter_apply": False,
            "would_send_to_broker": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
