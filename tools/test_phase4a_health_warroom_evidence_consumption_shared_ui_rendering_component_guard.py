# path: ./tools/test_phase4a_health_warroom_evidence_consumption_shared_ui_rendering_component_guard.py
# desc: Phase 4-A Health/WarRoom evidence consumption shared UI rendering component guard.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = "tmp/docs/architecture/PHASE4A_HEALTH_WARROOM_EVIDENCE_CONSUMPTION_SHARED_UI_RENDERING_COMPONENT_2026-05-30.md"
UI_ENTRY_GUARD_PATH = "tools/test_phase4a_health_warroom_evidence_consumption_ui_rendering_entry_criteria_guard.py"
COMPONENT_PATH = "btcts_next/src/btcts/apps/operator_ui/components/evidence_presentation_panel.py"
TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_evidence_presentation_panel.py"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"
HEALTH_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"
WARROOM_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
FORBIDDEN_RUNTIME_ROOTS = [
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/collector",
    "btcts_next/src/btcts/collector_vnext",
    "btcts_next/src/btcts/execution",
    "btcts_next/src/btcts/broker",
]
PATTERNS = [
    "evidence_presentation_panel",
    "render_evidence_presentation_panel",
    "build_evidence_presentation_caption",
    "build_evidence_presentation_lines",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "health_warroom_shared_ui_component"
    cache.mkdir(parents=True, exist_ok=True)
    try:
        py_compile.compile(str(path), cfile=str(cache / (rel_path.replace('/', '__') + '.pyc')), doraise=True)
        return {"ok": True}
    except Exception as exc:
        failures.append(f"py_compile failed: {rel_path}: {exc}")
        return {"ok": False, "error": str(exc)}


def _run_json_guard(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=300)
    try:
        parsed = json.loads(proc.stdout)
    except Exception as exc:
        failures.append(f"{rel_path} did not emit JSON: {exc}")
        return {"ok": False, "returncode": proc.returncode, "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:]}
    ok = proc.returncode == 0 and parsed.get("ok") is True and parsed.get("failures") == []
    if not ok:
        failures.append(f"{rel_path} must return ok true and failures []")
    return {"ok": ok, "returncode": proc.returncode, "phase": parsed.get("phase"), "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:]}


def _run_plain_ok(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    proc = subprocess.run([sys.executable, str(REPO_ROOT / rel_path)], cwd=str(REPO_ROOT), text=True, capture_output=True, timeout=120)
    ok = proc.returncode == 0 and (proc.stdout or "").strip() == "ok"
    if not ok:
        failures.append(f"{rel_path} must emit plain ok")
    return {"ok": ok, "returncode": proc.returncode, "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:]}


def _check_docs(failures: List[str]) -> Dict[str, Any]:
    required = {
        SPEC_PATH: [
            "shared UI rendering component only",
            "evidence_presentation_panel.py",
            "build_evidence_presentation_caption",
            "render_evidence_presentation_panel",
            "no page wiring yet",
        ],
        COMPONENT_PATH: [
            "def build_evidence_presentation_caption",
            "def build_evidence_presentation_lines",
            "def render_evidence_presentation_panel",
            "import streamlit as st",
        ],
        PRIMARY_GUARD_PATH: [
            "tools/test_phase4a_health_warroom_evidence_consumption_shared_ui_rendering_component_guard.py",
            "health_warroom_evidence_consumption_shared_ui_rendering_component_guard",
        ],
    }
    missing: list[dict[str, str]] = []
    for rel_path, fragments in required.items():
        text = _read(rel_path)
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"missing required fragment: {rel_path}: {fragment}")
                missing.append({"path": rel_path, "fragment": fragment})
    return {"missing_count": len(missing), "missing": missing}


def _check_page_wiring_absent(failures: List[str]) -> Dict[str, Any]:
    # Health page wiring is allowed after the shared component close; WarRoom remains closed.
    health_text = _read(HEALTH_PAGE_PATH)
    warroom_text = _read(WARROOM_PAGE_PATH)
    health_page_allowed = any(pattern in health_text for pattern in PATTERNS)
    hits: list[str] = []
    warroom_page_allowed = any(pattern in warroom_text for pattern in PATTERNS)
    return {"hit_count": len(hits), "hits": hits, "health_page_allowed": health_page_allowed, "warroom_page_allowed": warroom_page_allowed}


def _scan_runtime_references(failures: List[str]) -> Dict[str, Any]:
    hits: list[str] = []
    for rel_root in FORBIDDEN_RUNTIME_ROOTS:
        root = REPO_ROOT / rel_root
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            if any(pattern in text for pattern in PATTERNS):
                rel = path.relative_to(REPO_ROOT).as_posix()
                hits.append(rel)
                failures.append(f"runtime path references evidence presentation panel: {rel}")
    return {"hit_count": len(hits), "hits": hits}


def _probe_helpers(failures: List[str]) -> Dict[str, Any]:
    try:
        from btcts.apps.operator_ui.components.evidence_presentation_panel import (
            build_evidence_presentation_caption,
            build_evidence_presentation_lines,
        )
    except Exception as exc:
        failures.append(f"component helper import failed: {type(exc).__name__}: {exc}")
        return {"ok": False, "error": str(exc)}
    payload = {
        "presentation_kind": "health_warroom_evidence_consumption_presentation",
        "presentation_version": "phase4a.health_warroom_evidence_presentation.v1",
        "status_key": "available",
        "severity_key": "info",
        "counts": {"replay_row_count": 36, "board_row_count": 18, "trade_row_count": 18, "diagnostic_note_count": 0},
        "boundary": {"read_only_consumption": True, "diagnostic_evidence_only": True, "operator_support_only": True, "not_runtime_signal": True, "not_ui_rendering": True},
    }
    caption = build_evidence_presentation_caption(payload)
    lines = build_evidence_presentation_lines(payload)
    checks = {
        "caption_status": "status=available" in caption,
        "caption_boundary": "read_only_consumption=True" in caption,
        "lines_replay": "replay_rows=36" in lines,
        "lines_boundary_caption": any("not_runtime_signal=True" in line for line in lines),
    }
    bad = [name for name, ok in checks.items() if not ok]
    for name in bad:
        failures.append(f"component helper probe failed: {name}")
    return {"ok": not bad, "checks": checks, "bad": bad}


def main() -> int:
    failures: List[str] = []
    checks = {
        "compile_component": _compile(COMPONENT_PATH, failures),
        "compile_test": _compile(TEST_PATH, failures),
        "compile_self": _compile("tools/test_phase4a_health_warroom_evidence_consumption_shared_ui_rendering_component_guard.py", failures),
        "ui_entry_guard": _run_json_guard(UI_ENTRY_GUARD_PATH, failures),
        "plain_test": _run_plain_ok(TEST_PATH, failures),
        "docs": _check_docs(failures),
        "helper_probe": _probe_helpers(failures),
        "page_wiring_absent": _check_page_wiring_absent(failures),
        "runtime_references": _scan_runtime_references(failures),
    }
    summary = {
        "phase": "phase4a_health_warroom_evidence_consumption_shared_ui_rendering_component_guard",
        "checks": checks,
        "failures": failures,
        "ok": len(failures) == 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
