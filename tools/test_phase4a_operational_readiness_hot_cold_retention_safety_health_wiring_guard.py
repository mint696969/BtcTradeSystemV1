# path: ./tools/test_phase4a_operational_readiness_hot_cold_retention_safety_health_wiring_guard.py
# desc: Phase 4-A Hot/Cold retention safety Health wiring guard. No D/E scan, no copy/delete.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_safety_health_wiring_guard.py"
PANEL_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_safety_panel_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_RETENTION_SAFETY_HEALTH_WIRING_2026-06-02.md"
HEALTH_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"
HEALTH_TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_health_page_evidence_presentation_wiring.py"
PANEL_PATH = "btcts_next/src/btcts/apps/operator_ui/components/hot_cold_retention_safety_panel.py"

FORBIDDEN_HEALTH_TOKENS = [
    "rglob(",
    "glob(",
    "os.scandir(",
    ".unlink(",
    ".rmdir(",
    "shutil.rmtree(",
    "os.remove(",
    "os.unlink(",
    "archive_gc_enable",
    "build_explicit_hot_cold_delete_plan",
    "run_explicit_hot_cold_small_batch_delete",
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_retention_safety_health_wiring"
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
        "Hot/Cold retention safety Health wiring",
        "already-provided payload from the Health snapshot only",
        "hot_cold_retention_safety_payload",
        "hot_cold_retention_safety",
        "operational_readiness_hot_cold_retention_safety",
        "render_hot_cold_retention_safety_panel(payload, expanded=False)",
        "does not build the payload",
        "does not scan D/E",
        "does not copy or delete files",
        SELF_PATH,
    ]
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing spec fragment: {fragment}")
    return {"missing": missing}


def _check_health_wiring(failures: list[str]) -> dict[str, Any]:
    health = _read(HEALTH_PAGE_PATH)
    required = [
        "from btcts.apps.operator_ui.components.hot_cold_retention_safety_panel import",
        "render_hot_cold_retention_safety_panel",
        "def _snapshot_hot_cold_retention_safety_payload(snapshot: dict) -> dict | None:",
        "Return already-provided Hot/Cold retention safety payload from the Health snapshot only.",
        "hot_cold_retention_safety_payload",
        "hot_cold_retention_safety",
        "operational_readiness_hot_cold_retention_safety",
        "def _render_hot_cold_retention_safety_section() -> None:",
        "render_hot_cold_retention_safety_panel(safety_payload, expanded=False)",
        'health_widget_slot("hot_cold_retention_safety_panel")',
    ]
    missing = [fragment for fragment in required if fragment not in health]
    forbidden_hits = [token for token in FORBIDDEN_HEALTH_TOKENS if token in health]
    for fragment in missing:
        failures.append(f"Health page missing safety wiring fragment: {fragment}")
    for token in forbidden_hits:
        failures.append(f"Health page contains forbidden scan/delete token: {token}")

    evidence_idx = health.find('health_widget_slot("evidence_presentation_panel")')
    safety_idx = health.find('health_widget_slot("hot_cold_retention_safety_panel")')
    if safety_idx < 0 or evidence_idx < 0:
        failures.append("Health safety/evidence slot ordering cannot be checked")
    elif safety_idx > evidence_idx:
        failures.append("Hot/Cold safety panel should be rendered before Real-data validation evidence panel")

    return {"missing": missing, "forbidden_hits": forbidden_hits, "safety_slot_index": safety_idx, "evidence_slot_index": evidence_idx}


def _check_test_updated(failures: list[str]) -> dict[str, Any]:
    text = _read(HEALTH_TEST_PATH)
    required = [
        "render_hot_cold_retention_safety_panel",
        "_snapshot_hot_cold_retention_safety_payload",
        'health_widget_slot("hot_cold_retention_safety_panel")',
        "hot_cold_retention_safety_payload",
        "operational_readiness_hot_cold_retention_safety",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"Health page test missing safety wiring assertion: {fragment}")
    return {"missing": missing}


def _check_panel_still_bounded(failures: list[str]) -> dict[str, Any]:
    text = _read(PANEL_PATH)
    required = [
        "def render_hot_cold_retention_safety_panel",
        "Does not scan files or execute copy/delete.",
        "not_filesystem_scan",
        "not_copy_executor",
        "not_delete_executor",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"panel missing bounded fragment: {fragment}")
    return {"missing": missing}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_health_page": _compile(HEALTH_PAGE_PATH, failures),
        "compile_health_test": _compile(HEALTH_TEST_PATH, failures),
        "panel_guard": _run_json_guard(PANEL_GUARD_PATH, failures),
        "health_plain_test": _run_plain_ok(HEALTH_TEST_PATH, failures),
        "spec": _check_spec(failures),
        "health_wiring": _check_health_wiring(failures),
        "health_test_updated": _check_test_updated(failures),
        "panel_still_bounded": _check_panel_still_bounded(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_retention_safety_health_wiring_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
