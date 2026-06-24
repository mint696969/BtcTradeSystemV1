# path: ./tools/test_phase4a_prediction_system_ps_q18ai_warroom_render_disabled_packet_panel_guard.py
# desc: Focused guard for PS-Q18AI WarRoom render-disabled packet status/value panel mount.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ai_warroom_render_disabled_packet_panel import FALSE_BOUNDARIES, TRUE_BOUNDARIES, build_latest_prediction_summary_widget_q18ai_warroom_panel_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ai_warroom_render_disabled_packet_panel.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18ai_warroom_render_disabled_packet_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AI_LATEST_PREDICTION_SUMMARY_WIDGET_WARROOM_RENDER_DISABLED_PACKET_PANEL_2026-06-24.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ai_warroom_render_disabled_packet_panel.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AI_LATEST_PREDICTION_SUMMARY_WIDGET_WARROOM_RENDER_DISABLED_PACKET_PANEL_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ai_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ai_warroom_render_disabled_packet_panel.py",
    "tools/test_phase4a_prediction_system_ps_q18ai_warroom_render_disabled_packet_panel_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    for path in (WARROOM, PANEL, UNIT, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    warroom_text = _read(WARROOM) if WARROOM.exists() else ""
    for marker in (
        "render_latest_prediction_summary_widget_q18ai_warroom_render_disabled_packet_panel",
        "warroom_latest_prediction_summary_widget_q18ai_render_disabled_packet_panel",
        "_render_prediction_warroom_latest_prediction_summary_widget_q18ai_render_disabled_packet_panel_section()",
    ):
        if marker not in warroom_text:
            failures.append(f"missing warroom marker: {marker}")
    panel_text = _read(PANEL) if PANEL.exists() else ""
    for required in ("st.dataframe", "refresh=false", "build_latest_prediction_summary_widget_q18ah_render_disabled_packet_result_packet"):
        if required not in panel_text:
            failures.append(f"missing panel marker: {required}")
    for forbidden in ("open(", "read_text(", "read_bytes(", "write_text(", "write_bytes(", "json.loads", "send_order(", "create_order("):
        if forbidden in panel_text:
            failures.append(f"forbidden token in panel source: {forbidden}")
    packet = build_latest_prediction_summary_widget_q18ai_warroom_panel_packet()
    if packet.get("ok") is not True:
        failures.append(f"panel packet must be ok: {packet}")
    if packet.get("display_row_count") != 12:
        failures.append("display row count must be 12")
    for key in TRUE_BOUNDARIES:
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in ("PS-Q18AI", "warroom_display_mounted=true", "auto_refresh_enabled=false", "Next: bounded auto-refresh runner/panel"):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {"ok": not failures, "guard": "ps_q18ai_warroom_render_disabled_packet_panel_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "missing_dirty": sorted(missing), "failures": failures, "display_row_count": packet.get("display_row_count")}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ai_warroom_render_disabled_packet_panel_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
