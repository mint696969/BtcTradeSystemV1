# path: ./tools/test_phase4a_prediction_system_ps_q22w_recurring_failure_preserve_success_close_guard.py
# desc: Close guard for PS-Q22W recurring failure preservation.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q22W_RECURRING_FAILURE_PRESERVE_SUCCESS_2026-06-28.md",
    "tools/run_phase4a_prediction_system_ps_q22s_mountain2_actual_scheduled_latest_refresh_tick_once.py",
    "tools/diagnose_phase4a_prediction_system_ps_q22v_post_enablement_tick_readiness.py",
    "tools/test_phase4a_prediction_system_ps_q22w_recurring_failure_preserve_success.py",
    "tools/test_phase4a_prediction_system_ps_q22w_recurring_failure_preserve_success_close_guard.py",
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
        "guard": "ps_q22w_recurring_failure_preserve_success_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED),
        "contract": {
            "q22s_failure_preserves_previous_success": True,
            "q22s_records_q21i_result_summary": True,
            "q22v_accepts_retryable_q22s_failure": True,
            "scheduler_mutation_executed": False,
            "latest_prediction_artifact_written": False,
            "status_artifact_written_by_patch": False,
            "would_send_to_broker": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


def test_ps_q22w_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
