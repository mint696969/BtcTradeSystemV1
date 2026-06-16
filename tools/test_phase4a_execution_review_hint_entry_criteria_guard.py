# path: ./tools/test_phase4a_execution_review_hint_entry_criteria_guard.py
# desc: Phase 4-A Execution review hint entry criteria guard.

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

DOC_PATH = "tmp/docs/architecture/PHASE4A_EXECUTION_REVIEW_HINT_ENTRY_CRITERIA_2026-05-23.md"
POSITION_DOC_PATH = "tmp/docs/architecture/PHASE4A_POSITION_REVIEW_HINT_ENTRY_CRITERIA_2026-05-23.md"
DPE_DOC_PATH = "tmp/docs/architecture/PHASE4A_DIRECTION_POSITION_EXECUTION_ENTRY_CRITERIA_2026-05-17.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATUS_PATH = "tmp/gpt_room/08_STATUS.md"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
POSITION_GUARD_PATH = "tools/test_phase4a_position_review_hint_entry_criteria_guard.py"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"

COMPILE_TARGETS = [
    POSITION_GUARD_PATH,
    "tools/test_phase4a_direction_position_execution_entry_criteria_guard.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_position_review_hint_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_position_review_hint_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_execution_review_hint_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_execution_review_hint_contract.py",
]

SCAN_ROOTS = [
    "btcts_next/src/btcts/processing/l4_consumer_models",
    "btcts_next/src/btcts/replay",
    "btcts_next/src/btcts/apps/operator_ui",
    "btcts_next/src/btcts/market_engine",
]

PREMATURE_EXECUTION_TOKENS = [
    "PredictionExecutionHint",
    "build_prediction_execution",
    "order_size",
    "order_price",
    "broker_account",
    "place_order",
    "broker_order",
    "live_order_placement",
    "auto_trade",
    "account_mutation",
    "broker_adapter_operation",
]

ALLOWED_NEGATIVE_ASSERTION_FILES = {
    "btcts_next/src/btcts/replay/tests/test_replay_prediction_artifacts.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract_boundary.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_builder.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_position_review_hint_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_execution_review_hint_contract.py",
}

ALLOWED_EXECUTION_REVIEW_HINT_SKELETON_FILES = {
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_execution_review_hint_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/__init__.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_execution_review_hint_contract.py",
}


def _read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _compile_targets(failures: List[str]) -> Dict[str, Any]:
    passed: List[str] = []
    failed: List[Dict[str, str]] = []
    cache_root = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "execution_review_hint_entry"
    cache_root.mkdir(parents=True, exist_ok=True)

    for rel_path in COMPILE_TARGETS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            failed.append({"path": rel_path, "error": "missing"})
            failures.append(f"compile target missing: {rel_path}")
            continue
        try:
            cfile = cache_root / (rel_path.replace("/", "__").replace("\\", "__") + ".pyc")
            py_compile.compile(str(path), cfile=str(cfile), doraise=True)
            passed.append(rel_path)
        except Exception as exc:
            failed.append({"path": rel_path, "error": str(exc)})
            failures.append(f"py_compile failed: {rel_path}: {exc}")

    return {"passed_count": len(passed), "failed": failed}


def _run_json_guard(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / rel_path)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=900,
    )
    parsed: Dict[str, Any] | None = None
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"json guard did not emit valid JSON: {rel_path}: {exc}")

    ok = proc.returncode == 0 and isinstance(parsed, dict) and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"json guard must return ok true and failures []: {rel_path}")
    return {
        "returncode": proc.returncode,
        "ok": bool(ok),
        "phase": parsed.get("phase") if isinstance(parsed, dict) else None,
        "stdout_tail": (proc.stdout or "")[-1600:],
        "stderr_tail": (proc.stderr or "")[-1600:],
    }


def _check_docs(failures: List[str]) -> Dict[str, Any]:
    required = {
        DOC_PATH: [
            "Execution review hint entry criteria",
            "Execution review hint is not live order placement.",
            "Execution review hint is not broker adapter operation.",
            "review-only timing / urgency / feasibility hint",
            "PredictionExecutionReviewHint contract skeleton only",
            "tools/test_phase4a_execution_review_hint_entry_criteria_guard.py",
        ],
        POSITION_DOC_PATH: [
            "Position review hint contract skeleton post-commit checkpoint is complete",
            "commit = fae01765 Add guarded Position review hint contract skeleton",
            "Position remains review-only management contract.",
        ],
        DPE_DOC_PATH: [
            "Execution hint is timing / urgency / feasibility reading only, not broker/order automation.",
            "Execution layer",
            "live order placement",
        ],
        INDEX_PATH: [
            "PHASE4A_EXECUTION_REVIEW_HINT_ENTRY_CRITERIA_2026-05-23.md",
            "Execution review hint entry criteria",
            "Position review hint contract skeleton close / commit checkpoint complete",
        ],
        STATUS_PATH: [
            "Execution review hint entry criteria",
            "runtime / UI / market_engine へはまだ接続しない",
            "broker/order automation は開かない",
        ],
        FOCUS_PATH: [
            "phase4a_execution_review_hint_entry_criteria",
            "execution_review_hint_entry_criteria_only",
            "keep_execution_review_hint_not_live_order_placement",
            "keep_broker_order_closed_for_execution_entry",
        ],
    }
    missing: List[Dict[str, str]] = []
    for rel_path, fragments in required.items():
        text = _read_text(rel_path)
        if not text:
            failures.append(f"required doc/status/focus missing or empty: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__missing_or_empty__"})
            continue
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"required doc/status/focus fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    index_text = _read_text(INDEX_PATH)
    current_pos = index_text.find("### current formal spec")
    execution_pos = index_text.find("PHASE4A_EXECUTION_REVIEW_HINT_ENTRY_CRITERIA_2026-05-23.md")
    position_pos = index_text.find("PHASE4A_POSITION_REVIEW_HINT_ENTRY_CRITERIA_2026-05-23.md")
    ordering_ok = current_pos >= 0 and execution_pos >= 0 and position_pos >= 0 and current_pos < execution_pos < position_pos
    if not ordering_ok:
        failures.append("Execution review hint entry criteria doc must be first current formal spec")

    return {"missing_count": len(missing), "missing": missing, "ordering_ok": bool(ordering_ok)}


def _check_execution_review_hint_skeleton(failures: List[str]) -> Dict[str, Any]:
    required_by_file = {
        "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_execution_review_hint_contract.py": [
            "class PredictionExecutionReviewHint",
            "review-only timing / urgency / feasibility material",
            "not live order placement",
            "not broker adapter operation",
            "not account mutation",
            "not final autonomous trading decision",
            "scenario_ref",
            "direction_ref",
            "position_ref",
            "execution_context_ref",
            "timing_hint",
            "urgency_hint",
            "passive_aggressive_hint",
            "feasibility_hint",
            "review_needed",
            "evidence_trace_refs",
        ],
        "btcts_next/src/btcts/processing/l4_consumer_models/contracts/__init__.py": [
            "PredictionExecutionReviewHint",
            "__all__",
        ],
        "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_execution_review_hint_contract.py": [
            "test_prediction_execution_review_hint_contract_minimal_shape",
            "test_prediction_execution_review_hint_contract_is_review_only_read_model",
            "test_prediction_execution_review_hint_contract_does_not_own_broker_or_order_fields",
        ],
    }
    forbidden_by_contract = [
        "order_size",
        "order_price",
        "leverage",
        "broker_account",
        "place_order",
        "broker_order",
        "live_order_placement",
        "auto_trade",
        "account_mutation",
        "broker_adapter_operation",
    ]
    missing: List[Dict[str, str]] = []
    forbidden: List[Dict[str, str]] = []

    for rel_path, fragments in required_by_file.items():
        text = _read_text(rel_path)
        if not text:
            failures.append(f"execution review hint skeleton file missing or empty: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__missing_or_empty__"})
            continue
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"execution review hint skeleton fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    contract_text = _read_text("btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_execution_review_hint_contract.py")
    for fragment in forbidden_by_contract:
        if fragment in contract_text:
            failures.append(f"execution review hint contract must not own broker/order field: {fragment}")
            forbidden.append({"path": "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_execution_review_hint_contract.py", "fragment": fragment})

    return {
        "missing_count": len(missing),
        "missing": missing,
        "forbidden_count": len(forbidden),
        "forbidden": forbidden,
    }


def _scan_premature_tokens(failures: List[str]) -> Dict[str, Any]:
    hits: List[Dict[str, str]] = []
    for root_rel in SCAN_ROOTS:
        root = REPO_ROOT / root_rel
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            text = path.read_text(encoding="utf-8")
            for token in PREMATURE_EXECUTION_TOKENS:
                if token not in text:
                    continue
                if rel in ALLOWED_NEGATIVE_ASSERTION_FILES:
                    continue
                if rel in ALLOWED_EXECUTION_REVIEW_HINT_SKELETON_FILES and token == "PredictionExecutionReviewHint":
                    continue
                failures.append(f"premature Execution/broker-order token: {rel}: {token}")
                hits.append({"path": rel, "token": token})
    return {"hit_count": len(hits), "hits": hits}


def _check_primary_guard_current(failures: List[str]) -> Dict[str, Any]:
    text = _read_text(PRIMARY_GUARD_PATH)
    required = [
        "tools/test_phase4a_position_review_hint_entry_criteria_guard.py",
        "position_review_hint_entry_criteria_guard",
    ]
    missing: List[str] = []
    for fragment in required:
        if fragment not in text:
            failures.append(f"primary guard missing Position entry guard connection: {fragment}")
            missing.append(fragment)
    return {"missing_count": len(missing), "missing": missing}


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    position_guard = _run_json_guard(POSITION_GUARD_PATH, failures)
    docs = _check_docs(failures)
    execution_review_hint_skeleton = _check_execution_review_hint_skeleton(failures)
    premature_tokens = _scan_premature_tokens(failures)
    primary_guard_current = _check_primary_guard_current(failures)

    summary = {
        "phase": "phase4a_execution_review_hint_entry_criteria_guard",
        "checks": {
            "compile": compile_result,
            "position_guard": position_guard,
            "docs": docs,
            "execution_review_hint_skeleton": execution_review_hint_skeleton,
            "premature_tokens": premature_tokens,
            "primary_guard_current": primary_guard_current,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
