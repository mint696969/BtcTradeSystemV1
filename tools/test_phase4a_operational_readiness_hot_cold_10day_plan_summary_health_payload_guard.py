# path: ./tools/test_phase4a_operational_readiness_hot_cold_10day_plan_summary_health_payload_guard.py
# desc: Phase 4-A guard for using reviewed 10-day Hot/Cold plan summary in Health payload. No D/E scan, no copy/delete.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_10day_plan_summary_health_payload_guard.py"
CLOSE_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_safety_health_display_close_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_10DAY_PLAN_SUMMARY_HEALTH_PAYLOAD_2026-06-02.md"
SERVICE_PATH = "btcts_next/src/btcts/apps/operator_ui/hot_cold_retention_safety_service.py"
SERVICE_TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_hot_cold_retention_safety_service.py"
TEN_DAY_OUTPUT_PATH = "tmp/work/operator_operational_readiness/outputs/hot_cold_10day_dry_run_plan_and_review_v1_20260602T140216.582610Z.json"
TEN_DAY_PLAN_HASH = "e5bf5d3c6630c10084fc44c97614dc48c3bc4e8147e98683831eefa2923f9eb6"

FORBIDDEN_SERVICE_TOKENS = [
    "rglob(",
    "glob(",
    "os.scandir(",
    ".unlink(",
    ".rmdir(",
    "shutil.rmtree(",
    "os.remove(",
    "os.unlink(",
    "archive_gc_enable",
    "D:" + "\\",
    "E:" + "\\",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_10day_plan_summary_health_payload"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_plain_ok(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _check_spec(failures: list[str]) -> dict[str, Any]:
    required = [
        "Hot/Cold 10-day plan summary Health payload",
        TEN_DAY_OUTPUT_PATH,
        TEN_DAY_PLAN_HASH,
        "candidate_delete_files = 0",
        "too_new_files = 56",
        "status = safe_no_delete_candidates",
        "no_candidates_older_than_10_days",
        "does not",
        "scan D/E",
        "copy files",
        "delete files",
        SELF_PATH,
    ]
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing spec fragment: {fragment}")
    return {"missing": missing}


def _check_output_summary(failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / TEN_DAY_OUTPUT_PATH
    if not path.exists():
        failures.append(f"10-day output missing: {TEN_DAY_OUTPUT_PATH}")
        return {"exists": False}
    data = json.loads(path.read_text(encoding="utf-8"))
    too_new = ((data.get("review_exclusions") or {}).get("too_new") or {})
    ok = (
        data.get("ok") is True
        and data.get("plan_hash") == TEN_DAY_PLAN_HASH
        and float(data.get("min_age_hours") or 0.0) == 240.0
        and int(data.get("candidate_delete_files") or 0) == 0
        and float(data.get("candidate_delete_gb") or 0.0) == 0.0
        and int(too_new.get("files") or 0) == 56
        and float(too_new.get("gb") or 0.0) >= 126.0
        and data.get("no_delete_no_unlink_no_rmdir") is True
    )
    if not ok:
        failures.append("10-day output summary must be ok with zero candidates and too_new retention files")
    return {"ok": ok, "plan_hash": data.get("plan_hash"), "candidate_delete_files": data.get("candidate_delete_files"), "too_new": too_new}


def _check_service_source(failures: list[str]) -> dict[str, Any]:
    text = _read(SERVICE_PATH)
    required = [
        "TEN_DAY_PLAN_REVIEW_OUTPUT_REL",
        "hot_cold_10day_dry_run_plan_and_review_v1_20260602T140216.582610Z.json",
        "def _build_from_10day_review",
        "safe_no_delete_candidates",
        "no_candidates_older_than_10_days",
        "reviewed_10day_dry_run_plan",
        "No D-hot files are currently eligible for 10-day retention delete. Keep monitoring.",
        "too_new_files",
        "not_filesystem_scan",
        "not_copy_executor",
        "not_delete_executor",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    forbidden_hits = [token for token in FORBIDDEN_SERVICE_TOKENS if token in text]
    for fragment in missing:
        failures.append(f"service missing required 10-day summary fragment: {fragment}")
    for token in forbidden_hits:
        failures.append(f"service contains forbidden D/E scan/delete token: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _check_payload_probe(failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "-c", "from btcts.apps.operator_ui.hot_cold_retention_safety_service import load_hot_cold_retention_safety_payload; import json; print(json.dumps(load_hot_cold_retention_safety_payload(), ensure_ascii=False, sort_keys=True))"],
        cwd=str(REPO_ROOT / "btcts_next" / "src"),
        text=True,
        capture_output=True,
        timeout=120,
    )
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"payload probe did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}
    counts = parsed.get("counts") or {}
    ok = (
        parsed.get("status_key") == "safe_no_delete_candidates"
        and parsed.get("severity_key") == "info"
        and parsed.get("delete_readiness_key") == "no_candidates_older_than_10_days"
        and parsed.get("copy_verification_key") == "reviewed_10day_dry_run_plan"
        and counts.get("candidate_files") == 0
        and counts.get("too_new_files") == 56
        and (parsed.get("plan") or {}).get("plan_hash") == TEN_DAY_PLAN_HASH
        and (parsed.get("boundary") or {}).get("not_filesystem_scan") is True
        and (parsed.get("boundary") or {}).get("not_delete_executor") is True
    )
    if not ok:
        failures.append("payload must prefer latest reviewed 10-day zero-candidate plan summary")
    return {"ok": ok, "status_key": parsed.get("status_key"), "delete_readiness_key": parsed.get("delete_readiness_key"), "counts": counts}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_service": _compile(SERVICE_PATH, failures),
        "compile_service_test": _compile(SERVICE_TEST_PATH, failures),
        "service_plain_test": _run_plain_ok(SERVICE_TEST_PATH, failures),
        "spec": _check_spec(failures),
        "output_summary": _check_output_summary(failures),
        "service_source": _check_service_source(failures),
        "payload_probe": _check_payload_probe(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_10day_plan_summary_health_payload_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
