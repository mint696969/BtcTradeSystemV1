# path: ./tools/test_phase4a_operational_readiness_hot_cold_10day_plan_summary_health_payload_close_guard.py
# desc: Close guard for Phase 4-A Hot/Cold reviewed 10-day plan summary Health payload. No D/E scan/copy/delete/GC.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_10day_plan_summary_health_payload_close_guard.py"
PAYLOAD_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_10day_plan_summary_health_payload_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_10DAY_PLAN_SUMMARY_HEALTH_PAYLOAD_2026-06-02.md"
SERVICE_PATH = "btcts_next/src/btcts/apps/operator_ui/hot_cold_retention_safety_service.py"
SERVICE_TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_hot_cold_retention_safety_service.py"
TEN_DAY_OUTPUT_PATH = "tmp/work/operator_operational_readiness/outputs/hot_cold_10day_dry_run_plan_and_review_v1_20260602T140216.582610Z.json"
TEN_DAY_PLAN_HASH = "e5bf5d3c6630c10084fc44c97614dc48c3bc4e8147e98683831eefa2923f9eb6"

COMPILE_FILES = [
    SELF_PATH,
    PAYLOAD_GUARD_PATH,
    SERVICE_PATH,
    SERVICE_TEST_PATH,
]

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
    "--execute",
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_10day_plan_summary_health_payload_close"
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
    return {
        "ok": ok,
        "returncode": proc.returncode,
        "phase": parsed.get("phase"),
        "json": parsed,
        "stdout_tail": (proc.stdout or "")[-1800:],
        "stderr_tail": (proc.stderr or "")[-1800:],
    }


def _run_plain_ok(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _check_spec(failures: list[str]) -> dict[str, Any]:
    text = _read(SPEC_PATH)
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
        PAYLOAD_GUARD_PATH,
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"10-day plan summary close spec missing fragment: {fragment}")
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
        "def load_hot_cold_retention_safety_payload",
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
        failures.append(f"service missing required 10-day summary close fragment: {fragment}")
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


def _check_payload_guard_boundary(payload_result: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    parsed = payload_result.get("json") if isinstance(payload_result, dict) else None
    checks = parsed.get("checks") if isinstance(parsed, dict) else None
    service_source = checks.get("service_source") if isinstance(checks, dict) else None
    output_summary = checks.get("output_summary") if isinstance(checks, dict) else None
    payload_probe = checks.get("payload_probe") if isinstance(checks, dict) else None
    ok = (
        isinstance(service_source, dict)
        and service_source.get("missing") == []
        and service_source.get("forbidden_hits") == []
        and isinstance(output_summary, dict)
        and output_summary.get("ok") is True
        and isinstance(payload_probe, dict)
        and payload_probe.get("ok") is True
    )
    if not ok:
        failures.append("payload guard must prove reviewed 10-day summary Health payload boundary")
    return {
        "ok": ok,
        "verified_by_payload_guard": True,
        "service_source": service_source,
        "output_summary": output_summary,
        "payload_probe": payload_probe,
        "path": PAYLOAD_GUARD_PATH,
    }


def main() -> int:
    failures: list[str] = []
    payload_guard = _run_json_guard(PAYLOAD_GUARD_PATH, failures)
    checks = {
        "compile_files": {rel: _compile(rel, failures) for rel in COMPILE_FILES},
        "payload_guard": payload_guard,
        "service_plain_test": _run_plain_ok(SERVICE_TEST_PATH, failures),
        "spec": _check_spec(failures),
        "output_summary": _check_output_summary(failures),
        "service_source": _check_service_source(failures),
        "payload_probe": _check_payload_probe(failures),
        "payload_guard_boundary": _check_payload_guard_boundary(payload_guard, failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_10day_plan_summary_health_payload_close_guard",
        "close_status": "closed" if not failures else "open",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
