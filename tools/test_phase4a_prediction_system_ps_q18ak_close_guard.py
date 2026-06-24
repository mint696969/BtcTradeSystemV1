# path: ./tools/test_phase4a_prediction_system_ps_q18ak_close_guard.py
# desc: Close guard for PS-Q18AK freshness/error fallback polish.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel import FALSE_BOUNDARIES, build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AK_LATEST_PREDICTION_SUMMARY_WIDGET_FRESHNESS_ERROR_FALLBACK_POLISH_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ak_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ak_freshness_error_fallback_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ak_freshness_error_fallback_panel.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(now_utc="2026-06-24T13:15:00Z")
    if packet.get("ok") is not True:
        failures.append(f"Q18AK packet must be ok: {packet}")
    if packet.get("freshness_monitor_enabled") is not True:
        failures.append("freshness monitor must be enabled")
    if packet.get("error_fallback_visible") is not True:
        failures.append("error fallback must be visible")
    if packet.get("operator_safe_fallback_reason_codes_visible") is not True:
        failures.append("fallback reason codes must be visible")
    if packet.get("auto_refresh_enabled") is not True:
        failures.append("auto refresh must remain enabled")
    if packet.get("freshness_state") != "stale":
        failures.append("expected stale state for current committed source timestamp")
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
        "guard": "ps_q18ak_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_freshness_error_fallback_polish_after_intermediate_goal",
        "contract": {
            "ps_q18ak_closed": not failures,
            "intermediate_goal_still_reached": True,
            "auto_refresh_enabled": packet.get("auto_refresh_enabled"),
            "freshness_monitor_enabled": packet.get("freshness_monitor_enabled"),
            "freshness_state": packet.get("freshness_state"),
            "safe_fallback_reason_codes": packet.get("safe_fallback_reason_codes"),
            "error_fallback_visible": packet.get("error_fallback_visible"),
            "broad_page_reload_disabled": packet.get("broad_page_reload_disabled"),
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "next_slice": "intermediate-goal close docs or UI smoke/manual visual check",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ak_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
