# path: ./tools/test_phase4a_prediction_system_ps_q18aw_close_guard.py
# desc: Close guard for PS-Q18AW manual UI smoke execution record.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record import (  # noqa: E402
    FALSE_BOUNDARIES,
    build_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AW_WARROOM_OBSERVATION_QUICK_STATUS_MANUAL_UI_SMOKE_EXECUTION_RECORD_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18aw_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record.py",
    "tools/test_phase4a_prediction_system_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = build_ps_q18aw_observation_quick_status_manual_ui_smoke_execution_record()
    if packet.get("manual_ui_smoke_result") != "pass":
        failures.append("manual UI smoke result must be pass")
    if packet.get("pass_check_count") != 10:
        failures.append("pass check count must be 10")
    if packet.get("page_reload_enabled") is not False:
        failures.append("page reload must stay disabled")
    if packet.get("fragment_refresh_enabled") is not True:
        failures.append("fragment refresh must be true")
    if not (packet.get("quick_status_refresh_heartbeat_utc") < packet.get("later_refresh_heartbeat_utc_1") < packet.get("later_refresh_heartbeat_utc_2")):
        failures.append("heartbeat evidence must advance")
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
        "guard": "ps_q18aw_close_guard",
        "phase": "phase3_warroom_observation_quick_status_manual_ui_smoke_execution_record_pass_closed",
        "contract": {
            "ps_q18aw_closed": not failures,
            "manual_ui_smoke_result": packet.get("manual_ui_smoke_result"),
            "pass_check_count": packet.get("pass_check_count"),
            "page_reload_enabled": packet.get("page_reload_enabled"),
            "fragment_refresh_enabled": packet.get("fragment_refresh_enabled"),
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


def test_ps_q18aw_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
