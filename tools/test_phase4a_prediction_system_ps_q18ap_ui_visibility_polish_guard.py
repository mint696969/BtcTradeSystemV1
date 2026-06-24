# path: ./tools/test_phase4a_prediction_system_ps_q18ap_ui_visibility_polish_guard.py
# desc: Focused guard for PS-Q18AP UI visibility polish.

from __future__ import annotations

import ast
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

Q18AJ = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel.py"
Q18AK = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AP_WARROOM_LATEST_PREDICTION_UI_VISIBILITY_POLISH_2026-06-24.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AP_WARROOM_LATEST_PREDICTION_UI_VISIBILITY_POLISH_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ap_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ap_ui_visibility_polish.py",
    "tools/test_phase4a_prediction_system_ps_q18ap_ui_visibility_polish_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    for path in (Q18AJ, Q18AK):
        try:
            ast.parse(_read(path), filename=str(path))
        except SyntaxError as exc:
            failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    q18aj_text = _read(Q18AJ)
    q18ak_text = _read(Q18AK)
    for marker in ("latest_prediction_summary_widget_q18aj_searchable_plain_text", "PS_Q18AP_SEARCHABLE_REFRESH_HEARTBEAT", "st.text"):
        if marker not in q18aj_text:
            failures.append(f"missing Q18AJ marker: {marker}")
    for marker in ("latest_prediction_summary_widget_q18ak_searchable_plain_text", "PS_Q18AP_SEARCHABLE_FRESHNESS_STATUS", "freshness_state=", "safe_fallback_reason_codes=", "st.text"):
        if marker not in q18ak_text:
            failures.append(f"missing Q18AK marker: {marker}")
    for forbidden in ("render_page_auto_refresh", "location.reload", "send_order(", "create_order(", "write_text(", "write_bytes("):
        if forbidden in q18aj_text or forbidden in q18ak_text:
            failures.append(f"forbidden token in panel files: {forbidden}")
    q18aj = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet()
    q18ak = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(now_utc="2026-06-24T04:57:45Z")
    q18aj_plain = latest_prediction_summary_widget_q18aj_searchable_plain_text(q18aj)
    q18ak_plain = latest_prediction_summary_widget_q18ak_searchable_plain_text(q18ak)
    for marker in ("auto_refresh_enabled=true", "refresh_heartbeat_utc=", "refresh_interval_sec=5"):
        if marker not in q18aj_plain:
            failures.append(f"missing Q18AJ plain marker: {marker}")
    for marker in ("freshness_state=stale", "safe_fallback_reason_codes=source_generated_at_stale", "observed_now_utc=2026-06-24T04:57:45Z"):
        if marker not in q18ak_plain:
            failures.append(f"missing Q18AK plain marker: {marker}")
    for key in Q18AJ_FALSE_BOUNDARIES:
        if q18aj.get(key) is not False:
            failures.append(f"Q18AJ {key} must stay false")
    for key in Q18AK_FALSE_BOUNDARIES:
        if q18ak.get(key) is not False:
            failures.append(f"Q18AK {key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in ("PS-Q18AP", "PS_Q18AP_SEARCHABLE_REFRESH_HEARTBEAT", "PS_Q18AP_SEARCHABLE_FRESHNESS_STATUS", "freshness_state=stale", "safe_fallback_reason_codes=source_generated_at_stale", "broker_private_api_allowed=false"):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q18ap_ui_visibility_polish_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "q18aj_plain_contains_heartbeat": "refresh_heartbeat_utc=" in q18aj_plain,
        "q18ak_plain_contains_searchable_freshness": "freshness_state=stale" in q18ak_plain and "safe_fallback_reason_codes=source_generated_at_stale" in q18ak_plain,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ap_ui_visibility_polish_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
