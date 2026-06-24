# path: ./tools/test_phase4a_prediction_system_ps_q18ax_latest_prediction_observation_milestone_close_guard.py
# desc: Focused guard for PS-Q18AX latest prediction observation milestone close.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18ax_latest_prediction_observation_milestone_close import (  # noqa: E402
    EVIDENCE_CHAIN,
    FALSE_BOUNDARIES,
    build_ps_q18ax_latest_prediction_observation_milestone_close_packet,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AX_LATEST_PREDICTION_OBSERVATION_MILESTONE_CLOSE_2026-06-24.md"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18ax_latest_prediction_observation_milestone_close.py"
PS_Q18AW_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AW_WARROOM_OBSERVATION_QUICK_STATUS_MANUAL_UI_SMOKE_EXECUTION_RECORD_2026-06-24.md"
PS_Q18AT_DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AT_LATEST_PREDICTION_IMPLEMENTATION_GATE_REVIEW_PACKET_2026-06-24.md"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AX_LATEST_PREDICTION_OBSERVATION_MILESTONE_CLOSE_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18ax_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18ax_latest_prediction_observation_milestone_close.py",
    "tools/test_phase4a_prediction_system_ps_q18ax_latest_prediction_observation_milestone_close_guard.py",
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
    packet = build_ps_q18ax_latest_prediction_observation_milestone_close_packet()
    if packet.get("latest_prediction_observation_milestone_closed") is not True:
        failures.append("milestone must be closed")
    if packet.get("milestone_close_result") != "closed_with_manual_ui_smoke_pass":
        failures.append("milestone close result mismatch")
    if packet.get("evidence_chain_count") != len(EVIDENCE_CHAIN):
        failures.append("evidence chain count mismatch")
    if packet.get("implementation_gate_review_result") != "blocked_not_ready_to_enable":
        failures.append("implementation gate must stay blocked")
    if packet.get("implementation_gate_opened") is not False:
        failures.append("implementation gate must not be opened")
    if packet.get("real_rendering_enabled") is not False:
        failures.append("real rendering must stay disabled")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    q18aw_text = _read(PS_Q18AW_DOC) if PS_Q18AW_DOC.exists() else ""
    if "manual_ui_smoke_result=pass" not in q18aw_text:
        failures.append("PS-Q18AW pass evidence missing")
    if "repo_head_at_uicheck=625de736" not in q18aw_text:
        failures.append("PS-Q18AW uicheck head evidence missing")
    q18at_text = _read(PS_Q18AT_DOC) if PS_Q18AT_DOC.exists() else ""
    if "implementation_gate_review_result=blocked_not_ready_to_enable" not in q18at_text:
        failures.append("PS-Q18AT blocked implementation gate evidence missing")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "PS-Q18AX",
        "latest_prediction_observation_milestone_closed=true",
        "milestone_close_result=closed_with_manual_ui_smoke_pass",
        "manual_ui_smoke_result=pass",
        "implementation_gate_review_result=blocked_not_ready_to_enable",
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
        "guard": "ps_q18ax_latest_prediction_observation_milestone_close_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "milestone_close_result": packet.get("milestone_close_result"),
        "evidence_chain_count": packet.get("evidence_chain_count"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18ax_latest_prediction_observation_milestone_close_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
