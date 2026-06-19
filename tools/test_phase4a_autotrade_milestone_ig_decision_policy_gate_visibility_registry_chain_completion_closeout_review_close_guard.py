# path: ./tools/test_phase4a_autotrade_milestone_ig_decision_policy_gate_visibility_registry_chain_completion_closeout_review_close_guard.py
# desc: Close guard for S170 decision policy gate visibility registry chain completion closeout review. Syntax-checks touched files and reruns focused IG guard.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOUCHED = (
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_registry_chain_completion_closeout_review.py",
    REPO_ROOT / "tools/test_phase4a_autotrade_milestone_ig_decision_policy_gate_visibility_registry_chain_completion_closeout_review_guard.py",
    REPO_ROOT / "tools/test_phase4a_autotrade_milestone_ig_decision_policy_gate_visibility_registry_chain_completion_closeout_review_close_guard.py",
)
GUARD = REPO_ROOT / "tools/test_phase4a_autotrade_milestone_ig_decision_policy_gate_visibility_registry_chain_completion_closeout_review_guard.py"


def _syntax(path: Path, failures: list[str]) -> dict[str, object]:
    if not path.exists():
        failures.append(f"missing syntax target: {path.relative_to(REPO_ROOT)}")
        return {"ok": False, "missing": True}
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        return {"ok": True}
    except Exception as exc:
        failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
        return {"ok": False, "error": str(exc)}


def main() -> int:
    failures: list[str] = []
    syntax = {str(path.relative_to(REPO_ROOT)): _syntax(path, failures) for path in TOUCHED}
    guard_proc = subprocess.run([sys.executable, str(GUARD)], cwd=REPO_ROOT, text=True, capture_output=True, timeout=90)
    try:
        guard_payload = json.loads(guard_proc.stdout)
    except Exception as exc:
        guard_payload = {"ok": False, "error": f"guard stdout was not JSON: {exc}", "stdout_tail": guard_proc.stdout[-1600:]}
    if guard_proc.returncode != 0 or guard_payload.get("ok") is not True:
        failures.append("focused IG decision policy gate visibility registry chain completion closeout review guard did not close")
    payload = {
        "ok": not failures,
        "phase": "phase4a_autotrade_milestone_ig_decision_policy_gate_visibility_registry_chain_completion_closeout_review_close_guard",
        "status": "closed" if not failures else "open",
        "contract": {
            "syntax_checked_without_pyc": all(item.get("ok") is True for item in syntax.values()),
            "focused_guard_closed": guard_proc.returncode == 0 and guard_payload.get("ok") is True,
        },
        "syntax": syntax,
        "focused_guard": {
            "returncode": guard_proc.returncode,
            "ok": guard_payload.get("ok"),
            "status": guard_payload.get("status"),
            "contract": guard_payload.get("contract"),
            "failures": guard_payload.get("failures"),
        },
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_decision_policy_gate_visibility_registry_chain_completion_closeout_review_close_guard_closes() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
