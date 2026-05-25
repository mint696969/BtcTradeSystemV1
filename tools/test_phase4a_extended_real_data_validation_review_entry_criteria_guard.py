# path: ./tools/test_phase4a_extended_real_data_validation_review_entry_criteria_guard.py
# desc: Phase 4-A extended real-data validation review entry criteria guard.

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

DOC_PATH = "tmp/docs/architecture/PHASE4A_EXTENDED_REAL_DATA_VALIDATION_REVIEW_ENTRY_CRITERIA_2026-05-25.md"
BROADER_DOC_PATH = "tmp/docs/architecture/PHASE4A_BROADER_REAL_DATA_VALIDATION_REVIEW_ENTRY_CRITERIA_2026-05-24.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATUS_PATH = "tmp/gpt_room/08_STATUS.md"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
HANDOFF_PATH = "tmp/gpt_room/memory/handoffs/2026-05-25_phase4a_broader_real_data_validation_review_slice_handoff.md"
BROADER_REVIEW_SCRIPT = "tmp/work/phase4a_broader_real_data_validation_review_probe/review_broader_real_data_validation_review_output_v1.py"
BROADER_GUARD_PATH = "tools/test_phase4a_broader_real_data_validation_review_entry_criteria_guard.py"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"
FUTURE_PROBE_PATH = "tools/probe_phase4a_extended_real_data_validation_review.py"

COMPILE_TARGETS = [
    BROADER_GUARD_PATH,
    BROADER_REVIEW_SCRIPT,
    FUTURE_PROBE_PATH,
]

FORBIDDEN_PATH_PREFIXES = [
    "btcts_next/src/btcts/apps/operator_ui",
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/execution",
    "btcts_next/src/btcts/broker",
    "btcts_next/src/btcts/collector",
    "btcts_next/src/btcts/collector_vnext",
]


def _read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _compile_targets(failures: List[str]) -> Dict[str, Any]:
    passed = []
    failed = []
    cache_root = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "extended_real_data_validation_review_entry"
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


def _run_json(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=1500)
    parsed = None
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"json command did not emit valid JSON: {rel_path}: {exc}")
    ok = proc.returncode == 0 and isinstance(parsed, dict) and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"json command must return ok true and failures []: {rel_path}")
    return {"returncode": proc.returncode, "ok": bool(ok), "phase": parsed.get("phase") if isinstance(parsed, dict) else None, "stdout_tail": (proc.stdout or "")[-1800:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _check_docs(failures: List[str]) -> Dict[str, Any]:
    required = {
        DOC_PATH: [
            "extended real-data validation review entry criteria",
            "This entry does not open extended validation implementation yet.",
            "extended real-data validation review != production replay job",
            "tools/test_phase4a_extended_real_data_validation_review_entry_criteria_guard.py",
            "tools/probe_phase4a_extended_real_data_validation_review.py",
            "ERV-E3. Review declares explicit max_dates / max_files_per_date / max_lines_per_file limits.",
        ],
        BROADER_DOC_PATH: [
            "## 11. Broader review probe implementation checkpoint",
            "## 12. Broader review probe output shape review",
            "manual, bounded, diagnostic-only, and tmp-output-only",
        ],
        INDEX_PATH: [
            "PHASE4A_EXTENDED_REAL_DATA_VALIDATION_REVIEW_ENTRY_CRITERIA_2026-05-25.md",
            "PHASE4A_BROADER_REAL_DATA_VALIDATION_REVIEW_ENTRY_CRITERIA_2026-05-24.md",
        ],
        STATUS_PATH: [
            "broader real-data validation review slice final close checkpoint",
            "broader real-data validation review slice handoff summary",
            "collector state / runtime / UI / market_engine / collector writer/backfill / broker-order / inference / training は開いていない",
        ],
        FOCUS_PATH: [
            "extended_real_data_validation_review_entry_commit_checkpoint_12e307dc_is_complete",
            "extended_real_data_validation_review_probe_commit_checkpoint_0b2777bf_is_complete",
            "next_review_extended_real_data_validation_review_probe_output_shape",
            "keep_collector_state_e_drive_archive_d_drive_hot_runtime_ui_market_engine_broker_order_inference_training_closed_after_extended_entry_checkpoint",
        ],
        HANDOFF_PATH: [
            "Phase 4-A broader real-data validation review slice handoff",
            "Responsibility boundaries preserved",
        ],
    }
    missing = []
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
    extended_pos = index_text.find("PHASE4A_EXTENDED_REAL_DATA_VALIDATION_REVIEW_ENTRY_CRITERIA_2026-05-25.md")
    broader_pos = index_text.find("PHASE4A_BROADER_REAL_DATA_VALIDATION_REVIEW_ENTRY_CRITERIA_2026-05-24.md")
    ordering_ok = current_pos >= 0 and extended_pos >= 0 and broader_pos >= 0 and current_pos < extended_pos < broader_pos
    if not ordering_ok:
        failures.append("extended real-data validation review entry criteria doc must be first current formal spec")
    return {"missing_count": len(missing), "missing": missing, "ordering_ok": bool(ordering_ok)}


def _check_future_probe_implementation(failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / FUTURE_PROBE_PATH
    if not path.exists():
        failures.append(f"extended real-data validation review probe must exist after implementation entry: {FUTURE_PROBE_PATH}")
        return {"exists": False, "missing_count": 1, "missing": [FUTURE_PROBE_PATH], "forbidden_count": 0, "forbidden": []}

    text = path.read_text(encoding="utf-8")
    required = [
        "phase4a_extended_real_data_validation_review_probe",
        "max_dates",
        "max_files_per_date",
        "max_lines_per_file",
        "writes_only_to_tmp_work",
        "does_not_write_to_data_root",
        "does_not_write_to_d_drive_hot_runtime",
        "does_not_mutate_collector_state",
        "does_not_open_runtime_ui_market_engine_or_broker_order",
        "does_not_open_inference_or_training",
        "BASELINE_BROADER",
        "probe_phase4a_extended_real_data_validation_review.out.json",
    ]
    forbidden = [
        "btcts_next/src/btcts/apps/operator_ui",
        "btcts_next/src/btcts/market_engine",
        "btcts_next/src/btcts/collector_vnext",
        "btcts_next/src/btcts/execution",
        "btcts_next/src/btcts/broker",
        "place_order",
        "live_order_placement",
        "auto_trade",
        "model_training",
        "inference_job",
    ]
    missing = []
    forbidden_hits = []
    for fragment in required:
        if fragment not in text:
            missing.append(fragment)
            failures.append(f"extended review probe missing required boundary fragment: {fragment}")
    for fragment in forbidden:
        if fragment in text:
            forbidden_hits.append(fragment)
            failures.append(f"extended review probe contains forbidden fragment: {fragment}")
    probe_run = _run_json(FUTURE_PROBE_PATH, failures)
    return {
        "exists": True,
        "missing_count": len(missing),
        "missing": missing,
        "forbidden_count": len(forbidden_hits),
        "forbidden": forbidden_hits,
        "probe_run": probe_run,
    }


def _check_forbidden_path_opening(failures: List[str]) -> Dict[str, Any]:
    hits = []
    for rel in FORBIDDEN_PATH_PREFIXES:
        root = REPO_ROOT / rel
        if not root.exists():
            continue
        for path in root.rglob("*real_data*validation*review*.py"):
            rel_path = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            hits.append(rel_path)
            failures.append(f"extended real-data validation review must not live in forbidden path: {rel_path}")
    return {"hit_count": len(hits), "hits": hits}


def _check_primary_connection_static(failures: List[str]) -> Dict[str, Any]:
    text = _read_text(PRIMARY_GUARD_PATH)
    required = [
        "tools/test_phase4a_extended_real_data_validation_review_entry_criteria_guard.py",
        "extended_real_data_validation_review_entry_criteria_guard",
    ]
    missing = []
    for fragment in required:
        if fragment not in text:
            missing.append(fragment)
            failures.append(f"primary guard missing extended real-data validation review entry connection: {fragment}")
    return {"missing_count": len(missing), "missing": missing}


def main() -> int:
    failures: List[str] = []
    compile_result = _compile_targets(failures)
    broader_review = _run_json(BROADER_REVIEW_SCRIPT, failures)
    broader_guard = _run_json(BROADER_GUARD_PATH, failures)
    docs = _check_docs(failures)
    future_probe_implementation = _check_future_probe_implementation(failures)
    primary_connection_static = _check_primary_connection_static(failures)
    forbidden_path_opening = _check_forbidden_path_opening(failures)
    summary = {
        "phase": "phase4a_extended_real_data_validation_review_entry_criteria_guard",
        "checks": {
            "compile": compile_result,
            "broader_review": broader_review,
            "broader_guard": broader_guard,
            "docs": docs,
            "future_probe_implementation": future_probe_implementation,
            "primary_connection_static": primary_connection_static,
            "forbidden_path_opening": forbidden_path_opening,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
