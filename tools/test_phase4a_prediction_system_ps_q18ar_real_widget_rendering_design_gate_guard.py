# path: ./tools/test_phase4a_prediction_system_ps_q18ar_real_widget_rendering_design_gate_guard.py
# desc: Focused guard for PS-Q18AR explicit real-widget rendering design gate.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18ar_real_widget_rendering_design_gate import (  # noqa: E402
    FALSE_BOUNDARIES,
    FUTURE_RELEASE_REQUIREMENTS,
    build_ps_q18ar_real_widget_rendering_design_gate_packet,
)

WIDGET = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/latest_prediction_summary_widget.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AR_LATEST_PREDICTION_EXPLICIT_REAL_WIDGET_RENDERING_DESIGN_GATE_2026-06-24.md"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18ar_real_widget_rendering_design_gate.py"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AR_LATEST_PREDICTION_EXPLICIT_REAL_WIDGET_RENDERING_DESIGN_GATE_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ar_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ar_real_widget_rendering_design_gate.py",
    "tools/test_phase4a_prediction_system_ps_q18ar_real_widget_rendering_design_gate_guard.py",
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
    if "import streamlit" in widget_text or "from streamlit" in widget_text:
        failures.append("current widget must not import Streamlit")
    if "build_read_only_prediction_widget_skeleton_packet" not in widget_text:
        failures.append("current widget must still build read-only skeleton packet")
    if "def render_latest_prediction_summary_widget" not in widget_text:
        failures.append("current widget render function missing")
    for forbidden in ("st.", "dataframe(", "button(", "write_text(", "write_bytes(", "send_order(", "create_order("):
        if forbidden in widget_text:
            failures.append(f"forbidden runtime/render token in current widget: {forbidden}")
    packet = build_ps_q18ar_real_widget_rendering_design_gate_packet()
    if packet.get("real_widget_rendering_design_gate_state") != "design_only_rendering_not_enabled":
        failures.append("design gate must remain design_only_rendering_not_enabled")
    if packet.get("future_release_requirement_count") != len(FUTURE_RELEASE_REQUIREMENTS):
        failures.append("future release requirement count mismatch")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "PS-Q18AR",
        "design_only_rendering_not_enabled",
        "future_real_render_gate_required=true",
        "rollback_to_skeleton_packet_path",
        "no_broker_private_api",
        "real_prediction_widget_rendering_allowed=false",
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
        "guard": "ps_q18ar_real_widget_rendering_design_gate_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "design_gate_state": packet.get("real_widget_rendering_design_gate_state"),
        "future_release_requirement_count": packet.get("future_release_requirement_count"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ar_real_widget_rendering_design_gate_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
