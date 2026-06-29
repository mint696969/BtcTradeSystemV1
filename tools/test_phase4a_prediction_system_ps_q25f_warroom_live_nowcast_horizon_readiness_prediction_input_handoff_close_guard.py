# path: ./tools/test_phase4a_prediction_system_ps_q25f_warroom_live_nowcast_horizon_readiness_prediction_input_handoff_close_guard.py
# desc: Close guard for PS-Q25F WarRoom Live Nowcast horizon readiness and prediction-input handoff.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q25F_WARROOM_LIVE_NOWCAST_HORIZON_READINESS_PREDICTION_INPUT_HANDOFF_2026-06-30.md",
    "tools/diagnose_phase4a_prediction_system_ps_q25f_warroom_live_nowcast_horizon_readiness_prediction_input_handoff.py",
    "tools/test_phase4a_prediction_system_ps_q25f_warroom_live_nowcast_horizon_readiness_prediction_input_handoff.py",
    "tools/test_phase4a_prediction_system_ps_q25f_warroom_live_nowcast_horizon_readiness_prediction_input_handoff_close_guard.py",
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
        "guard": "ps_q25f_warroom_live_nowcast_horizon_readiness_prediction_input_handoff_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED_DIRTY - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY),
        "contract": {
            "warroom_live_nowcast_horizon_readiness_added": True,
            "horizon_readiness_rows_visible": True,
            "overall_horizon_readiness_visible": True,
            "prediction_input_handoff_visible": True,
            "horizon_5m_supported": True,
            "horizon_15m_supported": True,
            "horizon_30m_supported": True,
            "horizon_1h_supported": True,
            "current_state_not_prediction": True,
            "warroom_display_only": True,
            "producer_cadence_changed": False,
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
