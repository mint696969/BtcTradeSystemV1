# path: ./tools/test_phase4a_prediction_system_ps_q18al_intermediate_goal_close_guard.py
# desc: Focused structural guard for PS-Q18AL WarRoom latest prediction auto-refresh intermediate-goal close.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel import build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel import build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AL_WARROOM_LATEST_PREDICTION_AUTO_REFRESH_INTERMEDIATE_GOAL_CLOSE_2026-06-24.md"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18al_intermediate_goal_close.py"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AL_WARROOM_LATEST_PREDICTION_AUTO_REFRESH_INTERMEDIATE_GOAL_CLOSE_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18al_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18al_intermediate_goal_close.py",
    "tools/test_phase4a_prediction_system_ps_q18al_intermediate_goal_close_guard.py",
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
        "_render_prediction_warroom_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_section(fragment_enabled=fragment_enabled)",
        "_render_prediction_warroom_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_section(fragment_enabled=fragment_enabled)",
    ):
        if marker not in warroom_text:
            failures.append(f"missing WarRoom close marker: {marker}")
    q18aj = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet(fragment_supported=True, ui_auto_refresh=True)
    q18ak = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(now_utc="2026-06-24T13:20:00Z", fragment_supported=True, ui_auto_refresh=True)
    if q18aj.get("auto_refresh_enabled") is not True:
        failures.append("Q18AJ auto_refresh_enabled must be true")
    if q18aj.get("fragment_slot_refresh_path_enabled") is not True:
        failures.append("Q18AJ fragment slot refresh must be true")
    if q18ak.get("freshness_monitor_enabled") is not True:
        failures.append("Q18AK freshness monitor must be true")
    if q18ak.get("error_fallback_visible") is not True:
        failures.append("Q18AK error fallback must be visible")
    if q18ak.get("freshness_state") != "stale":
        failures.append("Q18AK freshness_state must be stale for close guard")
    for packet_name, packet in (("q18aj", q18aj), ("q18ak", q18ak)):
        for key in ("real_prediction_widget_render_invoked", "streamlit_real_widget_render_invoked", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "parameter_apply_allowed", "ledger_append_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed"):
            if packet.get(key) is not False:
                failures.append(f"{packet_name}:{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in ("PS-Q18AL", "WarRoom tab automatically refreshes prediction display=true", "PS-Q18AJ auto_refresh_enabled=true", "PS-Q18AK freshness_monitor_enabled=true", "autotrade_trigger_allowed=false", "broker_private_api_allowed=false"):
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
        "guard": "ps_q18al_intermediate_goal_close_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "intermediate_goal_reached": q18aj.get("auto_refresh_enabled") is True and q18ak.get("freshness_monitor_enabled") is True,
        "freshness_state": q18ak.get("freshness_state"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18al_intermediate_goal_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
