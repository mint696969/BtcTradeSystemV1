# path: ./tools/test_phase4a_prediction_system_ps_q18am_ui_smoke_guard.py
# desc: Focused guard for PS-Q18AM UI smoke/manual visual check packet.

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

from tools.test_phase4a_prediction_system_ps_q18am_ui_smoke_check import build_ps_q18am_ui_smoke_check_packet  # noqa: E402

WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AM_WARROOM_LATEST_PREDICTION_AUTO_REFRESH_UI_SMOKE_CHECK_2026-06-24.md"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18am_ui_smoke_check.py"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AM_WARROOM_LATEST_PREDICTION_AUTO_REFRESH_UI_SMOKE_CHECK_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18am_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18am_ui_smoke_check.py",
    "tools/test_phase4a_prediction_system_ps_q18am_ui_smoke_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    for path in (DOC, UNIT):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    warroom_text = _read(WARROOM)
    for marker in (
        "render_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel",
        "render_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel",
        "warroom_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel",
        "warroom_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel",
    ):
        if marker not in warroom_text:
            failures.append(f"missing WarRoom marker: {marker}")
    packet = build_ps_q18am_ui_smoke_check_packet()
    if packet.get("ok") is not True:
        failures.append(f"smoke packet must be ok: {packet}")
    for key in (
        "auto_refresh_enabled",
        "fragment_slot_refresh_path_enabled",
        "partial_update_enabled",
        "broad_page_reload_disabled",
        "freshness_monitor_enabled",
        "error_fallback_visible",
    ):
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in (
        "real_prediction_widget_render_invoked",
        "streamlit_real_widget_render_invoked",
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "parameter_apply_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
    ):
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "PS-Q18AM",
        "Manual smoke checklist",
        "WarRoom tab automatically refreshes prediction display=true",
        "broad page reload=false",
        "autotrade_trigger_allowed=false",
        "broker_private_api_allowed=false",
    ):
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
        "guard": "ps_q18am_ui_smoke_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "manual_checklist_count": packet.get("manual_checklist_count"),
        "intermediate_goal_reached": packet.get("intermediate_goal_reached"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18am_ui_smoke_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
