# path: ./tools/test_phase4a_direction_unconnected_scope_cleanup_guard.py
# desc: Phase 4-A Direction unconnected scope cleanup guard.

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

DOC_PATH = "tmp/docs/architecture/PHASE4A_DIRECTION_UNCONNECTED_SCOPE_CLEANUP_2026-05-23.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATUS_PATH = "tmp/gpt_room/08_STATUS.md"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
AUDIT_PATH = "tools/test_phase4a_direction_replay_material_slice_audit.py"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"

COMPILE_TARGETS = [
    AUDIT_PATH,
    "tools/test_phase4a_direction_read_only_boundary_guard.py",
    "tools/test_phase4a_direction_replay_artifact_entry_criteria_guard.py",
    "tools/test_phase4a_direction_replay_artifact_entry_close_guard.py",
    "tools/test_phase4a_direction_replay_calibration_review_material_entry_guard.py",
    "btcts_next/src/btcts/replay/replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/replay_report.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_direction_builder.py",
]

ALLOWED_DIRECTION_TOKEN_FILES = {
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts/__init__.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/prediction_direction_builder.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/shared/__init__.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract_boundary.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_builder.py",
    "btcts_next/src/btcts/replay/replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/replay_session.py",
    "btcts_next/src/btcts/replay/replay_export.py",
    "btcts_next/src/btcts/replay/replay_runner.py",
    "btcts_next/src/btcts/replay/replay_report.py",
    "btcts_next/src/btcts/replay/tests/test_replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/tests/test_prediction_replay_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export_prediction_artifacts.py",
    "tools/test_phase4a_direction_position_execution_entry_criteria_guard.py",
    "tools/test_phase4a_direction_read_only_boundary_guard.py",
    "tools/test_phase4a_direction_replay_artifact_entry_criteria_guard.py",
    "tools/test_phase4a_direction_replay_artifact_entry_close_guard.py",
    "tools/test_phase4a_direction_replay_calibration_review_material_entry_guard.py",
    "tools/test_phase4a_direction_replay_material_slice_audit.py",
    "tools/test_phase4a_direction_unconnected_scope_cleanup_guard.py",
    "tools/test_phase4a_replay_market_engine_parity_total_guard.py",
}

DIRECTION_TOKENS = [
    "PredictionDirectionOutput",
    "PredictionDirectionBuildInput",
    "HorizonDirectionReading",
    "build_prediction_direction_input_from_scenario",
    "build_prediction_direction_output",
    "prediction_direction_output_to_snapshot",
    "prediction_direction_snapshot",
    "prediction_direction_summary",
    "direction_replay_calibration_review_material",
    "diagnostic_quality",
]

FORBIDDEN_RUNTIME_OWNER_TOKENS = [
    "PredictionPositionHint",
    "PredictionExecutionHint",
    "build_prediction_position",
    "build_prediction_execution",
    "position_size",
    "order_size",
    "broker_account",
    "place_order",
    "broker_order",
    "live_order_placement",
    "auto_trade",
]

SCAN_ROOTS = [
    "btcts_next/src/btcts/processing/l4_consumer_models",
    "btcts_next/src/btcts/replay",
    "btcts_next/src/btcts/apps/operator_ui",
    "btcts_next/src/btcts/market_engine",
]

ALLOWED_NEGATIVE_ASSERTION_TOKEN_FILES = {
    "btcts_next/src/btcts/replay/tests/test_replay_prediction_artifacts.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_contract_boundary.py",
    "btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_direction_builder.py",
}


def _read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _compile_targets(failures: List[str]) -> Dict[str, Any]:
    passed: List[str] = []
    failed: List[Dict[str, str]] = []
    cache_root = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "direction_unconnected_scope_cleanup"
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
            "Direction unconnected scope cleanup",
            "This cleanup is not implementation expansion",
            "live runtime Direction wiring",
            "operator UI Direction surfacing",
            "market_engine Direction integration",
            "Position hint contract",
            "Execution hint contract",
            "broker/order automation",
            "tools/test_phase4a_direction_unconnected_scope_cleanup_guard.py",
        ],
        INDEX_PATH: [
            "PHASE4A_DIRECTION_UNCONNECTED_SCOPE_CLEANUP_2026-05-23.md",
            "Direction unconnected scope cleanup",
            "Direction replay material slice audit primary connection close",
        ],
        STATUS_PATH: [
            "Phase 4-A Direction 系の未接続領域整理",
            "runtime / UI / market_engine へはまだ接続しない",
            "Position / Execution は閉じたまま維持する",
        ],
        FOCUS_PATH: [
            "phase4a_direction_unconnected_scope_cleanup",
            "next_phase4a_direction_unconnected_scope_cleanup_only",
            "keep_runtime_ui_market_engine_position_execution_closed_after_audit_primary_close",
        ],
    }
    missing: List[Dict[str, str]] = []
    for rel_path, fragments in required.items():
        text = _read_text(rel_path)
        if not text:
            failures.append(f"required doc missing or empty: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__missing_or_empty__"})
            continue
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"required doc/status/focus fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    index_text = _read_text(INDEX_PATH)
    current_pos = index_text.find("### current formal spec")
    cleanup_pos = index_text.find("PHASE4A_DIRECTION_UNCONNECTED_SCOPE_CLEANUP_2026-05-23.md")
    material_pos = index_text.find("PHASE4A_DIRECTION_REPLAY_CALIBRATION_REVIEW_MATERIAL_ENTRY_CRITERIA_2026-05-23.md")
    ordering_ok = current_pos >= 0 and cleanup_pos >= 0 and material_pos >= 0 and current_pos < cleanup_pos < material_pos
    if not ordering_ok:
        failures.append("Direction unconnected scope cleanup doc must be first current formal spec")

    return {"missing_count": len(missing), "missing": missing, "ordering_ok": bool(ordering_ok)}


def _check_primary_connection(failures: List[str]) -> Dict[str, Any]:
    text = _read_text(PRIMARY_GUARD_PATH)
    required = [
        "tools/test_phase4a_direction_replay_material_slice_audit.py",
        "direction_replay_material_slice_audit",
    ]
    missing: List[str] = []
    for fragment in required:
        if fragment not in text:
            failures.append(f"primary guard missing Direction material audit connection: {fragment}")
            missing.append(fragment)
    return {"missing_count": len(missing), "missing": missing}


def _check_direction_token_boundaries(failures: List[str]) -> Dict[str, Any]:
    unapproved_direction_hits: List[Dict[str, str]] = []
    forbidden_owner_hits: List[Dict[str, str]] = []

    for root_rel in SCAN_ROOTS:
        root = REPO_ROOT / root_rel
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            text = path.read_text(encoding="utf-8")
            for token in DIRECTION_TOKENS:
                if token in text and rel not in ALLOWED_DIRECTION_TOKEN_FILES:
                    failures.append(f"Direction token outside allowed unconnected scope inventory: {rel}: {token}")
                    unapproved_direction_hits.append({"path": rel, "token": token})
            for token in FORBIDDEN_RUNTIME_OWNER_TOKENS:
                if token not in text:
                    continue
                if rel in ALLOWED_NEGATIVE_ASSERTION_TOKEN_FILES:
                    # These files intentionally mention forbidden owner/order tokens
                    # as boundary assertions. The contract/source files are scanned
                    # separately, so test-only mentions must not be treated as leaks.
                    continue
                failures.append(f"forbidden runtime/owner/order token in active scope: {rel}: {token}")
                forbidden_owner_hits.append({"path": rel, "token": token})

    return {
        "unapproved_direction_hit_count": len(unapproved_direction_hits),
        "unapproved_direction_hits": unapproved_direction_hits,
        "forbidden_owner_hit_count": len(forbidden_owner_hits),
        "forbidden_owner_hits": forbidden_owner_hits,
    }


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    audit_guard = _run_json_guard(AUDIT_PATH, failures)
    docs = _check_docs(failures)
    primary_connection = _check_primary_connection(failures)
    token_boundaries = _check_direction_token_boundaries(failures)

    summary = {
        "phase": "phase4a_direction_unconnected_scope_cleanup_guard",
        "checks": {
            "compile": compile_result,
            "audit_guard": audit_guard,
            "docs": docs,
            "primary_connection": primary_connection,
            "token_boundaries": token_boundaries,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
