# path: ./tools/test_phase4a_prediction_system_ps_q26h_warroom_top_reading_caption_japanese_localization_close_guard.py
# desc: Close guard for PS-Q26H WarRoom top reading caption and page-level token Japanese localization.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_top_reading_caption_japanese_localization_q26h.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q26H_WARROOM_TOP_READING_CAPTION_JAPANESE_LOCALIZATION_2026-07-01.md",
    "tools/diagnose_phase4a_prediction_system_ps_q26h_warroom_top_reading_caption_japanese_localization.py",
    "tools/test_phase4a_prediction_system_ps_q26h_warroom_top_reading_caption_japanese_localization.py",
    "tools/test_phase4a_prediction_system_ps_q26h_warroom_top_reading_caption_japanese_localization_close_guard.py",
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
    result = {"ok": dirty == EXPECTED_DIRTY, "guard": "ps_q26h_warroom_top_reading_caption_japanese_localization_close_guard", "dirty_paths": sorted(dirty), "missing_dirty": sorted(EXPECTED_DIRTY - dirty), "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY), "contract": {"reading_block_captions_japanese_localized": True, "quick_status_plain_text_japanese_localized": True, "quick_status_rows_japanese_localized": True, "page_level_false_fragments_reduced": True, "trade_guidance_added": False, "trade_signal_added": False, "scheduler_enabled": False, "producer_enabled": False, "runtime_artifact_write_allowed": False, "status_artifact_write_allowed": False, "prediction_artifact_write_allowed": False, "view_artifact_write_allowed": False, "autotrade_trigger_allowed": False, "broker_private_api_allowed": False, "ledger_append": False, "mode_apply": False, "parameter_apply": False, "would_send_to_broker": False}}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
