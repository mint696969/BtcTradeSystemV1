# path: ./tools/test_phase4a_prediction_system_ps_q18as_close_guard.py
# desc: Close guard for PS-Q18AS still-disabled real-render prototype.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BTCTS_SRC = REPO_ROOT / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import (  # noqa: E402
    REAL_RENDER_PROTOTYPE_FALSE_BOUNDARIES,
    build_latest_prediction_summary_widget_real_render_prototype_packet,
    render_latest_prediction_summary_widget,
)

EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/latest_prediction_summary_widget.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AS_LATEST_PREDICTION_STILL_DISABLED_REAL_RENDER_PROTOTYPE_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18as_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18as_still_disabled_real_render_prototype.py",
    "tools/test_phase4a_prediction_system_ps_q18as_still_disabled_real_render_prototype_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    skeleton = render_latest_prediction_summary_widget()
    packet = build_latest_prediction_summary_widget_real_render_prototype_packet(requested_enable_real_render=True, implementation_gate_open=True, manual_ui_review_passed=True, rollback_plan_ready=True)
    if skeleton.get("component_state") != "read_only_component_skeleton_render_disabled":
        failures.append("existing render function must still return skeleton")
    if packet.get("prototype_state") != "still_disabled_real_render_prototype_blocked":
        failures.append("prototype must stay blocked")
    if packet.get("skeleton_packet_preserved") is not True:
        failures.append("skeleton packet must be preserved")
    if packet.get("real_rendering_enabled") is not False:
        failures.append("real rendering must stay disabled")
    if "separate_future_implementation_gate_required" not in packet.get("prototype_blockers", []):
        failures.append("future implementation gate blocker missing")
    for key in REAL_RENDER_PROTOTYPE_FALSE_BOUNDARIES:
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
        "guard": "ps_q18as_close_guard",
        "phase": "phase3_latest_prediction_still_disabled_real_render_prototype_closed_rendering_not_enabled",
        "contract": {
            "ps_q18as_closed": not failures,
            "prototype_state": packet.get("prototype_state"),
            "skeleton_packet_preserved": packet.get("skeleton_packet_preserved"),
            "real_rendering_enabled": packet.get("real_rendering_enabled"),
            "real_prediction_widget_render_invoked": False,
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


def test_ps_q18as_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
