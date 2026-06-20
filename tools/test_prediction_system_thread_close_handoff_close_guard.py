# path: ./tools/test_prediction_system_thread_close_handoff_close_guard.py
# desc: Close guard for Prediction System thread-close handoff/docs.

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOUCHED = (
    REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_INFERENCE_FORMAL_SPEC_BTC_BITFLYER_2026-06-20.md",
    REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_ROADMAP_STATUS_PS_Q8F_HANDOFF_2026-06-21.md",
    REPO_ROOT / "tools/test_prediction_system_thread_close_handoff_guard.py",
    REPO_ROOT / "tools/test_prediction_system_thread_close_handoff_close_guard.py",
)
GUARDS = (
    REPO_ROOT / "tools/test_prediction_system_thread_close_handoff_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q8e_mount_review_ux_contract_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q8d_guarded_warroom_page_insertion_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q8c_warroom_page_insertion_contract_guard.py",
)
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/autotrade/",
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
)


def _syntax(path: Path, failures: list[str]) -> None:
    if path.suffix != ".py":
        return
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except Exception as exc:
        failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")


def _run(path: Path, failures: list[str]) -> None:
    proc = subprocess.run([sys.executable, str(path)], cwd=REPO_ROOT, text=True, capture_output=True, timeout=120)
    if proc.returncode != 0:
        failures.append(f"guard failed: {path.relative_to(REPO_ROOT)}\nSTDOUT:\n{proc.stdout[-2000:]}\nSTDERR:\n{proc.stderr[-2000:]}")


def main() -> int:
    failures: list[str] = []
    for path in TOUCHED:
        if not path.exists():
            failures.append(f"missing touched file: {path.relative_to(REPO_ROOT)}")
        _syntax(path, failures)
    for guard in GUARDS:
        _run(guard, failures)
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    failures.extend(f"protected runtime/view dirty: {line}" for line in proc.stdout.splitlines() if any(prefix in line for prefix in PROTECTED_PREFIXES))
    if failures:
        print("[FAIL] Prediction System thread-close handoff close guard")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("[OK] Prediction System thread-close handoff close guard")
    return 0


def test_prediction_system_thread_close_handoff_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
