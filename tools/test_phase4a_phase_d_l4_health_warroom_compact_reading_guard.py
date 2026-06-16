# path: ./tools/test_phase4a_phase_d_l4_health_warroom_compact_reading_guard.py
# desc: Phase 4-A Phase D L4 Health / WarRoom compact reading guard.

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
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/active_event_reading.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/market_summary.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/health_digest.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/market_summary_adapter.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/health_digest_adapter.py",
    "btcts_next/src/btcts/apps/operator_ui/components/market_summary_presenter.py",
    "btcts_next/src/btcts/apps/operator_ui/components/health_top_panels.py",
]

PLAIN_TESTS = [
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_active_event_reading.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_market_summary_active_event_compact_reading.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_market_state_bridge.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_health_digest_adapter.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_health_top_panels_digest_caption.py",
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
        timeout=180,
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


def _check_required_fragments(failures: List[str]) -> Dict[str, Any]:
    checks = {
        "btcts_next/src/btcts/processing/l4_consumer_models/shared/active_event_reading.py": [
            "ACTIVE_EVENT_STABLE_KEYS",
            "build_active_event_compact_rows",
            "event_name",
            "meaning_version",
            "half_life_sec",
        ],
        "btcts_next/src/btcts/processing/l4_consumer_models/shared/market_summary.py": [
            "orderbook_active_event_compact_rows",
            "build_active_event_compact_rows(",
        ],
        "btcts_next/src/btcts/processing/l4_consumer_models/shared/health_digest.py": [
            "active_event_compact_rows",
            "build_active_event_compact_rows(",
        ],
        "btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/market_summary_adapter.py": [
            "orderbook_active_event_compact_rows_kind",
            "active_event_stable_subset_rows",
            "orderbook_active_event_compact_rows",
        ],
        "btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/health_digest_adapter.py": [
            "active_event_compact_rows_kind",
            "active_event_stable_subset_rows",
            "orderbook_active_event_compact_rows",
        ],
        "btcts_next/src/btcts/apps/operator_ui/components/market_summary_presenter.py": [
            "orderbook_active_event_compact_rows",
            "orderbook_active_event_contracts",
            "active_event_compact_reading_line",
        ],
        "btcts_next/src/btcts/apps/operator_ui/components/health_top_panels.py": [
            "active_event_compact_rows_count",
            "active_event_compact_rows=",
            "active_event_rows=",
        ],
    }

    missing: List[Dict[str, str]] = []

    for rel_path, fragments in checks.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        if not path.exists():
            failures.append(f"fragment check file missing: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__file_missing__"})
            continue

        for fragment in fragments:
            if fragment not in text:
                failures.append(f"required fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    return {
        "missing_count": len(missing),
        "missing": missing,
    }


def _check_presenter_prefers_compact_rows(failures: List[str]) -> Dict[str, Any]:
    rel_path = "btcts_next/src/btcts/apps/operator_ui/components/market_summary_presenter.py"
    path = REPO_ROOT / rel_path
    text = path.read_text(encoding="utf-8") if path.exists() else ""

    compact_pos = text.find('summary_payload.get("orderbook_active_event_compact_rows")')
    contracts_pos = text.find('summary_payload.get("orderbook_active_event_contracts")')

    ok = compact_pos >= 0 and contracts_pos >= 0 and compact_pos < contracts_pos
    if not ok:
        failures.append(
            "market_summary_presenter must prefer compact rows before raw contract rows"
        )

    return {
        "compact_pos": compact_pos,
        "contracts_pos": contracts_pos,
        "ok": bool(ok),
    }


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    plain_test_results = {
        rel_path: _run_plain_test(rel_path, failures)
        for rel_path in PLAIN_TESTS
    }
    required_fragments = _check_required_fragments(failures)
    presenter_precedence = _check_presenter_prefers_compact_rows(failures)

    summary = {
        "phase": "phase4a_phase_d_l4_health_warroom_compact_reading_guard",
        "checks": {
            "compile": compile_result,
            "plain_tests": plain_test_results,
            "required_fragments": required_fragments,
            "presenter_precedence": presenter_precedence,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())