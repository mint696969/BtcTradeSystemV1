# path: ./tools/test_phase4a_prediction_system_ps_q18aj_close_guard.py
# desc: Close guard for PS-Q18AJ bounded WarRoom auto-refresh panel.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel import FALSE_BOUNDARIES, TRUE_BOUNDARIES, build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AJ_LATEST_PREDICTION_SUMMARY_WIDGET_BOUNDED_AUTO_REFRESH_PANEL_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18aj_bounded_auto_refresh_panel.py",
    "tools/test_phase4a_prediction_system_ps_q18aj_bounded_auto_refresh_panel_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18aj_close_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet(fragment_supported=True, ui_auto_refresh=True)
    if packet.get("ok") is not True:
        failures.append(f"Q18AJ packet must be ok: {packet}")
    if packet.get("auto_refresh_enabled") is not True:
        failures.append("auto refresh must be enabled")
    if packet.get("broad_page_reload_disabled") is not True:
        failures.append("broad page reload must stay disabled")
    for key in TRUE_BOUNDARIES:
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "parameter_apply_allowed", "ledger_append_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed"):
        if packet.get(key) is not False:
            failures.append(f"{key} must remain false in close guard")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q18aj_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_bounded_auto_refresh_panel_intermediate_goal_reached",
        "contract": {
            "ps_q18aj_closed": not failures,
            "intermediate_goal_reached": not failures,
            "auto_refresh_enabled": packet.get("auto_refresh_enabled"),
            "fragment_slot_refresh_path_enabled": packet.get("fragment_slot_refresh_path_enabled"),
            "partial_update_enabled": packet.get("partial_update_enabled"),
            "broad_page_reload_disabled": packet.get("broad_page_reload_disabled"),
            "refresh_mode": packet.get("refresh_mode"),
            "refresh_interval_sec": packet.get("refresh_interval_sec"),
            "component_source_generated_at": packet.get("component_source_generated_at"),
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "next_slice": "freshness/error fallback polish or intermediate-goal close docs",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18aj_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
