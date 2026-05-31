# path: ./tools/test_phase4a_post_phasec_total_guard.py
# desc: Phase 4-A post Phase C total regression guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]

GUARD_SCRIPTS = [
    "tools/test_phase4a_phasec_close_bundle.py",
    "tools/test_phase4a_post_phasec_downstream_boundary_check.py",
    "tools/test_phase4a_l3_l4_consumer_boundary_audit.py",
]


def _compile_guard_scripts(failures: List[str]) -> Dict[str, Any]:
    passed: List[str] = []
    failed: List[Dict[str, str]] = []

    for rel_path in GUARD_SCRIPTS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            failed.append({"path": rel_path, "error": "missing"})
            failures.append(f"guard script missing: {rel_path}")
            continue

        try:
            py_compile.compile(str(path), doraise=True)
            passed.append(rel_path)
        except Exception as exc:
            failed.append({"path": rel_path, "error": str(exc)})
            failures.append(f"guard script py_compile failed: {rel_path}: {exc}")

    return {
        "passed_count": len(passed),
        "failed": failed,
    }


def _run_json_guard(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"guard script missing: {rel_path}")
        return {
            "returncode": None,
            "ok": False,
            "json": None,
            "stdout_tail": "",
            "stderr_tail": "",
        }

    proc = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=900,
    )

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    parsed = None

    try:
        parsed = json.loads(stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit valid JSON: {exc}")

    script_ok = (
        proc.returncode == 0
        and isinstance(parsed, dict)
        and parsed.get("ok") is True
        and parsed.get("failures") == []
    )

    if not script_ok:
        failures.append(f"{rel_path} must return ok:true with failures:[]")

    return {
        "returncode": proc.returncode,
        "ok": bool(script_ok),
        "phase": parsed.get("phase") if isinstance(parsed, dict) else None,
        "json": parsed,
        "stdout_tail": stdout[-2000:],
        "stderr_tail": stderr[-2000:],
    }


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_guard_scripts(failures)
    guard_results = {
        rel_path: _run_json_guard(rel_path, failures)
        for rel_path in GUARD_SCRIPTS
    }

    summary = {
        "phase": "phase4a_post_phasec_total_guard",
        "checks": {
            "compile": compile_result,
            "guards": guard_results,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())