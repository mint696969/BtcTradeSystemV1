# path: ./tools/test_phase4a_operational_readiness_hot_cold_safety_thread_close_guard.py
# desc: Close current Hot/Cold safety thread after final 3 safe entries. No copy/delete executor.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_safety_thread_close_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_SAFETY_THREAD_CLOSE_2026-06-02.md"
DUP_DATASET_ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_entry_guard.py"
LOW_LOAD_ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_low_load_copy_scheduler_entry_guard.py"
PERIODIC_REFRESH_ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_periodic_10day_health_payload_refresh_entry_guard.py"
HEALTH_PAYLOAD_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_10day_plan_summary_health_payload_guard.py"
COPY_MANIFEST_WRITER_CLOSE_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_copy_manifest_writer_dry_run_close_guard.py"
PRIMARY_COMPACT_PATH = "tmp/work/phase4a_health_warroom_evidence_consumption_ui_rendering/run_primary_guard_compact_v1.py"
PLAN_SUMMARY_PATH = "tmp/work/operator_operational_readiness/outputs/hot_cold_10day_dry_run_plan_and_review_v1_20260602T140216.582610Z.json"
EXPECTED_PLAN_HASH = "e5bf5d3c6630c10084fc44c97614dc48c3bc4e8147e98683831eefa2923f9eb6"

FORBIDDEN_REPO_TOKENS = [
    "archive_gc_enable=True",
    "gc_enabled=True",
    "--execute",
    "DELETE_D_HOT_BATCH_e5bf5d3c",
    "execute_delete",
    "execute_hot_delete",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_safety_thread_close"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str], *, timeout: int = 1200) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=timeout)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1800:], "stderr_tail": (proc.stderr or "")[-1800:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "stdout_tail": (proc.stdout or "")[-1800:], "stderr_tail": (proc.stderr or "")[-1800:]}


def _run_primary_compact(failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / PRIMARY_COMPACT_PATH)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=3600)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"primary compact did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1800:], "stderr_tail": (proc.stderr or "")[-1800:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failed_guard_count") == 0 and parsed.get("top_failure_count") == 0
    if not ok:
        failures.append("primary compact must be ok with no failed guards")
    return {"ok": ok, "returncode": proc.returncode, "failed_guard_count": parsed.get("failed_guard_count"), "top_failure_count": parsed.get("top_failure_count"), "failed_guards": parsed.get("failed_guards"), "json_path": parsed.get("json_path"), "log_path": parsed.get("log_path")}


def _check_spec(failures: list[str]) -> dict[str, Any]:
    required = [
        "Hot/Cold safety thread close",
        "977436f0 Hot/Cold retention safety Health display",
        "4a2fc643 Hot/Cold 10-day plan summary Health payload",
        "2d91e90e Hot/Cold copy manifest model",
        "3635722a Hot/Cold copy manifest writer dry-run",
        "Hot/Cold duplicate-safe logical dataset view entry criteria",
        "Hot/Cold low-load copy scheduler entry criteria",
        "Hot/Cold periodic 10-day Health payload refresh entry criteria",
        "candidate_delete_files = 0",
        "No delete is required now.",
        "Health uses bounded precomputed payload only and does not scan D/E.",
        "Old 48h-style first batch is abandoned for execute.",
        "Simulation/training/replay must use duplicate-safe logical identity",
        "Low-load copy scheduler must be bounded/throttled/resumable and remains design-only.",
        "Periodic 10-day Health payload refresh must run outside UI/render path and dry-run only.",
        "copy executor",
        "delete executor",
        "archive GC enablement",
        "production manifest writer",
        "scheduler runtime loop",
        "Return to the main roadmap",
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
        and float(too_new.get("gb") or 0.0) >= 126.0
        and data.get("no_delete_no_unlink_no_rmdir") is True
    )
    if not ok:
        failures.append("latest 10-day plan summary must remain zero-candidate/no-delete")
    return {"ok": ok, "plan_hash": data.get("plan_hash"), "candidate_delete_files": data.get("candidate_delete_files"), "too_new": too_new}


def _check_no_executor_opened(failures: list[str]) -> dict[str, Any]:
    hits: list[str] = []
    for rel_path in [
        "btcts_next/src/btcts/collector_vnext/archive/config.py",
        "btcts_next/src/btcts/collector_vnext/archive/copy_manifest.py",
        "btcts_next/src/btcts/apps/operator_ui/hot_cold_retention_safety_service.py",
        "btcts_next/src/btcts/apps/operator_ui/views/health_page.py",
    ]:
        text = _read(rel_path)
        for token in FORBIDDEN_REPO_TOKENS:
            if token in text:
                hits.append(f"{rel_path}:{token}")
                failures.append(f"forbidden executor/delete token opened: {rel_path}: {token}")
    return {"hits": hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "duplicate_safe_dataset_view_entry_guard": _run_json_guard(DUP_DATASET_ENTRY_GUARD_PATH, failures),
        "low_load_copy_scheduler_entry_guard": _run_json_guard(LOW_LOAD_ENTRY_GUARD_PATH, failures),
        "periodic_10day_health_payload_refresh_entry_guard": _run_json_guard(PERIODIC_REFRESH_ENTRY_GUARD_PATH, failures),
        "health_payload_guard": _run_json_guard(HEALTH_PAYLOAD_GUARD_PATH, failures),
        "copy_manifest_writer_close_guard": _run_json_guard(COPY_MANIFEST_WRITER_CLOSE_GUARD_PATH, failures),
        "spec": _check_spec(failures),
        "latest_10day_plan": _check_latest_10day_plan(failures),
        "no_executor_opened": _check_no_executor_opened(failures),
        "primary_compact": _run_primary_compact(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_safety_thread_close_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
