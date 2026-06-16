# path: ./tools/test_phase4a_operational_readiness_hot_cold_10day_retention_health_safety_entry_guard.py
# desc: Phase 4-A 10-day hot retention + Health safety summary entry guard. No delete.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_10day_retention_health_safety_entry_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_10DAY_RETENTION_HEALTH_SAFETY_ENTRY_2026-06-02.md"
HEALTH_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"
DRY_RUN_ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_dry_run_plan_entry_criteria_guard.py"
SMALL_BATCH_ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_small_batch_delete_entry_criteria_guard.py"
PRE_EXEC_VERIFY_OUTPUT_PATH = "tmp/work/operator_operational_readiness/outputs/hot_cold_first_batch_pre_execute_verification_v1_20260602T064046.474691Z.json"
PREVIOUS_PLAN_HASH = "d70a1c26dc5195a202e5da0bd4531e86168fb5e8d8a5f63c3bfa193448c09755"
MIN_RETENTION_HOURS = 240.0


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_10day_retention_health_safety_entry"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=600)
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
        "Operational readiness hot/cold 10-day retention and Health safety entry",
        "D:\\btc_ts_hot keeps the most recent 10 days of completed data.",
        "min_age_hours = 240",
        "hot_retention_days = 10",
        "Files older than 10 days may become delete candidates only after cold verification.",
        "Files currently being written, incomplete files, temporary files, partial files, and unstable-size files",
        "bounded batches",
        "resumable manifests",
        "throttling/sleep between operations",
        "Simulation, replay, virtual trading, and training must not double-count duplicate physical copies",
        "logical dataset view / manifest / catalog",
        "previous_first_batch_action = abandon_for_execute_under_10_day_policy",
        "Hot/Cold retention safety",
        "Do not scan D/E from the Health render path.",
        SELF_PATH,
    ]
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing spec fragment: {fragment}")
    return {"missing": missing}


def _check_current_health_safety_display_boundary(failures: list[str]) -> dict[str, Any]:
    health = _read(HEALTH_PAGE_PATH)
    health_service = _read("btcts_next/src/btcts/apps/operator_ui/health_data_service.py")
    safety_service = _read("btcts_next/src/btcts/apps/operator_ui/hot_cold_retention_safety_service.py")
    panel = _read("btcts_next/src/btcts/apps/operator_ui/components/hot_cold_retention_safety_panel.py")
    required = {
        HEALTH_PAGE_PATH: [
            "render_hot_cold_retention_safety_panel",
            "_snapshot_hot_cold_retention_safety_payload",
            'health_widget_slot("hot_cold_retention_safety_panel")',
        ],
        "btcts_next/src/btcts/apps/operator_ui/health_data_service.py": [
            "load_hot_cold_retention_safety_payload",
            '"operational_readiness_hot_cold_retention_safety"',
        ],
        "btcts_next/src/btcts/apps/operator_ui/hot_cold_retention_safety_service.py": [
            "HOT_RETENTION_DAYS = 10",
            "MIN_DELETE_AGE_HOURS = 240.0",
            "not_filesystem_scan",
            "not_copy_executor",
            "not_delete_executor",
        ],
        "btcts_next/src/btcts/apps/operator_ui/components/hot_cold_retention_safety_panel.py": [
            "render_hot_cold_retention_safety_panel",
            "not_filesystem_scan",
            "not_copy_executor",
            "not_delete_executor",
        ],
    }
    text_by_path = {
        HEALTH_PAGE_PATH: health,
        "btcts_next/src/btcts/apps/operator_ui/health_data_service.py": health_service,
        "btcts_next/src/btcts/apps/operator_ui/hot_cold_retention_safety_service.py": safety_service,
        "btcts_next/src/btcts/apps/operator_ui/components/hot_cold_retention_safety_panel.py": panel,
    }
    forbidden = [
        "rglob(",
        "glob(",
        "os.scandir(",
        "build_explicit_hot_cold_delete_plan",
        "shutil.rmtree(",
        ".unlink(",
        ".rmdir(",
        "os.remove(",
        "os.unlink(",
        "os.rmdir(",
        "archive_gc_enable",
        "run_explicit_hot_cold_small_batch_delete",
        "D:" + "\\",
        "E:" + "\\",
    ]
    missing: list[dict[str, str]] = []
    forbidden_hits: list[dict[str, str]] = []
    for rel_path, fragments in required.items():
        text = text_by_path[rel_path]
        for fragment in fragments:
            if fragment not in text:
                missing.append({"path": rel_path, "fragment": fragment})
                failures.append(f"Health safety display boundary missing fragment: {rel_path}: {fragment}")
        for token in forbidden:
            if token in text:
                forbidden_hits.append({"path": rel_path, "token": token})
                failures.append(f"Health safety display boundary contains forbidden runtime token: {rel_path}: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _check_previous_pre_execute_is_blocked_by_10day_policy(failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / PRE_EXEC_VERIFY_OUTPUT_PATH
    if not path.exists():
        failures.append(f"pre-execute verification output missing: {PRE_EXEC_VERIFY_OUTPUT_PATH}")
        return {"exists": False}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"pre-execute verification output unreadable: {exc}")
        return {"exists": True, "json_ok": False}
    counts = data.get("counts") or {}
    stdout_tail = str(data.get("stdout_tail") or "")
    if data.get("plan_hash") != PREVIOUS_PLAN_HASH:
        failures.append("previous pre-execute plan_hash mismatch")
    if data.get("execute") is not False or data.get("dry_run") is not True:
        failures.append("previous pre-execute verification must be dry-run only")
    if int(counts.get("deleted_files") or 0) != 0:
        failures.append("previous pre-execute verification must have deleted_files=0")
    if int(counts.get("selected_files") or 0) != 4:
        failures.append("previous pre-execute selected_files expected 4")

    # The selected rows are in the small-batch output path referenced by this verification.
    small_batch_path_raw = str(data.get("small_batch_output_path") or "")
    small_batch_path = Path(small_batch_path_raw)
    if not small_batch_path.exists():
        failures.append(f"referenced small-batch dry-run output missing: {small_batch_path_raw}")
        return {"exists": True, "small_batch_exists": False, "counts": counts, "stdout_tail": stdout_tail[-800:]}
    try:
        small = json.loads(small_batch_path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"small-batch dry-run output unreadable: {exc}")
        return {"exists": True, "small_batch_exists": True, "json_ok": False}
    ages = [float(row.get("age_hours_now") or 0.0) for row in (small.get("preflight_rows") or [])]
    min_age = min(ages) if ages else 0.0
    blocked_under_10d = min_age < MIN_RETENTION_HOURS
    if not blocked_under_10d:
        failures.append("previous first batch is not demonstrably below 10-day threshold; expected it to be blocked")
    return {
        "exists": True,
        "small_batch_exists": True,
        "previous_plan_hash": data.get("plan_hash"),
        "selected_files": counts.get("selected_files"),
        "deleted_files": counts.get("deleted_files"),
        "min_selected_age_hours": round(min_age, 3),
        "required_min_age_hours": MIN_RETENTION_HOURS,
        "blocked_under_10day_policy": blocked_under_10d,
    }


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "dry_run_entry_guard": _run_json_guard(DRY_RUN_ENTRY_GUARD_PATH, failures),
        "small_batch_entry_guard": _run_json_guard(SMALL_BATCH_ENTRY_GUARD_PATH, failures),
        "spec": _check_spec(failures),
        "current_health_safety_display_boundary": _check_current_health_safety_display_boundary(failures),
        "previous_pre_execute_blocked_by_10day_policy": _check_previous_pre_execute_is_blocked_by_10day_policy(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_10day_retention_health_safety_entry_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
