# path: ./tools/test_phase4a_direction_replay_material_slice_audit.py
# desc: Deep audit for Phase 4-A Direction replay artifact/report/review-material slice after close.

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

JSON_GUARDS = [
    "tools/test_phase4a_direction_read_only_boundary_guard.py",
    "tools/test_phase4a_direction_replay_artifact_entry_criteria_guard.py",
    "tools/test_phase4a_direction_replay_artifact_entry_close_guard.py",
    "tools/test_phase4a_direction_replay_calibration_review_material_entry_guard.py",
]

PLAIN_TESTS = [
    "btcts_next/src/btcts/replay/tests/test_replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/tests/test_prediction_replay_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export_prediction_artifacts.py",
]

COMPILE_TARGETS = [
    "btcts_next/src/btcts/replay/replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/replay_session.py",
    "btcts_next/src/btcts/replay/replay_export.py",
    "btcts_next/src/btcts/replay/replay_runner.py",
    "btcts_next/src/btcts/replay/replay_report.py",
    *PLAIN_TESTS,
    *JSON_GUARDS,
]

CURRENT_DOCS = [
    "tmp/docs/architecture/PHASE4A_DIRECTION_REPLAY_ARTIFACT_ENTRY_CLOSE_2026-05-23.md",
    "tmp/docs/architecture/PHASE4A_DIRECTION_REPLAY_CALIBRATION_REVIEW_MATERIAL_ENTRY_CRITERIA_2026-05-23.md",
    "tmp/docs/_INDEX.md",
    "tmp/gpt_room/08_STATUS.md",
    "tmp/gpt_room/09_FOCUS.json",
]

ALLOWED_REPLAY_MATERIAL_FILES = {
    "btcts_next/src/btcts/replay/replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/replay_session.py",
    "btcts_next/src/btcts/replay/replay_export.py",
    "btcts_next/src/btcts/replay/replay_runner.py",
    "btcts_next/src/btcts/replay/replay_report.py",
    "btcts_next/src/btcts/replay/tests/test_replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/tests/test_prediction_replay_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export_prediction_artifacts.py",
}

DIRECTION_SLICE_TOKENS = [
    "prediction_direction_snapshot",
    "prediction_direction_snapshots",
    "prediction_direction_summary",
    "direction_replay_calibration_review_material",
    "diagnostic_quality",
    "phase4a.direction_replay_calibration_review.v1",
]

FORBIDDEN_OWNER_TOKENS = [
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

FORBIDDEN_SCAN_ROOTS = [
    "btcts_next/src/btcts/replay",
    "btcts_next/src/btcts/apps/operator_ui",
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts",
]

ALLOWED_NEGATIVE_ASSERTION_TOKEN_FILES = {
    "btcts_next/src/btcts/replay/tests/test_replay_prediction_artifacts.py",
}

REQUIRED_REPORT_FRAGMENTS = [
    "def _build_prediction_direction_summary(",
    "def _build_direction_replay_calibration_review_material(",
    "prediction_direction_summary = _build_prediction_direction_summary(",
    '"direction_replay_calibration_review_material"',
    '"review_only": True',
    '"read_only_contract": True',
    '"not_runtime_wiring": True',
    '"not_ui_wiring": True',
    '"not_market_engine_wiring": True',
    '"review_priority"',
    '"review_flags"',
]

REQUIRED_TEST_FRAGMENTS = {
    "btcts_next/src/btcts/replay/tests/test_prediction_replay_export.py": [
        '"prediction_direction_summary"',
        '"direction_replay_calibration_review_material"',
        '"review_priority": "medium"',
        '"review_flags": ["caution_horizon_review"]',
        '"direction_replay_calibration_review_material"] is None',
    ],
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export_prediction_artifacts.py": [
        '"prediction_direction_summary"',
        '"direction_replay_calibration_review_material"',
        '"review_only"',
        '"not_runtime_wiring"',
        '"not_ui_wiring"',
    ],
}

REQUIRED_DOC_FRAGMENTS = {
    "tmp/docs/architecture/PHASE4A_DIRECTION_REPLAY_CALIBRATION_REVIEW_MATERIAL_ENTRY_CRITERIA_2026-05-23.md": [
        "Direction replay calibration/review material read model is closed",
        "phase4a.direction_replay_calibration_review.v1",
        "review_only = true",
        "not_runtime_wiring = true",
        "not_ui_wiring = true",
        "not_market_engine_wiring = true",
        "This close does not open UI, market_engine, runtime, Position, Execution, broker, or order behavior.",
    ],
    "tmp/docs/architecture/PHASE4A_DIRECTION_REPLAY_ARTIFACT_ENTRY_CLOSE_2026-05-23.md": [
        "Direction read-only artifact-only replay entry, summary/report review, and diagnostics quality are closed.",
        "Direction replay calibration/review material read model is closed",
        "direction replay calibration/review material tests: ok",
    ],
    "tmp/docs/_INDEX.md": [
        "Direction replay calibration/review material read model close",
        "Direction artifact diagnostics quality close",
        "runtime / UI / market_engine へはまだ接続しない",
        "Position / Execution は閉じたまま維持する",
    ],
    "tmp/gpt_room/08_STATUS.md": [
        "Direction replay calibration/review material read model close",
        "runtime / UI / market_engine / Position / Execution は開いていない",
        "Direction replay calibration/review material entry guard: ok true",
    ],
    "tmp/gpt_room/09_FOCUS.json": [
        "phase4a_direction_unconnected_scope_cleanup",
        "direction_replay_calibration_review_material_read_model_is_closed",
        "keep_direction_review_material_out_of_ui_market_engine_position_execution",
        "run_direction_replay_material_slice_audit_before_more_feature_work",
    ],
}


def _read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _compile_targets(failures: List[str]) -> Dict[str, Any]:
    passed: List[str] = []
    failed: List[Dict[str, str]] = []
    cache_root = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "direction_replay_material_slice_audit"
    cache_root.mkdir(parents=True, exist_ok=True)

    for rel_path in COMPILE_TARGETS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            failures.append(f"compile target missing: {rel_path}")
            failed.append({"path": rel_path, "error": "missing"})
            continue
        try:
            cfile = cache_root / (rel_path.replace("/", "__").replace("\\", "__") + ".pyc")
            py_compile.compile(str(path), cfile=str(cfile), doraise=True)
            passed.append(rel_path)
        except Exception as exc:
            failures.append(f"py_compile failed: {rel_path}: {exc}")
            failed.append({"path": rel_path, "error": str(exc)})
    return {"passed_count": len(passed), "failed": failed}


def _run_plain_tests(failures: List[str]) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    for rel_path in PLAIN_TESTS:
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / rel_path)],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            timeout=900,
        )
        ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
        if not ok:
            failures.append(f"plain test failed or did not emit ok: {rel_path}")
        results[rel_path] = {
            "returncode": proc.returncode,
            "ok": bool(ok),
            "stdout_tail": (proc.stdout or "")[-1200:],
            "stderr_tail": (proc.stderr or "")[-1200:],
        }
    return results


def _run_json_guards(failures: List[str]) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    for rel_path in JSON_GUARDS:
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / rel_path)],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            timeout=900,
        )
        parsed: Dict[str, Any] | None = None
        parse_error = None
        try:
            parsed = json.loads(proc.stdout)
        except Exception as exc:
            parse_error = str(exc)
            failures.append(f"json guard emitted invalid JSON: {rel_path}: {exc}")
        ok = proc.returncode == 0 and isinstance(parsed, dict) and parsed.get("ok") is True and parsed.get("failures") == []
        if not ok:
            failures.append(f"json guard failed: {rel_path}")
        results[rel_path] = {
            "returncode": proc.returncode,
            "ok": bool(ok),
            "phase": parsed.get("phase") if isinstance(parsed, dict) else None,
            "parse_error": parse_error,
            "stdout_tail": (proc.stdout or "")[-1600:],
            "stderr_tail": (proc.stderr or "")[-1600:],
        }
    return results


def _check_report_and_tests(failures: List[str]) -> Dict[str, Any]:
    missing: List[Dict[str, str]] = []
    report_text = _read_text("btcts_next/src/btcts/replay/replay_report.py")
    for fragment in REQUIRED_REPORT_FRAGMENTS:
        if fragment not in report_text:
            failures.append(f"replay_report material fragment missing: {fragment}")
            missing.append({"path": "btcts_next/src/btcts/replay/replay_report.py", "fragment": fragment})

    for rel_path, fragments in REQUIRED_TEST_FRAGMENTS.items():
        text = _read_text(rel_path)
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"test material assertion fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})
    return {"missing_count": len(missing), "missing": missing}


def _check_docs(failures: List[str]) -> Dict[str, Any]:
    missing: List[Dict[str, str]] = []
    for rel_path, fragments in REQUIRED_DOC_FRAGMENTS.items():
        text = _read_text(rel_path)
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"doc/status/focus fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    index_text = _read_text("tmp/docs/_INDEX.md")
    current_pos = index_text.find("### current formal spec")
    entry_pos = index_text.find("PHASE4A_DIRECTION_REPLAY_CALIBRATION_REVIEW_MATERIAL_ENTRY_CRITERIA_2026-05-23.md")
    close_pos = index_text.find("PHASE4A_DIRECTION_REPLAY_ARTIFACT_ENTRY_CLOSE_2026-05-23.md")
    ordering_ok = current_pos >= 0 and entry_pos >= 0 and close_pos >= 0 and current_pos < entry_pos < close_pos
    if not ordering_ok:
        failures.append("current formal spec ordering is wrong for Direction review material slice")

    return {"missing_count": len(missing), "missing": missing, "ordering_ok": bool(ordering_ok)}


def _check_wiring_boundaries(failures: List[str]) -> Dict[str, Any]:
    unapproved_direction_hits: List[Dict[str, str]] = []
    forbidden_owner_hits: List[Dict[str, str]] = []

    for root_rel in FORBIDDEN_SCAN_ROOTS:
        root = REPO_ROOT / root_rel
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            text = path.read_text(encoding="utf-8")
            for token in DIRECTION_SLICE_TOKENS:
                if token in text and rel not in ALLOWED_REPLAY_MATERIAL_FILES:
                    failures.append(f"Direction replay material token outside allowed replay slice: {rel}: {token}")
                    unapproved_direction_hits.append({"path": rel, "token": token})
            for token in FORBIDDEN_OWNER_TOKENS:
                if token not in text:
                    continue
                if rel in ALLOWED_NEGATIVE_ASSERTION_TOKEN_FILES:
                    negative_assertion = f'"{token}" not in direction_snapshot' in text
                    if negative_assertion:
                        continue
                failures.append(f"forbidden Position/Execution/order token in scanned scope: {rel}: {token}")
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
    plain_tests = _run_plain_tests(failures)
    json_guards = _run_json_guards(failures)
    report_and_tests = _check_report_and_tests(failures)
    docs = _check_docs(failures)
    wiring_boundaries = _check_wiring_boundaries(failures)

    summary = {
        "phase": "phase4a_direction_replay_material_slice_audit",
        "checks": {
            "compile": compile_result,
            "plain_tests": plain_tests,
            "json_guards": json_guards,
            "report_and_tests": report_and_tests,
            "docs": docs,
            "wiring_boundaries": wiring_boundaries,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
