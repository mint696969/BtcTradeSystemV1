# path: ./tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_entry_guard.py
# desc: Phase 4-A duplicate-safe Hot/Cold logical dataset view entry guard. No reader/training/copy/delete.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_entry_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_DUPLICATE_SAFE_DATASET_VIEW_ENTRY_2026-06-02.md"
COPY_MANIFEST_CLOSE_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_writer_dry_run_close_guard.py"
PLAN_SUMMARY_PATH = "tmp/work/operator_operational_readiness/outputs/hot_cold_10day_dry_run_plan_and_review_v1_20260602T140216.582610Z.json"
EXPECTED_PLAN_HASH = "e5bf5d3c6630c10084fc44c97614dc48c3bc4e8147e98683831eefa2923f9eb6"


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_duplicate_safe_dataset_view_entry"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=1200)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1600:], "stderr_tail": (proc.stderr or "")[-1600:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "stdout_tail": (proc.stdout or "")[-1600:], "stderr_tail": (proc.stderr or "")[-1600:]}


def _check_spec(failures: list[str]) -> dict[str, Any]:
    required = [
        "Hot/Cold duplicate-safe logical dataset view entry criteria",
        "logical_file_id = exchange + symbol + rel_file",
        "exchange = bitflyer",
        "symbol = BTC_JPY",
        "Physical root must not be part of logical_file_id.",
        "prefer hot for partitions within hot_retention_days = 10",
        "prefer cold for partitions older than hot_retention_days when cold is verified",
        "never include both hot and cold physical paths for the same logical_file_id",
        "logical_file_id",
        "storage_tier_selected",
        "hot_present",
        "cold_present",
        "cold_verified_by_manifest",
        "normalize rel_file and reject root escape",
        "allow only data/market_data and data/collector_raw",
        "forbid state/collector_vnext and logs/collector_vnext",
        "never raw double-rglob hot+cold directly into simulation/training",
        "never treat physical path as the unique dataset identity",
        "be deterministic for the same manifest/catalog input",
        "read D/E data files",
        "connect to simulation",
        "connect to training",
        "copy files",
        "delete files",
        "candidate_delete_files = 0",
        "No delete is required now.",
        SELF_PATH,
    ]
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing spec fragment: {fragment}")
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


def _check_no_dataset_reader_opened(failures: list[str]) -> dict[str, Any]:
    suspicious_hits: list[str] = []
    for rel_path in [
        "btcts_next/src/btcts/collector_vnext/archive/copy_manifest.py",
        "btcts_next/src/btcts/apps/operator_ui/hot_cold_retention_safety_service.py",
    ]:
        text = _read(rel_path)
        for token in [
            "logical_dataset_view",
            "read_parquet(",
            "read_json(",
            "rglob(\"*.parquet\")",
            "rglob(\"*.jsonl\")",
        ]:
            if token in text:
                suspicious_hits.append(f"{rel_path}:{token}")
    if suspicious_hits:
        failures.append("dataset reader/model must not be opened in entry-only slice: " + ", ".join(suspicious_hits))
    return {"suspicious_hits": suspicious_hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "copy_manifest_close_guard": _run_json_guard(COPY_MANIFEST_CLOSE_GUARD_PATH, failures),
        "spec": _check_spec(failures),
        "latest_10day_plan": _check_latest_10day_plan(failures),
        "no_dataset_reader_opened": _check_no_dataset_reader_opened(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_entry_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
