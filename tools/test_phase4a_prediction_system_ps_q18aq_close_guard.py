# path: ./tools/test_phase4a_prediction_system_ps_q18aq_close_guard.py
# desc: Close guard for PS-Q18AQ manual UI re-smoke pass record.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18aq_manual_ui_resmoke_pass import (  # noqa: E402
    FALSE_BOUNDARIES,
    build_ps_q18aq_manual_ui_resmoke_pass_packet,
)

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AQ_WARROOM_LATEST_PREDICTION_MANUAL_UI_RESMOKE_PASS_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18aq_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18aq_manual_ui_resmoke_pass.py",
    "tools/test_phase4a_prediction_system_ps_q18aq_manual_ui_resmoke_pass_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = build_ps_q18aq_manual_ui_resmoke_pass_packet()
    if packet.get("manual_ui_resmoke_result") != "pass":
        failures.append("manual UI re-smoke result must be pass")
    for key in ("browser_find_freshness_state", "browser_find_safe_fallback_reason_codes", "browser_find_refresh_heartbeat_utc", "ps_q18ao_searchability_gap_closed", "ps_q18ao_refresh_visibility_gap_closed"):
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
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
        "guard": "ps_q18aq_close_guard",
        "phase": "phase3_warroom_latest_prediction_manual_ui_resmoke_pass_closed",
        "contract": {
            "ps_q18aq_closed": not failures,
            "manual_ui_resmoke_result": packet.get("manual_ui_resmoke_result"),
            "browser_find_freshness_state": packet.get("browser_find_freshness_state"),
            "browser_find_safe_fallback_reason_codes": packet.get("browser_find_safe_fallback_reason_codes"),
            "browser_find_refresh_heartbeat_utc": packet.get("browser_find_refresh_heartbeat_utc"),
            "ps_q18ao_searchability_gap_closed": packet.get("ps_q18ao_searchability_gap_closed"),
            "ps_q18ao_refresh_visibility_gap_closed": packet.get("ps_q18ao_refresh_visibility_gap_closed"),
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


def test_ps_q18aq_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
