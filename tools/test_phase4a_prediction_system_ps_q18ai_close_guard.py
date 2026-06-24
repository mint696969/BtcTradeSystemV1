# path: ./tools/test_phase4a_prediction_system_ps_q18ai_close_guard.py
# desc: Close guard for PS-Q18AI WarRoom render-disabled packet status/value panel mount.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ai_warroom_render_disabled_packet_panel import FALSE_BOUNDARIES, TRUE_BOUNDARIES, build_latest_prediction_summary_widget_q18ai_warroom_panel_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ai_warroom_render_disabled_packet_panel.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AI_LATEST_PREDICTION_SUMMARY_WIDGET_WARROOM_RENDER_DISABLED_PACKET_PANEL_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ai_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ai_warroom_render_disabled_packet_panel.py",
    "tools/test_phase4a_prediction_system_ps_q18ai_warroom_render_disabled_packet_panel_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = build_latest_prediction_summary_widget_q18ai_warroom_panel_packet()
    if packet.get("ok") is not True:
        failures.append(f"Q18AI packet must be ok: {packet}")
    if packet.get("warroom_display_mounted") is not True:
        failures.append("warroom display must be mounted")
    if packet.get("display_row_count") != 12:
        failures.append("display row count must be 12")
    for key in TRUE_BOUNDARIES:
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    for key in ("refresh_invocation_allowed", "auto_refresh_enabled", "real_prediction_widget_render_invoked", "runtime_artifact_write_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed"):
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
        "guard": "ps_q18ai_close_guard",
        "phase": "phase3_latest_prediction_summary_widget_warroom_render_disabled_packet_panel_before_auto_refresh",
        "contract": {
            "ps_q18ai_closed": not failures,
            "warroom_display_mounted": packet.get("warroom_display_mounted"),
            "display_row_count": packet.get("display_row_count"),
            "component_packet_state": packet.get("component_packet_state"),
            "component_source_generated_at": packet.get("component_source_generated_at"),
            "auto_refresh_enabled": False,
            "refresh_invocation_allowed": False,
            "real_prediction_widget_render_invoked": False,
            "next_slice": "bounded auto-refresh runner/panel for latest prediction packet",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ai_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
