# path: ./tools/test_phase4a_prediction_system_ps_q19y_actual_point_selection_decision_lock_close_guard.py
# desc: Close guard for PS-Q19Y actual-point selection policy decision lock.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q19y_actual_point_selection_decision_lock import (  # noqa: E402
    FALSE_BOUNDARIES,
    NEXT_THREAD_MARKERS,
    REQUIRED_MARKERS,
    SPEC,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q19Y_ACTUAL_POINT_SELECTION_DECISION_LOCK_2026-06-25.md",
    "tools/test_phase4a_prediction_system_ps_q19y_actual_point_selection_decision_lock.py",
    "tools/test_phase4a_prediction_system_ps_q19y_actual_point_selection_decision_lock_close_guard.py",
}

FORBIDDEN_DIRTY_PREFIXES = (
    "tools/review_prediction_vs_actual_market_ps_q19r.py",
    "tools/compare_actual_point_selection_policy_ps_q19x.py",
    "btcts_next/",
)


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    paths: set[str] = set()
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].replace(chr(92), "/")
        if "/__pycache__/" in path or path.endswith(".pyc"):
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
    for marker in NEXT_THREAD_MARKERS:
        if marker not in text:
            failures.append(f"missing next-thread marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    forbidden_dirty = [path for path in dirty for prefix in FORBIDDEN_DIRTY_PREFIXES if path.startswith(prefix)]
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    if forbidden_dirty:
        failures.append(f"behavior/runtime files dirty in decision lock: {sorted(set(forbidden_dirty))}")
    result = {
        "ok": not failures,
        "guard": "ps_q19y_actual_point_selection_decision_lock_close_guard",
        "contract": {
            "ps_q19y_actual_point_selection_decision_lock": True,
            "policy_decision_locked": True,
            "ps_q19r_behavior_change_allowed_now": False,
            "nearest_quality_ok_within_tolerance_candidate_status": "deferred",
            "collector_reanchor_crossed_book_repair_preferred_next": True,
            "runtime_artifact_write_performed_by_decision_lock": False,
            "status_artifact_write_performed_by_decision_lock": False,
            "prediction_artifact_write_performed_by_decision_lock": False,
            "view_artifact_write_performed_by_decision_lock": False,
            "collector_state_write_performed_by_decision_lock": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "warroom_ui_trigger_enabled": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "would_send_to_broker": False,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "forbidden_dirty": sorted(set(forbidden_dirty)),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q19y_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
