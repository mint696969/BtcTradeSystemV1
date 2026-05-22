# path: ./tools/test_phase4a_ai_ui_prediction_tactic_consumer_boundary_audit.py
# desc: Phase 4-A AI/UI prediction-tactic consumer boundary audit.

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
    "btcts_next/src/btcts/apps/operator_ui/components/market_state_bridge.py",
    "btcts_next/src/btcts/apps/operator_ui/components/ai_operator_display_sources.py",
    "btcts_next/src/btcts/apps/operator_ui/components/ai_operator_tactic_context.py",
    "btcts_next/src/btcts/apps/operator_ui/components/ai_operator_tactic_presenter.py",
    "btcts_next/src/btcts/apps/operator_ui/components/strategy_state_panel.py",
]

PLAIN_TESTS = [
    "btcts_next/src/btcts/apps/operator_ui/tests/test_market_state_bridge_prediction_tactic.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_ai_operator_display_sources.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_ai_operator_tactic_presenter.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_strategy_state_tactic_compact_reading.py",
]

ALLOWED_TACTIC_BUILDER_BRIDGES = {
    "btcts_next/src/btcts/apps/operator_ui/components/market_state_bridge.py",
}

FORBIDDEN_UI_OWNER_FRAGMENTS = [
    "build_prediction_tactic_review_record",
    "build_prediction_tactic_operation_record",
    "PredictionTacticReviewBuildInput",
    "PredictionTacticOperationBuildInput",
    "TacticReviewRecord",
    "TacticOperationRecord",
    "from btcts.processing.l4_consumer_models.shared.prediction_tactic_",
    "btcts.processing.l4_consumer_models.shared.prediction_tactic_",
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


def _scan_ui_tactic_owner_leak(failures: List[str]) -> Dict[str, Any]:
    root = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components"
    hits: List[Dict[str, str]] = []

    for path in root.rglob("*.py"):
        rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        text = path.read_text(encoding="utf-8")

        if "build_prediction_tactic_" in text and rel not in ALLOWED_TACTIC_BUILDER_BRIDGES:
            hits.append({"path": rel, "fragment": "build_prediction_tactic_"})
            failures.append(
                "AI/UI components must not call prediction-tactic builders directly "
                f"outside the bridge: {rel}"
            )

        for fragment in FORBIDDEN_UI_OWNER_FRAGMENTS:
            if fragment in text:
                hits.append({"path": rel, "fragment": fragment})
                failures.append(
                    "AI/UI must remain consumer/surfacing layer, not tactic owner: "
                    f"{rel}: {fragment}"
                )

    return {
        "hit_count": len(hits),
        "hits": hits,
    }


def _check_bridge_builds_proposal_only(failures: List[str]) -> Dict[str, Any]:
    rel_path = "btcts_next/src/btcts/apps/operator_ui/components/market_state_bridge.py"
    path = REPO_ROOT / rel_path
    text = path.read_text(encoding="utf-8") if path.exists() else ""

    required_fragments = [
        "def load_prediction_tactic_proposal_payload(",
        "build_prediction_system_input(",
        "build_prediction_scenario_output(",
        "build_prediction_tactic_proposal_output(",
        '"bridge_type": "prediction_tactic_proposal_payload"',
        "return _materialize_payload(tactic_output)",
    ]
    forbidden_fragments = [
        "build_prediction_tactic_review_record(",
        "build_prediction_tactic_operation_record(",
    ]

    missing: List[str] = []
    forbidden: List[str] = []

    for fragment in required_fragments:
        if fragment not in text:
            missing.append(fragment)
            failures.append(f"prediction-tactic bridge missing required fragment: {fragment}")

    for fragment in forbidden_fragments:
        if fragment in text:
            forbidden.append(fragment)
            failures.append(f"prediction-tactic bridge must not own review/operation: {fragment}")

    return {
        "missing": missing,
        "forbidden": forbidden,
    }


def _check_ai_ui_consumers_use_bridge(failures: List[str]) -> Dict[str, Any]:
    checks = {
        "btcts_next/src/btcts/apps/operator_ui/components/ai_operator_display_sources.py": [
            "load_prediction_tactic_proposal_payload",
            '"tactic_context": load_prediction_tactic_proposal_payload()',
        ],
        "btcts_next/src/btcts/apps/operator_ui/components/strategy_state_panel.py": [
            "load_prediction_tactic_proposal_payload",
            "tactic_payload = load_prediction_tactic_proposal_payload()",
            "build_tactic_compact_reading_line(tactic_payload)",
        ],
        "btcts_next/src/btcts/apps/operator_ui/components/ai_operator_tactic_presenter.py": [
            "not an automatic decision",
            "review_only",
            "build_tactic_compact_reading_line",
        ],
    }

    missing: List[Dict[str, str]] = []

    for rel_path, fragments in checks.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        if not path.exists():
            failures.append(f"AI/UI consumer file missing: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__file_missing__"})
            continue

        for fragment in fragments:
            if fragment not in text:
                failures.append(f"AI/UI consumer boundary fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

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
    owner_leak_scan = _scan_ui_tactic_owner_leak(failures)
    bridge_shape = _check_bridge_builds_proposal_only(failures)
    consumer_bridge_usage = _check_ai_ui_consumers_use_bridge(failures)

    summary = {
        "phase": "phase4a_ai_ui_prediction_tactic_consumer_boundary_audit",
        "checks": {
            "compile": compile_result,
            "plain_tests": plain_test_results,
            "owner_leak_scan": owner_leak_scan,
            "bridge_shape": bridge_shape,
            "consumer_bridge_usage": consumer_bridge_usage,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())