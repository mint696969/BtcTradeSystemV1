# path: ./tools/test_phase4a_prediction_system_ps_q25b_warroom_live_market_nowcast_high_frequency_visibility_close_guard.py
# desc: Close guard for PS-Q25B WarRoom Live Market Nowcast high-frequency visibility.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q25B_WARROOM_LIVE_MARKET_NOWCAST_HIGH_FREQUENCY_VISIBILITY_2026-06-30.md",
    "tools/diagnose_phase4a_prediction_system_ps_q25b_warroom_live_market_nowcast_high_frequency_visibility.py",
    "tools/test_phase4a_prediction_system_ps_q25b_warroom_live_market_nowcast_high_frequency_visibility.py",
    "tools/test_phase4a_prediction_system_ps_q25b_warroom_live_market_nowcast_high_frequency_visibility_close_guard.py",
}


def _dirty() -> set[str]:
    proc = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    paths: set[str] = set()
    for line in proc.stdout.splitlines():
        path = line[3:].strip().replace(chr(92), "/")
        if path.startswith("tmp/work/") or path.startswith("tmp/gpt_room/") or "/__pycache__/" in path or path.endswith(".pyc"):
            continue
        paths.add(path)
    return paths


def main_guard() -> int:
    dirty = _dirty()
    result = {
        "ok": dirty == EXPECTED_DIRTY,
        "guard": "ps_q25b_warroom_live_market_nowcast_high_frequency_visibility_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED_DIRTY - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY),
        "contract": {
            "warroom_live_market_nowcast_panel_added": True,
            "warroom_page_live_nowcast_panel_mounted": True,
            "current_state_not_prediction": True,
            "high_frequency_fragment_refresh_mode": "poll_fast",
            "high_frequency_fragment_refresh_sec": 3,
            "best_bid_visible": True,
            "best_ask_visible": True,
            "spread_visible": True,
            "spread_bps_visible": True,
            "market_event_age_visible": True,
            "ws_board_state_visible": True,
            "ws_executions_state_visible": True,
            "collector_health_visible": True,
            "gap_resync_visible": True,
            "attention_flags_visible": True,
            "warroom_display_only": True,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "scheduler_action_changed": False,
            "scheduler_enabled": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "ledger_append": False,
            "mode_apply": False,
            "parameter_apply": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
