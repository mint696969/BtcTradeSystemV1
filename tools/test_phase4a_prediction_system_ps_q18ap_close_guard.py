# path: ./tools/test_phase4a_prediction_system_ps_q18ap_close_guard.py
# desc: Close guard for PS-Q18AP UI visibility polish.

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

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel import (  # noqa: E402
    FALSE_BOUNDARIES as Q18AJ_FALSE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet,
    latest_prediction_summary_widget_q18aj_searchable_plain_text,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel import (  # noqa: E402
    FALSE_BOUNDARIES as Q18AK_FALSE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet,
    latest_prediction_summary_widget_q18ak_searchable_plain_text,
)

EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AP_WARROOM_LATEST_PREDICTION_UI_VISIBILITY_POLISH_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ap_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ap_ui_visibility_polish.py",
    "tools/test_phase4a_prediction_system_ps_q18ap_ui_visibility_polish_guard.py",
}


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    q18aj = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet()
    q18ak = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(now_utc="2026-06-24T04:57:45Z")
    q18aj_plain = latest_prediction_summary_widget_q18aj_searchable_plain_text(q18aj)
    q18ak_plain = latest_prediction_summary_widget_q18ak_searchable_plain_text(q18ak)
    if "refresh_heartbeat_utc=" not in q18aj_plain:
        failures.append("refresh heartbeat plain token missing")
    if "auto_refresh_enabled=true" not in q18aj_plain:
        failures.append("auto_refresh_enabled plain token missing")
    if "freshness_state=stale" not in q18ak_plain:
        failures.append("freshness_state plain token missing")
    if "safe_fallback_reason_codes=source_generated_at_stale" not in q18ak_plain:
        failures.append("safe_fallback_reason_codes plain token missing")
    for key in Q18AJ_FALSE_BOUNDARIES:
        if q18aj.get(key) is not False:
            failures.append(f"Q18AJ {key} must stay false")
    for key in Q18AK_FALSE_BOUNDARIES:
        if q18ak.get(key) is not False:
            failures.append(f"Q18AK {key} must stay false")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q18ap_close_guard",
        "phase": "phase3_warroom_latest_prediction_ui_visibility_polish_ready_for_manual_resmoke",
        "contract": {
            "ps_q18ap_closed": not failures,
            "searchable_refresh_heartbeat_visible": "refresh_heartbeat_utc=" in q18aj_plain,
            "searchable_freshness_state_visible": "freshness_state=stale" in q18ak_plain,
            "searchable_safe_fallback_reason_codes_visible": "safe_fallback_reason_codes=source_generated_at_stale" in q18ak_plain,
            "real_prediction_widget_render_invoked": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "next_slice": "manual UI smoke re-check for searchable tokens and visible heartbeat",
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ap_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
