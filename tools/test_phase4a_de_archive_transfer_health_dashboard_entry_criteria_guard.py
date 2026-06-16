# path: ./tools/test_phase4a_de_archive_transfer_health_dashboard_entry_criteria_guard.py
# desc: Phase 4-A D/E archive transfer Health dashboard entry criteria and summary producer guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SPEC_PATH = "tmp/docs/architecture/PHASE4A_DE_ARCHIVE_TRANSFER_HEALTH_DASHBOARD_ENTRY_CRITERIA_2026-05-31.md"
SUMMARY_PATH = "btcts_next/src/btcts/collector_vnext/archive/health_summary.py"
SUMMARY_TEST_PATH = "tools/test_archive_transfer_health_summary.py"
WORKER_PATH = "btcts_next/src/btcts/collector_vnext/archive/worker.py"

COMPILE_TARGETS = [
    SUMMARY_PATH,
    SUMMARY_TEST_PATH,
    WORKER_PATH,
]

REQUIRED_SPEC_FRAGMENTS = [
    "D/E Archive Transfer Health Dashboard Entry Criteria",
    "Health UI must not scan D or E directly",
    "archive_transfer_health_summary.json",
    "verified_on_e_drive_by_size_and_sha256",
    "hash_mismatch",
    "size_mismatch",
    "missing_on_e",
    "delete_candidate_not_hash_verified_on_e",
    "OK = green",
    "Warn = amber",
    "Crit = red",
    "normal OK state must not show every filename",
    "Warn/Crit may show bad_files with D/E paths",
    "This slice does not implement Health page wiring",
]

REQUIRED_SUMMARY_FRAGMENTS = [
    "SUMMARY_SCHEMA_VERSION = \"archive_transfer_health_summary.v1\"",
    "hashlib.sha256",
    "archive_transfer_health_summary_path",
    "build_archive_transfer_health_summary",
    "write_archive_transfer_health_summary",
    "verified_on_e_drive_by_size_and_sha256",
    "delete_candidate_hash_mismatch",
    "ui_must_not_scan_d_or_e",
    "normal_ok_shows_all_files",
]

REQUIRED_WORKER_FRAGMENTS = [
    "build_archive_transfer_health_summary",
    "write_archive_transfer_health_summary",
    "archive.transfer_health_summary.updated",
    "copy_items=plan",
    "gc_items=gc_plan",
]

FORBIDDEN_WORKER_FRAGMENTS = [
    "from btcts.apps.operator_ui",
    "streamlit",
]


def _read_text(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _compile_targets(failures: list[str]) -> dict[str, Any]:
    failed: list[dict[str, str]] = []
    cache_root = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "de_archive_transfer_health"
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
        except Exception as exc:
            failures.append(f"py_compile failed: {rel_path}: {exc}")
            failed.append({"path": rel_path, "error": str(exc)})
    return {"failed": failed, "passed_count": len(COMPILE_TARGETS) - len(failed)}


def _check_fragments(rel_path: str, fragments: list[str], failures: list[str]) -> list[str]:
    text = _read_text(rel_path)
    missing: list[str] = []
    if not text:
        failures.append(f"required file missing or empty: {rel_path}")
        return ["__file_missing__"]
    for fragment in fragments:
        if fragment not in text:
            failures.append(f"missing fragment in {rel_path}: {fragment}")
            missing.append(fragment)
    return missing


def _run_summary_test(failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / SUMMARY_TEST_PATH)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=120,
    )
    ok = proc.returncode == 0 and proc.stdout.strip() == "ok"
    if not ok:
        failures.append("summary producer unit test must emit plain ok")
    return {
        "returncode": proc.returncode,
        "ok": ok,
        "stdout_tail": (proc.stdout or "")[-1200:],
        "stderr_tail": (proc.stderr or "")[-1200:],
    }


def main() -> int:
    failures: list[str] = []
    compile_result = _compile_targets(failures)
    spec_missing = _check_fragments(SPEC_PATH, REQUIRED_SPEC_FRAGMENTS, failures)
    summary_missing = _check_fragments(SUMMARY_PATH, REQUIRED_SUMMARY_FRAGMENTS, failures)
    worker_missing = _check_fragments(WORKER_PATH, REQUIRED_WORKER_FRAGMENTS, failures)
    worker_text = _read_text(WORKER_PATH)
    forbidden_hits = []
    for fragment in FORBIDDEN_WORKER_FRAGMENTS:
        if fragment in worker_text:
            forbidden_hits.append(fragment)
            failures.append(f"worker must not import UI/Streamlit: {fragment}")
    summary_test = _run_summary_test(failures)
    payload = {
        "ok": not failures,
        "phase": "phase4a_de_archive_transfer_health_dashboard_entry_criteria_and_summary_producer",
        "failures": failures,
        "compile": compile_result,
        "spec_missing": spec_missing,
        "summary_missing": summary_missing,
        "worker_missing": worker_missing,
        "forbidden_worker_hits": forbidden_hits,
        "summary_test": summary_test,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())