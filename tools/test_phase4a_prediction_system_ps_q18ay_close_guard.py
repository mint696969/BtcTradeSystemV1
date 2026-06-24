# path: ./tools/test_phase4a_prediction_system_ps_q18ay_close_guard.py
# desc: Close guard for PS-Q18AY WarRoom operator-first cleanup preflight.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18ay_warroom_operator_first_cleanup_preflight import (  # noqa: E402
    FALSE_BOUNDARIES,
    build_ps_q18ay_warroom_operator_first_cleanup_preflight_packet,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AY_WARROOM_OPERATOR_FIRST_CLEANUP_PREFLIGHT_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ay_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ay_warroom_operator_first_cleanup_preflight.py",
    "tools/test_phase4a_prediction_system_ps_q18ay_warroom_operator_first_cleanup_preflight_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = build_ps_q18ay_warroom_operator_first_cleanup_preflight_packet()
    if packet.get("docs_guard_only") is not True:
        failures.append("PS-Q18AY must remain docs/guard only")
    if packet.get("warroom_runtime_changed") is not False:
        failures.append("WarRoom runtime must not change in PS-Q18AY")
    if packet.get("code_deleted_this_slice") is not False:
        failures.append("code must not be deleted in PS-Q18AY")
    if packet.get("delete_requires_reference_audit") is not True:
        failures.append("delete requires reference audit")
    if packet.get("next_safe_slice") != "PS-Q18AZ WarRoom operator-first render path cleanup":
        failures.append("next safe slice mismatch")
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
        "guard": "ps_q18ay_close_guard",
        "phase": "phase3_warroom_operator_first_cleanup_preflight_closed_docs_guard_only",
        "contract": {
            "ps_q18ay_closed": not failures,
            "cleanup_goal": packet.get("warroom_cleanup_goal"),
            "docs_guard_only": packet.get("docs_guard_only"),
            "code_deleted_this_slice": packet.get("code_deleted_this_slice"),
            "component_file_delete_allowed_this_slice": packet.get("component_file_delete_allowed_this_slice"),
            "future_real_render_enablement_allowed_this_slice": packet.get("future_real_render_enablement_allowed_this_slice"),
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


def test_ps_q18ay_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
