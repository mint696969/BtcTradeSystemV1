# path: ./tools/test_phase4a_prediction_system_ps_q18an_real_widget_rendering_gate_guard.py
# desc: Focused guard for PS-Q18AN real-widget rendering gate preflight.

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

from tools.test_phase4a_prediction_system_ps_q18an_real_widget_rendering_gate_preflight import (  # noqa: E402
    FALSE_BOUNDARIES,
    build_ps_q18an_real_widget_rendering_gate_preflight_packet,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AN_LATEST_PREDICTION_REAL_WIDGET_RENDERING_GATE_PREFLIGHT_2026-06-24.md"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18an_real_widget_rendering_gate_preflight.py"
WIDGET = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/latest_prediction_summary_widget.py"
SHARED = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/_shared.py"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AN_LATEST_PREDICTION_REAL_WIDGET_RENDERING_GATE_PREFLIGHT_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18an_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18an_real_widget_rendering_gate_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18an_real_widget_rendering_gate_preflight.py",
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
    widget_text = _read(WIDGET)
    shared_text = _read(SHARED)
    if "import streamlit" in widget_text:
        failures.append("latest_prediction_summary_widget must not import streamlit in Q18AN preflight")
    if "build_read_only_prediction_widget_skeleton_packet" not in widget_text:
        failures.append("latest_prediction_summary_widget must still use read-only skeleton packet builder")
    if "read_only_component_skeleton_render_disabled" not in shared_text:
        failures.append("shared skeleton must retain render-disabled component state")
    packet = build_ps_q18an_real_widget_rendering_gate_preflight_packet()
    if packet.get("ok") is not True:
        failures.append(f"preflight packet must be ok: {packet}")
    if packet.get("real_widget_rendering_gate_state") != "preflight_only_rendering_not_enabled":
        failures.append("real widget gate must remain preflight only")
    if packet.get("component_packet_state") != "read_only_component_skeleton_render_disabled":
        failures.append("component packet must remain render-disabled")
    if packet.get("gate_release_requirement_count") != 10:
        failures.append("gate release requirements must be complete")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in ("PS-Q18AN", "real_prediction_widget_rendering_allowed=false", "component_runtime_binding_allowed=false", "Gate release requirements", "no_broker_private_api"):
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
        "guard": "ps_q18an_real_widget_rendering_gate_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "real_widget_rendering_gate_state": packet.get("real_widget_rendering_gate_state"),
        "component_packet_state": packet.get("component_packet_state"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18an_real_widget_rendering_gate_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
