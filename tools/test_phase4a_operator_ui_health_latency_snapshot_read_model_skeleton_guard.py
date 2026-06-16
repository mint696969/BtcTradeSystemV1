# path: ./tools/test_phase4a_operator_ui_health_latency_snapshot_read_model_skeleton_guard.py
# desc: Phase 4-A Operator UI Health latency snapshot read-model skeleton guard.

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

SELF_PATH = "tools/test_phase4a_operator_ui_health_latency_snapshot_read_model_skeleton_guard.py"
ENTRY_GUARD_PATH = "tools/test_phase4a_operator_ui_health_latency_snapshot_responsibility_entry_criteria_guard.py"
READ_MODEL_PATH = "btcts_next/src/btcts/apps/operator_ui/health_snapshot_read_model.py"
READ_MODEL_TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_health_snapshot_read_model.py"
HEALTH_SERVICE_PATH = "btcts_next/src/btcts/apps/operator_ui/health_data_service.py"
HEALTH_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"
AUDIT_MODEL_PATH = "btcts_next/src/btcts/apps/operator_ui/health_audit_read_model.py"

COMPILE_TARGETS = [
    SELF_PATH,
    READ_MODEL_PATH,
    READ_MODEL_TEST_PATH,
    HEALTH_SERVICE_PATH,
    HEALTH_PAGE_PATH,
    AUDIT_MODEL_PATH,
]

REQUIRED_READ_MODEL_FRAGMENTS = [
    'HEALTH_SNAPSHOT_READ_MODEL_VERSION = "health_snapshot_read_model.v1"',
    "HEALTH_SNAPSHOT_BUNDLE_KEYS = (",
    "def build_health_snapshot_read_model(",
    "compose_existing_bundles_only_no_io",
    "views_are_render_only",
    "must not read audit",
    "scan data roots, call Streamlit, mutate collector runtime state",
]

FORBIDDEN_READ_MODEL_FRAGMENTS = [
    "read_jsonl_tail",
    "_read_recent_audit_rows",
    "core_paths",
    "load_state(",
    "load_latest_market_state",
    "market_state_diagnostics",
    "streamlit",
    ".rglob(",
    "os.walk(",
    "archive_gc",
    "place_order",
    "broker_order",
]

REQUIRED_HEALTH_SERVICE_FRAGMENTS = [
    "from btcts.apps.operator_ui.health_snapshot_read_model import (",
    "build_health_snapshot_read_model",
    "return build_health_snapshot_read_model(",
    "current_state_bundle=current_state_bundle",
    "timeline_bundle=timeline_bundle",
    "continuity_bundle=continuity_bundle",
    "anomaly_bundle=anomaly_bundle",
    "page_meta_bundle=page_meta_bundle",
    "from btcts.apps.operator_ui.health_audit_read_model import (",
    "load_health_audit_input",
    "audit_input = load_health_audit_input(range_key=range_key)",
    "audit_rows = list(audit_input.rows)",
]

FORBIDDEN_HEALTH_PAGE_FRAGMENTS = [
    "build_health_snapshot_read_model",
    "health_snapshot_read_model.py",
    "read_jsonl_tail(",
    ".rglob(",
    "os.walk(",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: list[str]) -> dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False, "missing": True}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "operator_ui_health_snapshot_read_model_skeleton"
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
    stdout_tail = (proc.stdout or "")[-2000:]
    stderr_tail = (proc.stderr or "")[-2000:]
    ok = proc.returncode == 0 and proc.stdout.strip() == "ok"
    if not ok:
        failures.append(
            f"{rel_path} must emit plain ok; "
            f"returncode={proc.returncode}; stdout_tail={stdout_tail!r}; stderr_tail={stderr_tail!r}"
        )
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": stdout_tail, "stderr_tail": stderr_tail}


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
    compile_checks = {rel: _compile(rel, failures) for rel in COMPILE_TARGETS}
    checks = {
        "compile": compile_checks,
        "entry_guard": _run_json_guard(ENTRY_GUARD_PATH, failures),
        "read_model_source": _check_fragments(READ_MODEL_PATH, REQUIRED_READ_MODEL_FRAGMENTS, FORBIDDEN_READ_MODEL_FRAGMENTS, failures),
        "health_service_wiring": _check_fragments(HEALTH_SERVICE_PATH, REQUIRED_HEALTH_SERVICE_FRAGMENTS, [], failures),
        "health_page_render_only": _check_fragments(HEALTH_PAGE_PATH, [], FORBIDDEN_HEALTH_PAGE_FRAGMENTS, failures),
        "read_model_test": _run_plain_ok(READ_MODEL_TEST_PATH, failures),
        "health_digest_regression": _run_plain_ok("btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_health_digest.py", failures),
        "coverage_regression": _run_plain_ok("btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_coverage.py", failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operator_ui_health_latency_snapshot_read_model_skeleton_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
