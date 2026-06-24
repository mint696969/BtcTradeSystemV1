# path: ./tools/test_phase4a_prediction_system_ps_q18al_close_guard.py
# desc: Close guard for PS-Q18AL intermediate-goal close.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel import build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel import build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AL_WARROOM_LATEST_PREDICTION_AUTO_REFRESH_INTERMEDIATE_GOAL_CLOSE_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18al_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18al_intermediate_goal_close.py",
    "tools/test_phase4a_prediction_system_ps_q18al_intermediate_goal_close_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    q18aj = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet(fragment_supported=True, ui_auto_refresh=True)
    q18ak = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(now_utc="2026-06-24T13:20:00Z", fragment_supported=True, ui_auto_refresh=True)
    if q18aj.get("ok") is not True:
        failures.append("Q18AJ packet must be ok")
    if q18ak.get("ok") is not True:
        failures.append("Q18AK packet must be ok")
    if q18aj.get("auto_refresh_enabled") is not True or q18aj.get("fragment_slot_refresh_path_enabled") is not True:
        failures.append("intermediate auto-refresh path must be enabled")
    if q18ak.get("freshness_monitor_enabled") is not True or q18ak.get("error_fallback_visible") is not True:
        failures.append("freshness/fallback polish must be enabled")
    for packet_name, packet in (("q18aj", q18aj), ("q18ak", q18ak)):
        for key in ("real_prediction_widget_render_invoked", "streamlit_real_widget_render_invoked", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "parameter_apply_allowed", "ledger_append_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed"):
            if packet.get(key) is not False:
                failures.append(f"{packet_name}:{key} must stay false")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q18al_close_guard",
        "phase": "phase3_warroom_latest_prediction_auto_refresh_intermediate_goal_closed",
        "contract": {
            "ps_q18al_closed": not failures,
            "intermediate_goal_reached": q18aj.get("auto_refresh_enabled") is True,
            "fragment_slot_refresh_path_enabled": q18aj.get("fragment_slot_refresh_path_enabled"),
            "partial_update_enabled": q18aj.get("partial_update_enabled"),
            "broad_page_reload_disabled": q18aj.get("broad_page_reload_disabled"),
            "freshness_monitor_enabled": q18ak.get("freshness_monitor_enabled"),
            "error_fallback_visible": q18ak.get("error_fallback_visible"),
            "freshness_state": q18ak.get("freshness_state"),
            "safe_fallback_reason_codes": q18ak.get("safe_fallback_reason_codes"),
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "next_slice": "UI smoke/manual visual check or separate real-widget rendering gate",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18al_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
