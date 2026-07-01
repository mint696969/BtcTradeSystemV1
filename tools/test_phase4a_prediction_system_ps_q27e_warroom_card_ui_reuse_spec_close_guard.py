# path: ./tools/test_phase4a_prediction_system_ps_q27e_warroom_card_ui_reuse_spec_close_guard.py
# desc: Close guard for PS-Q27E WarRoom card UI reuse spec.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q27E_WARROOM_CARD_UI_REUSE_SPEC_2026-07-02.md",
    "tools/diagnose_phase4a_prediction_system_ps_q27e_warroom_card_ui_reuse_spec.py",
    "tools/test_phase4a_prediction_system_ps_q27e_warroom_card_ui_reuse_spec.py",
    "tools/test_phase4a_prediction_system_ps_q27e_warroom_card_ui_reuse_spec_close_guard.py",
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
        "guard": "ps_q27e_warroom_card_ui_reuse_spec_close_guard",
        "dirty_paths": sorted(dirty),
        "missing_dirty": sorted(EXPECTED_DIRTY - dirty),
        "unexpected_dirty": sorted(dirty - EXPECTED_DIRTY),
        "contract": {
            "spec_only_change": True,
            "market_regime_card_ui_is_canonical_reference": True,
            "future_prediction_card_reuse_expected": True,
            "next_thread_ready_for_market_regime_live_data_binding_design": True,
            "card_width_px": 208,
            "horizon_font_size_rem": "0.92rem",
            "primary_label_font_size_rem": "1.14rem",
            "confidence_font_size_rem": "1.60rem",
            "short_tag_font_size_rem": "1.04rem",
            "freshness_badge_font_size_rem": "0.78rem",
            "freshness_badge_font_weight": 900,
            "freshness_badge_min_width_px": 42,
            "detail_disclosure_mode": "card_overlay",
            "detail_overlay_background": "#F2F4F7",
            "detail_overlay_background_matches_unknown": True,
            "production_ui_code_changed": False,
            "runtime_code_changed": False,
            "warroom_page_changed": False,
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
            "ledger_append_allowed": False,
            "mode_apply_allowed": False,
            "parameter_apply_allowed": False,
            "would_send_to_broker": False,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main_guard())
