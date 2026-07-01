# path: ./tools/test_phase4a_prediction_system_ps_q27d_market_regime_card_typography_badge_tune_close_guard.py
# desc: Close guard for PS-Q27D market regime card typography and freshness badge tune.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_card_renderer_q26y.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q27D_MARKET_REGIME_CARD_TYPOGRAPHY_BADGE_TUNE_2026-07-01.md",
    "tools/diagnose_phase4a_prediction_system_ps_q27d_market_regime_card_typography_badge_tune.py",
    "tools/test_phase4a_prediction_system_ps_q27d_market_regime_card_typography_badge_tune.py",
    "tools/test_phase4a_prediction_system_ps_q27d_market_regime_card_typography_badge_tune_close_guard.py",
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
        "guard": "ps_q27d_market_regime_card_typography_badge_tune_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED_DIRTY - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY),
        "contract": {
            "visual_typography_tune_only": True,
            "time_axis_font_size_unchanged": True,
            "horizon_font_size_rem": "0.92rem",
            "regime_font_size_rem": "1.14rem",
            "confidence_font_size_rem": "1.60rem",
            "tag_font_size_rem": "1.04rem",
            "freshness_badge_visibility_tuned": True,
            "freshness_badge_font_size_rem": "0.78rem",
            "freshness_badge_font_weight": 900,
            "freshness_badge_min_width_px": 42,
            "detail_overlay_background": "#F2F4F7",
            "detail_overlay_background_matches_unknown": True,
            "detail_disclosure_mode": "card_overlay",
            "card_detail_overlay_enabled": True,
            "overlay_close_button_enabled": True,
            "card_width_px": 208,
            "production_ui_code_changed": True,
            "warroom_page_changed": False,
            "warroom_page_mounted_unchanged": True,
            "sample_data_only": True,
            "live_data_connected": False,
            "runtime_read_allowed": False,
            "read_only": True,
            "display_only": True,
            "non_executing": True,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "ledger_append": False,
            "mode_apply": False,
            "parameter_apply": False,
            "would_send_to_broker": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
