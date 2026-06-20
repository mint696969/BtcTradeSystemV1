# path: ./tools/test_prediction_system_ps_q2_source_artifact_coverage_close_guard.py
# desc: Close guard for PS-Q2 source/artifact input coverage contract slice.

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOUCHED = (
    REPO_ROOT / "btcts_next/src/btcts/prediction/source_artifact_coverage.py",
    REPO_ROOT / "btcts_next/src/btcts/prediction/__init__.py",
    REPO_ROOT / "btcts_next/src/btcts/prediction/system_contract.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q2_source_artifact_coverage_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q2_source_artifact_coverage_close_guard.py",
)
FOCUSED_GUARD = REPO_ROOT / "tools/test_prediction_system_ps_q2_source_artifact_coverage_guard.py"
SPEC_GUARD = REPO_ROOT / "tools/test_prediction_system_inference_formal_spec_guard.py"
PS_C_GUARD = REPO_ROOT / "tools/test_prediction_system_ps_c_contracts_guard.py"
PROTECTED_PREFIXES = (
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
        failures.append(f"guard failed: {path.relative_to(REPO_ROOT)}\nSTDOUT:\n{proc.stdout[-2000:]}\nSTDERR:\n{proc.stderr[-2000:]}")


def main() -> int:
    failures: list[str] = []
    for path in TOUCHED:
        _syntax(path, failures)
    for guard in (FOCUSED_GUARD, SPEC_GUARD, PS_C_GUARD):
        _run(guard, failures)
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    protected_dirty_hits = [line for line in proc.stdout.splitlines() if any(prefix in line for prefix in PROTECTED_PREFIXES)]
    failures.extend(f"protected collector/autotrade dirty: {line}" for line in protected_dirty_hits)
    if failures:
        print("[FAIL] Prediction System PS-Q2 source/artifact coverage close guard")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("[OK] Prediction System PS-Q2 source/artifact coverage close guard")
    return 0


def test_prediction_system_ps_q2_source_artifact_coverage_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
