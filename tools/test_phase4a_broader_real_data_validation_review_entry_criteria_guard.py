# path: ./tools/test_phase4a_broader_real_data_validation_review_entry_criteria_guard.py
# desc: Phase 4-A broader real-data validation review entry criteria guard.

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

DOC_PATH = "tmp/docs/architecture/PHASE4A_BROADER_REAL_DATA_VALIDATION_REVIEW_ENTRY_CRITERIA_2026-05-24.md"
REPLAY_REPORT_DOC_PATH = "tmp/docs/architecture/PHASE4A_READ_ONLY_REAL_DATA_REPLAY_REPORT_VALIDATION_ENTRY_CRITERIA_2026-05-23.md"
INVENTORY_DOC_PATH = "tmp/docs/architecture/PHASE4A_READ_ONLY_REAL_DATA_VALIDATION_PROBE_ENTRY_CRITERIA_2026-05-23.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATUS_PATH = "tmp/gpt_room/08_STATUS.md"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
INVENTORY_PROBE_PATH = "tools/probe_phase4a_read_only_real_data_validation_inventory.py"
REPLAY_REPORT_PROBE_PATH = "tools/probe_phase4a_read_only_real_data_replay_report_validation.py"
REAL_DATA_ENTRY_GUARD_PATH = "tools/test_phase4a_read_only_real_data_validation_probe_entry_criteria_guard.py"
REPLAY_REPORT_ENTRY_GUARD_PATH = "tools/test_phase4a_read_only_real_data_replay_report_validation_entry_criteria_guard.py"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"
FUTURE_REVIEW_PROBE_PATH = "tools/probe_phase4a_broader_real_data_validation_review.py"

COMPILE_TARGETS = [
    INVENTORY_PROBE_PATH,
    REPLAY_REPORT_PROBE_PATH,
    FUTURE_REVIEW_PROBE_PATH,
    REAL_DATA_ENTRY_GUARD_PATH,
    REPLAY_REPORT_ENTRY_GUARD_PATH,
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
    passed: List[str] = []
    failed: List[Dict[str, str]] = []
    cache_root = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "broader_real_data_validation_review_entry"
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


def _run_json_command(rel_path: str, failures: List[str], *, timeout: int = 900) -> Dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / rel_path)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    parsed = None
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"json command did not emit valid JSON: {rel_path}: {exc}")

    ok = proc.returncode == 0 and isinstance(parsed, dict) and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"json command must return ok true and failures []: {rel_path}")
    return {
        "returncode": proc.returncode,
        "ok": bool(ok),
        "phase": parsed.get("phase") if isinstance(parsed, dict) else None,
        "stdout_tail": (proc.stdout or "")[-1800:],
        "stderr_tail": (proc.stderr or "")[-1800:],
    }


def _check_docs(failures: List[str]) -> Dict[str, Any]:
    required = {
        DOC_PATH: [
            "broader real-data validation review entry criteria",
            "This entry does not open broader real-data validation implementation yet.",
            "broader real-data validation review != production replay job",
            "tools/test_phase4a_broader_real_data_validation_review_entry_criteria_guard.py",
            "tools/probe_phase4a_broader_real_data_validation_review.py",
        ],
        REPLAY_REPORT_DOC_PATH: [
            "read-only real-data replay/report validation probe implementation post-commit checkpoint is complete",
            "read-only real-data replay/report validation probe shape review is complete",
            "channel_count = 4",
            "source_path_count = 8",
            "replay_row_count = 24",
            "report_board_count = 12",
            "report_trade_count = 12",
        ],
        INVENTORY_DOC_PATH: [
            "read-only real-data inventory probe implementation post-commit checkpoint is complete",
            "read-only real-data inventory probe schema-shape review is complete",
            "channel_count = 4",
            "json_ok_count = 24",
            "json_error_count = 0",
        ],
        INDEX_PATH: [
            "PHASE4A_BROADER_REAL_DATA_VALIDATION_REVIEW_ENTRY_CRITERIA_2026-05-24.md",
            "broader real-data validation review entry criteria",
            "read-only real-data replay/report validation probe shape review complete",
            "D-drive hot runtime storage",
            "E-drive archive data",
        ],
        STATUS_PATH: [
            "broader real-data validation review entry criteria",
            "manual / bounded / tmp-output-only / disconnected",
            "D-drive hot runtime storage",
            "E-drive archive",
        ],
        FOCUS_PATH: [
            "phase4a_broader_real_data_validation_review_entry_criteria",
            "broader_real_data_validation_review_entry_criteria_only",
            "keep_broader_real_data_validation_review_manual_bounded_tmp_output_only",
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
    broader_pos = index_text.find("PHASE4A_BROADER_REAL_DATA_VALIDATION_REVIEW_ENTRY_CRITERIA_2026-05-24.md")
    replay_pos = index_text.find("PHASE4A_READ_ONLY_REAL_DATA_REPLAY_REPORT_VALIDATION_ENTRY_CRITERIA_2026-05-23.md")
    ordering_ok = current_pos >= 0 and broader_pos >= 0 and replay_pos >= 0 and current_pos < broader_pos < replay_pos
    if not ordering_ok:
        failures.append("broader real-data validation review entry criteria doc must be first current formal spec")

    return {"missing_count": len(missing), "missing": missing, "ordering_ok": bool(ordering_ok)}


def _check_future_probe_implementation(failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / FUTURE_REVIEW_PROBE_PATH
    if not path.exists():
        failures.append(f"broader real-data validation review probe must exist after implementation entry: {FUTURE_REVIEW_PROBE_PATH}")
        return {"exists": False, "missing_count": 1, "missing": [FUTURE_REVIEW_PROBE_PATH], "forbidden_count": 0, "forbidden": []}

    text = path.read_text(encoding="utf-8")
    required = [
        "phase4a_broader_real_data_validation_review_probe",
        "read_only_existing_outputs",
        "writes_only_to_tmp_work",
        "does_not_write_to_data_root",
        "does_not_write_to_d_drive_hot_runtime",
        "does_not_mutate_collector_state",
        "does_not_open_runtime_ui_market_engine_or_broker_order",
        "does_not_open_inference_or_training",
        "DEFAULT_INVENTORY",
        "DEFAULT_REPLAY_REPORT",
        "DEFAULT_OUT",
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
            failures.append(f"broader review probe missing required boundary fragment: {fragment}")
    for fragment in forbidden:
        if fragment in text:
            forbidden_hits.append(fragment)
            failures.append(f"broader review probe contains forbidden fragment: {fragment}")

    probe_run = _run_json_command(FUTURE_REVIEW_PROBE_PATH, failures)
    return {
        "exists": True,
        "missing_count": len(missing),
        "missing": missing,
        "forbidden_count": len(forbidden_hits),
        "forbidden": forbidden_hits,
        "probe_run": probe_run,
    }


def _check_primary_connection_static(failures: List[str]) -> Dict[str, Any]:
    text = _read_text(PRIMARY_GUARD_PATH)
    required = [
        "tools/test_phase4a_read_only_real_data_validation_probe_entry_criteria_guard.py",
        "tools/test_phase4a_read_only_real_data_replay_report_validation_entry_criteria_guard.py",
        "tools/test_phase4a_broader_real_data_validation_review_entry_criteria_guard.py",
        "broader_real_data_validation_review_entry_criteria_guard",
    ]
    missing: List[str] = []
    for fragment in required:
        if fragment not in text:
            missing.append(fragment)
            failures.append(f"primary guard missing broader real-data validation review entry connection: {fragment}")
    return {"missing_count": len(missing), "missing": missing}


def _check_forbidden_path_opening(failures: List[str]) -> Dict[str, Any]:
    hits: List[str] = []
    for rel in FORBIDDEN_PATH_PREFIXES:
        root = REPO_ROOT / rel
        if not root.exists():
            continue
        for path in root.rglob("*real_data*validation*review*.py"):
            rel_path = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            hits.append(rel_path)
            failures.append(f"broader real-data validation review must not live in forbidden path: {rel_path}")
    return {"hit_count": len(hits), "hits": hits}


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    inventory_probe = _run_json_command(INVENTORY_PROBE_PATH, failures)
    real_data_entry_guard = _run_json_command(REAL_DATA_ENTRY_GUARD_PATH, failures)
    replay_report_entry_guard = _run_json_command(REPLAY_REPORT_ENTRY_GUARD_PATH, failures)
    docs = _check_docs(failures)
    future_probe_implementation = _check_future_probe_implementation(failures)
    primary_connection_static = _check_primary_connection_static(failures)
    forbidden_path_opening = _check_forbidden_path_opening(failures)

    summary = {
        "phase": "phase4a_broader_real_data_validation_review_entry_criteria_guard",
        "checks": {
            "compile": compile_result,
            "inventory_probe": inventory_probe,
            "real_data_entry_guard": real_data_entry_guard,
            "replay_report_entry_guard": replay_report_entry_guard,
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
