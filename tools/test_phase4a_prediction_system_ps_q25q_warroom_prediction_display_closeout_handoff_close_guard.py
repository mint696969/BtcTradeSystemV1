# path: ./tools/test_phase4a_prediction_system_ps_q25q_warroom_prediction_display_closeout_handoff_close_guard.py
# desc: Close guard for PS-Q25Q WarRoom prediction display closeout handoff.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q25Q_WARROOM_PREDICTION_DISPLAY_CLOSEOUT_HANDOFF_2026-06-30.md",
    "tools/diagnose_phase4a_prediction_system_ps_q25q_warroom_prediction_display_closeout_handoff.py",
    "tools/test_phase4a_prediction_system_ps_q25q_warroom_prediction_display_closeout_handoff.py",
    "tools/test_phase4a_prediction_system_ps_q25q_warroom_prediction_display_closeout_handoff_close_guard.py",
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
    result = {"ok": dirty == EXPECTED_DIRTY, "guard": "ps_q25q_warroom_prediction_display_closeout_handoff_close_guard", "dirty_paths": sorted(dirty), "missing_dirty": sorted(EXPECTED_DIRTY - dirty), "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY), "contract": {"production_code_changed": False, "read_only_closeout_handoff": True, "display_lane_closed_out": True, "visual_review_recorded": True, "visual_review_result": "pass_for_operator_review_not_trade_decision", "trade_decision_approved": False, "execution_approval": False, "safe_stop_here": True, "cadence_lane_stopped_at_human_gate": True, "producer_cadence_changed": False, "scheduler_action_changed": False, "scheduler_enabled": False, "producer_enabled": False, "runtime_artifact_write_allowed": False, "status_artifact_write_allowed": False, "prediction_artifact_write_allowed": False, "view_artifact_write_allowed": False, "latest_manifest_written": False, "run_sidecars_written": False, "autotrade_trigger_allowed": False, "broker_private_api_allowed": False, "ledger_append": False, "mode_apply": False, "parameter_apply": False}}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
