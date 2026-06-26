# path: ./tools/test_phase4a_prediction_system_ps_q21p_disabled_lock_smoke_temp_path_only_close_guard.py
# desc: Close guard for PS-Q21P disabled temp/mock lock smoke.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q21p_disabled_lock_smoke_temp_path_only import (  # noqa: E402
    FALSE_BOUNDARIES,
    REQUIRED_MARKERS,
    SPEC,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q21P_DISABLED_LOCK_SMOKE_TEMP_PATH_ONLY_2026-06-26.md",
    "tools/smoke_phase4a_prediction_system_ps_q21p_disabled_lock_smoke_temp_path_only.py",
    "tools/test_phase4a_prediction_system_ps_q21p_disabled_lock_smoke_temp_path_only.py",
    "tools/test_phase4a_prediction_system_ps_q21p_disabled_lock_smoke_temp_path_only_close_guard.py",
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
        "guard": "ps_q21p_disabled_lock_smoke_temp_path_only_close_guard",
        "contract": {
            "ps_q21p_disabled_lock_smoke_temp_path_only": True,
            "temp_mock_lock_smoke_only": True,
            "d_hot_lock_file_created": False,
            "d_hot_lock_file_written": False,
            "d_hot_lock_acquire_attempted": False,
            "d_hot_lock_release_attempted": False,
            "lock_file_creation_allowed_for_d_hot": False,
            "scheduler_registration_allowed": False,
            "scheduler_enablement_allowed": False,
            "producer_enablement_allowed": False,
            "producer_loop_allowed": False,
            "recurring_enablement_allowed_now": False,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "warroom_ui_trigger_allowed": False,
            "approval_or_ledger_allowed": False,
            "parameter_apply_allowed": False,
            "parameter_staging_write_allowed": False,
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


def test_ps_q21p_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
