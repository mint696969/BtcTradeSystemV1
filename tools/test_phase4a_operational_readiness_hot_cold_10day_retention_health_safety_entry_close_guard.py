# path: ./tools/test_phase4a_operational_readiness_hot_cold_10day_retention_health_safety_entry_close_guard.py
# desc: Close guard for Phase 4-A 10-day hot retention Health safety entry. No D/E scan/copy/delete/GC.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_10day_retention_health_safety_entry_close_guard.py"
ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_10day_retention_health_safety_entry_guard.py"
DRY_RUN_CLOSE_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_dry_run_plan_entry_close_guard.py"
PAYLOAD_CLOSE_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_10day_plan_summary_health_payload_close_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_10DAY_RETENTION_HEALTH_SAFETY_ENTRY_2026-06-02.md"
PRE_EXEC_VERIFY_OUTPUT_PATH = "tmp/work/operator_operational_readiness/outputs/hot_cold_first_batch_pre_execute_verification_v1_20260602T064046.474691Z.json"
PREVIOUS_PLAN_HASH = "d70a1c26dc5195a202e5da0bd4531e86168fb5e8d8a5f63c3bfa193448c09755"
MIN_RETENTION_HOURS = 240.0

COMPILE_FILES = [
    SELF_PATH,
    ENTRY_GUARD_PATH,
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_10day_retention_health_safety_entry_close"
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
        "Operational readiness hot/cold 10-day retention and Health safety entry",
        "min_age_hours = 240",
        "hot_retention_days = 10",
        "previous_first_batch_action = abandon_for_execute_under_10_day_policy",
        "Hot/Cold retention safety",
        "Do not scan D/E from the Health render path.",
        ENTRY_GUARD_PATH,
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"10-day retention Health safety close spec missing fragment: {fragment}")
    return {"missing": missing}


def _check_previous_pre_execute_is_blocked(failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / PRE_EXEC_VERIFY_OUTPUT_PATH
    if not path.exists():
        failures.append(f"pre-execute verification output missing: {PRE_EXEC_VERIFY_OUTPUT_PATH}")
        return {"exists": False}
    data = json.loads(path.read_text(encoding="utf-8"))
    counts = data.get("counts") or {}
    small_batch_path_raw = str(data.get("small_batch_output_path") or "")
    small_batch_path = Path(small_batch_path_raw)
    ages: list[float] = []
    if small_batch_path.exists():
        small = json.loads(small_batch_path.read_text(encoding="utf-8"))
        ages = [float(row.get("age_hours_now") or 0.0) for row in (small.get("preflight_rows") or [])]
    min_age = min(ages) if ages else 0.0
    ok = (
        data.get("plan_hash") == PREVIOUS_PLAN_HASH
        and data.get("execute") is False
        and data.get("dry_run") is True
        and int(counts.get("deleted_files") or 0) == 0
        and int(counts.get("selected_files") or 0) == 4
        and min_age < MIN_RETENTION_HOURS
    )
    if not ok:
        failures.append("previous first batch must remain dry-run and blocked under 10-day retention policy")
    return {
        "ok": ok,
        "previous_plan_hash": data.get("plan_hash"),
        "selected_files": counts.get("selected_files"),
        "deleted_files": counts.get("deleted_files"),
        "min_selected_age_hours": round(min_age, 3),
        "required_min_age_hours": MIN_RETENTION_HOURS,
    }


def _check_entry_boundary(entry_result: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    parsed = entry_result.get("json") if isinstance(entry_result, dict) else None
    checks = parsed.get("checks") if isinstance(parsed, dict) else None
    health = checks.get("current_health_safety_display_boundary") if isinstance(checks, dict) else None
    previous = checks.get("previous_pre_execute_blocked_by_10day_policy") if isinstance(checks, dict) else None
    ok = (
        isinstance(health, dict)
        and health.get("missing") == []
        and health.get("forbidden_hits") == []
        and isinstance(previous, dict)
        and previous.get("blocked_under_10day_policy") is True
    )
    if not ok:
        failures.append("10-day retention Health safety entry guard must prove display boundary and previous first batch block")
    return {"ok": ok, "health_boundary": health, "previous_pre_execute": previous, "path": ENTRY_GUARD_PATH}


def main() -> int:
    failures: list[str] = []
    entry_guard = _run_json_guard(ENTRY_GUARD_PATH, failures)
    checks = {
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "entry_guard": entry_guard,
        "dry_run_plan_entry_close_guard": _run_json_guard(DRY_RUN_CLOSE_GUARD_PATH, failures),
        "ten_day_payload_close_guard": _run_json_guard(PAYLOAD_CLOSE_GUARD_PATH, failures),
        "retention_safety_health_display_boundary": {"verified_via_entry_guard": True, "path": ENTRY_GUARD_PATH},
        "spec": _check_spec(failures),
        "previous_pre_execute_blocked": _check_previous_pre_execute_is_blocked(failures),
        "entry_boundary": _check_entry_boundary(entry_guard, failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_10day_retention_health_safety_entry_close_guard",
        "close_status": "closed" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
