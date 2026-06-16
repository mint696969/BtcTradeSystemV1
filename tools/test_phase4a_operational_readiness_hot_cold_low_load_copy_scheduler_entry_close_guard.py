# path: ./tools/test_phase4a_operational_readiness_hot_cold_low_load_copy_scheduler_entry_close_guard.py
# desc: Close guard for Phase 4-A low-load Hot/Cold copy scheduler entry. No scheduler runtime/copy/delete/GC.

from __future__ import annotations

import json
import os
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_low_load_copy_scheduler_entry_close_guard.py"
ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_low_load_copy_scheduler_entry_guard.py"
DUP_DATASET_ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_entry_guard.py"
COPY_MANIFEST_CLOSE_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_writer_dry_run_close_guard.py"
ARCHIVE_CONFIG_PATH = "btcts_next/src/btcts/collector_vnext/archive/config.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_LOW_LOAD_COPY_SCHEDULER_ENTRY_2026-06-02.md"
PLAN_SUMMARY_PATH = "tmp/work/operator_operational_readiness/outputs/hot_cold_10day_dry_run_plan_and_review_v1_20260602T140216.582610Z.json"
EXPECTED_PLAN_HASH = "e5bf5d3c6630c10084fc44c97614dc48c3bc4e8147e98683831eefa2923f9eb6"

COMPILE_FILES = [
    SELF_PATH,
    ENTRY_GUARD_PATH,
    DUP_DATASET_ENTRY_GUARD_PATH,
    COPY_MANIFEST_CLOSE_GUARD_PATH,
    ARCHIVE_CONFIG_PATH,
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_low_load_copy_scheduler_entry_close"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str], *, skip_primary_compact_guard: bool = False) -> dict[str, Any]:
    env = os.environ.copy()
    if skip_primary_compact_guard:
        env["BTCTS_HOT_COLD_SKIP_PRIMARY_COMPACT_GUARD"] = "1"
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / rel_path)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=1800,
        env=env,
    )
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1800:], "stderr_tail": (proc.stderr or "")[-1800:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {
        "ok": ok,
        "returncode": proc.returncode,
        "phase": parsed.get("phase"),
        "json": parsed,
        "stdout_tail": (proc.stdout or "")[-1800:],
        "stderr_tail": (proc.stderr or "")[-1800:],
    }


def _check_spec(failures: list[str]) -> dict[str, Any]:
    text = _read(SPEC_PATH)
    required = [
        "Hot/Cold low-load copy scheduler entry criteria",
        "run outside Health render path",
        "use bounded scan batches",
        "use max_files_per_cycle",
        "use max_bytes_per_cycle",
        "sleep/throttle between file copies",
        "support resume from manifest/catalog state",
        "prefer incremental planning over full D/E recursive scans",
        "avoid copying files younger than stable_age_sec",
        "surface summary to Health from precomputed payload only",
        "max_files_per_cycle <= 64",
        "max_bytes_per_cycle <= 256 MiB",
        "stable_age_sec >= 3600",
        "scan_interval_sec >= 30",
        "copy files",
        "delete files",
        "enable archive GC",
        "open scheduler runtime loop",
        ENTRY_GUARD_PATH,
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"low-load close spec missing fragment: {fragment}")
    return {"missing": missing}


def _check_archive_config_anchors(failures: list[str]) -> dict[str, Any]:
    text = _read(ARCHIVE_CONFIG_PATH)
    required = [
        "scan_interval_sec: int = 30",
        "stable_age_sec: int = 3600",
        "copy_min_age_days: int = 1",
        "max_files_per_cycle: int = 64",
        "max_bytes_per_cycle: int = 256 * 1024 * 1024",
        "gc_enabled: bool = False",
        "gc_dry_run: bool = True",
        "max(10, env_int(\"BTCTS_ARCHIVE_SCAN_INTERVAL_SEC\", 30))",
        "max(1800, env_int(\"BTCTS_ARCHIVE_STABLE_AGE_SEC\", 3600))",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"archive config missing low-load close anchor: {fragment}")
    return {"missing": missing}


def _check_entry_boundary(entry_result: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    parsed = entry_result.get("json") if isinstance(entry_result, dict) else None
    checks = parsed.get("checks") if isinstance(parsed, dict) else None
    boundary = checks.get("no_scheduler_runtime_opened") if isinstance(checks, dict) else None
    suspicious_hits = boundary.get("suspicious_hits") if isinstance(boundary, dict) else None
    ok = suspicious_hits == []
    if not ok:
        failures.append("low-load entry guard must report no scheduler runtime suspicious hits")
    return {
        "ok": ok,
        "verified_by_entry_guard": True,
        "suspicious_hits": suspicious_hits,
        "path": ENTRY_GUARD_PATH,
    }


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


def main() -> int:
    failures: list[str] = []
    entry_guard = _run_json_guard(ENTRY_GUARD_PATH, failures, skip_primary_compact_guard=True)
    checks = {
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "entry_guard": entry_guard,
        "duplicate_safe_entry_guard": {"verified_via_entry_guard": True, "path": DUP_DATASET_ENTRY_GUARD_PATH},
        "copy_manifest_close_guard": {"verified_via_entry_guard": True, "path": COPY_MANIFEST_CLOSE_GUARD_PATH},
        "spec": _check_spec(failures),
        "archive_config_anchors": _check_archive_config_anchors(failures),
        "latest_10day_plan": _check_latest_10day_plan(failures),
        "entry_boundary": _check_entry_boundary(entry_guard, failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_low_load_copy_scheduler_entry_close_guard",
        "close_status": "closed" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
