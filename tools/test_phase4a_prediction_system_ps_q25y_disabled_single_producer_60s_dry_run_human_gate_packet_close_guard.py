# path: ./tools/test_phase4a_prediction_system_ps_q25y_disabled_single_producer_60s_dry_run_human_gate_packet_close_guard.py
# desc: Close guard for PS-Q25Y disabled single-producer 60s dry-run human gate packet.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q25Y_DISABLED_SINGLE_PRODUCER_60S_DRY_RUN_HUMAN_GATE_PACKET_2026-06-30.md",
    "tools/diagnose_phase4a_prediction_system_ps_q25y_disabled_single_producer_60s_dry_run_human_gate_packet.py",
    "tools/test_phase4a_prediction_system_ps_q25y_disabled_single_producer_60s_dry_run_human_gate_packet.py",
    "tools/test_phase4a_prediction_system_ps_q25y_disabled_single_producer_60s_dry_run_human_gate_packet_close_guard.py",
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
    result = {"ok": dirty == EXPECTED_DIRTY, "guard": "ps_q25y_disabled_single_producer_60s_dry_run_human_gate_packet_close_guard", "dirty_paths": sorted(dirty), "missing_dirty": sorted(EXPECTED_DIRTY - dirty), "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY), "contract": {"selected_option_id": "single_producer_60s_candidate", "selected_target_cadence_sec": 60, "dry_run_human_gate_packet_added": True, "gate_marker_only": True, "decision_packet_only": True, "human_gate_required_before_any_dry_run": True, "human_gate_granted_by_this_packet": False, "separate_execution_slice_required": True, "manual_one_shot_run_allowed": False, "execute_dry_run_allowed": False, "scheduler_enablement_allowed": False, "producer_enablement_allowed": False, "scheduler_enabled": False, "producer_enabled": False, "runtime_artifact_write_allowed": False, "status_artifact_write_allowed": False, "prediction_artifact_write_allowed": False, "latest_manifest_written": False, "run_sidecars_written": False, "lock_file_created": False, "lock_file_deleted": False, "warroom_ui_trigger_allowed": False, "autotrade_trigger_allowed": False, "broker_private_api_allowed": False, "ledger_append": False, "mode_apply": False, "parameter_apply": False}}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
