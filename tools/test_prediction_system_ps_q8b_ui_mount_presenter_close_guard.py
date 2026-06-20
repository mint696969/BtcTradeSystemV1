# path: ./tools/test_prediction_system_ps_q8b_ui_mount_presenter_close_guard.py
# desc: Close guard for PS-Q8B Prediction WarRoom UI mount presenter packet.

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOUCHED = (
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_ui_mount_presenter.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q8b_ui_mount_presenter_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q8b_ui_mount_presenter_close_guard.py",
)
GUARDS = (
    REPO_ROOT / "tools/test_prediction_system_ps_q8b_ui_mount_presenter_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q8a_ui_mount_catalog_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q7l_readiness_widget_registry_registration_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q7k_supplemental_handoff_readiness_widget_group_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q7j_supplemental_handoff_readiness_summary_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q6i_handoff_catalog_visibility_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q6f_supplemental_widget_registry_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q4b_warroom_widget_groups_guard.py",
)
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/autotrade/",
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
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
    for guard in GUARDS:
        _run(guard, failures)
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    failures.extend(f"protected runtime/view dirty: {line}" for line in proc.stdout.splitlines() if any(prefix in line for prefix in PROTECTED_PREFIXES))
    if failures:
        print("[FAIL] Prediction System PS-Q8B UI mount presenter close guard")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("[OK] Prediction System PS-Q8B UI mount presenter close guard")
    return 0


def test_prediction_system_ps_q8b_ui_mount_presenter_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
