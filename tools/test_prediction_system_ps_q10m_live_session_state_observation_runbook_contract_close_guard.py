# path: ./tools/test_prediction_system_ps_q10m_live_session_state_observation_runbook_contract_close_guard.py
# desc: Close guard for PS-Q10M live session-state observation runbook contract.

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOUCHED = (
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_live_session_state_observation_runbook_contract.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q10m_live_session_state_observation_runbook_contract_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q10m_live_session_state_observation_runbook_contract_close_guard.py",
)
GUARDS = (
    REPO_ROOT / "tools/test_prediction_system_ps_q10m_live_session_state_observation_runbook_contract_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q10l_actual_session_state_panel_handoff_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q10l_actual_session_state_panel_handoff_close_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q10k_actual_review_packet_session_state_handoff_harness_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q10k_actual_review_packet_session_state_handoff_harness_close_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9v_warroom_top_default_expanded_ui_layout_guard.py",
)
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_source_handoff.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_local_observation_hook.py",
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/autotrade/",
)


def _syntax(path: Path, failures: list[str]) -> None:
    if not path.exists():
        failures.append(f"missing touched file: {path.relative_to(REPO_ROOT)}")
        return
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except Exception as exc:
        failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")


def _run(path: Path, failures: list[str]) -> None:
    proc = subprocess.run([sys.executable, str(path)], cwd=REPO_ROOT, text=True, capture_output=True, timeout=120)
    if proc.returncode != 0:
        failures.append(
            f"guard failed: {path.relative_to(REPO_ROOT)}\n"
            f"STDOUT:\n{proc.stdout[-2000:]}\nSTDERR:\n{proc.stderr[-2000:]}"
        )


def main() -> int:
    failures: list[str] = []
    for path in TOUCHED:
        _syntax(path, failures)
    for guard in GUARDS:
        _run(guard, failures)
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    protected_dirty_hits = [line for line in proc.stdout.splitlines() if any(prefix in line for prefix in PROTECTED_PREFIXES)]
    failures.extend(f"protected dirty path: {line}" for line in protected_dirty_hits)
    if failures:
        print("[FAIL] Prediction System PS-Q10M live session-state observation runbook contract close guard")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("[OK] Prediction System PS-Q10M live session-state observation runbook contract close guard")
    return 0


def test_prediction_system_ps_q10m_live_session_state_observation_runbook_contract_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
