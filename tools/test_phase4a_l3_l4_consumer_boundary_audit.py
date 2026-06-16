# path: ./tools/test_phase4a_l3_l4_consumer_boundary_audit.py
# desc: Phase 4-A post Phase C L3/L4/UI consumer boundary audit.

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
    "btcts_next/src/btcts/apps/operator_ui/components/market_monitor_logic.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_market_monitor_logic.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/market_summary.py",
    "btcts_next/src/btcts/processing/l3_market_semantics/continuity/interpretation_engine.py",
]

FORBIDDEN_HINT_FRAGMENTS = [
    "integration_hint",
    "dedupe_hint",
    "completeness_hint",
    "origin_hint",
]

FORBIDDEN_L2_DIRECT_IMPORT_FRAGMENTS = [
    "btcts.ingestion.l2_canonical.orderbook.",
    "btcts.ingestion.l2_canonical.tradeflow.",
]


def _assert(cond: bool, message: str, failures: List[str]) -> None:
    if not cond:
        failures.append(message)


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


def _run_script(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"script missing: {rel_path}")
        return {
            "returncode": None,
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

    if proc.returncode != 0:
        failures.append(f"{rel_path} failed with returncode={proc.returncode}")

    return {
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-2000:],
        "stderr_tail": (proc.stderr or "")[-2000:],
    }


def _check_l3_l4_ui_do_not_consume_structural_hints(failures: List[str]) -> Dict[str, Any]:
    roots = [
        "btcts_next/src/btcts/processing",
        "btcts_next/src/btcts/apps",
    ]

    hits: List[Dict[str, str]] = []

    for root_rel in roots:
        root = REPO_ROOT / root_rel
        if not root.exists():
            continue

        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")

            for fragment in FORBIDDEN_HINT_FRAGMENTS:
                if fragment in text:
                    hits.append({"path": rel, "fragment": fragment})
                    failures.append(
                        f"L3/L4/UI must not consume collector structural hints as meaning: {rel}: {fragment}"
                    )

    return {
        "hit_count": len(hits),
        "hits": hits,
    }


def _check_l4_ui_do_not_import_l2_private_modules(failures: List[str]) -> Dict[str, Any]:
    roots = [
        "btcts_next/src/btcts/processing/l4_consumer_models",
        "btcts_next/src/btcts/apps",
    ]

    hits: List[Dict[str, str]] = []

    for root_rel in roots:
        root = REPO_ROOT / root_rel
        if not root.exists():
            continue

        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")

            for fragment in FORBIDDEN_L2_DIRECT_IMPORT_FRAGMENTS:
                if fragment in text:
                    hits.append({"path": rel, "fragment": fragment})
                    failures.append(
                        f"L4/UI must not import L2 private modules directly: {rel}: {fragment}"
                    )

    return {
        "hit_count": len(hits),
        "hits": hits,
    }


def _check_ui_market_monitor_summary_precedence(failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/market_monitor_logic.py"
    _assert(path.exists(), "market_monitor_logic.py must exist", failures)

    text = path.read_text(encoding="utf-8") if path.exists() else ""

    required_fragments = [
        "def _pick_status_value(",
        "(summary.get(key) if summary else None)",
        "or (state.get(key) if state else None)",
        "or board.get(key)",
    ]

    missing: List[str] = []
    for fragment in required_fragments:
        if fragment not in text:
            missing.append(fragment)
            failures.append(f"market monitor must prefer summary/state over board fallback: {fragment}")

    board_first_fragments = [
        'board.get("trust_state")',
        'board.get("continuity_state")',
        'board.get("interpretation_bucket")',
        'board.get("interpretation_reason")',
    ]
    for fragment in board_first_fragments:
        if fragment in text:
            failures.append(f"market monitor must not read board status directly before summary/state: {fragment}")
            missing.append(f"forbidden:{fragment}")

    return {
        "missing_or_forbidden_count": len(missing),
        "details": missing,
    }


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    market_monitor_logic_test = _run_script(
        "btcts_next/src/btcts/apps/operator_ui/tests/test_market_monitor_logic.py",
        failures,
    )
    structural_hint_usage = _check_l3_l4_ui_do_not_consume_structural_hints(failures)
    l2_private_imports = _check_l4_ui_do_not_import_l2_private_modules(failures)
    ui_summary_precedence = _check_ui_market_monitor_summary_precedence(failures)

    summary = {
        "phase": "phase4a_post_phasec_l3_l4_consumer_boundary_audit",
        "checks": {
            "compile": compile_result,
            "market_monitor_logic_test": market_monitor_logic_test,
            "structural_hint_usage": structural_hint_usage,
            "l2_private_imports": l2_private_imports,
            "ui_summary_precedence": ui_summary_precedence,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())