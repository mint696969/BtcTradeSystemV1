# path: ./tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_entry_close_guard.py
# desc: Close guard for Phase 4-A duplicate-safe Hot/Cold logical dataset view entry criteria. No reader/training/copy/delete.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_entry_close_guard.py"
ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_entry_guard.py"
COPY_MANIFEST_CLOSE_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_writer_dry_run_close_guard.py"
PLAN_SUMMARY_PATH = "tmp/work/operator_operational_readiness/outputs/hot_cold_10day_dry_run_plan_and_review_v1_20260602T140216.582610Z.json"
EXPECTED_PLAN_HASH = "e5bf5d3c6630c10084fc44c97614dc48c3bc4e8147e98683831eefa2923f9eb6"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_DUPLICATE_SAFE_DATASET_VIEW_ENTRY_2026-06-02.md"

COMPILE_FILES = [
    ENTRY_GUARD_PATH,
    COPY_MANIFEST_CLOSE_GUARD_PATH,
    "tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_model_guard.py",
    "tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_model_close_guard.py",
    "tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_writer_dry_run_guard.py",
    "btcts_next/src/btcts/collector_vnext/archive/copy_manifest.py",
    "btcts_next/src/btcts/collector_vnext/archive/test_copy_manifest.py",
]

FORBIDDEN_RUNTIME_TOKENS = [
    "shutil.copy",
    "copy2(",
    "copytree(",
    ".unlink(",
    ".rmdir(",
    "os.remove(",
    "os.unlink(",
    "os.rmdir(",
    "archive_gc_enable =",
    "archive_gc_enable:",
    "archive_gc_enable(",
    "execute_copy_plan",
    "execute_gc_plan",
    "logical_dataset_view",
    "read_parquet(",
    "read_json(",
    "rglob(\"*.parquet\")",
    "rglob(\"*.jsonl\")",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_duplicate_safe_dataset_view_entry_close"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=1800)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1600:], "stderr_tail": (proc.stderr or "")[-1600:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _check_spec(failures: list[str]) -> dict[str, Any]:
    text = _read(SPEC_PATH)
    required = [
        "Hot/Cold duplicate-safe logical dataset view entry criteria",
        "logical_file_id = exchange + symbol + rel_file",
        "Physical root must not be part of logical_file_id.",
        "never include both hot and cold physical paths for the same logical_file_id",
        "never raw double-rglob hot+cold directly into simulation/training",
        "read D/E data files",
        "connect to simulation",
        "connect to training",
        "copy files",
        "delete files",
        "candidate_delete_files = 0",
        "No delete is required now.",
        ENTRY_GUARD_PATH,
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"duplicate-safe dataset view close spec missing fragment: {fragment}")
    return {"missing": missing}


def _check_latest_10day_plan(failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / PLAN_SUMMARY_PATH
    if not path.exists():
        failures.append(f"latest 10-day plan summary missing: {PLAN_SUMMARY_PATH}")
        return {"exists": False}
    data = json.loads(path.read_text(encoding="utf-8"))
    too_new = ((data.get("review_exclusions") or {}).get("too_new") or {})
    ok = (
        data.get("ok") is True
        and data.get("plan_hash") == EXPECTED_PLAN_HASH
        and int(data.get("candidate_delete_files") or 0) == 0
        and float(data.get("candidate_delete_gb") or 0.0) == 0.0
        and int(too_new.get("files") or 0) == 56
        and data.get("no_delete_no_unlink_no_rmdir") is True
    )
    if not ok:
        failures.append("latest 10-day plan summary must remain zero-candidate/no-delete")
    return {"ok": ok, "plan_hash": data.get("plan_hash"), "candidate_delete_files": data.get("candidate_delete_files"), "too_new": too_new}


def _check_boundaries(failures: list[str]) -> dict[str, Any]:
    scan_files = [
        "btcts_next/src/btcts/collector_vnext/archive/copy_manifest.py",
        "btcts_next/src/btcts/apps/operator_ui/hot_cold_retention_safety_service.py",
    ]
    hits: list[dict[str, str]] = []
    for rel_path in scan_files:
        text = _read(rel_path)
        for token in FORBIDDEN_RUNTIME_TOKENS:
            if token in text:
                hits.append({"path": rel_path, "token": token})
    if hits:
        failures.append("duplicate-safe dataset view entry close must not open reader/copy/delete/runtime tokens")
    return {"hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "entry_guard": _run_json_guard(ENTRY_GUARD_PATH, failures),
        "copy_manifest_close_guard": {"verified_via_entry_guard": True, "path": COPY_MANIFEST_CLOSE_GUARD_PATH},
        "spec": _check_spec(failures),
        "latest_10day_plan": _check_latest_10day_plan(failures),
        "boundaries": _check_boundaries(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_entry_close_guard",
        "close_status": "closed" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
