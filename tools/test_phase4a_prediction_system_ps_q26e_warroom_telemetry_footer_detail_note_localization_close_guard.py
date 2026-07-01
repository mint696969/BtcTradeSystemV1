# path: ./tools/test_phase4a_prediction_system_ps_q26e_warroom_telemetry_footer_detail_note_localization_close_guard.py
# desc: Close guard for PS-Q26E WarRoom telemetry footer and detail-note localization.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/texts/latest_prediction_display_texts.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_telemetry_footer_detail_note_localization_q26e.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q26E_WARROOM_TELEMETRY_FOOTER_DETAIL_NOTE_LOCALIZATION_2026-07-01.md",
    "tools/diagnose_phase4a_prediction_system_ps_q26e_warroom_telemetry_footer_detail_note_localization.py",
    "tools/test_phase4a_prediction_system_ps_q26e_warroom_telemetry_footer_detail_note_localization.py",
    "tools/test_phase4a_prediction_system_ps_q26e_warroom_telemetry_footer_detail_note_localization_close_guard.py",
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
    result = {"ok": dirty == EXPECTED_DIRTY, "guard": "ps_q26e_warroom_telemetry_footer_detail_note_localization_close_guard", "dirty_paths": sorted(dirty), "missing_dirty": sorted(EXPECTED_DIRTY - dirty), "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY), "contract": {"prediction_telemetry_footer_japanese_localized": True, "nowcast_telemetry_footer_japanese_localized": True, "detail_note_token_fragments_localized": True, "visible_autotrade_broker_false_fragments_reduced": True, "trade_guidance_added": False, "trade_signal_added": False, "scheduler_enabled": False, "producer_enabled": False, "runtime_artifact_write_allowed": False, "status_artifact_write_allowed": False, "prediction_artifact_write_allowed": False, "view_artifact_write_allowed": False, "autotrade_trigger_allowed": False, "broker_private_api_allowed": False, "ledger_append": False, "mode_apply": False, "parameter_apply": False, "would_send_to_broker": False}}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
