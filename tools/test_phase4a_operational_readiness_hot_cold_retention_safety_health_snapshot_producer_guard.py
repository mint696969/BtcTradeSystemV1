# path: ./tools/test_phase4a_operational_readiness_hot_cold_retention_safety_health_snapshot_producer_guard.py
# desc: Phase 4-A Hot/Cold retention safety Health snapshot producer guard. No D/E scan, no copy/delete.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_safety_health_snapshot_producer_guard.py"
HEALTH_WIRING_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_safety_health_wiring_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_RETENTION_SAFETY_HEALTH_SNAPSHOT_PRODUCER_2026-06-02.md"
SERVICE_PATH = "btcts_next/src/btcts/apps/operator_ui/hot_cold_retention_safety_service.py"
SERVICE_TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_hot_cold_retention_safety_service.py"
HEALTH_SERVICE_PATH = "btcts_next/src/btcts/apps/operator_ui/health_data_service.py"

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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_retention_safety_health_snapshot_producer"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=900)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1600:], "stderr_tail": (proc.stderr or "")[-1600:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "stdout_tail": (proc.stdout or "")[-1600:], "stderr_tail": (proc.stderr or "")[-1600:]}


def _run_plain_ok(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _check_spec(failures: list[str]) -> dict[str, Any]:
    required = [
        "Hot/Cold retention safety Health snapshot producer",
        "hot_cold_retention_safety_payload",
        "build_hot_cold_retention_safety_payload",
        "load_hot_cold_retention_safety_payload",
        "bounded precomputed JSON outputs",
        "does not",
        "scan D/E",
        "copy files",
        "delete files",
        "hot_retention_days = 10",
        "min_delete_age_hours = 240",
        "previous 48h-style plan is abandoned for execute",
        SELF_PATH,
    ]
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing spec fragment: {fragment}")
    return {"missing": missing}


def _check_service_source(failures: list[str]) -> dict[str, Any]:
    text = _read(SERVICE_PATH)
    required = [
        "HOT_RETENTION_DAYS = 10",
        "MIN_DELETE_AGE_HOURS = 240.0",
        "def build_hot_cold_retention_safety_payload",
        "def load_hot_cold_retention_safety_payload",
        "Does not scan hot/cold roots.",
        '\"candidate_files\": 0',
        "previous_plan_abandoned_for_execute",
        "Rebuild dry-run plan with min_age_hours=240 before any delete.",
        "not_filesystem_scan",
        "not_copy_executor",
        "not_delete_executor",
        "no_double_count_hot_cold_for_simulation_training",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    forbidden_hits = [token for token in FORBIDDEN_SERVICE_TOKENS if token in text]
    for fragment in missing:
        failures.append(f"service missing required fragment: {fragment}")
    for token in forbidden_hits:
        failures.append(f"service contains forbidden D/E scan/delete token: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _check_health_service_wiring(failures: list[str]) -> dict[str, Any]:
    text = _read(HEALTH_SERVICE_PATH)
    required = [
        "from btcts.apps.operator_ui.hot_cold_retention_safety_service import",
        "load_hot_cold_retention_safety_payload",
        "hot_cold_retention_safety_payload = load_hot_cold_retention_safety_payload()",
        '"hot_cold_retention_safety_payload": hot_cold_retention_safety_payload',
        '"hot_cold_retention_safety": hot_cold_retention_safety_payload',
        '"operational_readiness_hot_cold_retention_safety": hot_cold_retention_safety_payload',
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"health_data_service missing safety producer wiring: {fragment}")
    return {"missing": missing}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_service": _compile(SERVICE_PATH, failures),
        "compile_service_test": _compile(SERVICE_TEST_PATH, failures),
        "compile_health_service": _compile(HEALTH_SERVICE_PATH, failures),
        "health_wiring_guard": _run_json_guard(HEALTH_WIRING_GUARD_PATH, failures),
        "service_plain_test": _run_plain_ok(SERVICE_TEST_PATH, failures),
        "spec": _check_spec(failures),
        "service_source": _check_service_source(failures),
        "health_service_wiring": _check_health_service_wiring(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_retention_safety_health_snapshot_producer_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
