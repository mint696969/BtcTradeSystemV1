# path: ./tools/test_phase4a_prediction_system_ps_q18ax_close_guard.py
# desc: Close guard for PS-Q18AX latest prediction observation milestone close.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18ax_latest_prediction_observation_milestone_close import (  # noqa: E402
    FALSE_BOUNDARIES,
    build_ps_q18ax_latest_prediction_observation_milestone_close_packet,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AX_LATEST_PREDICTION_OBSERVATION_MILESTONE_CLOSE_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ax_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ax_latest_prediction_observation_milestone_close.py",
    "tools/test_phase4a_prediction_system_ps_q18ax_latest_prediction_observation_milestone_close_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = build_ps_q18ax_latest_prediction_observation_milestone_close_packet()
    if packet.get("latest_prediction_observation_milestone_closed") is not True:
        failures.append("latest prediction observation milestone must be closed")
    if packet.get("milestone_close_result") != "closed_with_manual_ui_smoke_pass":
        failures.append("milestone close result must be closed_with_manual_ui_smoke_pass")
    if packet.get("manual_ui_smoke_result") != "pass":
        failures.append("manual UI smoke result must remain pass")
    if packet.get("implementation_gate_opened") is not False:
        failures.append("implementation gate must remain closed")
    if packet.get("real_rendering_enabled") is not False:
        failures.append("real rendering must remain disabled")
    if packet.get("trading_execution_behavior_changed") is not False:
        failures.append("trading/execution behavior must not change")
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
        "guard": "ps_q18ax_close_guard",
        "phase": "phase3_latest_prediction_observation_milestone_close_closed_docs_guard_only",
        "contract": {
            "ps_q18ax_closed": not failures,
            "latest_prediction_observation_milestone_closed": packet.get("latest_prediction_observation_milestone_closed"),
            "milestone_close_result": packet.get("milestone_close_result"),
            "manual_ui_smoke_result": packet.get("manual_ui_smoke_result"),
            "implementation_gate_review_result": packet.get("implementation_gate_review_result"),
            "implementation_gate_opened": packet.get("implementation_gate_opened"),
            "real_rendering_enabled": packet.get("real_rendering_enabled"),
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


def test_ps_q18ax_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
