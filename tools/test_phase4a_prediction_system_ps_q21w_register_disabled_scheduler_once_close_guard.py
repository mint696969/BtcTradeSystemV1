# path: ./tools/test_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once_close_guard.py
# desc: Close guard for PS-Q21W gated one-time disabled scheduler registration tool.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once import (  # noqa: E402
    FALSE_BOUNDARIES,
    REQUIRED_MARKERS,
    SPEC,
)

REQUIRED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q21W_REGISTER_DISABLED_SCHEDULER_ONCE_2026-06-26.md",
    "tools/run_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once.py",
    "tools/test_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once.py",
}

OPTIONAL_DIRTY = {
    "tools/test_phase4a_prediction_system_ps_q21w_register_disabled_scheduler_once_close_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    paths: set[str] = set()
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].replace(chr(92), "/")
        if "/__pycache__/" in path or path.endswith(".pyc"):
            continue
        if path.startswith("tmp/work/") or path.startswith("tmp/gpt_room/"):
            continue
        paths.add(path)
    return paths


def main_guard() -> int:
    failures: list[str] = []
    text = SPEC.read_text(encoding="utf-8-sig") if SPEC.exists() else ""
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing required marker: {marker}")
    for marker in FALSE_BOUNDARIES:
        if marker not in text:
            failures.append(f"missing false boundary: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - REQUIRED_DIRTY - OPTIONAL_DIRTY
    missing = REQUIRED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q21w_register_disabled_scheduler_once_close_guard",
        "contract": {
            "ps_q21w_register_disabled_scheduler_once": True,
            "default_execution_is_dry_run_no_registration": True,
            "execute_registration_requires_confirmation": "REGISTER_DISABLED_NON_UI_SCHEDULER_ONCE_WITH_ROLLBACK_PLAN",
            "registered_task_state_required": "Disabled",
            "registered_task_trigger_count_required": 0,
            "producer_loop_still_separate_approval": True,
            "scheduler_registered_by_default": False,
            "producer_loop_enabled": False,
            "producer_runner_invoked": False,
            "latest_prediction_artifact_written": False,
            "status_artifact_written": False,
            "warroom_ui_trigger_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "would_send_to_broker": False,
            "would_write_collector_state": False,
        },
        "dirty_paths": sorted(dirty),
        "required_dirty": sorted(REQUIRED_DIRTY),
        "optional_dirty": sorted(OPTIONAL_DIRTY),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q21w_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
