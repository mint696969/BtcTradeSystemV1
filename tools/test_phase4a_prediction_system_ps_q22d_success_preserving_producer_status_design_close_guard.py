# path: ./tools/test_phase4a_prediction_system_ps_q22d_success_preserving_producer_status_design_close_guard.py
# desc: Close guard for PS-Q22D success-preserving producer status design.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q22D_SUCCESS_PRESERVING_PRODUCER_STATUS_DESIGN_2026-06-27.md",
    "tools/diagnose_phase4a_prediction_system_ps_q22d_success_preserving_producer_status_design.py",
    "tools/test_phase4a_prediction_system_ps_q22d_success_preserving_producer_status_design.py",
    "tools/test_phase4a_prediction_system_ps_q22d_success_preserving_producer_status_design_close_guard.py",
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
            "preserves_last_success_generated_at": True,
            "preserves_last_prediction_run_id": True,
            "producer_loop_enabled": False,
            "scheduler_enabled": False,
            "trigger_added": False,
            "recurring_enablement_allowed_now": False,
            "would_send_to_broker": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


def test_ps_q22d_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
