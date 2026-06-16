# path: ./tools/test_phase4a_direction_replay_calibration_review_material_entry_guard.py
# desc: Phase 4-A Direction replay calibration/review material entry criteria guard.

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

ENTRY_DOC = "tmp/docs/architecture/PHASE4A_DIRECTION_REPLAY_CALIBRATION_REVIEW_MATERIAL_ENTRY_CRITERIA_2026-05-23.md"
CLOSE_DOC = "tmp/docs/architecture/PHASE4A_DIRECTION_REPLAY_ARTIFACT_ENTRY_CLOSE_2026-05-23.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATUS_PATH = "tmp/gpt_room/08_STATUS.md"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"
CLOSE_GUARD_PATH = "tools/test_phase4a_direction_replay_artifact_entry_close_guard.py"

COMPILE_TARGETS = [
    CLOSE_GUARD_PATH,
    "btcts_next/src/btcts/replay/replay_prediction_artifacts.py",
    "btcts_next/src/btcts/replay/replay_report.py",
    "btcts_next/src/btcts/replay/tests/test_prediction_replay_export.py",
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export_prediction_artifacts.py",
]

FORBIDDEN_ROOTS = [
    "btcts_next/src/btcts/apps/operator_ui",
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/processing/l4_consumer_models/contracts",
]

FORBIDDEN_TOKENS = [
    "DirectionReplayCalibrationReviewMaterial",
    "direction_replay_calibration_review_material",
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

REQUIRED_MATERIAL_FRAGMENTS = {
    "btcts_next/src/btcts/replay/replay_report.py": [
        "_build_direction_replay_calibration_review_material",
        "direction_replay_calibration_review_material",
        "phase4a.direction_replay_calibration_review.v1",
        "review_only",
        "not_runtime_wiring",
        "not_ui_wiring",
        "not_market_engine_wiring",
    ],
    "btcts_next/src/btcts/replay/tests/test_prediction_replay_export.py": [
        "direction_replay_calibration_review_material",
        "review_priority",
        "review_flags",
    ],
    "btcts_next/src/btcts/replay/tests/test_replay_runner_export_prediction_artifacts.py": [
        "direction_replay_calibration_review_material",
        "review_only",
        "not_runtime_wiring",
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
    cache_root = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "direction_replay_calibration_review_material_entry"
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


def _run_close_guard(failures: List[str]) -> Dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / CLOSE_GUARD_PATH)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=900,
    )
    parsed: Dict[str, Any] | None = None
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"close guard did not emit JSON: {exc}")

    ok = proc.returncode == 0 and isinstance(parsed, dict) and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append("Direction artifact entry close guard must be green before review material entry")

    return {
        "returncode": proc.returncode,
        "ok": bool(ok),
        "json_phase": parsed.get("phase") if isinstance(parsed, dict) else None,
        "stdout_tail": (proc.stdout or "")[-1600:],
        "stderr_tail": (proc.stderr or "")[-1600:],
    }


def _check_docs(failures: List[str]) -> Dict[str, Any]:
    required = {
        ENTRY_DOC: [
            "Direction replay calibration/review material entry criteria",
            "review-only and read-only",
            "Direction replay calibration/review material != live runtime behavior",
            "Direction replay calibration/review material != UI surfacing",
            "Direction replay calibration/review material != market_engine integration",
            "Direction replay calibration/review material != Position hint",
            "Direction replay calibration/review material != Execution hint",
            "tools/test_phase4a_direction_replay_calibration_review_material_entry_guard.py",
            "Direction replay calibration/review material read model is closed",
            "phase4a.direction_replay_calibration_review.v1",
        ],
        CLOSE_DOC: [
            "Direction read-only artifact-only replay entry, summary/report review, and diagnostics quality are closed.",
            "diagnostic_quality",
            "Direction replay calibration/review material design",
            "Position / Execution runtime behavior",
        ],
        INDEX_PATH: [
            "PHASE4A_DIRECTION_REPLAY_CALIBRATION_REVIEW_MATERIAL_ENTRY_CRITERIA_2026-05-23.md",
            "Direction replay calibration/review material design only",
            "Direction replay calibration/review material read model close",
            "Direction artifact diagnostics quality close",
        ],
        STATUS_PATH: [
            "Direction replay calibration/review material design only",
            "Direction artifact diagnostics quality close",
            "runtime / UI / market_engine へはまだ接続しない",
            "Position / Execution は閉じたまま維持する",
        ],
        FOCUS_PATH: [
            "phase4a_direction_replay_calibration_review_material_entry_criteria",
            "next_direction_replay_calibration_review_material_design_only",
            "direction_replay_calibration_review_material_read_model_is_closed",
            "keep_ui_market_engine_position_execution_closed_after_diagnostics_quality_close",
        ],
    }
    missing: List[Dict[str, str]] = []
    for rel_path, fragments in required.items():
        text = _read_text(rel_path)
        if not text:
            failures.append(f"required file missing or empty: {rel_path}")
            missing.append({"path": rel_path, "fragment": "__missing_or_empty__"})
            continue
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"required fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})

    index_text = _read_text(INDEX_PATH)
    current_pos = index_text.find("### current formal spec")
    entry_pos = index_text.find("PHASE4A_DIRECTION_REPLAY_CALIBRATION_REVIEW_MATERIAL_ENTRY_CRITERIA_2026-05-23.md")
    close_pos = index_text.find("PHASE4A_DIRECTION_REPLAY_ARTIFACT_ENTRY_CLOSE_2026-05-23.md")
    ordering_ok = current_pos >= 0 and entry_pos >= 0 and close_pos >= 0 and current_pos < entry_pos < close_pos
    if not ordering_ok:
        failures.append("Direction replay calibration/review material entry doc must be first current formal spec")

    return {"missing_count": len(missing), "missing": missing, "ordering_ok": bool(ordering_ok)}


def _check_no_premature_wiring(failures: List[str]) -> Dict[str, Any]:
    hits: List[Dict[str, str]] = []
    for root_rel in FORBIDDEN_ROOTS:
        root = REPO_ROOT / root_rel
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            text = path.read_text(encoding="utf-8")
            for token in FORBIDDEN_TOKENS:
                if token in text:
                    hits.append({"path": rel, "token": token})
                    failures.append(f"premature Direction calibration/review material or Position/Execution wiring: {rel}: {token}")
    return {"hit_count": len(hits), "hits": hits}


def _check_material_shape(failures: List[str]) -> Dict[str, Any]:
    missing: List[Dict[str, str]] = []
    for rel_path, fragments in REQUIRED_MATERIAL_FRAGMENTS.items():
        text = _read_text(rel_path)
        for fragment in fragments:
            if fragment not in text:
                failures.append(
                    f"Direction replay calibration/review material fragment missing: {rel_path}: {fragment}"
                )
                missing.append({"path": rel_path, "fragment": fragment})
    return {"missing_count": len(missing), "missing": missing}


def _check_primary_connection(failures: List[str]) -> Dict[str, Any]:
    text = _read_text(PRIMARY_GUARD_PATH)
    required = [
        "tools/test_phase4a_direction_replay_calibration_review_material_entry_guard.py",
        "direction_replay_calibration_review_material_entry_guard",
    ]
    missing: List[str] = []
    for fragment in required:
        if fragment not in text:
            failures.append(f"primary guard connection missing: {fragment}")
            missing.append(fragment)
    return {"missing_count": len(missing), "missing": missing}


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    close_guard = _run_close_guard(failures)
    docs = _check_docs(failures)
    premature_wiring = _check_no_premature_wiring(failures)
    material_shape = _check_material_shape(failures)
    primary_connection = _check_primary_connection(failures)

    summary = {
        "phase": "phase4a_direction_replay_calibration_review_material_entry_guard",
        "checks": {
            "compile": compile_result,
            "close_guard": close_guard,
            "docs": docs,
            "premature_wiring": premature_wiring,
            "material_shape": material_shape,
            "primary_connection": primary_connection,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
