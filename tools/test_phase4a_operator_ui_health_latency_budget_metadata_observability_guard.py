# path: ./tools/test_phase4a_operator_ui_health_latency_budget_metadata_observability_guard.py
# desc: Phase 4-A Operator UI Health audit budget metadata observability guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operator_ui_health_latency_budget_metadata_observability_guard.py"
BUDGET_GUARD_PATH = "tools/test_phase4a_operator_ui_health_audit_tail_latency_budget_guard.py"
HEALTH_SERVICE_PATH = "btcts_next/src/btcts/apps/operator_ui/health_data_service.py"
HEALTH_DIGEST_TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_health_digest.py"
SNAPSHOT_MODEL_PATH = "btcts_next/src/btcts/apps/operator_ui/health_snapshot_read_model.py"
HEALTH_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"

COMPILE_TARGETS = [
    SELF_PATH,
    HEALTH_SERVICE_PATH,
    HEALTH_DIGEST_TEST_PATH,
    SNAPSHOT_MODEL_PATH,
    HEALTH_PAGE_PATH,
]

REQUIRED_HEALTH_SERVICE_FRAGMENTS = [
    "def health_audit_input_metadata(audit_input: HealthAuditInput) -> dict[str, Any]:",
    'metadata.pop("rows", None)',
    'metadata["rows_omitted_from_metadata"] = True',
    "audit_input: HealthAuditInput | None = None",
    '"health_audit_input": audit_metadata',
    '"health_audit_budget": audit_metadata',
    "audit_input=audit_input",
]

FORBIDDEN_HEALTH_SERVICE_FRAGMENTS = [
    '"rows": audit_metadata',
    '"rows": audit_input.rows',
]

REQUIRED_TEST_FRAGMENTS = [
    'page_meta_bundle["health_audit_budget"]["max_lines"] == 12000',
    'page_meta_bundle["health_audit_budget"]["row_count"] is None',
    'snapshot["health_audit_input"]["max_lines"] == 12000',
    'snapshot["health_audit_input"]["row_count"] == 0',
    '"rows" not in snapshot["health_audit_input"]',
    'snapshot["health_audit_budget"] == snapshot["health_audit_input"]',
]

FORBIDDEN_HEALTH_PAGE_FRAGMENTS = [
    "health_audit_input",
    "health_audit_budget",
    "read_jsonl_tail(",
    ".rglob(",
    "os.walk(",
]

FORBIDDEN_SNAPSHOT_MODEL_FRAGMENTS = [
    "health_audit_read_model",
    "read_jsonl_tail",
    "core_paths",
    "streamlit",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operator_ui_health_latency_budget_metadata_observability"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace("/", "__") + ".pyc")), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_plain_ok(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / rel_path)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=120,
    )
    ok = proc.returncode == 0 and proc.stdout.strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}


def _run_json_guard(rel_path: str, failures: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / rel_path)],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=1200,
    )
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-1200:], "stderr_tail": (proc.stderr or "")[-1200:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase")}


def _check_fragments(rel_path: str, required: list[str], forbidden: list[str], failures: list[str]) -> dict[str, Any]:
    text = _read(rel_path)
    if not text:
        failures.append(f"required file missing or empty: {rel_path}")
        return {"missing_file": True, "missing": required, "forbidden_hits": []}
    missing = [fragment for fragment in required if fragment not in text]
    forbidden_hits = [fragment for fragment in forbidden if fragment in text]
    for fragment in missing:
        failures.append(f"missing fragment in {rel_path}: {fragment}")
    for fragment in forbidden_hits:
        failures.append(f"forbidden fragment in {rel_path}: {fragment}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile": {rel: _compile(rel, failures) for rel in COMPILE_TARGETS},
        "budget_guard": _run_json_guard(BUDGET_GUARD_PATH, failures),
        "health_service_metadata_wiring": _check_fragments(HEALTH_SERVICE_PATH, REQUIRED_HEALTH_SERVICE_FRAGMENTS, FORBIDDEN_HEALTH_SERVICE_FRAGMENTS, failures),
        "health_digest_test_contract": _check_fragments(HEALTH_DIGEST_TEST_PATH, REQUIRED_TEST_FRAGMENTS, [], failures),
        "health_digest_regression": _run_plain_ok(HEALTH_DIGEST_TEST_PATH, failures),
        "coverage_regression": _run_plain_ok("btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_coverage.py", failures),
        "health_page_still_no_metadata_logic": _check_fragments(HEALTH_PAGE_PATH, [], FORBIDDEN_HEALTH_PAGE_FRAGMENTS, failures),
        "snapshot_model_still_pure": _check_fragments(SNAPSHOT_MODEL_PATH, [], FORBIDDEN_SNAPSHOT_MODEL_FRAGMENTS, failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operator_ui_health_latency_budget_metadata_observability_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
