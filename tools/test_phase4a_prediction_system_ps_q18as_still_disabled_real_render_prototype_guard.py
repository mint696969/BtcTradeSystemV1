# path: ./tools/test_phase4a_prediction_system_ps_q18as_still_disabled_real_render_prototype_guard.py
# desc: Focused guard for PS-Q18AS still-disabled real-render prototype.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BTCTS_SRC = REPO_ROOT / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.apps.operator_ui.components.prediction_widgets.latest_prediction_summary_widget import (  # noqa: E402
    REAL_RENDER_PROTOTYPE_FALSE_BOUNDARIES,
    build_latest_prediction_summary_widget_real_render_prototype_packet,
    render_latest_prediction_summary_widget,
)

WIDGET = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/latest_prediction_summary_widget.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AS_LATEST_PREDICTION_STILL_DISABLED_REAL_RENDER_PROTOTYPE_2026-06-24.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/latest_prediction_summary_widget.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AS_LATEST_PREDICTION_STILL_DISABLED_REAL_RENDER_PROTOTYPE_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18as_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18as_still_disabled_real_render_prototype.py",
    "tools/test_phase4a_prediction_system_ps_q18as_still_disabled_real_render_prototype_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    try:
        ast.parse(_read(WIDGET), filename=str(WIDGET))
    except SyntaxError as exc:
        failures.append(f"widget syntax failed: {exc}")
    widget_text = _read(WIDGET)
    for marker in (
        "build_latest_prediction_summary_widget_real_render_prototype_packet",
        "REAL_RENDER_PROTOTYPE_GATE_STATE",
        "still_disabled_real_render_prototype_blocked",
        "separate_future_implementation_gate_required",
    ):
        if marker not in widget_text:
            failures.append(f"missing widget marker: {marker}")
    for forbidden in ("import streamlit", "from streamlit", "st.", "dataframe(", "button(", "write_text(", "write_bytes(", "send_order(", "create_order("):
        if forbidden in widget_text:
            failures.append(f"forbidden token in widget: {forbidden}")
    skeleton = render_latest_prediction_summary_widget()
    if skeleton.get("component_state") != "read_only_component_skeleton_render_disabled":
        failures.append("existing render function must still return skeleton")
    packet = build_latest_prediction_summary_widget_real_render_prototype_packet(
        requested_enable_real_render=True,
        implementation_gate_open=True,
        manual_ui_review_passed=True,
        rollback_plan_ready=True,
    )
    if packet.get("prototype_state") != "still_disabled_real_render_prototype_blocked":
        failures.append("prototype state must remain blocked")
    if packet.get("real_rendering_enabled") is not False:
        failures.append("prototype must not enable real rendering")
    for key in REAL_RENDER_PROTOTYPE_FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "PS-Q18AS",
        "prototype_state=still_disabled_real_render_prototype_blocked",
        "skeleton_packet_preserved=true",
        "real_rendering_enabled=false",
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
        "guard": "ps_q18as_still_disabled_real_render_prototype_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "prototype_state": packet.get("prototype_state"),
        "real_rendering_enabled": packet.get("real_rendering_enabled"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18as_still_disabled_real_render_prototype_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
