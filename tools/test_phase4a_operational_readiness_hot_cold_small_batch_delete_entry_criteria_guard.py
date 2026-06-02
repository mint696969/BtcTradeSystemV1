# path: ./tools/test_phase4a_operational_readiness_hot_cold_small_batch_delete_entry_criteria_guard.py
# desc: Phase 4-A hot/cold small-batch guarded delete entry criteria guard. No execute.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_small_batch_delete_entry_criteria_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_SMALL_BATCH_GUARDED_DELETE_ENTRY_CRITERIA_2026-06-01.md"
ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_dry_run_plan_entry_criteria_guard.py"
SMALL_BATCH_PATH = "tmp/work/operator_operational_readiness/run_explicit_hot_cold_small_batch_delete_v1.py"
REVIEWER_PATH = "tmp/work/operator_operational_readiness/review_explicit_hot_cold_delete_plan_v1.py"
HANDOFF_PATH = "tmp/gpt_room/memory/handoffs/2026-06-01_hot_cold_retention_dry_run_plan_review_handoff.md"
PLAN_PATH = "tmp/work/operator_operational_readiness/outputs/explicit_hot_cold_delete_plan_dry_run_v1_20260601T210715.707697Z_d70a1c26dc5195a2.json"
EXPECTED_PLAN_HASH = "d70a1c26dc5195a202e5da0bd4531e86168fb5e8d8a5f63c3bfa193448c09755"
EXPECTED_CONFIRM_TOKEN = "DELETE_D_HOT_BATCH_d70a1c26dc5195a2"

REQUIRED_SMALL_BATCH_FRAGMENTS = [
    "SCHEMA_VERSION = \"run_explicit_hot_cold_small_batch_delete_v1\"",
    "EXPECTED_PLAN_SCHEMA = \"build_explicit_hot_cold_delete_plan_dry_run_v1\"",
    "EXPECTED_PLAN_ACTION = \"build_delete_plan_only_no_delete_no_unlink_no_rmdir\"",
    "EXPECTED_ALLOWED_PREFIXES = [\"data/market_data\", \"data/collector_raw\"]",
    "EXPECTED_FORBIDDEN_PREFIXES = [\"state/collector_vnext\", \"logs/collector_vnext\"]",
    "Default is dry-run",
    "Execute requires plan hash and confirmation token",
    "--execute requires --expected-plan-hash",
    "--execute requires --confirm-delete",
    "DELETE_D_HOT_BATCH_",
    "preflight_only_no_delete",
    "guarded_small_batch_unlink",
    "hot_path.unlink()",
    "This script never deletes cold files and never removes directories.",
]

FORBIDDEN_SMALL_BATCH_TOKENS = [
    "shutil.rmtree(",
    ".rmdir(",
    "os.remove(",
    "os.unlink(",
    "os.rmdir(",
    "send2trash",
    "archive_gc_enable",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operational_readiness_hot_cold_small_batch_entry"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=300)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _check_spec(failures: list[str]) -> dict[str, Any]:
    required = [
        "Operational readiness hot/cold small-batch guarded delete entry criteria",
        EXPECTED_PLAN_HASH,
        EXPECTED_CONFIRM_TOKEN,
        "Do not pass --execute in this entry slice.",
        "Do not unlink files in this entry slice.",
        "Do not delete cold files.",
        "Do not remove directories.",
        "Do not delete state/collector_vnext.",
        "Do not delete logs/collector_vnext.",
        "Do not enable archive GC.",
        "post-delete audit",
        SELF_PATH,
    ]
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing spec fragment: {fragment}")
    return {"missing": missing}


def _check_handoff_and_plan(failures: list[str]) -> dict[str, Any]:
    handoff = _read(HANDOFF_PATH)
    missing_handoff = [fragment for fragment in [EXPECTED_PLAN_HASH, "candidate_delete_files = 28", "candidate_delete_gb = 66.426735", "dry_run_only = true", "no_delete_no_unlink_no_rmdir = true"] if fragment not in handoff]
    for fragment in missing_handoff:
        failures.append(f"handoff missing reviewed-plan fragment: {fragment}")
    plan_path = REPO_ROOT / PLAN_PATH
    if not plan_path.exists():
        failures.append(f"reviewed plan file missing: {PLAN_PATH}")
        return {"missing_handoff": missing_handoff, "plan_exists": False}
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"reviewed plan JSON unreadable: {exc}")
        return {"missing_handoff": missing_handoff, "plan_exists": True, "json_ok": False}
    if plan.get("plan_hash") != EXPECTED_PLAN_HASH:
        failures.append("reviewed plan_hash mismatch")
    counts = plan.get("counts") or {}
    if counts.get("candidate_delete_files") != 28:
        failures.append("reviewed plan candidate_delete_files mismatch")
    if round(float(counts.get("candidate_delete_gb") or 0.0), 6) != 66.426735:
        failures.append("reviewed plan candidate_delete_gb mismatch")
    return {"missing_handoff": missing_handoff, "plan_exists": True, "plan_hash": plan.get("plan_hash")}


def _check_small_batch_source(failures: list[str]) -> dict[str, Any]:
    text = _read(SMALL_BATCH_PATH)
    missing = [fragment for fragment in REQUIRED_SMALL_BATCH_FRAGMENTS if fragment not in text]
    forbidden_hits = [token for token in FORBIDDEN_SMALL_BATCH_TOKENS if token in text]
    for fragment in missing:
        failures.append(f"small-batch script missing required guard fragment: {fragment}")
    for token in forbidden_hits:
        failures.append(f"small-batch script contains forbidden token: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _run_reviewer_on_plan(failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / REVIEWER_PATH), str(REPO_ROOT / PLAN_PATH)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=300)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"reviewer did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == [] and parsed.get("plan_hash_ok") is True
    if not ok:
        failures.append("reviewer must accept reviewed plan with hash ok")
    return {"ok": ok, "returncode": proc.returncode, "plan_hash": parsed.get("plan_hash"), "counts": parsed.get("counts"), "warnings": parsed.get("warnings")}


def _run_small_batch_dry_run_preflight(failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / SMALL_BATCH_PATH),
            "--plan-path",
            str(REPO_ROOT / PLAN_PATH),
            "--expected-plan-hash",
            EXPECTED_PLAN_HASH,
            "--max-files",
            "4",
            "--max-gb",
            "10",
            "--order",
            "oldest-first",
        ],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=300,
    )
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"small-batch dry-run preflight did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}
    counts = parsed.get("counts") or {}
    ok = (
        proc.returncode == 0
        and parsed.get("ok") is True
        and parsed.get("execute") is False
        and parsed.get("dry_run") is True
        and parsed.get("action") == "preflight_only_no_delete"
        and parsed.get("plan_hash_ok") is True
        and parsed.get("required_execute_confirmation_token") == EXPECTED_CONFIRM_TOKEN
        and int(counts.get("deleted_files") or 0) == 0
        and int(counts.get("selected_files") or 0) > 0
        and int(counts.get("preflight_failed_files") or 0) == 0
    )
    if not ok:
        failures.append("small-batch dry-run preflight must be ok, execute false, deleted_files 0, preflight all ok")
    return {
        "ok": ok,
        "returncode": proc.returncode,
        "execute": parsed.get("execute"),
        "dry_run": parsed.get("dry_run"),
        "action": parsed.get("action"),
        "required_execute_confirmation_token": parsed.get("required_execute_confirmation_token"),
        "counts": counts,
        "failures": parsed.get("failures"),
        "warnings": parsed.get("warnings"),
        "output_path": parsed.get("output_path"),
    }


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_small_batch": _compile(SMALL_BATCH_PATH, failures),
        "compile_reviewer": _compile(REVIEWER_PATH, failures),
        "dry_run_plan_entry_guard": _run_json_guard(ENTRY_GUARD_PATH, failures),
        "spec": _check_spec(failures),
        "handoff_and_plan": _check_handoff_and_plan(failures),
        "small_batch_source": _check_small_batch_source(failures),
        "reviewer_on_plan": _run_reviewer_on_plan(failures),
        "small_batch_dry_run_preflight": _run_small_batch_dry_run_preflight(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_small_batch_delete_entry_criteria_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
