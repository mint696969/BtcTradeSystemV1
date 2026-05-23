# path: ./tools/test_phase4a_direction_replay_artifact_entry_close_guard.py
# desc: Phase 4-A Direction read-only artifact-only replay entry close guard.

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

CLOSE_DOC = "tmp/docs/architecture/PHASE4A_DIRECTION_REPLAY_ARTIFACT_ENTRY_CLOSE_2026-05-23.md"
CRITERIA_DOC = "tmp/docs/architecture/PHASE4A_DIRECTION_REPLAY_ARTIFACT_ENTRY_CRITERIA_2026-05-23.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATUS_PATH = "tmp/gpt_room/08_STATUS.md"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"
CRITERIA_GUARD_PATH = "tools/test_phase4a_direction_replay_artifact_entry_criteria_guard.py"
READ_ONLY_GUARD_PATH = "tools/test_phase4a_direction_read_only_boundary_guard.py"

COMPILE_TARGETS = [
    "btcts_next/src/btcts/replay/replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/replay_session.py",
    "btcts_next/src/btcts/replay/replay_export.py",
    "btcts_next/src/btcts/replay/replay_runner.py",
    "btcts_next/src/btcts/replay/replay_report.py",
    "btcts_next/src/btcts/replay/tests/test_replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/tests/test_prediction_replay_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export_prediction_artifacts.py",
    CRITERIA_GUARD_PATH,
    READ_ONLY_GUARD_PATH,
]

PLAIN_TESTS = [
    "btcts_next/src/btcts/replay/tests/test_replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/tests/test_prediction_replay_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export_prediction_artifacts.py",
]

ARTIFACT_FILES = [
    "btcts_next/src/btcts/replay/replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/replay_session.py",
    "btcts_next/src/btcts/replay/replay_export.py",
    "btcts_next/src/btcts/replay/replay_runner.py",
    "btcts_next/src/btcts/replay/replay_report.py",
]

ALLOWED_DIRECTION_REFERENCES = {
    "btcts_next/src/btcts/replay/replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/replay_runner.py",
    "btcts_next/src/btcts/replay/replay_session.py",
    "btcts_next/src/btcts/replay/replay_export.py",
    "btcts_next/src/btcts/replay/replay_report.py",
    "btcts_next/src/btcts/replay/tests/test_replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/tests/test_prediction_replay_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export.py",
}

DIRECTION_TOKENS = [
    "PredictionDirectionOutput",
    "PredictionDirectionBuildInput",
    "build_prediction_direction_input_from_scenario",
    "build_prediction_direction_output",
    "prediction_direction_output_to_snapshot",
    "prediction_direction_builder",
    "prediction_direction_contract",
    "prediction_direction_snapshot",
    "prediction_direction_snapshots",
]

FORBIDDEN_TOKENS = [
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


def _read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _compile_targets(failures: List[str]) -> Dict[str, Any]:
    passed: List[str] = []
    failed: List[Dict[str, str]] = []
    cache_root = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "direction_replay_artifact_entry_close"
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
            failures.append(f"plain test must emit ok: {rel_path}")
        results[rel_path] = {
            "returncode": proc.returncode,
            "ok": bool(ok),
            "stdout_tail": (proc.stdout or "")[-1200:],
            "stderr_tail": (proc.stderr or "")[-1200:],
        }
    return results


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
        "json": parsed,
        "stdout_tail": (proc.stdout or "")[-1200:],
        "stderr_tail": (proc.stderr or "")[-1200:],
    }


def _check_docs(failures: List[str]) -> Dict[str, Any]:
    required = {
        CLOSE_DOC: [
            "Direction read-only artifact-only replay entry is closed.",
            "prediction_direction_summary",
            "prediction_direction_snapshot",
            "diagnostic_quality",
            "latest_diagnostic_quality_ok",
            "direction artifact diagnostics quality tests: ok",
            "source_kind = replay_artifact_only",
            "not_runtime_wiring = true",
            "not_ui_wiring = true",
            "Position / Execution runtime behavior",
            "tools/test_phase4a_direction_replay_artifact_entry_close_guard.py",
        ],
        CRITERIA_DOC: [
            "Direction read-only artifact-only replay entry implementation may be opened",
            "This does not open UI, live runtime, market_engine, Position, or Execution behavior.",
        ],
        INDEX_PATH: [
            "PHASE4A_DIRECTION_REPLAY_ARTIFACT_ENTRY_CLOSE_2026-05-23.md",
            "Direction read-only artifact-only replay entry close",
        ],
        STATUS_PATH: [
            "Direction read-only artifact-only replay entry は close",
            "allowed_artifact_hit_count = 3",
            "runtime / UI / market_engine integration はまだ開かない",
            "Position / Execution は閉じたまま維持する",
            "Direction artifact diagnostics quality: ok true",
        ],
        FOCUS_PATH: [
            "phase4a_direction_replay_artifact_entry_close",
            "direction_read_only_artifact_only_replay_entry_is_closed",
            "next_direction_artifact_summary_or_review_quality_only",
            "direction_artifact_diagnostics_quality_is_closed",
        ],
    }
    missing: List[Dict[str, str]] = []
    for rel_path, fragments in required.items():
        text = _read_text(rel_path)
        if not text:
            failures.append(f"required doc missing or empty: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__file_missing_or_empty__"})
            continue
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"required doc fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    index_text = _read_text(INDEX_PATH)
    current_pos = index_text.find("### current formal spec")
    close_pos = index_text.find("PHASE4A_DIRECTION_REPLAY_ARTIFACT_ENTRY_CLOSE_2026-05-23.md")
    criteria_pos = index_text.find("PHASE4A_DIRECTION_REPLAY_ARTIFACT_ENTRY_CRITERIA_2026-05-23.md")
    ordering_ok = current_pos >= 0 and close_pos >= 0 and criteria_pos >= 0 and current_pos < close_pos < criteria_pos
    if not ordering_ok:
        failures.append("Direction replay artifact entry close doc must be first current formal spec")

    return {"missing_count": len(missing), "missing": missing, "ordering_ok": bool(ordering_ok)}


def _check_artifact_shape(failures: List[str]) -> Dict[str, Any]:
    required_by_file = {
        "btcts_next/src/btcts/replay/replay_prediction_artifacts.py": [
            "build_prediction_direction_input_from_scenario",
            "build_prediction_direction_output",
            "prediction_direction_output_to_snapshot",
            "source_kind=\"replay_artifact_only\"",
            "\"artifact_only\": True",
            "\"not_runtime_wiring\": True",
            "\"not_ui_wiring\": True",
            "\"not_market_engine_wiring\": True",
            "diagnostic_quality",
            "phase4a.direction_artifact_diagnostics.v1",
            "prediction_direction_snapshot",
        ],
        "btcts_next/src/btcts/replay/replay_session.py": [
            "prediction_direction_snapshots",
            "add_prediction_direction_snapshot",
            "prediction_direction_snapshot_count",
        ],
        "btcts_next/src/btcts/replay/replay_export.py": [
            "prediction_direction_snapshots",
            "prediction_direction_snapshot_path",
            "prediction_direction_snapshot_count",
            "prediction_direction_snapshot.json",
        ],
        "btcts_next/src/btcts/replay/replay_runner.py": [
            "prediction_direction_snapshot",
            "add_prediction_direction_snapshot",
        ],
        "btcts_next/src/btcts/replay/replay_report.py": [
            "_build_prediction_direction_summary",
            "prediction_direction_summary",
            "latest_read_only_contract",
            "latest_not_runtime_wiring",
            "latest_not_ui_wiring",
            "latest_diagnostic_quality_version",
            "latest_diagnostic_quality_ok",
            "latest_diagnostic_quality_passed_count",
        ],
    }
    missing: List[Dict[str, str]] = []
    forbidden: List[Dict[str, str]] = []

    for rel_path, fragments in required_by_file.items():
        text = _read_text(rel_path)
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"artifact shape fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    for rel_path in ARTIFACT_FILES:
        text = _read_text(rel_path)
        for token in FORBIDDEN_TOKENS:
            if token in text:
                failures.append(f"artifact-only Direction entry must not include forbidden token: {rel_path}: {token}")
                forbidden.append({"path": rel_path, "token": token})

    return {
        "missing_count": len(missing),
        "missing": missing,
        "forbidden_count": len(forbidden),
        "forbidden": forbidden,
    }


def _check_no_unapproved_wiring(failures: List[str]) -> Dict[str, Any]:
    scan_roots = [
        "btcts_next/src/btcts/replay",
        "btcts_next/src/btcts/apps/operator_ui",
        "btcts_next/src/btcts/market_engine",
    ]
    hits: List[Dict[str, str]] = []
    allowed_hits: List[Dict[str, str]] = []

    for root_rel in scan_roots:
        root = REPO_ROOT / root_rel
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            text = path.read_text(encoding="utf-8")
            for token in DIRECTION_TOKENS:
                if token not in text:
                    continue
                if rel in ALLOWED_DIRECTION_REFERENCES:
                    allowed_hits.append({"path": rel, "token": token})
                    continue
                hits.append({"path": rel, "token": token})
                failures.append(f"unapproved Direction wiring outside artifact-only replay entry: {rel}: {token}")

    return {
        "hit_count": len(hits),
        "hits": hits,
        "allowed_hit_count": len(allowed_hits),
        "allowed_hits": allowed_hits,
    }


def _check_primary_connection(failures: List[str]) -> Dict[str, Any]:
    primary_text = _read_text(PRIMARY_GUARD_PATH)
    required = [
        "tools/test_phase4a_direction_replay_artifact_entry_close_guard.py",
        "direction_replay_artifact_entry_close_guard",
    ]
    missing: List[str] = []
    for fragment in required:
        if fragment not in primary_text:
            failures.append(f"primary guard connection missing: {fragment}")
            missing.append(fragment)
    return {"missing_count": len(missing), "missing": missing}


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    plain_tests = _run_plain_tests(failures)
    criteria_guard = _run_json_guard(CRITERIA_GUARD_PATH, failures)
    read_only_guard = _run_json_guard(READ_ONLY_GUARD_PATH, failures)
    docs = _check_docs(failures)
    artifact_shape = _check_artifact_shape(failures)
    wiring = _check_no_unapproved_wiring(failures)
    primary_connection = _check_primary_connection(failures)

    summary = {
        "phase": "phase4a_direction_replay_artifact_entry_close_guard",
        "checks": {
            "compile": compile_result,
            "plain_tests": plain_tests,
            "criteria_guard": criteria_guard,
            "read_only_guard": read_only_guard,
            "docs": docs,
            "artifact_shape": artifact_shape,
            "wiring": wiring,
            "primary_connection": primary_connection,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
