# path: ./tools/test_phase4a_prediction_system_ps_q18ar_close_guard.py
# desc: Close guard for PS-Q18AR explicit real-widget rendering design gate.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18ar_real_widget_rendering_design_gate import (  # noqa: E402
    FALSE_BOUNDARIES,
    build_ps_q18ar_real_widget_rendering_design_gate_packet,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AR_LATEST_PREDICTION_EXPLICIT_REAL_WIDGET_RENDERING_DESIGN_GATE_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ar_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ar_real_widget_rendering_design_gate.py",
    "tools/test_phase4a_prediction_system_ps_q18ar_real_widget_rendering_design_gate_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = build_ps_q18ar_real_widget_rendering_design_gate_packet()
    if packet.get("real_widget_rendering_design_gate_state") != "design_only_rendering_not_enabled":
        failures.append("design gate state must be design_only_rendering_not_enabled")
    if packet.get("future_real_render_gate_required") is not True:
        failures.append("future real render gate must be required")
    if packet.get("manual_ui_review_required_before_enablement") is not True:
        failures.append("manual UI review must be required before enablement")
    if packet.get("rollback_plan_required_before_enablement") is not True:
        failures.append("rollback plan must be required before enablement")
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
        "guard": "ps_q18ar_close_guard",
        "phase": "phase3_latest_prediction_real_widget_rendering_design_gate_closed_rendering_not_enabled",
        "contract": {
            "ps_q18ar_closed": not failures,
            "real_widget_rendering_design_gate_state": packet.get("real_widget_rendering_design_gate_state"),
            "future_release_requirement_count": packet.get("future_release_requirement_count"),
            "real_prediction_widget_rendering_allowed": False,
            "streamlit_real_widget_render_invoked": False,
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


def test_ps_q18ar_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
