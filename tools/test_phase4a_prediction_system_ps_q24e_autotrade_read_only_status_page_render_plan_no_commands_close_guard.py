# path: ./tools/test_phase4a_prediction_system_ps_q24e_autotrade_read_only_status_page_render_plan_no_commands_close_guard.py
# desc: Close guard for PS-Q24E AutoTrade read-only status page render-plan/no commands slice.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/autotrade_prediction_status_page_render_plan.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q24E_AUTOTRADE_READ_ONLY_STATUS_PAGE_RENDER_PLAN_NO_COMMANDS_2026-06-29.md",
    "tools/diagnose_phase4a_prediction_system_ps_q23r_closeout_steady_state_guard_sync.py",
    "tools/diagnose_phase4a_prediction_system_ps_q24e_autotrade_read_only_status_page_render_plan_no_commands.py",
    "tools/test_phase4a_prediction_system_ps_q24e_autotrade_read_only_status_page_render_plan_no_commands.py",
    "tools/test_phase4a_prediction_system_ps_q24e_autotrade_read_only_status_page_render_plan_no_commands_close_guard.py",
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
        "guard": "ps_q24e_autotrade_read_only_status_page_render_plan_no_commands_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED_DIRTY - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY),
        "contract": {
            "q24d_page_section_packet_ready": True,
            "render_plan_packet_component_added": True,
            "autotrade_page_not_modified": True,
            "render_plan_not_wired_to_page": True,
            "render_plan_packet_only": True,
            "read_only_diagnostic": True,
            "ui_runtime_wiring_changed": False,
            "ui_rendering_added": False,
            "command_buttons_added": False,
            "forms_added": False,
            "session_state_added": False,
            "callbacks_added": False,
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
