# path: ./tools/test_phase4a_prediction_system_ps_q18bc_warroom_header_compact_polish_cleanup_close_guard.py
# desc: Focused guard for PS-Q18BC WarRoom header compact polish and cleanup close.

from __future__ import annotations

import ast
import inspect
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for path in (REPO_ROOT, SRC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import btcts.apps.operator_ui.components.warroom_header as warroom_header  # noqa: E402
from tools.test_phase4a_prediction_system_ps_q18bc_warroom_header_compact_polish_cleanup_close import (  # noqa: E402
    FALSE_BOUNDARIES,
    build_ps_q18bc_cleanup_close_packet,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18BC_WARROOM_HEADER_COMPACT_POLISH_CLEANUP_CLOSE_2026-06-24.md"
HEADER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/warroom_header.py"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18bc_warroom_header_compact_polish_cleanup_close.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/warroom_header.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18BC_WARROOM_HEADER_COMPACT_POLISH_CLEANUP_CLOSE_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18bc_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18bc_warroom_header_compact_polish_cleanup_close.py",
    "tools/test_phase4a_prediction_system_ps_q18bc_warroom_header_compact_polish_cleanup_close_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    for path in (HEADER, UNIT):
        try:
            ast.parse(_read(path), filename=str(path))
        except SyntaxError as exc:
            failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    header_text = _read(HEADER)
    render_source = inspect.getsource(warroom_header.render)
    for removed_render_marker in (
        "build_warroom_market_reading_caption(",
        "build_warroom_operational_reading_caption(",
        "summary_widget_caption(",
        "load_execution_market_summary_widget_model(",
        "load_execution_market_summary_status_payload(",
        "render_scrollable_text_block(",
    ):
        if removed_render_marker in render_source:
            failures.append(f"long diagnostic render marker still in render(): {removed_render_marker}")
    for preserved_marker in (
        "def build_warroom_market_reading_caption",
        "def build_warroom_operational_reading_caption",
        "render_compact_metric_grid",
        "warroom_header_summary_caption",
        "warroom_generic_source_caption",
    ):
        if preserved_marker not in header_text:
            failures.append(f"required marker missing: {preserved_marker}")
    packet = build_ps_q18bc_cleanup_close_packet()
    if packet.get("warroom_cleanup_optimization_complete") is not True:
        failures.append("cleanup optimization must be complete")
    if packet.get("component_modules_deleted_this_slice") is not False:
        failures.append("component modules must not be deleted")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "PS-Q18BC",
        "warroom_header_normal_ui_compact=true",
        "warroom_header_long_market_reading_caption_hidden=true",
        "warroom_header_long_operational_reading_caption_hidden=true",
        "warroom_header_summary_widget_diagnostic_caption_hidden=true",
        "caption_builder_functions_preserved=true",
        "warroom_cleanup_optimization_complete=true",
        "real_prediction_widget_rendering_allowed=false",
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
        "guard": "ps_q18bc_warroom_header_compact_polish_cleanup_close_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "warroom_cleanup_optimization_complete": packet.get("warroom_cleanup_optimization_complete"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18bc_warroom_header_compact_polish_cleanup_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
