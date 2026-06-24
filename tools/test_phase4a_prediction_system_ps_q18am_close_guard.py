# path: ./tools/test_phase4a_prediction_system_ps_q18am_close_guard.py
# desc: Close guard for PS-Q18AM UI smoke/manual visual check packet.

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

from tools.test_phase4a_prediction_system_ps_q18am_ui_smoke_check import build_ps_q18am_ui_smoke_check_packet  # noqa: E402

EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AM_WARROOM_LATEST_PREDICTION_AUTO_REFRESH_UI_SMOKE_CHECK_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18am_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18am_ui_smoke_check.py",
    "tools/test_phase4a_prediction_system_ps_q18am_ui_smoke_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    packet = build_ps_q18am_ui_smoke_check_packet()
    if packet.get("ok") is not True:
        failures.append(f"Q18AM packet must be ok: {packet}")
    if packet.get("manual_visual_check_required") is not True:
        failures.append("manual visual check must be required")
    if packet.get("manual_checklist_count") != 7:
        failures.append("manual checklist count must be 7")
    if packet.get("intermediate_goal_reached") is not True:
        failures.append("intermediate goal must remain reached")
    for key in ("auto_refresh_enabled", "fragment_slot_refresh_path_enabled", "partial_update_enabled", "broad_page_reload_disabled", "freshness_monitor_enabled", "error_fallback_visible"):
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in ("real_prediction_widget_render_invoked", "streamlit_real_widget_render_invoked", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "parameter_apply_allowed", "ledger_append_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed"):
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
        "guard": "ps_q18am_close_guard",
        "phase": "phase3_warroom_latest_prediction_auto_refresh_ui_smoke_packet_ready",
        "contract": {
            "ps_q18am_closed": not failures,
            "intermediate_goal_reached": packet.get("intermediate_goal_reached"),
            "manual_visual_check_required": packet.get("manual_visual_check_required"),
            "manual_checklist_count": packet.get("manual_checklist_count"),
            "auto_refresh_enabled": packet.get("auto_refresh_enabled"),
            "freshness_monitor_enabled": packet.get("freshness_monitor_enabled"),
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "next_slice": "manual UI smoke execution record or separate real-widget rendering gate",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18am_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
