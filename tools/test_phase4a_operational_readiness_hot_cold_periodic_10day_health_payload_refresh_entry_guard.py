# path: ./tools/test_phase4a_operational_readiness_hot_cold_periodic_10day_health_payload_refresh_entry_guard.py
# desc: Phase 4-A periodic 10-day Health payload refresh entry guard. No scheduler/runtime/copy/delete.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_periodic_10day_health_payload_refresh_entry_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_PERIODIC_10DAY_HEALTH_PAYLOAD_REFRESH_ENTRY_2026-06-02.md"
LOW_LOAD_ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_low_load_copy_scheduler_entry_guard.py"
DUP_DATASET_ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_entry_guard.py"
HEALTH_PAYLOAD_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_10day_plan_summary_health_payload_guard.py"
HEALTH_SERVICE_PATH = "btcts_next/src/btcts/apps/operator_ui/hot_cold_retention_safety_service.py"
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_periodic_10day_health_payload_refresh_entry"
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
        "Hot/Cold periodic 10-day Health payload refresh entry criteria",
        "TEN_DAY_PLAN_REVIEW_OUTPUT_REL",
        "load_hot_cold_retention_safety_payload()",
        "run outside Health render path",
        "run outside Streamlit fragment rendering",
        "produce a bounded precomputed JSON summary",
        "use min_age_hours = 240",
        "use hot_retention_days = 10",
        "be dry-run only",
        "set no_delete_no_unlink_no_rmdir = true",
        "never pass --execute",
        "never delete files",
        "never copy files",
        "never enable archive GC",
        "write output atomically",
        "Health read only the bounded summary JSON",
        "fresh: summary age <= 24h",
        "stale: summary age > 24h and <= 72h",
        "expired_or_unknown: summary age > 72h or missing",
        "candidate_delete_files = 0 -> status=safe_no_delete_candidates",
        "candidate_delete_files > 0 -> status=review_required",
        "summary missing -> status=unknown",
        "summary stale -> status=stale",
        "No Health status may mean automatic delete is allowed.",
        "Hot/Cold duplicate-safe logical dataset view entry criteria",
        "Hot/Cold low-load copy scheduler entry criteria",
        "run a periodic scheduler",
        "modify Streamlit render loop",
        "scan D/E recursively",
        "copy files",
        "delete files",
        SELF_PATH,
    ]
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing spec fragment: {fragment}")
    return {"missing": missing}


def _check_health_service_current_anchor(failures: list[str]) -> dict[str, Any]:
    text = _read(HEALTH_SERVICE_PATH)
    required = [
        "TEN_DAY_PLAN_REVIEW_OUTPUT_REL",
        "hot_cold_10day_dry_run_plan_and_review_v1_20260602T140216.582610Z.json",
        "def load_hot_cold_retention_safety_payload",
        "Does not scan D/E.",
        "not_filesystem_scan",
        "not_copy_executor",
        "not_delete_executor",
        "no_double_count_hot_cold_for_simulation_training",
    ]
    forbidden = [
        "--execute",
        "archive_gc_enable",
        "run_periodic_10day_refresh",
        "schedule.every",
        "APScheduler",
        "streamlit_autorefresh",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    forbidden_hits = [fragment for fragment in forbidden if fragment in text]
    for fragment in missing:
        failures.append(f"Health service missing safe current anchor: {fragment}")
    for fragment in forbidden_hits:
        failures.append(f"Health service must not open runtime refresh/delete behavior: {fragment}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


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
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "duplicate_safe_dataset_view_entry_guard": _run_json_guard(DUP_DATASET_ENTRY_GUARD_PATH, failures),
        "low_load_copy_scheduler_entry_guard": _run_json_guard(LOW_LOAD_ENTRY_GUARD_PATH, failures),
        "health_payload_guard": _run_json_guard(HEALTH_PAYLOAD_GUARD_PATH, failures),
        "spec": _check_spec(failures),
        "health_service_current_anchor": _check_health_service_current_anchor(failures),
        "latest_10day_plan": _check_latest_10day_plan(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_periodic_10day_health_payload_refresh_entry_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
