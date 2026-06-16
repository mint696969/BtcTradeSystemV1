# path: ./tools/test_phase4a_warroom_evidence_presentation_page_wiring_guard.py
# desc: Phase 4-A WarRoom evidence presentation page wiring guard.

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
SPEC_PATH = "tmp/docs/architecture/PHASE4A_WARROOM_EVIDENCE_PRESENTATION_PAGE_WIRING_2026-05-30.md"
HEALTH_GUARD_PATH = "tools/test_phase4a_health_evidence_presentation_page_wiring_guard.py"
WARROOM_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
HEALTH_PAGE_PATH = "btcts_next/src/btcts/apps/operator_ui/views/health_page.py"
SLOT_DEFS_PATH = "btcts_next/src/btcts/apps/operator_ui/components/slot_definitions.py"
TEST_PATH = "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_page_evidence_presentation_wiring.py"
PRIMARY_GUARD_PATH = "tools/test_phase4a_replay_market_engine_parity_total_guard.py"
FORBIDDEN_RUNTIME_ROOTS = [
    "btcts_next/src/btcts/market_engine",
    "btcts_next/src/btcts/collector",
    "btcts_next/src/btcts/collector_vnext",
    "btcts_next/src/btcts/execution",
    "btcts_next/src/btcts/broker",
]
PATTERNS = [
    "render_evidence_presentation_panel",
    "evidence_presentation_panel",
    "_warroom_evidence_presentation_payload",
]


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _compile(rel_path: str, failures: List[str]) -> Dict[str, Any]:
    path = REPO_ROOT / rel_path
    if not path.exists():
        failures.append(f"missing compile target: {rel_path}")
        return {"ok": False}
    cache = REPO_ROOT / "tmp" / "_guard_py_compile_cache" / "warroom_evidence_page_wiring"
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
            "WarRoom page evidence presentation wiring only",
            "session_state only",
            'st.session_state["warroom_evidence_presentation_payload"]',
            "tools/test_phase4a_warroom_evidence_presentation_page_wiring_guard.py",
        ],
        WARROOM_PAGE_PATH: [
            "from btcts.apps.operator_ui.components.evidence_presentation_panel import",
            "render_evidence_presentation_panel",
            "def _warroom_evidence_presentation_payload",
            'warroom_widget_slot("evidence_presentation_panel")',
        ],
        HEALTH_PAGE_PATH: [
            "render_evidence_presentation_panel",
            "def _snapshot_evidence_presentation_payload",
        ],
        SLOT_DEFS_PATH: [
            '"evidence_presentation_panel"',
            '"zone_id": "secondary"',
        ],
        PRIMARY_GUARD_PATH: [
            "tools/test_phase4a_warroom_evidence_presentation_page_wiring_guard.py",
            "warroom_evidence_presentation_page_wiring_guard",
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


def _check_wiring_boundaries(failures: List[str]) -> Dict[str, Any]:
    warroom = _read(WARROOM_PAGE_PATH)
    forbidden_warroom = [
        "D:" + "\\",
        "E:" + "\\",
        "health_warroom_evidence_presentation_payload(",
        "health_warroom_evidence_presentation_model(",
        "build_real_data_validation_evidence_summary(",
        "load_health_snapshot",
        "runtime_state_path",
        "market_engine_signal",
        "collector_write_path",
        "place" + "_" + "order(",
        "broker" + "_" + "order(",
        "training_dataset",
        "inference_job",
    ]
    hits = [token for token in forbidden_warroom if token in warroom]
    for token in hits:
        failures.append(f"warroom_page contains forbidden evidence wiring token: {token}")
    slot_pos = warroom.find('warroom_widget_slot("evidence_presentation_panel")')
    section_pos = warroom.find("def _render_warroom_evidence_presentation()")
    if section_pos < 0 or slot_pos < section_pos:
        failures.append("warroom evidence presentation slot must be after section function definition")
    return {"hits": hits, "section_pos": section_pos, "slot_pos": slot_pos}


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
                failures.append(f"runtime path references WarRoom evidence presentation wiring: {rel}")
    return {"hit_count": len(hits), "hits": hits}


def main() -> int:
    failures: List[str] = []
    checks = {
        "compile_warroom_page": _compile(WARROOM_PAGE_PATH, failures),
        "compile_slot_defs": _compile(SLOT_DEFS_PATH, failures),
        "compile_test": _compile(TEST_PATH, failures),
        "compile_self": _compile("tools/test_phase4a_warroom_evidence_presentation_page_wiring_guard.py", failures),
        "health_guard": _run_json_guard(HEALTH_GUARD_PATH, failures),
        "plain_test": _run_plain_ok(TEST_PATH, failures),
        "docs": _check_docs(failures),
        "wiring_boundaries": _check_wiring_boundaries(failures),
        "runtime_references": _scan_runtime_references(failures),
    }
    summary = {
        "phase": "phase4a_warroom_evidence_presentation_page_wiring_guard",
        "checks": checks,
        "failures": failures,
        "ok": len(failures) == 0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
