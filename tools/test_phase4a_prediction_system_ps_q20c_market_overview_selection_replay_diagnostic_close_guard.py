# path: ./tools/test_phase4a_prediction_system_ps_q20c_market_overview_selection_replay_diagnostic_close_guard.py
# desc: Close guard for PS-Q20C compact market.overview selection replay diagnostic.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q20c_market_overview_selection_replay_diagnostic import (  # noqa: E402
    FALSE_BOUNDARIES,
    REQUIRED_MARKERS,
    SPEC,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q20C_MARKET_OVERVIEW_SELECTION_REPLAY_DIAGNOSTIC_2026-06-26.md",
    "tools/replay_market_overview_selection_ps_q20c.py",
    "tools/test_phase4a_prediction_system_ps_q20c_market_overview_selection_replay_diagnostic.py",
    "tools/test_phase4a_prediction_system_ps_q20c_market_overview_selection_replay_diagnostic_close_guard.py",
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
        "guard": "ps_q20c_market_overview_selection_replay_diagnostic_close_guard",
        "contract": {
            "ps_q20c_market_overview_selection_replay_diagnostic": True,
            "uses_ps_q20b_consumer_row_selection_contract": True,
            "bounded_gpt_friendly_output": True,
            "no_new_giant_files": True,
            "canonical_timestamp_axis": "UTC_ISO8601_Z",
            "ps_q19r_scoring_policy_changed": False,
            "collector_runtime_behavior_changed": False,
            "runtime_artifact_write_performed_by_replay": False,
            "collector_state_write_performed_by_replay": False,
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
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q20c_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
