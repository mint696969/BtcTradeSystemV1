# path: ./tools/test_phase4a_phase_e_warroom_operational_reading_guard.py
# desc: Phase 4-A Phase E WarRoom operational reading surfacing guard.

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

COMPILE_TARGETS = [
    "btcts_next/src/btcts/apps/operator_ui/components/warroom_header.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_header_reading_caption.py",
]

PLAIN_TESTS = [
    "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_header_reading_caption.py",
]


def _compile_targets(failures: List[str]) -> Dict[str, Any]:
    passed: List[str] = []
    failed: List[Dict[str, str]] = []

    for rel_path in COMPILE_TARGETS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            failed.append({"path": rel_path, "error": "missing"})
            failures.append(f"compile target missing: {rel_path}")
            continue

        try:
            py_compile.compile(str(path), doraise=True)
            passed.append(rel_path)
        except Exception as exc:
            failed.append({"path": rel_path, "error": str(exc)})
            failures.append(f"py_compile failed: {rel_path}: {exc}")

    return {
        "passed_count": len(passed),
        "failed": failed,
    }


def _run_plain_test(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"test missing: {rel_path}")
        return {
            "returncode": None,
            "ok": False,
            "stdout_tail": "",
            "stderr_tail": "",
        }

    proc = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=120,
    )

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    ok = proc.returncode == 0 and stdout.strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain 'ok'")

    return {
        "returncode": proc.returncode,
        "ok": bool(ok),
        "stdout_tail": stdout[-2000:],
        "stderr_tail": stderr[-2000:],
    }


def _check_warroom_operational_reading_shape(failures: List[str]) -> Dict[str, Any]:
    rel_path = "btcts_next/src/btcts/apps/operator_ui/components/warroom_header.py"
    path = REPO_ROOT / rel_path
    text = path.read_text(encoding="utf-8") if path.exists() else ""

    required_fragments = [
        "load_market_summary_status_payload",
        "active_event_compact_reading_line",
        "def build_warroom_operational_reading_caption(",
        "operational_reading=",
        "active_event=",
        "review_mode=operator_review_only",
        "execution=not_instruction",
        "summary_payload = load_market_summary_status_payload()",
        "build_warroom_operational_reading_caption(",
    ]
    forbidden_fragments = [
        "execution=instruction",
        "review_mode=auto_execution",
        "final_decision",
        "automatic decision",
    ]

    missing: List[str] = []
    forbidden: List[str] = []

    for fragment in required_fragments:
        if fragment not in text:
            missing.append(fragment)
            failures.append(f"WarRoom operational reading fragment missing: {fragment}")

    for fragment in forbidden_fragments:
        if fragment in text:
            forbidden.append(fragment)
            failures.append(f"WarRoom operational reading must remain review-only: {fragment}")

    return {
        "missing": missing,
        "forbidden": forbidden,
    }


def _check_test_contract(failures: List[str]) -> Dict[str, Any]:
    rel_path = "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_header_reading_caption.py"
    path = REPO_ROOT / rel_path
    text = path.read_text(encoding="utf-8") if path.exists() else ""

    required_fragments = [
        "build_warroom_operational_reading_caption",
        "orderbook_active_event_compact_rows",
        "raw_contract_should_not_be_used",
        "operational_reading=trend_up",
        "active_event=near_wall_continued",
        "review_mode=operator_review_only",
        "execution=not_instruction",
    ]

    missing: List[str] = []

    for fragment in required_fragments:
        if fragment not in text:
            missing.append(fragment)
            failures.append(f"WarRoom operational reading test fragment missing: {fragment}")

    return {
        "missing_count": len(missing),
        "missing": missing,
    }


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    plain_test_results = {
        rel_path: _run_plain_test(rel_path, failures)
        for rel_path in PLAIN_TESTS
    }
    operational_shape = _check_warroom_operational_reading_shape(failures)
    test_contract = _check_test_contract(failures)

    summary = {
        "phase": "phase4a_phase_e_warroom_operational_reading_guard",
        "checks": {
            "compile": compile_result,
            "plain_tests": plain_test_results,
            "operational_shape": operational_shape,
            "test_contract": test_contract,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())