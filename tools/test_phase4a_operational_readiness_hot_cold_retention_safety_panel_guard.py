# path: ./tools/test_phase4a_operational_readiness_hot_cold_retention_safety_panel_guard.py
# desc: Phase 4-A Hot/Cold retention safety panel component guard. No Health page wiring, no D/E scan.

from __future__ import annotations

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

SELF_PATH = "tools/test_phase4a_operational_readiness_hot_cold_retention_safety_panel_guard.py"
ENTRY_GUARD_PATH = "tools/test_phase4a_operational_readiness_hot_cold_10day_retention_health_safety_entry_guard.py"
SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_RETENTION_SAFETY_PANEL_COMPONENT_2026-06-02.md"
PANEL_PATH = "btcts_next/src/btcts/apps/operator_ui/components/hot_cold_retention_safety_panel.py"
TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_hot_cold_retention_safety_panel.py"
HEALTH_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"
HEALTH_WIRING_SPEC_PATH = "tmp/docs/architecture/PHASE4A_OPERATIONAL_READINESS_HOT_COLD_RETENTION_SAFETY_HEALTH_WIRING_2026-06-02.md"

FORBIDDEN_PANEL_TOKENS = [
    "Path(",
    "rglob(",
    "glob(",
    "os.scandir(",
    ".unlink(",
    ".rmdir(",
    "shutil.rmtree(",
    "os.remove(",
    "os.unlink(",
    "archive_gc_enable",
    "load_health_snapshot(",
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
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "hot_cold_retention_safety_panel"
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
        "Hot/Cold retention safety panel component",
        "already-built Hot/Cold retention safety payloads",
        "build_hot_cold_retention_safety_caption",
        "build_hot_cold_retention_safety_lines",
        "render_hot_cold_retention_safety_panel",
        "display-only",
        "scan D/E",
        "copy files",
        "delete files",
        "Health page wiring is not implemented in this slice",
        SELF_PATH,
    ]
    text = _read(SPEC_PATH)
    missing = [fragment for fragment in required if fragment not in text]
    for fragment in missing:
        failures.append(f"missing spec fragment: {fragment}")
    return {"missing": missing}


def _check_panel_source(failures: list[str]) -> dict[str, Any]:
    text = _read(PANEL_PATH)
    required = [
        "def build_hot_cold_retention_safety_caption",
        "def build_hot_cold_retention_safety_lines",
        "def render_hot_cold_retention_safety_panel",
        "Does not scan files or execute copy/delete.",
        "read_only_display",
        "already_built_payload_only",
        "not_filesystem_scan",
        "not_copy_executor",
        "not_delete_executor",
        "not_runtime_state_writer",
        "not_collector_state_mutation",
        "not_market_engine_input",
        "not_broker_or_order_automation",
        "not_inference_or_training",
    ]
    missing = [fragment for fragment in required if fragment not in text]
    forbidden_hits = [token for token in FORBIDDEN_PANEL_TOKENS if token in text]
    for fragment in missing:
        failures.append(f"panel missing required fragment: {fragment}")
    for token in forbidden_hits:
        failures.append(f"panel contains forbidden scan/delete token: {token}")
    return {"missing": missing, "forbidden_hits": forbidden_hits}


def _check_health_not_wired_yet(failures: list[str]) -> dict[str, Any]:
    health_wiring_open = (REPO_ROOT / HEALTH_WIRING_SPEC_PATH).exists()
    health = _read(HEALTH_PAGE_PATH)
    hits = [
        token for token in [
            "render_hot_cold_retention_safety_panel",
            "build_hot_cold_retention_safety_caption",
            "hot_cold_retention_safety_panel",
        ]
        if token in health
    ]
    if not health_wiring_open:
        for token in hits:
            failures.append(f"Health page must not be wired to safety panel in component-only slice: {token}")
    return {"hits": hits, "health_wiring_open": health_wiring_open}


def main() -> int:
    failures: list[str] = []
    checks = {
        "compile_self": _compile(SELF_PATH, failures),
        "compile_panel": _compile(PANEL_PATH, failures),
        "compile_test": _compile(TEST_PATH, failures),
        "entry_guard": _run_json_guard(ENTRY_GUARD_PATH, failures),
        "plain_test": _run_plain_ok(TEST_PATH, failures),
        "spec": _check_spec(failures),
        "panel_source": _check_panel_source(failures),
        "health_not_wired_yet": _check_health_not_wired_yet(failures),
    }
    payload = {
        "ok": not failures,
        "phase": "phase4a_operational_readiness_hot_cold_retention_safety_panel_guard",
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
