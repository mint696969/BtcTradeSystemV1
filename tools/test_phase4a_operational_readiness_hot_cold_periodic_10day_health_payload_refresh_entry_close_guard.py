# path: ./tools/test_phase4a_operational_readiness_hot_cold_periodic_10day_health_payload_refresh_entry_close_guard.py
# desc: Close guard for Phase 4-A periodic 10-day Health payload refresh entry. No scheduler/runtime/copy/delete/GC.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_periodic_10day_health_payload_refresh_entry_close_guard.py"
ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_periodic_10day_health_payload_refresh_entry_guard.py"
LOW_LOAD_ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_low_load_copy_scheduler_entry_guard.py"
DUP_DATASET_ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_duplicate_safe_dataset_view_entry_guard.py"
HEALTH_PAYLOAD_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_10day_plan_summary_health_payload_guard.py"
HEALTH_SERVICE_PATH = "btcts_next/src/btcts/apps/operator_ui/hot_cold_retention_safety_service.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_PERIODIC_10DAY_HEALTH_PAYLOAD_REFRESH_ENTRY_2026-06-02.md"
PLAN_SUMMARY_PATH = "tmp/work/operator_operational_readiness/outputs/hot_cold_10day_dry_run_plan_and_review_v1_20260602T140216.582610Z.json"
EXPECTED_PLAN_HASH = "e5bf5d3c6630c10084fc44c97614dc48c3bc4e8147e98683831eefa2923f9eb6"

COMPILE_FILES = [
    SELF_PATH,
    ENTRY_GUARD_PATH,
    LOW_LOAD_ENTRY_GUARD_PATH,
    DUP_DATASET_ENTRY_GUARD_PATH,
    HEALTH_PAYLOAD_GUARD_PATH,
    HEALTH_SERVICE_PATH,
]

FORBIDDEN_SERVICE_TOKENS = [
    "--execute",
    "archive_gc_enable",
    "run_periodic_10day_refresh",
    "schedule.every",
    "APScheduler",
    "streamlit_autorefresh",
    "shutil.copy",
    "copy2(",
    "copytree(",
    ".unlink(",
    ".rmdir(",
    "os.remove(",
    "os.unlink(",
    "os.rmdir(",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_periodic_10day_health_payload_refresh_entry_close"
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
        "stdout_tail": (proc.stdout or "")[-1800:],
        "stderr_tail": (proc.stderr or "")[-1800:],
    }


def _check_spec(failures: list[str]) -> dict[str, Any]:
    text = _read(SPEC_PATH)
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
        "Health read only the bounded summary JSON",
        "fresh: summary age <= 24h",
        "stale: summary age > 24h and <= 72h",
        "expired_or_unknown: summary age > 72h or missing",
        ENTRY_GUARD_PATH,
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"periodic 10-day close spec missing fragment: {fragment}")
    return {"missing": missing}


def _check_health_service_boundary(failures: list[str]) -> dict[str, Any]:
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
    missing = [fragment for fragment in required if fragment not in text]
    forbidden_hits = [token for token in FORBIDDEN_SERVICE_TOKENS if token in text]
    for fragment in missing:
        failures.append(f"Health service missing periodic refresh close anchor: {fragment}")
    for token in forbidden_hits:
        failures.append(f"Health service must not open runtime/copy/delete behavior: {token}")
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
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "entry_guard": _run_json_guard(ENTRY_GUARD_PATH, failures),
        "health_payload_guard": _run_json_guard(HEALTH_PAYLOAD_GUARD_PATH, failures),
        "low_load_entry_guard": {"verified_via_entry_guard": True, "path": LOW_LOAD_ENTRY_GUARD_PATH},
        "duplicate_safe_entry_guard": {"verified_via_entry_guard": True, "path": DUP_DATASET_ENTRY_GUARD_PATH},
        "spec": _check_spec(failures),
        "health_service_boundary": _check_health_service_boundary(failures),
        "latest_10day_plan": _check_latest_10day_plan(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_periodic_10day_health_payload_refresh_entry_close_guard",
        "close_status": "closed" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
