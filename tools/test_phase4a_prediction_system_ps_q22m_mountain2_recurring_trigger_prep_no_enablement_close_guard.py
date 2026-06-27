# path: ./tools/test_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement_close_guard.py
# desc: Close guard for PS-Q22M Mountain2 recurring/trigger preparation no enablement.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q22M_MOUNTAIN2_RECURRING_TRIGGER_PREP_NO_ENABLEMENT_2026-06-27.md",
    "tools/diagnose_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement.py",
    "tools/test_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement.py",
    "tools/test_phase4a_prediction_system_ps_q22m_mountain2_recurring_trigger_prep_no_enablement_close_guard.py",
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
        "guard": "ps_q22m_mountain2_recurring_trigger_prep_no_enablement_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED),
        "contract": {
            "read_only_no_enablement": True,
            "scheduler_enabled": False,
            "trigger_added": False,
            "trigger_addition_allowed_now": False,
            "recurring_enablement_allowed_now": False,
            "periodic_execution_enabled": False,
            "latest_prediction_artifact_written": False,
            "producer_runner_invoked": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "would_send_to_broker": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


def test_ps_q22m_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
