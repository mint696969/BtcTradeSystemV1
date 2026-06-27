# path: ./tools/test_phase4a_prediction_system_ps_q22g_shadow_once_status_writer_design_close_guard.py
# desc: Close guard for PS-Q22G shadow-once status writer design.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q22G_SHADOW_ONCE_STATUS_WRITER_DESIGN_2026-06-27.md",
    "tools/diagnose_phase4a_prediction_system_ps_q22g_shadow_once_status_writer_design.py",
    "tools/test_phase4a_prediction_system_ps_q22g_shadow_once_status_writer_design.py",
    "tools/test_phase4a_prediction_system_ps_q22g_shadow_once_status_writer_design_close_guard.py",
}


def _dirty() -> set[str]:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out = set()
    for line in proc.stdout.splitlines():
        p = line[2:].strip().replace(chr(92), "/")
        if p.startswith("tmp/work/") or p.startswith("tmp/gpt_room/") or p.endswith(".pyc") or "/__pycache__/" in p:
            continue
        out.add(p)
    return out


def main_guard() -> int:
    dirty = _dirty()
    result = {
        "ok": dirty == EXPECTED,
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED),
        "contract": {
            "read_only_no_write": True,
            "future_shadow_once_uses_q22e_status_writer": True,
            "q16b_scaffold_status_not_future_target": True,
            "latest_prediction_artifact_written": False,
            "producer_loop_enabled": False,
            "scheduler_enabled": False,
            "trigger_added": False,
            "recurring_enablement_allowed_now": False,
            "would_send_to_broker": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


def test_ps_q22g_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
