# path: ./tools/test_phase4a_position_review_hint_entry_criteria_guard.py
# desc: Phase 4-A Position review hint entry criteria guard.

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

DOC_PATH = "tmp/docs/architecture/PHASE4A_POSITION_REVIEW_HINT_ENTRY_CRITERIA_2026-05-23.md"
HANDOFF_DOC_PATH = "tmp/docs/architecture/PHASE4A_DIRECTION_SLICE_HANDOFF_SUMMARY_2026-05-23.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATUS_PATH = "tmp/gpt_room/08_STATUS.md"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
DIRECTION_AUDIT_PATH = "tools/test_phase4a_direction_replay_material_slice_audit.py"
DIRECTION_CLEANUP_PATH = "tools/test_phase4a_direction_unconnected_scope_cleanup_guard.py"

COMPILE_TARGETS = [
    DIRECTION_AUDIT_PATH,
    DIRECTION_CLEANUP_PATH,
    "tools/test_phase4a_direction_position_execution_entry_criteria_guard.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_direction_builder.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_position_review_hint_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_position_review_hint_contract.py",
]

SCAN_ROOTS = [
    "btcts_next/src/btcts/processing/l4_consumer_models",
    "btcts_next/src/btcts/replay",
    "btcts_next/src/btcts/apps/operator_ui",
    "btcts_next/src/btcts/market_engine",
]

PREMATURE_POSITION_EXECUTION_TOKENS = [
    "PredictionPositionHint",
    "PredictionExecutionHint",
    "build_prediction_position",
    "build_prediction_execution",
    "position_size",
    "order_size",
    "order_price",
    "leverage",
    "broker_account",
    "place_order",
    "broker_order",
    "live_order_placement",
    "auto_trade",
]

ALLOWED_NEGATIVE_ASSERTION_FILES = {
    "btcts_next/src/btcts/replay/tests/test_replay_prediction_artifacts.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract_boundary.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_builder.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_position_review_hint_contract.py",
}

ALLOWED_POSITION_REVIEW_HINT_SKELETON_FILES = {
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_position_review_hint_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/__init__.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_position_review_hint_contract.py",
}


def _read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _compile_targets(failures: List[str]) -> Dict[str, Any]:
    passed: List[str] = []
    failed: List[Dict[str, str]] = []
    cache_root = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "position_review_hint_entry"
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
            "Position review hint entry criteria",
            "Position review hint is not live position mutation.",
            "Position review hint is not broker/order automation.",
            "review-only management hint",
            "PredictionPositionReviewHint contract skeleton only",
            "tools/test_phase4a_position_review_hint_entry_criteria_guard.py",
        ],
        HANDOFF_DOC_PATH: [
            "Post-commit checkpoint close",
            "commit = d7779763 Add guarded Direction replay material slice",
            "Direction slice does not open runtime/UI/market_engine/Position/Execution.",
        ],
        INDEX_PATH: [
            "PHASE4A_POSITION_REVIEW_HINT_ENTRY_CRITERIA_2026-05-23.md",
            "Position review hint entry criteria",
            "Direction slice handoff summary close / commit checkpoint complete",
        ],
        STATUS_PATH: [
            "Position review hint entry criteria",
            "runtime / UI / market_engine へはまだ接続しない",
            "Execution は閉じたまま維持する",
        ],
        FOCUS_PATH: [
            "phase4a_position_review_hint_entry_criteria",
            "position_review_hint_entry_criteria_only",
            "keep_position_review_hint_not_live_mutation",
            "keep_execution_broker_order_closed_for_position_entry",
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
    position_pos = index_text.find("PHASE4A_POSITION_REVIEW_HINT_ENTRY_CRITERIA_2026-05-23.md")
    handoff_pos = index_text.find("PHASE4A_DIRECTION_SLICE_HANDOFF_SUMMARY_2026-05-23.md")
    ordering_ok = current_pos >= 0 and position_pos >= 0 and handoff_pos >= 0 and current_pos < position_pos < handoff_pos
    if not ordering_ok:
        failures.append("Position review hint entry criteria doc must be first current formal spec")

    return {"missing_count": len(missing), "missing": missing, "ordering_ok": bool(ordering_ok)}


def _check_position_review_hint_skeleton(failures: List[str]) -> Dict[str, Any]:
    required_by_file = {
        "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_position_review_hint_contract.py": [
            "class PredictionPositionReviewHint",
            "review-only management material",
            "not live position mutation",
            "not execution instruction",
            "not broker/order automation",
            "not final trading decision owner",
            "scenario_ref",
            "direction_ref",
            "position_context_ref",
            "management_hint",
            "exposure_risk_hint",
            "review_needed",
            "evidence_trace_refs",
        ],
        "btcts_next/src/btcts/processing/l4_consumer_models/contracts/__init__.py": [
            "PredictionPositionReviewHint",
            "__all__",
        ],
        "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_position_review_hint_contract.py": [
            "test_prediction_position_review_hint_contract_minimal_shape",
            "test_prediction_position_review_hint_contract_is_review_only_read_model",
            "test_prediction_position_review_hint_contract_does_not_own_execution_or_order_fields",
        ],
    }
    forbidden_by_contract = [
        "position_size",
        "order_size",
        "order_price",
        "leverage",
        "broker_account",
        "place_order",
        "broker_order",
        "live_order_placement",
        "auto_trade",
    ]
    missing: List[Dict[str, str]] = []
    forbidden: List[Dict[str, str]] = []

    for rel_path, fragments in required_by_file.items():
        text = _read_text(rel_path)
        if not text:
            failures.append(f"position review hint skeleton file missing or empty: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__missing_or_empty__"})
            continue
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"position review hint skeleton fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    contract_text = _read_text("btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_position_review_hint_contract.py")
    for fragment in forbidden_by_contract:
        if fragment in contract_text:
            failures.append(f"position review hint contract must not own execution/order field: {fragment}")
            forbidden.append({"path": "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_position_review_hint_contract.py", "fragment": fragment})

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
            for token in PREMATURE_POSITION_EXECUTION_TOKENS:
                if token not in text:
                    continue
                if rel in ALLOWED_NEGATIVE_ASSERTION_FILES:
                    continue
                if rel in ALLOWED_POSITION_REVIEW_HINT_SKELETON_FILES and token == "PredictionPositionReviewHint":
                    continue
                failures.append(f"premature Position/Execution/broker-order token: {rel}: {token}")
                hits.append({"path": rel, "token": token})
    return {"hit_count": len(hits), "hits": hits}


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    direction_audit = _run_json_guard(DIRECTION_AUDIT_PATH, failures)
    direction_cleanup = _run_json_guard(DIRECTION_CLEANUP_PATH, failures)
    docs = _check_docs(failures)
    position_review_hint_skeleton = _check_position_review_hint_skeleton(failures)
    premature_tokens = _scan_premature_tokens(failures)

    summary = {
        "phase": "phase4a_position_review_hint_entry_criteria_guard",
        "checks": {
            "compile": compile_result,
            "direction_audit": direction_audit,
            "direction_cleanup": direction_cleanup,
            "docs": docs,
            "position_review_hint_skeleton": position_review_hint_skeleton,
            "premature_tokens": premature_tokens,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
