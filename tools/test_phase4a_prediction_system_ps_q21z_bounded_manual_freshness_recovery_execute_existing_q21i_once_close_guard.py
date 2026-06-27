# path: ./tools/test_phase4a_prediction_system_ps_q21z_bounded_manual_freshness_recovery_execute_existing_q21i_once_close_guard.py
# desc: Close guard for PS-Q21Z gated one-shot wrapper around existing PS-Q21I bounded manual freshness recovery.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q21z_bounded_manual_freshness_recovery_execute_existing_q21i_once import (  # noqa: E402
    FALSE_BOUNDARIES,
    REQUIRED_MARKERS,
    SPEC,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q21Z_BOUNDED_MANUAL_FRESHNESS_RECOVERY_EXECUTE_EXISTING_Q21I_ONCE_2026-06-27.md",
    "tools/run_phase4a_prediction_system_ps_q21z_bounded_manual_freshness_recovery_execute_existing_q21i_once.py",
    "tools/test_phase4a_prediction_system_ps_q21z_bounded_manual_freshness_recovery_execute_existing_q21i_once.py",
    "tools/test_phase4a_prediction_system_ps_q21z_bounded_manual_freshness_recovery_execute_existing_q21i_once_close_guard.py",
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
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q21z_bounded_manual_freshness_recovery_execute_existing_q21i_once_close_guard",
        "contract": {
            "ps_q21z_bounded_manual_freshness_recovery_execute_existing_q21i_once": True,
            "default_execution_is_dry_run_no_write": True,
            "execute_existing_q21i_once_requires_confirmation": "WRITE_D_HOT_LATEST_PREDICTION_ONCE",
            "producer_loop_shadow_once_still_separate": True,
            "producer_loop_enabled": False,
            "producer_runner_invoked": False,
            "scheduler_enablement_allowed_now": False,
            "trigger_addition_allowed_now": False,
            "recurring_enablement_allowed_now": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "would_send_to_broker": False,
            "would_write_collector_state": False,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q21z_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
