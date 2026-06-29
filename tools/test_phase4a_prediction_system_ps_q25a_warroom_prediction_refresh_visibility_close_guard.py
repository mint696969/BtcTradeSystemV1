# path: ./tools/test_phase4a_prediction_system_ps_q25a_warroom_prediction_refresh_visibility_close_guard.py
# desc: Close guard for PS-Q25A WarRoom prediction refresh visibility slice.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q25A_WARROOM_PREDICTION_REFRESH_VISIBILITY_2026-06-30.md",
    "tools/diagnose_phase4a_prediction_system_ps_q25a_warroom_prediction_refresh_visibility.py",
    "tools/test_phase4a_prediction_system_ps_q25a_warroom_prediction_refresh_visibility.py",
    "tools/test_phase4a_prediction_system_ps_q25a_warroom_prediction_refresh_visibility_close_guard.py",
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
        "guard": "ps_q25a_warroom_prediction_refresh_visibility_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED_DIRTY - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY),
        "contract": {
            "warroom_prediction_panel_update_visibility_added": True,
            "prediction_data_generated_at_visible": True,
            "prediction_data_generated_at_jst_visible": True,
            "panel_refresh_heartbeat_jst_visible": True,
            "prediction_data_generation_and_panel_refresh_separated": True,
            "fragment_flag_status_uses_actual_render_argument": True,
            "warroom_display_only": True,
            "autotrade_page_not_modified": True,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "scheduler_action_changed": False,
            "scheduler_enabled": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "ledger_append": False,
            "mode_apply": False,
            "parameter_apply": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
