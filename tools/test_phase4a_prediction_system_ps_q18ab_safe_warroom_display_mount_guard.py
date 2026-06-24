# path: ./tools/test_phase4a_prediction_system_ps_q18ab_safe_warroom_display_mount_guard.py
# desc: Focused guard for PS-Q18AB latest_prediction_summary_widget safe WarRoom display mount panel.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path
import sys

BTCTS_SRC = Path(__file__).resolve().parents[1] / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ab_safe_display_mount_panel import (
    FALSE_BOUNDARIES,
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AB_SAFE_DISPLAY_MOUNT_PANEL_ACK,
    TRUE_BOUNDARIES,
    build_latest_prediction_summary_widget_q18ab_safe_display_mount_panel_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL_INIT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/__init__.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ab_safe_display_mount_panel.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18ab_latest_prediction_summary_widget_safe_warroom_display_mount.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AB_LATEST_PREDICTION_SUMMARY_WIDGET_SAFE_WARROOM_DISPLAY_MOUNT_2026-06-24.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/__init__.py",
    "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ab_safe_display_mount_panel.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AB_LATEST_PREDICTION_SUMMARY_WIDGET_SAFE_WARROOM_DISPLAY_MOUNT_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ab_latest_prediction_summary_widget_safe_warroom_display_mount.py",
    "tools/test_phase4a_prediction_system_ps_q18ab_safe_warroom_display_mount_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ab_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _is_noise_path(rel: str) -> bool:
    return "/__pycache__/" in rel or rel.endswith(".pyc")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    paths: set[str] = set()
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        rel = line[3:].replace(chr(92), "/")
        absolute = REPO_ROOT / rel
        if rel.endswith("/") and absolute.exists():
            for child in absolute.rglob("*"):
                if child.is_file():
                    child_rel = child.relative_to(REPO_ROOT).as_posix()
                    if not _is_noise_path(child_rel):
                        paths.add(child_rel)
        elif not _is_noise_path(rel):
            paths.add(rel)
    return paths


def main_guard() -> int:
    failures: list[str] = []
    for path in (WARROOM_PAGE, PANEL_INIT, PANEL, UNIT, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        if path.suffix == ".py":
            try:
                ast.parse(_read(path), filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    panel_text = _read(PANEL) if PANEL.exists() else ""
    for forbidden in ("Path(", "open(", "read_text(", "read_bytes(", "write_text(", "write_bytes(", "data_read", "data_slice", "glob(", "rglob(", "exists(", "is_file(", "stat(", "render_latest_prediction_summary_widget(", "send_order(", "create_order("):
        if forbidden in panel_text:
            failures.append(f"forbidden token in panel: {forbidden}")
    page_text = _read(WARROOM_PAGE) if WARROOM_PAGE.exists() else ""
    import_token = "render_latest_prediction_summary_widget_q18ab_safe_display_mount_panel"
    if page_text.count(import_token) != 2:
        failures.append(f"warroom_page should contain Q18AB panel import and call exactly once each; count={page_text.count(import_token)}")
    if "Prediction WarRoom latest summary safe display mount" not in page_text:
        failures.append("missing folded section title")
    packet = build_latest_prediction_summary_widget_q18ab_safe_display_mount_panel_packet()
    if packet.get("ok") is not True:
        failures.append(f"safe display mount packet should be ok: {packet}")
    if packet.get("safe_display_mount_panel_ack") != LATEST_PREDICTION_SUMMARY_WIDGET_Q18AB_SAFE_DISPLAY_MOUNT_PANEL_ACK:
        failures.append("safe display mount ack mismatch")
    if packet.get("safe_display_mount_panel_row_count") != 12:
        failures.append("expected 12 safe display mount rows")
    if packet.get("warroom_display_mounted") is not True:
        failures.append("warroom display should be mounted in this slice")
    for key in TRUE_BOUNDARIES:
        if packet.get(key) is not True:
            failures.append(f"{key} must be true")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in ("PS-Q18AB", "safe_display_mount_panel_row_count=12", "warroom_display_mounted=true", "actual_source_read_invoked=false", "real_prediction_widget_rendering_allowed=false", "Next: filesystem exists-check execution"):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {"ok": not failures, "guard": "ps_q18ab_safe_warroom_display_mount_guard", "dirty_paths": sorted(dirty), "unexpected_dirty": sorted(unexpected), "missing_dirty": sorted(missing), "failures": failures}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ab_safe_warroom_display_mount_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
