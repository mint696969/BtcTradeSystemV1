# path: ./tools/test_phase4a_operator_ui_health_audit_tail_latency_budget_guard.py
# desc: Phase 4-A Operator UI Health audit-tail latency budget guard.

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

SELF_PATH = "tools/test_phase4a_operator_ui_health_audit_tail_latency_budget_guard.py"
AUDIT_MODEL_PATH = "btcts_next/src/btcts/apps/operator_ui/health_audit_read_model.py"
AUDIT_TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_health_audit_read_model.py"
AUDIT_BOUNDARY_GUARD_PATH = "tools/test_phase4a_operator_ui_health_audit_read_model_bounded_inputs_guard.py"
SNAPSHOT_MODEL_PATH = "btcts_next/src/btcts/apps/operator_ui/health_snapshot_read_model.py"
HEALTH_SERVICE_PATH = "btcts_next/src/btcts/apps/operator_ui/health_data_service.py"
HEALTH_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"

COMPILE_TARGETS = [
    SELF_PATH,
    AUDIT_MODEL_PATH,
    AUDIT_TEST_PATH,
    SNAPSHOT_MODEL_PATH,
    HEALTH_SERVICE_PATH,
    HEALTH_PAGE_PATH,
]

REQUIRED_AUDIT_MODEL_FRAGMENTS = [
    "HEALTH_AUDIT_MAX_LINES_BY_RANGE = {",
    '"1h": 12000',
    '"24h": 36000',
    '"1w": 72000',
    'HEALTH_AUDIT_DEFAULT_MAX_LINES = HEALTH_AUDIT_MAX_LINES_BY_RANGE["1h"]',
    "def audit_max_lines_for_range(range_key: str) -> int:",
    "HEALTH_AUDIT_MAX_LINES_BY_RANGE.get(",
    "bounded_input_only",
]

FORBIDDEN_AUDIT_MODEL_FRAGMENTS = [
    "return 50000",
    "return 120000",
    "return 240000",
    "streamlit",
    ".rglob(",
    "os.walk(",
    "load_state(",
    "build_health_snapshot_read_model",
    "place_order",
    "broker_order",
]

REQUIRED_TEST_FRAGMENTS = [
    'audit_max_lines_for_range("1h") == 12000',
    'audit_max_lines_for_range("24h") == 36000',
    'audit_max_lines_for_range("1w") == 72000',
    'audit_max_lines_for_range("unknown") == 12000',
    "calls == [36000]",
    "audit_input.max_lines == 36000",
]

FORBIDDEN_HEALTH_PAGE_FRAGMENTS = [
    "health_audit_read_model",
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operator_ui_health_audit_tail_latency_budget"
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
        "audit_boundary_guard": _run_json_guard(AUDIT_BOUNDARY_GUARD_PATH, failures),
        "audit_model_budget": _check_fragments(AUDIT_MODEL_PATH, REQUIRED_AUDIT_MODEL_FRAGMENTS, FORBIDDEN_AUDIT_MODEL_FRAGMENTS, failures),
        "audit_model_test_fragments": _check_fragments(AUDIT_TEST_PATH, REQUIRED_TEST_FRAGMENTS, [], failures),
        "audit_model_test": _run_plain_ok(AUDIT_TEST_PATH, failures),
        "coverage_regression": _run_plain_ok("btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_coverage.py", failures),
        "health_digest_regression": _run_plain_ok("btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_health_digest.py", failures),
        "health_page_render_only": _check_fragments(HEALTH_PAGE_PATH, [], FORBIDDEN_HEALTH_PAGE_FRAGMENTS, failures),
        "snapshot_model_still_pure": _check_fragments(SNAPSHOT_MODEL_PATH, [], FORBIDDEN_SNAPSHOT_MODEL_FRAGMENTS, failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operator_ui_health_audit_tail_latency_budget_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
