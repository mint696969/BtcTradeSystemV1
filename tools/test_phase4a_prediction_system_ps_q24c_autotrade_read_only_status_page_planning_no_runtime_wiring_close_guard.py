# path: ./tools/test_phase4a_prediction_system_ps_q24c_autotrade_read_only_status_page_planning_no_runtime_wiring_close_guard.py
# desc: Close guard for PS-Q24C AutoTrade read-only status page planning / no runtime wiring slice.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q24C_AUTOTRADE_READ_ONLY_STATUS_PAGE_PLANNING_NO_RUNTIME_WIRING_2026-06-29.md",
    "tools/diagnose_phase4a_prediction_system_ps_q23r_closeout_steady_state_guard_sync.py",
    "tools/diagnose_phase4a_prediction_system_ps_q24c_autotrade_read_only_status_page_planning_no_runtime_wiring.py",
    "tools/test_phase4a_prediction_system_ps_q24c_autotrade_read_only_status_page_planning_no_runtime_wiring.py",
    "tools/test_phase4a_prediction_system_ps_q24c_autotrade_read_only_status_page_planning_no_runtime_wiring_close_guard.py",
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
        "guard": "ps_q24c_autotrade_read_only_status_page_planning_no_runtime_wiring_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED_DIRTY - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY),
        "contract": {
            "q24b_display_compat_ready": True,
            "autotrade_page_not_modified": True,
            "prediction_status_display_not_wired_to_page": True,
            "existing_command_surface_acknowledged": True,
            "planning_only": True,
            "read_only_diagnostic": True,
            "ui_runtime_wiring_changed": False,
            "streamlit_rendering_added": False,
            "command_buttons_added": False,
            "runtime_artifact_write_changed": False,
            "shadow_decision_append": False,
            "mode_apply": False,
            "ledger_append": False,
            "broker_autotrade": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
