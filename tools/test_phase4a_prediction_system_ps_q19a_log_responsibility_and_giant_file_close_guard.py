# path: ./tools/test_phase4a_prediction_system_ps_q19a_log_responsibility_and_giant_file_close_guard.py
# desc: Close guard for PS-Q19A log responsibility split design and giant hot audit containment handoff.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q19a_log_responsibility_and_giant_file_guard import (  # noqa: E402
    FALSE_BOUNDARIES,
    REQUIRED_MARKERS,
    SPEC,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q19A_LOG_RESPONSIBILITY_AND_GIANT_FILE_GUARD_2026-06-25.md",
    "tools/rotate_hot_audit_log_ps_q19a.py",
    "tools/prune_giant_log_candidates_ps_q19a.py",
    "tools/test_phase4a_prediction_system_ps_q19a_log_responsibility_and_giant_file_guard.py",
    "tools/test_phase4a_prediction_system_ps_q19a_log_responsibility_and_giant_file_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q19a_giant_log_prune_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
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
    for marker in (
        "active_audit_size_bytes_observed_over_13gb=true",
        "active_audit_line_count_observed_over_14m=true",
        "PS-Q19B_AUDIT_TELEMETRY_SPLIT_MINIMAL",
        "WarRoom realtime prediction display should remain deferred",
        "prune_giant_log_candidates_tool_added=true",
        "active_hot_audit_delete_allowed=false",
        "hot_archive_log_delete_allowed=true",
        "cold_log_delete_allowed_with_include_cold=true",
    ):
        if marker not in text:
            failures.append(f"missing close marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q19a_log_responsibility_and_giant_file_close_guard",
        "phase": "ps_q19a_log_gate_before_warroom_realtime_prediction",
        "contract": {
            "ps_q19a_log_responsibility_gate": True,
            "giant_active_audit_file_observed": True,
            "rotation_tool_added": True,
            "prune_tool_added": True,
            "runtime_behavior_changed": False,
            "collector_behavior_changed": False,
            "ui_code_changed": False,
            "prediction_runtime_changed": False,
            "warroom_realtime_prediction_work_deferred_until_log_gate": True,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "would_send_to_broker": False,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q19a_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
