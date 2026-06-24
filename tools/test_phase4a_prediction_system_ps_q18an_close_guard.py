# path: ./tools/test_phase4a_prediction_system_ps_q18an_close_guard.py
# desc: Close guard for PS-Q18AN real-widget rendering gate preflight.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BTCTS_SRC = REPO_ROOT / "btcts_next" / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from tools.test_phase4a_prediction_system_ps_q18an_real_widget_rendering_gate_preflight import (  # noqa: E402
    FALSE_BOUNDARIES,
    build_ps_q18an_real_widget_rendering_gate_preflight_packet,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AN_LATEST_PREDICTION_REAL_WIDGET_RENDERING_GATE_PREFLIGHT_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18an_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18an_real_widget_rendering_gate_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18an_real_widget_rendering_gate_preflight.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = build_ps_q18an_real_widget_rendering_gate_preflight_packet()
    if packet.get("ok") is not True:
        failures.append(f"Q18AN packet must be ok: {packet}")
    if packet.get("real_widget_rendering_gate_state") != "preflight_only_rendering_not_enabled":
        failures.append("real widget rendering gate must remain preflight only")
    if packet.get("real_widget_rendering_allowed") is not False:
        failures.append("real widget rendering must not be allowed")
    if packet.get("component_packet_state") != "read_only_component_skeleton_render_disabled":
        failures.append("component packet must remain render-disabled")
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
        "guard": "ps_q18an_close_guard",
        "phase": "phase3_latest_prediction_real_widget_rendering_gate_preflight_closed_rendering_not_enabled",
        "contract": {
            "ps_q18an_closed": not failures,
            "intermediate_goal_reached": packet.get("intermediate_goal_reached"),
            "real_widget_rendering_gate_state": packet.get("real_widget_rendering_gate_state"),
            "real_widget_rendering_allowed": packet.get("real_widget_rendering_allowed"),
            "component_packet_state": packet.get("component_packet_state"),
            "gate_release_requirement_count": packet.get("gate_release_requirement_count"),
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "next_slice": packet.get("recommended_next_slice"),
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18an_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
