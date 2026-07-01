# path: ./tools/test_phase4a_prediction_system_ps_q26n_warroom_operator_focus_nav_close_guard.py
# desc: Close guard for PS-Q26N WarRoom operator focus navigation.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_operator_focus_nav_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_operator_focus_nav_q26n.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q26N_WARROOM_OPERATOR_FOCUS_NAV_2026-07-01.md",
    "tools/diagnose_phase4a_prediction_system_ps_q26n_warroom_operator_focus_nav.py",
    "tools/test_phase4a_prediction_system_ps_q26n_warroom_operator_focus_nav.py",
    "tools/test_phase4a_prediction_system_ps_q26n_warroom_operator_focus_nav_close_guard.py",
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
        "guard": "ps_q26n_warroom_operator_focus_nav_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED_DIRTY - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY),
        "contract": {
            "production_ui_code_changed": True,
            "warroom_page_change_boundary": "import_and_single_render_call_only",
            "externalized_panel_module": True,
            "layout_only_change": True,
            "operator_first_navigation_visible": True,
            "top_expanded_default": True,
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
