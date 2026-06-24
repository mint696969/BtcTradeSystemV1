# path: ./tools/test_phase4a_prediction_system_ps_q18at_close_guard.py
# desc: Close guard for PS-Q18AT implementation-gate review packet.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BTCTS_SRC = REPO_ROOT / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18at_implementation_gate_review_packet import (  # noqa: E402
    build_ps_q18at_implementation_gate_review_packet,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AT_LATEST_PREDICTION_IMPLEMENTATION_GATE_REVIEW_PACKET_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18at_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18at_implementation_gate_review_packet.py",
    "tools/test_phase4a_prediction_system_ps_q18at_implementation_gate_review_packet_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = build_ps_q18at_implementation_gate_review_packet()
    if packet.get("implementation_gate_review_result") != "blocked_not_ready_to_enable":
        failures.append("implementation gate review must stay blocked")
    if packet.get("prototype_real_rendering_enabled") is not False:
        failures.append("prototype must not enable real rendering")
    for key in ("real_prediction_widget_rendering_allowed", "real_prediction_widget_render_invoked", "streamlit_real_widget_render_invoked", "component_runtime_binding_allowed", "component_props_bound_to_runtime", "autotrade_trigger_allowed", "broker_private_api_allowed", "would_send_to_broker"):
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
        "guard": "ps_q18at_close_guard",
        "phase": "phase3_latest_prediction_implementation_gate_review_packet_closed_blocked_not_enabled",
        "contract": {
            "ps_q18at_closed": not failures,
            "implementation_gate_review_result": packet.get("implementation_gate_review_result"),
            "blocker_count": packet.get("blocker_count"),
            "real_prediction_widget_render_invoked": False,
            "component_runtime_binding_allowed": False,
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


def test_ps_q18at_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
