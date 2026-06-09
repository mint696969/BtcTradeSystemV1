# path: ./tools/test_phase4a_operational_readiness_hot_cold_copy_correctness_manifest_entry_close_guard.py
# desc: Close guard for Phase 4-A Hot/Cold copy correctness manifest entry criteria. No copy/delete/GC/scheduler runtime.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_copy_correctness_manifest_entry_close_guard.py"
ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_copy_correctness_manifest_entry_guard.py"
HEALTH_PAYLOAD_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_10day_plan_summary_health_payload_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_COPY_CORRECTNESS_MANIFEST_ENTRY_2026-06-02.md"
PLAN_SUMMARY_PATH = "tmp/work/operator_operational_readiness/outputs/hot_cold_10day_dry_run_plan_and_review_v1_20260602T140216.582610Z.json"
EXPECTED_PLAN_HASH = "e5bf5d3c6630c10084fc44c97614dc48c3bc4e8147e98683831eefa2923f9eb6"

COMPILE_FILES = [
    SELF_PATH,
    ENTRY_GUARD_PATH,
    HEALTH_PAYLOAD_GUARD_PATH,
]

FORBIDDEN_REPO_TOKENS = [
    "hot_cold_copy_executor",
    "archive_gc_enable",
    "shutil.rmtree(",
    "send2trash",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_copy_correctness_manifest_entry_close"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str], *, timeout: int = 1800) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=timeout)
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
        "Hot/Cold copy correctness manifest entry criteria",
        "schema_version = hot_cold_copy_manifest_v1",
        "copy_intent = hot_to_cold_archive_copy",
        "rel_file is relative, normalized, and cannot escape root",
        "rel_prefix is one of data/market_data or data/collector_raw",
        "hot_size_bytes == cold_size_bytes",
        "hash_algorithm is sha256, blake3, or none_with_size_only_marker",
        "if hash is present: hot_hash == cold_hash",
        "copy_completed_at_utc is present",
        "verification_completed_at_utc is present",
        "size_stable_across_two_observations = true",
        "minimum_stability_seconds >= 60",
        "bounded batches",
        "resume from manifest",
        "atomic cold write through temporary path then rename",
        "logical dataset view",
        "Do not copy files.",
        "Do not delete files.",
        ENTRY_GUARD_PATH,
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"copy correctness entry close spec missing fragment: {fragment}")
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
        and float(too_new.get("gb") or 0.0) >= 126.0
        and data.get("no_delete_no_unlink_no_rmdir") is True
    )
    if not ok:
        failures.append("latest 10-day plan summary must remain zero-candidate/no-delete")
    return {"ok": ok, "plan_hash": data.get("plan_hash"), "candidate_delete_files": data.get("candidate_delete_files"), "too_new": too_new}


def _check_no_executor_opened(failures: list[str]) -> dict[str, Any]:
    hits: list[str] = []
    for rel_path in [
        "btcts_next/src/btcts/apps/operator_ui/hot_cold_retention_safety_service.py",
        "btcts_next/src/btcts/apps/operator_ui/health_data_service.py",
    ]:
        text = _read(rel_path)
        for token in FORBIDDEN_REPO_TOKENS:
            if token in text:
                hits.append(f"{rel_path}:{token}")
    if hits:
        failures.append("copy correctness entry close must not open executor/delete tokens")
    return {"hits": hits}


def _check_entry_boundary(entry_result: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    parsed = entry_result.get("json") if isinstance(entry_result, dict) else None
    checks = parsed.get("checks") if isinstance(parsed, dict) else None
    boundary = checks.get("no_executor_opened") if isinstance(checks, dict) else None
    hits = boundary.get("hits") if isinstance(boundary, dict) else None
    ok = hits == []
    if not ok:
        failures.append("copy correctness entry guard must report no executor/delete hits")
    return {
        "ok": ok,
        "verified_by_entry_guard": True,
        "hits": hits,
        "path": ENTRY_GUARD_PATH,
    }


def main() -> int:
    failures: list[str] = []
    entry_guard = _run_json_guard(ENTRY_GUARD_PATH, failures)
    checks = {
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "entry_guard": entry_guard,
        "health_payload_guard": _run_json_guard(HEALTH_PAYLOAD_GUARD_PATH, failures),
        "spec": _check_spec(failures),
        "latest_10day_plan": _check_latest_10day_plan(failures),
        "no_executor_opened": _check_no_executor_opened(failures),
        "entry_boundary": _check_entry_boundary(entry_guard, failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_copy_correctness_manifest_entry_close_guard",
        "close_status": "closed" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
