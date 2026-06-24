# path: ./tools/test_phase4a_prediction_system_ps_q18at_implementation_gate_review_packet_guard.py
# desc: Focused guard for PS-Q18AT implementation-gate review packet.

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
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18at_implementation_gate_review_packet import (  # noqa: E402
    IMPLEMENTATION_GATE_REVIEW_BLOCKERS,
    build_ps_q18at_implementation_gate_review_packet,
)

WIDGET = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_widgets/latest_prediction_summary_widget.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AT_LATEST_PREDICTION_IMPLEMENTATION_GATE_REVIEW_PACKET_2026-06-24.md"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18at_implementation_gate_review_packet.py"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AT_LATEST_PREDICTION_IMPLEMENTATION_GATE_REVIEW_PACKET_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18at_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18at_implementation_gate_review_packet.py",
    "tools/test_phase4a_prediction_system_ps_q18at_implementation_gate_review_packet_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    for path in (UNIT,):
        try:
            ast.parse(_read(path), filename=str(path))
        except SyntaxError as exc:
            failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    widget_text = _read(WIDGET)
    if "import streamlit" in widget_text or "from streamlit" in widget_text or "st." in widget_text:
        failures.append("widget must still not contain Streamlit rendering")
    if "build_latest_prediction_summary_widget_real_render_prototype_packet" not in widget_text:
        failures.append("PS-Q18AS prototype builder missing")
    packet = build_ps_q18at_implementation_gate_review_packet()
    if packet.get("implementation_gate_review_result") != "blocked_not_ready_to_enable":
        failures.append("review result must be blocked_not_ready_to_enable")
    if packet.get("prototype_real_rendering_enabled") is not False:
        failures.append("prototype real rendering must remain false")
    if packet.get("blocker_count") != len(IMPLEMENTATION_GATE_REVIEW_BLOCKERS):
        failures.append("blocker count mismatch")
    for key in ("real_prediction_widget_rendering_allowed", "streamlit_real_widget_render_invoked", "component_runtime_binding_allowed", "autotrade_trigger_allowed", "broker_private_api_allowed"):
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "PS-Q18AT",
        "implementation_gate_review_result=blocked_not_ready_to_enable",
        "prototype_state=still_disabled_real_render_prototype_blocked",
        "real_rendering_enabled=false",
        "manual_ui_review_required_before_enablement=true",
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
        "guard": "ps_q18at_implementation_gate_review_packet_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "implementation_gate_review_result": packet.get("implementation_gate_review_result"),
        "blocker_count": packet.get("blocker_count"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18at_implementation_gate_review_packet_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
