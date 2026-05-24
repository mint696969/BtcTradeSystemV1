# path: ./tools/test_phase4a_read_only_real_data_replay_report_validation_entry_criteria_guard.py
# desc: Phase 4-A read-only real-data replay/report validation entry criteria guard.

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

DOC_PATH = "tmp/docs/architecture/PHASE4A_READ_ONLY_REAL_DATA_REPLAY_REPORT_VALIDATION_ENTRY_CRITERIA_2026-05-23.md"
INVENTORY_DOC_PATH = "tmp/docs/architecture/PHASE4A_READ_ONLY_REAL_DATA_VALIDATION_PROBE_ENTRY_CRITERIA_2026-05-23.md"
INDEX_PATH = "tmp/docs/_INDEX.md"
STATUS_PATH = "tmp/gpt_room/08_STATUS.md"
FOCUS_PATH = "tmp/gpt_room/09_FOCUS.json"
INVENTORY_PROBE_PATH = "tools/probe_phase4a_read_only_real_data_validation_inventory.py"
INVENTORY_ENTRY_GUARD_PATH = "tools/test_phase4a_read_only_real_data_validation_probe_entry_criteria_guard.py"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"

COMPILE_TARGETS = [
    INVENTORY_PROBE_PATH,
    INVENTORY_ENTRY_GUARD_PATH,
    "btcts_next/src/btcts/replay/replay_report.py",
    "btcts_next/src/btcts/replay/replay_session.py",
    "btcts_next/src/btcts/replay/replay_runner.py",
]

FORBIDDEN_PATH_PREFIXES = [
    "btcts_next/src/btcts/apps/operator_ui",
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/execution",
    "btcts_next/src/btcts/broker",
    "btcts_next/src/btcts/collector",
    "btcts_next/src/btcts/collector_vnext",
]

FUTURE_PROBE_PATH = "tools/probe_phase4a_read_only_real_data_replay_report_validation.py"


def _read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _compile_targets(failures: List[str]) -> Dict[str, Any]:
    passed: List[str] = []
    failed: List[Dict[str, str]] = []
    cache_root = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "real_data_replay_report_validation_entry"
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
            "read-only real-data replay/report validation entry criteria",
            "This entry does not open replay/report validation implementation yet.",
            "read-only real-data replay/report validation != production replay job",
            "tools/test_phase4a_read_only_real_data_replay_report_validation_entry_criteria_guard.py",
            "tools/probe_phase4a_read_only_real_data_replay_report_validation.py",
        ],
        INVENTORY_DOC_PATH: [
            "read-only real-data inventory probe implementation post-commit checkpoint is complete",
            "read-only real-data inventory probe schema-shape review is complete",
            "channel_count = 4",
            "json_ok_count = 24",
            "json_error_count = 0",
            "required_envelope_key_count = 30",
        ],
        INDEX_PATH: [
            "PHASE4A_READ_ONLY_REAL_DATA_REPLAY_REPORT_VALIDATION_ENTRY_CRITERIA_2026-05-23.md",
            "read-only real-data replay/report validation entry criteria",
            "read-only real-data inventory probe schema-shape review complete",
            "runtime / UI / market_engine へはまだ接続しない",
        ],
        STATUS_PATH: [
            "read-only real-data replay/report validation entry criteria",
            "manual / bounded / tmp-output-only / disconnected",
            "D-drive hot runtime storage",
            "E-drive archive",
        ],
        FOCUS_PATH: [
            "phase4a_read_only_real_data_replay_report_validation_entry_criteria",
            "read_only_real_data_replay_report_validation_entry_criteria_only",
            "keep_replay_report_validation_manual_bounded_tmp_output_only",
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
    replay_report_pos = index_text.find("PHASE4A_READ_ONLY_REAL_DATA_REPLAY_REPORT_VALIDATION_ENTRY_CRITERIA_2026-05-23.md")
    inventory_pos = index_text.find("PHASE4A_READ_ONLY_REAL_DATA_VALIDATION_PROBE_ENTRY_CRITERIA_2026-05-23.md")
    ordering_ok = current_pos >= 0 and replay_report_pos >= 0 and inventory_pos >= 0 and current_pos < replay_report_pos < inventory_pos
    if not ordering_ok:
        failures.append("real-data replay/report validation entry criteria doc must be first current formal spec")

    return {"missing_count": len(missing), "missing": missing, "ordering_ok": bool(ordering_ok)}


def _check_replay_report_boundaries(failures: List[str]) -> Dict[str, Any]:
    required_by_file = {
        "btcts_next/src/btcts/replay/replay_report.py": [
            "def build_replay_report(",
            "prediction_direction_summary",
            "direction_replay_calibration_review_material",
        ],
        "btcts_next/src/btcts/replay/replay_session.py": [
            "class ReplaySession",
            "prediction_direction_snapshots",
            "def summary(self) -> Dict:",
        ],
    }
    forbidden = [
        "place_order",
        "broker_order_placement",
        "broker_order_writer",
        "broker_order_submit",
        "live_order_placement",
        "auto_trade",
        "write_text(",
        "mkdir(",
        "DATA_ROOT",
        "BTC_TS_DATA_DIR",
    ]
    missing: List[Dict[str, str]] = []
    hits: List[Dict[str, str]] = []
    for rel_path, fragments in required_by_file.items():
        text = _read_text(rel_path)
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"replay/report boundary fragment missing: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})
        for fragment in forbidden:
            if fragment in text:
                failures.append(f"replay/report file contains forbidden runtime/write token: {rel_path}: {fragment}")
                hits.append({"path": rel_path, "fragment": fragment})
    return {"missing_count": len(missing), "missing": missing, "forbidden_hit_count": len(hits), "forbidden_hits": hits}


def _check_future_probe_implementation(failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / FUTURE_PROBE_PATH
    text = _read_text(FUTURE_PROBE_PATH)
    missing: List[str] = []
    forbidden: List[str] = []
    required = [
        "phase4a_read_only_real_data_replay_report_validation_probe",
        "build_replay_report(",
        "ReplaySession(",
        "writes_only_to_tmp_work",
        "does_not_write_to_data_root",
        "does_not_write_to_d_drive_hot_runtime",
        "does_not_mutate_collector_state",
        "does_not_open_runtime_ui_market_engine_or_broker_order",
        'OUT_DIR = REPO_ROOT / "tmp" / "work" / "phase4a_real_data_validation_probe"',
        "allowed_root = OUT_DIR.resolve()",
    ]
    forbidden_fragments = [
        "place_order",
        "broker_order_placement",
        "broker_order_writer",
        "broker_order_submit",
        "live_order_placement",
        "auto_trade",
        "btcts_next/src/btcts/apps/operator_ui",
        "btcts_next/src/btcts/market_engine",
        "btcts_next/src/btcts/execution",
        "btcts_next/src/btcts/broker",
        "btcts_next/src/btcts/collector",
        "btcts_next/src/btcts/collector_vnext",
    ]
    if not path.exists() or not text:
        failures.append(f"future replay/report validation probe must be opened by this implementation slice: {FUTURE_PROBE_PATH}")
        return {"exists": False, "missing_count": 1, "missing": ["__file__"], "forbidden_count": 0, "forbidden": []}
    for fragment in required:
        if fragment not in text:
            missing.append(fragment)
            failures.append(f"replay/report validation probe fragment missing: {fragment}")
    for fragment in forbidden_fragments:
        if fragment in text:
            forbidden.append(fragment)
            failures.append(f"replay/report validation probe forbidden fragment: {fragment}")
    return {"exists": True, "missing_count": len(missing), "missing": missing, "forbidden_count": len(forbidden), "forbidden": forbidden}


def _check_forbidden_path_opening(failures: List[str]) -> Dict[str, Any]:
    hits: List[str] = []
    for rel in FORBIDDEN_PATH_PREFIXES:
        root = REPO_ROOT / rel
        if not root.exists():
            continue
        for path in root.rglob("*real_data*replay*report*validation*.py"):
            rel_path = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            hits.append(rel_path)
            failures.append(f"real-data replay/report validation must not live in forbidden path: {rel_path}")
    return {"hit_count": len(hits), "hits": hits}


def main() -> int:
    failures: List[str] = []

    compile_result = _compile_targets(failures)
    inventory_probe = _run_json_command(INVENTORY_PROBE_PATH, failures)
    inventory_entry_guard = _run_json_command(INVENTORY_ENTRY_GUARD_PATH, failures)
    docs = _check_docs(failures)
    replay_report_boundaries = _check_replay_report_boundaries(failures)
    future_probe_implementation = _check_future_probe_implementation(failures)
    forbidden_path_opening = _check_forbidden_path_opening(failures)

    summary = {
        "phase": "phase4a_read_only_real_data_replay_report_validation_entry_criteria_guard",
        "checks": {
            "compile": compile_result,
            "inventory_probe": inventory_probe,
            "inventory_entry_guard": inventory_entry_guard,
            "docs": docs,
            "replay_report_boundaries": replay_report_boundaries,
            "future_probe_implementation": future_probe_implementation,
            "forbidden_path_opening": forbidden_path_opening,
        },
        "failures": failures,
        "ok": len(failures) == 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())


