# path: ./tools/test_phase4a_prediction_system_ps_q18ao_close_guard.py
# desc: Close guard for PS-Q18AO manual UI smoke execution record.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18ao_manual_ui_smoke_execution_record import (  # noqa: E402
    FALSE_BOUNDARIES,
    build_ps_q18ao_manual_ui_smoke_execution_record_packet,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AO_WARROOM_LATEST_PREDICTION_MANUAL_UI_SMOKE_EXECUTION_RECORD_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ao_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ao_manual_ui_smoke_execution_record.py",
    "tools/test_phase4a_prediction_system_ps_q18ao_manual_ui_smoke_execution_record_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = build_ps_q18ao_manual_ui_smoke_execution_record_packet()
    if packet.get("manual_ui_smoke_result") != "observed_with_ux_gaps_not_full_pass":
        failures.append("manual UI smoke result must not be recorded as full pass")
    if packet.get("operator_searchability_gap_present") is not True:
        failures.append("searchability gap must be recorded")
    if packet.get("operator_refresh_visibility_gap_present") is not True:
        failures.append("refresh visibility gap must be recorded")
    if packet.get("next_safe_slice") != "PS-Q18AP UI visibility polish for searchable tokens and refresh heartbeat":
        failures.append("next safe slice must be PS-Q18AP UI visibility polish")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q18ao_close_guard",
        "phase": "phase3_warroom_latest_prediction_manual_ui_smoke_recorded_with_ux_gaps",
        "contract": {
            "ps_q18ao_closed": not failures,
            "manual_ui_smoke_result": packet.get("manual_ui_smoke_result"),
            "operator_searchability_gap_present": packet.get("operator_searchability_gap_present"),
            "operator_refresh_visibility_gap_present": packet.get("operator_refresh_visibility_gap_present"),
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "next_slice": packet.get("next_safe_slice"),
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ao_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
